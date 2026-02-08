"""
Yoga Engine (Phase 1) — PURE BPHS

Non‑negotiable constraints:
- No AI astrology, no heuristics, no normalization
- Backend is source of truth; frontend render-only
- D1 (Rāśi) + D9 (Navāṁśa) only
- Uses Shadbala ratios ONLY for strength gating & base power

Implemented (Phase 1):
1) Pancha Mahāpurūṣa Yogas (BPHS): Ruchaka, Bhadra, Hamsa, Malavya, Sasa
2) Gaja‑Kesari Yoga (BPHS): Jupiter in Kendra from Moon
3) Rāja Yoga (limited, BPHS-safe): conjunction OR mutual aspect OR parivartana (sign exchange)
   between a Kendra lord and a Trikona lord
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

import swisseph as swe

from src.utils.converters import normalize_degrees
from src.jyotish.kundli_engine import SIGN_LORDS
from src.jyotish.varga_drik import calculate_varga


SUPPORTED_PLANETS: Tuple[str, ...] = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

# ---------------------------------------------------------------------------
# Neecha Bhanga Raja Yoga (NBRY) — PURE BPHS (D1 + D9 only)
# ---------------------------------------------------------------------------
# Sign indices: Aries=0, Taurus=1, Gemini=2, Cancer=3, Leo=4, Virgo=5,
# Libra=6, Scorpio=7, Sagittarius=8, Capricorn=9, Aquarius=10, Pisces=11
NEECHA_SIGNS_D1: Dict[str, int] = {
    "Sun": 6,      # Libra
    "Moon": 7,     # Scorpio
    "Mars": 3,     # Cancer
    "Mercury": 11, # Pisces
    "Jupiter": 9,  # Capricorn
    "Venus": 5,    # Virgo
    "Saturn": 0,   # Aries
}

# BPHS lordship map as mandated by spec (do not infer/compute)
NEECHA_BHANGA_LORDS: Dict[str, Dict[str, str]] = {
    "Sun": {"sign_lord": "Venus", "exalt_lord": "Saturn"},
    "Moon": {"sign_lord": "Mars", "exalt_lord": "Venus"},
    "Mars": {"sign_lord": "Moon", "exalt_lord": "Jupiter"},
    "Mercury": {"sign_lord": "Jupiter", "exalt_lord": "Mercury"},
    "Jupiter": {"sign_lord": "Saturn", "exalt_lord": "Moon"},
    "Venus": {"sign_lord": "Mercury", "exalt_lord": "Venus"},
    "Saturn": {"sign_lord": "Mars", "exalt_lord": "Sun"},
}


KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}


KENDRA_DISTS = (0, 3, 6, 9)
TRIKONA_DISTS = (0, 4, 8)


YOGA_LEAD_RULES: Dict[str, Dict[str, Any]] = {
    # Pancha Mahapurusha (lead fixed; SINGLE influence)
    "Ruchaka Yoga": {"lead_planets": ["Mars"], "influence_mode": "SINGLE", "category": "Pancha Mahapurusha"},
    "Bhadra Yoga": {"lead_planets": ["Mercury"], "influence_mode": "SINGLE", "category": "Pancha Mahapurusha"},
    "Hamsa Yoga": {"lead_planets": ["Jupiter"], "influence_mode": "SINGLE", "category": "Pancha Mahapurusha"},
    "Malavya Yoga": {"lead_planets": ["Venus"], "influence_mode": "SINGLE", "category": "Pancha Mahapurusha"},
    "Sasa Yoga": {"lead_planets": ["Saturn"], "influence_mode": "SINGLE", "category": "Pancha Mahapurusha"},
    # Gaja-Kesari (dual influence)
    "Gaja‑Kesari Yoga": {"lead_planets": ["Jupiter", "Moon"], "influence_mode": "DUAL", "category": "Gaja-Kesari"},
    # Raja Yoga (dual influence, dynamic planets)
    "Rāja Yoga (Kendra–Trikona)": {"lead_planets": [], "influence_mode": "DUAL", "category": "Raja"},
}


def _sign_dist(target_sign: int, reference_sign: int) -> int:
    # Pure sign-distance math (0..11)
    return (int(target_sign) - int(reference_sign) + 12) % 12


def _is_kendra_from(reference_sign: int, target_sign: int) -> bool:
    return _sign_dist(target_sign, reference_sign) in KENDRA_DISTS


def _is_trikona_from(reference_sign: int, target_sign: int) -> bool:
    return _sign_dist(target_sign, reference_sign) in TRIKONA_DISTS


def _sidereal_lagna_sign(jd: float, lat: float, lon: float) -> Tuple[float, int]:
    """
    Compute sidereal ascendant longitude and sign using Lahiri ayanamsa.
    We compute tropical ascendant from Swiss Ephemeris and subtract Lahiri ayanamsa.
    """
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P")
    asc_tropical = float(ascmc[0])
    ayanamsa = float(swe.get_ayanamsa_ut(jd))
    asc_sidereal = normalize_degrees(asc_tropical - ayanamsa)
    return asc_sidereal, int(asc_sidereal // 30)


def _d1_sign_and_deg_in_sign(longitude: float) -> Tuple[int, float]:
    lon = normalize_degrees(float(longitude))
    sign = int(lon // 30)
    deg_in_sign = lon % 30.0
    return sign, deg_in_sign


def _d9_sign(longitude: float) -> int:
    return int(calculate_varga(float(longitude), 9)["sign"])


def _house_from_lagna_sign(planet_sign: int, lagna_sign: int) -> int:
    # Whole-sign house counting from Lagna sign (PURE positional mapping)
    return ((planet_sign - lagna_sign) % 12) + 1


def _kendra_from(reference_sign: int, target_sign: int) -> bool:
    # Kendra from reference sign: 1/4/7/10 => sign steps 0/3/6/9
    return _is_kendra_from(reference_sign, target_sign)


def _degree_maturity_multiplier(deg_in_sign: float) -> float:
    d = float(deg_in_sign)
    if 0.0 <= d < 6.0:
        return 0.25
    if 6.0 <= d < 12.0:
        return 0.50
    if 12.0 <= d < 18.0:
        return 1.00
    if 18.0 <= d < 24.0:
        return 0.50
    # 24°–30°
    return 0.10


def _house_multiplier(house_num: int) -> float:
    # Precedence (to avoid overlaps): Kendra > Trikona > Panaphara > Apoklima
    if house_num in (1, 4, 7, 10):
        return 1.00
    if house_num in (5, 9):
        return 0.75
    if house_num in (2, 8, 11):
        return 0.50
    if house_num in (3, 6, 12):
        return 0.25
    # House 5/9 already handled as Trikona; remaining is house 0 impossible
    return 0.25


def _avg(values: List[float]) -> float:
    return float(sum(values) / max(1, len(values)))


def _aspect_offsets(planet: str) -> Tuple[int, ...]:
    """
    Graha dṛṣṭi offsets in signs (0-11 steps) as per BPHS.
    - All: 7th (6)
    - Mars: 4th (3), 8th (7)
    - Jupiter: 5th (4), 9th (8)
    - Saturn: 3rd (2), 10th (9)
    """
    base = [6]
    if planet == "Mars":
        base += [3, 7]
    elif planet == "Jupiter":
        base += [4, 8]
    elif planet == "Saturn":
        base += [2, 9]
    return tuple(sorted(set(base)))


def _aspects(planet_a: str, sign_a: int, sign_b: int) -> bool:
    diff = (sign_b - sign_a) % 12
    return diff in _aspect_offsets(planet_a)


def _mutual_aspect(planet_a: str, sign_a: int, planet_b: str, sign_b: int) -> bool:
    return _aspects(planet_a, sign_a, sign_b) and _aspects(planet_b, sign_b, sign_a)


@dataclass(frozen=True)
class PlanetContext:
    name: str
    longitude: float
    d1_sign: int
    d1_deg_in_sign: float
    d9_sign: int
    shadbala_ratio: float
    is_vargottama: bool
    maturity_multiplier: float
    dist_from_lagna: int


def calculate_yoga_potency(
    *,
    yoga_name: str,
    category: str,
    planets: List[PlanetContext],
    lead_planets: List[PlanetContext],
    influence_mode: str,  # "SINGLE" | "DUAL"
    house_reference_sign: int,
    formation_house: Optional[int],
    formation_logic: str,
    shadbala_cutoff: float = 0.75,
    neecha_bhanga_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Dedicated Yoga potency calculator (STRICT, auditable).

    Rules (locked):
    - If ANY participating planet has Shadbala ratio < shadbala_cutoff → Mṛta, potency = 0
    - Influence mode:
        SINGLE → use ONLY lead planet metrics (Mahapurusha)
        DUAL   → average metrics of both lead planets (Gaja-Kesari, Raja Yoga)
    - HouseMultiplier: derived via sign-distance houses from a reference sign
    - DegreeMultiplier: avastha maturity law, per planet; averaged in DUAL
    - Vargottama Bonus: apply ×1.20 exactly once if vargottama applies
    - Potency = BaseRatio × HouseMultiplier × DegreeMultiplier × Vargottama × 100, clamped to 0–100
    - Status labels: Siddha / Madhya / Alpa / Mṛta (no heuristics)
    - is_triggered = potency_percent >= 25.0
    """
    # Special-case: Neecha Bhanga Raja Yoga (NBRY) potency override (PURE BPHS, spec-locked)
    is_nbry = yoga_name == "Neecha Bhanga Raja Yoga" and isinstance(neecha_bhanga_data, dict)
    if is_nbry:
        is_rescued = bool(neecha_bhanga_data.get("is_rescued", False))
        if not is_rescued:
            out = {
                "yoga_name": yoga_name,
                "category": category,
                "planets_involved": [p.name for p in planets],
                "formation_house": formation_house,
                "formation_logic": formation_logic,
                "potency_percent": 0.0,
                "status_label": "Mṛta (Inactive)",
                "is_triggered": False,
                "strength_breakdown": {
                    "avg_shadbala_ratio": round(_avg([p.shadbala_ratio for p in planets]), 4),
                    "house_multiplier": round(
                        _avg([_house_multiplier(_sign_dist(p.d1_sign, house_reference_sign) + 1) for p in planets]), 4
                    ),
                    "degree_multiplier": round(_avg([p.maturity_multiplier for p in planets]), 4),
                    "vargottama_applied": False,
                },
                "explanation": "Debilitation not cancelled as per BPHS (Neecha Bhanga Raja Yoga).",
                "neecha_bhanga_data": {
                    "is_rescued": False,
                    "rules_met": list(neecha_bhanga_data.get("rules_met", []) or []),
                },
            }
            return out

    cutoff_failed_planets = [p.name for p in planets if p.shadbala_ratio < shadbala_cutoff]
    # NBRY rescue bypass: do not kill the yoga due to Shadbala cutoff
    if cutoff_failed_planets and not (is_nbry and bool(neecha_bhanga_data.get("is_rescued", False))):
        out = {
            "yoga_name": yoga_name,
            "category": category,
            "planets_involved": [p.name for p in planets],
            "formation_house": formation_house,
            "formation_logic": formation_logic,
            "potency_percent": 0.0,
            "status_label": "Mṛta",
            "is_triggered": False,
            "strength_breakdown": {
                "avg_shadbala_ratio": round(_avg([p.shadbala_ratio for p in planets]), 4),
                "house_multiplier": round(
                    _avg([_house_multiplier(_sign_dist(p.d1_sign, house_reference_sign) + 1) for p in planets]), 4
                ),
                "degree_multiplier": round(_avg([p.maturity_multiplier for p in planets]), 4),
                "vargottama_applied": False,
                "cutoff": {"threshold": shadbala_cutoff, "failed_planets": cutoff_failed_planets},
            },
            "explanation": f"Strength cutoff failed (ratio < {shadbala_cutoff}) for: {', '.join(cutoff_failed_planets)}.",
        }
        if is_nbry:
            out["neecha_bhanga_data"] = {
                "is_rescued": bool(neecha_bhanga_data.get("is_rescued", False)),
                "rules_met": list(neecha_bhanga_data.get("rules_met", []) or []),
            }
        return out

    influence_mode = influence_mode.upper().strip()
    if influence_mode not in ("SINGLE", "DUAL"):
        raise ValueError(f"Invalid influence_mode: {influence_mode}")

    if influence_mode == "SINGLE":
        lead = lead_planets[0]
        base_ratio = float(lead.shadbala_ratio)
        degree_mult = float(lead.maturity_multiplier)
        house_mult = float(_house_multiplier(_sign_dist(lead.d1_sign, house_reference_sign) + 1))
        vargottama_applied = bool(lead.is_vargottama)
    else:
        # DUAL: average metrics of both lead planets (fixed by yoga law)
        base_ratio = _avg([p.shadbala_ratio for p in lead_planets])
        degree_mult = _avg([p.maturity_multiplier for p in lead_planets])
        house_mult = _avg([_house_multiplier(_sign_dist(p.d1_sign, house_reference_sign) + 1) for p in lead_planets])
        # Vargottama law: apply once if any lead planet is vargottama
        vargottama_applied = any(p.is_vargottama for p in lead_planets)

    vargottama_mult = 1.20 if vargottama_applied else 1.0

    potency = base_ratio * house_mult * degree_mult * vargottama_mult * 100.0
    # NBRY scar law (spec): potency is reduced, never inflated
    if is_nbry and bool(neecha_bhanga_data.get("is_rescued", False)):
        potency *= 0.90
    potency = max(0.0, min(100.0, float(potency)))

    if is_nbry and bool(neecha_bhanga_data.get("is_rescued", False)):
        status = "Siddha (Rescued)"
    else:
        if potency >= 80.0:
            status = "Siddha"
        elif potency >= 50.0:
            status = "Madhya"
        elif potency >= 25.0:
            status = "Alpa"
        else:
            status = "Mṛta"

    out = {
        "yoga_name": yoga_name,
        "category": category,
        "planets_involved": [p.name for p in planets],
        "formation_house": formation_house,
        "formation_logic": formation_logic,
        "potency_percent": round(potency, 2),
        "status_label": status,
        "is_triggered": bool(potency >= 25.0),
        "strength_breakdown": {
            "avg_shadbala_ratio": round(base_ratio, 4),
            "house_multiplier": round(house_mult, 4),
            "degree_multiplier": round(degree_mult, 4),
            "vargottama_applied": bool(vargottama_applied),
        },
        "explanation": "Calculated strictly as per BPHS (Bṛhat Parāśara Horā Śāstra).",
    }

    if is_nbry:
        out["neecha_bhanga_data"] = {
            "is_rescued": bool(neecha_bhanga_data.get("is_rescued", False)),
            "rules_met": list(neecha_bhanga_data.get("rules_met", []) or []),
        }

    return out


def check_neecha_bhanga(
    planet: PlanetContext,
    chart_ctx: Dict[str, PlanetContext],
    lagna_sign: int,
) -> Tuple[bool, List[str]]:
    """
    Neecha Bhanga checks (PURE BPHS) for a planet that is Neecha in D1.

    Returns (is_rescued, rules_met) if ANY BPHS law cancels debilitation:
      1) Neecha-Adhipati (Sign Lord) in Kendra from Lagna
      2) Uccha-Adhipati (Exaltation Lord) in Kendra from Lagna
      3) Neecha planet aspected by its Sign Lord (Parāśari graha-dṛṣṭi)
      4) Vargottama (D1 sign == D9 sign)
      5) Sign Lord and Exaltation Lord are in mutual Kendra (0/3/6/9)
    """
    if planet.name not in SUPPORTED_PLANETS:
        return False, []
    if planet.name not in NEECHA_SIGNS_D1:
        return False, []
    if int(planet.d1_sign) != int(NEECHA_SIGNS_D1[planet.name]):
        return False, []

    lords = NEECHA_BHANGA_LORDS.get(planet.name, {})
    sign_lord_name = lords.get("sign_lord")
    exalt_lord_name = lords.get("exalt_lord")

    sign_lord = chart_ctx.get(sign_lord_name) if sign_lord_name else None
    exalt_lord = chart_ctx.get(exalt_lord_name) if exalt_lord_name else None

    rules: List[str] = []

    # 1) Neecha-Adhipati in Kendra from Lagna (keep check as-is; refine label)
    if sign_lord and _is_kendra_from(int(lagna_sign), int(sign_lord.d1_sign)):
        rules.append("Neecha-Adhipati in Kendra (Lagna)")

    # 1b) Neecha-Adhipati in Kendra from Moon (Chandra Lagna)
    moon = chart_ctx.get("Moon")
    if sign_lord and moon and _is_kendra_from(int(moon.d1_sign), int(sign_lord.d1_sign)):
        rules.append("Neecha-Adhipati in Kendra (Moon)")

    # 2) Uccha-Adhipati in Kendra from Lagna
    if exalt_lord and _is_kendra_from(int(lagna_sign), int(exalt_lord.d1_sign)):
        rules.append("Uccha-Adhipati in Kendra")

    # 3) Aspected by sign lord (Parāśari aspects)
    if sign_lord and _aspects(str(sign_lord.name), int(sign_lord.d1_sign), int(planet.d1_sign)):
        rules.append("Aspectual Rescue (Drishti)")

    # 4) Vargottama
    if int(planet.d1_sign) == int(planet.d9_sign):
        rules.append("Vargottama Rescue")

    # 5) Sign lord and exaltation lord in mutual Kendra
    if sign_lord and exalt_lord and _is_kendra_from(int(sign_lord.d1_sign), int(exalt_lord.d1_sign)):
        rules.append("Mutual Kendra (Lords)")

    return bool(rules), rules


def scan_d1_d9_positions(jd: float, lat: float, lon: float) -> Dict[str, Dict[str, Any]]:
    """
    Scan D1 + D9 positions for the 7 classical planets.
    Returns a dict keyed by planet with: longitude, d1_sign, d1_deg_in_sign, d9_sign, vargottama, house_from_lagna.
    """
    asc_sid, lagna_sign = _sidereal_lagna_sign(jd, lat, lon)
    # Sidereal longitudes computed directly with the CURRENT sidereal mode context.
    # Ayanamsa synchronization is enforced at the start of detect_yogas().
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TRUEPOS | swe.FLG_SPEED
    planet_map = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
    }

    out: Dict[str, Dict[str, Any]] = {
        "_meta": {
            "lagna_longitude": round(float(asc_sid), 6),
            "lagna_sign": int(lagna_sign),
        }
    }

    for p in SUPPORTED_PLANETS:
        xx, ret = swe.calc_ut(float(jd), int(planet_map[p]), flag)
        if ret < 0:
            raise ValueError(f"SwissEph calc failed for {p}: {ret}")
        lon_p = normalize_degrees(float(xx[0]))
        d1_sign, d1_deg = _d1_sign_and_deg_in_sign(lon_p)
        d9_sign = _d9_sign(lon_p)
        out[p] = {
            "longitude": round(lon_p, 6),
            "d1_sign": d1_sign,
            "d1_deg_in_sign": round(d1_deg, 6),
            "d9_sign": d9_sign,
            "is_vargottama": bool(d1_sign == d9_sign),
            "house_from_lagna": _house_from_lagna_sign(d1_sign, lagna_sign),
        }

    return out


def _build_planet_context(
    jd: float,
    lat: float,
    lon: float,
    shadbala: Dict[str, Dict[str, Any]],
) -> Dict[str, PlanetContext]:
    scans = scan_d1_d9_positions(jd, lat, lon)
    lagna_sign = int(scans["_meta"]["lagna_sign"])

    ctx: Dict[str, PlanetContext] = {}
    for p in SUPPORTED_PLANETS:
        lon_p = float(scans[p]["longitude"])
        d1_sign = int(scans[p]["d1_sign"])
        d1_deg = float(scans[p]["d1_deg_in_sign"])
        d9_sign = int(scans[p]["d9_sign"])
        ratio = float(shadbala.get(p, {}).get("ratio", 0.0))
        maturity = _degree_maturity_multiplier(d1_deg)
        is_vargottama = bool(d1_sign == d9_sign)
        dist_lagna = _sign_dist(d1_sign, lagna_sign)
        ctx[p] = PlanetContext(
            name=p,
            longitude=lon_p,
            d1_sign=d1_sign,
            d1_deg_in_sign=d1_deg,
            d9_sign=d9_sign,
            shadbala_ratio=ratio,
            is_vargottama=is_vargottama,
            maturity_multiplier=maturity,
            dist_from_lagna=dist_lagna,
        )

    return ctx


def _mahapurusha_rules() -> Dict[str, Dict[str, Any]]:
    # Sign indices: Aries=0, Taurus=1, ..., Pisces=11
    return {
        "Ruchaka": {"planet": "Mars", "signs": {0, 7, 9}, "category": "Pancha Mahapurusha",
                    "explanation": "Mars in own/exaltation sign (Aries/Scorpio/Capricorn) in a Kendra."},
        "Bhadra": {"planet": "Mercury", "signs": {2, 5}, "category": "Pancha Mahapurusha",
                   "explanation": "Mercury in own/exaltation sign (Gemini/Virgo) in a Kendra."},
        "Hamsa": {"planet": "Jupiter", "signs": {8, 11, 3}, "category": "Pancha Mahapurusha",
                  "explanation": "Jupiter in own/exaltation sign (Sagittarius/Pisces/Cancer) in a Kendra."},
        "Malavya": {"planet": "Venus", "signs": {1, 6, 11}, "category": "Pancha Mahapurusha",
                    "explanation": "Venus in own/exaltation sign (Taurus/Libra/Pisces) in a Kendra."},
        "Sasa": {"planet": "Saturn", "signs": {9, 10, 6}, "category": "Pancha Mahapurusha",
                 "explanation": "Saturn in own/exaltation sign (Capricorn/Aquarius/Libra) in a Kendra."},
    }


def _parivartana(planet_a: str, sign_a: int, planet_b: str, sign_b: int) -> bool:
    """
    Parivartana (sign exchange) between two planets:
    planet_a occupies sign ruled by planet_b AND planet_b occupies sign ruled by planet_a.
    """
    return SIGN_LORDS.get(sign_a) == planet_b and SIGN_LORDS.get(sign_b) == planet_a


def build_d1_sign_map_for_sambandha(jd: float) -> Dict[str, int]:
    """
    Build a D1 sign map for dasha-sambandha checks.

    Includes Vimshottari lords: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu.
    Uses Swiss Ephemeris with the CURRENT sidereal mode (caller must ensure Lahiri is set).
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TRUEPOS | swe.FLG_SPEED

    planet_map = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.TRUE_NODE,
    }

    out: Dict[str, int] = {}
    rahu_lon: Optional[float] = None
    for name, swe_id in planet_map.items():
        xx, ret = swe.calc_ut(float(jd), int(swe_id), flag)
        if ret < 0:
            raise ValueError(f"SwissEph calc failed for {name}: {ret}")
        lon = normalize_degrees(float(xx[0]))
        out[name] = int(lon // 30)
        if name == "Rahu":
            rahu_lon = lon

    # Ketu = Rahu + 180 (sidereal), sign-only
    if rahu_lon is None:
        raise ValueError("Rahu longitude missing while building d1 sign map")
    out["Ketu"] = int(normalize_degrees(rahu_lon + 180.0) // 30)
    return out


def is_dasha_connected(dasha_lord: Optional[str], yoga_planets: List[str], chart_data: Dict[str, Any]) -> bool:
    """
    BPHS Sambandha (Dasha × Yoga connection).

    Returns True if ANY of:
    1) Identity: dasha_lord is one of yoga_planets
    2) Yuti: dasha_lord in same D1 sign as any yoga_planet
    3) Drishti: dasha_lord aspects any yoga_planet (reuse Parāśari graha-dṛṣṭi logic)
    4) Parivartana: sign exchange between dasha_lord and a yoga_planet
    """
    if not dasha_lord:
        return False
    if dasha_lord in yoga_planets:
        return True

    d1_signs: Dict[str, int] = chart_data.get("d1_signs", {}) if isinstance(chart_data, dict) else {}
    if dasha_lord not in d1_signs:
        return False
    dasha_sign = int(d1_signs[dasha_lord])

    for p in yoga_planets:
        if p not in d1_signs:
            continue
        p_sign = int(d1_signs[p])

        # 2) Yuti (same sign)
        if dasha_sign == p_sign:
            return True

        # 3) Drishti (reuse existing graha-dṛṣṭi offsets)
        if _aspects(dasha_lord, dasha_sign, p_sign):
            return True

        # 4) Parivartana (exchange)
        if _parivartana(dasha_lord, dasha_sign, p, p_sign):
            return True

    return False


def detect_yogas(
    jd: float,
    lat: float,
    lon: float,
    shadbala: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Returns Phase‑1 yogas that FORM in D1.
    - Yogas that fail formation are NOT returned.
    - Yogas that form but are weak still return with status Mṛta (as per potency / cutoff).
    - Exception (spec): Neecha Bhanga Raja Yoga is returned as a first-class yoga when a planet is Neecha;
      it is marked "Siddha (Rescued)" if Bhanga exists, otherwise "Mṛta (Inactive)".
    """
    # 1) AYANAMSA SYNCHRONIZATION (CRITICAL) — execute once per request
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    planet_ctx = _build_planet_context(jd, lat, lon, shadbala)
    _, lagna_sign = _sidereal_lagna_sign(jd, lat, lon)

    yogas: List[Dict[str, Any]] = []

    # A) Pancha Mahāpurūṣa
    for yoga_name, rule in _mahapurusha_rules().items():
        p = planet_ctx[rule["planet"]]
        in_sign = p.d1_sign in rule["signs"]
        # Controlled scope: Lagna (primary) OR Chandra Lagna (secondary)
        moon_sign = int(planet_ctx["Moon"].d1_sign)
        in_kendra_lagna = _is_kendra_from(int(lagna_sign), p.d1_sign)
        in_kendra_moon = _is_kendra_from(moon_sign, p.d1_sign)
        formation_met = bool(in_sign and (in_kendra_lagna or in_kendra_moon))
        if not formation_met:
            continue

        formation_basis = "Lagna" if in_kendra_lagna else "Chandra Lagna"
        reference_sign = int(lagna_sign) if in_kendra_lagna else moon_sign
        formation_house = _sign_dist(p.d1_sign, reference_sign) + 1
        # API-safe formation text (no debug tokens)
        formation_logic = f"{rule['explanation'].replace('own/exaltation', 'own or exaltation')} (D1)."

        yoga_full_name = f"{yoga_name} Yoga"
        lead_names = YOGA_LEAD_RULES[yoga_full_name]["lead_planets"]
        lead_planets = [planet_ctx[n] for n in lead_names]
        res = calculate_yoga_potency(
            yoga_name=yoga_full_name,
            category=YOGA_LEAD_RULES[yoga_full_name]["category"],
            planets=[p],
            lead_planets=lead_planets,
            influence_mode=YOGA_LEAD_RULES[yoga_full_name]["influence_mode"],
            house_reference_sign=reference_sign,
            formation_house=formation_house,
            formation_logic=formation_logic,
        )
        # Explicit visibility (no silent mixing)
        res["formation_basis"] = formation_basis
        yogas.append(res)

    # B) Gaja‑Kesari
    moon = planet_ctx["Moon"]
    jup = planet_ctx["Jupiter"]
    formation_met = _is_kendra_from(moon.d1_sign, jup.d1_sign)
    if formation_met:
        formation_house = _sign_dist(jup.d1_sign, moon.d1_sign) + 1  # house from Moon (1/4/7/10)
        # API-safe formation text (no sign indices)
        formation_logic = "Jupiter in a Kendra from the Moon (1st, 4th, 7th, or 10th) as per BPHS."
        yoga_full_name = "Gaja‑Kesari Yoga"
        yogas.append(
            calculate_yoga_potency(
                yoga_name=yoga_full_name,
                category=YOGA_LEAD_RULES[yoga_full_name]["category"],
                planets=[moon, jup],
                lead_planets=[jup, moon],
                influence_mode=YOGA_LEAD_RULES[yoga_full_name]["influence_mode"],
                house_reference_sign=moon.d1_sign,
                formation_house=formation_house,
                formation_logic=formation_logic,
                shadbala_cutoff=0.65,  # relational yoga cutoff refinement (BPHS-conservative)
            )
        )

    # C) Limited Rāja Yoga (Kendra lord ↔ Trikona lord) — pick strongest valid pair
    kendra_lords = set()
    for dist in KENDRA_DISTS:
        sign_idx = (int(lagna_sign) + dist) % 12
        kendra_lords.add(SIGN_LORDS[sign_idx])

    trikona_lords = set()
    for dist in TRIKONA_DISTS:
        sign_idx = (int(lagna_sign) + dist) % 12
        trikona_lords.add(SIGN_LORDS[sign_idx])

    # Candidate pairs among classical planets only
    candidates: List[Tuple[str, str, str, str, str]] = []  # (kendra_lord, trikona_lord, mode, A, B)
    for a in SUPPORTED_PLANETS:
        for b in SUPPORTED_PLANETS:
            if a >= b:
                continue
            if (a in kendra_lords and b in trikona_lords) or (b in kendra_lords and a in trikona_lords):
                k_lord = a if a in kendra_lords else b
                t_lord = b if a in kendra_lords else a
                sign_a = planet_ctx[a].d1_sign
                sign_b = planet_ctx[b].d1_sign
                if sign_a == sign_b:
                    candidates.append((k_lord, t_lord, "conjunction", a, b))
                elif _mutual_aspect(a, sign_a, b, sign_b):
                    candidates.append((k_lord, t_lord, "mutual_aspect", a, b))
                elif _parivartana(a, sign_a, b, sign_b):
                    candidates.append((k_lord, t_lord, "parivartana", a, b))

    if candidates:
        # Select strongest pair by average shadbala ratio (PAIR SELECTION ONLY; lead is fixed as dual influence)
        best = max(candidates, key=lambda t: (planet_ctx[t[3]].shadbala_ratio + planet_ctx[t[4]].shadbala_ratio) / 2.0)
        k_lord, t_lord, mode, a, b = best
        k_ctx = planet_ctx[k_lord]
        t_ctx = planet_ctx[t_lord]

        # API-safe formation text (no key=value fragments)
        formation_logic = (
            f"Rāja Yoga via {mode.replace('_', ' ')} between a Kendra lord and a Trikona lord (BPHS). "
            f"Kendra lord {k_lord} and Trikona lord {t_lord}."
        )
        yoga_full_name = "Rāja Yoga (Kendra–Trikona)"
        yogas.append(
            calculate_yoga_potency(
                yoga_name=yoga_full_name,
                category=YOGA_LEAD_RULES[yoga_full_name]["category"],
                planets=[k_ctx, t_ctx],
                lead_planets=[k_ctx, t_ctx],
                influence_mode=YOGA_LEAD_RULES[yoga_full_name]["influence_mode"],
                house_reference_sign=int(lagna_sign),
                formation_house=None,
                formation_logic=formation_logic,
                shadbala_cutoff=0.65,  # relational yoga cutoff refinement (BPHS-conservative)
            )
        )

    # D) Neecha Bhanga Raja Yoga (FIRST-CLASS) — PURE BPHS (D1 rules + D9 vargottama)
    nb_neecha: List[PlanetContext] = []
    nb_rescued: List[Tuple[PlanetContext, List[str]]] = []
    for p_name in SUPPORTED_PLANETS:
        p = planet_ctx[p_name]
        if int(p.d1_sign) != int(NEECHA_SIGNS_D1.get(p_name, -999)):
            continue
        nb_neecha.append(p)
        is_rescued, rules_met = check_neecha_bhanga(p, planet_ctx, int(lagna_sign))
        if is_rescued:
            nb_rescued.append((p, rules_met))

    if nb_rescued:
        # Deterministic selection: choose the rescued planet yielding the highest NBRY potency.
        # (This is selection only; all calculations remain BPHS-locked and constant-time.)
        yoga_full_name = "Neecha Bhanga Raja Yoga"
        candidates: List[Dict[str, Any]] = []
        for rescued_planet, rules_met in nb_rescued:
            cand = calculate_yoga_potency(
                yoga_name=yoga_full_name,
                category="Raja",
                planets=[rescued_planet],
                lead_planets=[rescued_planet],
                influence_mode="SINGLE",
                house_reference_sign=int(lagna_sign),
                formation_house=_sign_dist(rescued_planet.d1_sign, int(lagna_sign)) + 1,
                formation_logic="Debilitation cancelled as per BPHS.",
                neecha_bhanga_data={"is_rescued": True, "rules_met": rules_met},
            )
            candidates.append(cand)

        # Tie-break: planet name (stable)
        best = max(candidates, key=lambda c: (float(c.get("potency_percent", 0.0) or 0.0), ",".join(c.get("planets_involved", []) or [])))
        best["explanation"] = (
            "Debilitation cancelled as per BPHS (Neecha Bhanga Raja Yoga). "
            "Results manifest during appropriate Dashas."
        )
        # Formation logic: API-safe, human-readable
        if (best.get("planets_involved") or []):
            p_name = (best.get("planets_involved") or ["Planet"])[0]
            best["formation_logic"] = f"{p_name} is debilitated; debilitation cancelled as per BPHS (Neecha Bhanga Raja Yoga)."
        yogas.append(best)
    elif nb_neecha:
        # If a planet is Neecha but not rescued, expose NBRY as first-class but inactive (spec).
        nb_neecha.sort(key=lambda p: (p.shadbala_ratio, p.name))
        neecha_planet = nb_neecha[-1]
        yoga_full_name = "Neecha Bhanga Raja Yoga"
        yogas.append(
            calculate_yoga_potency(
                yoga_name=yoga_full_name,
                category="Raja",
                planets=[neecha_planet],
                lead_planets=[neecha_planet],
                influence_mode="SINGLE",
                house_reference_sign=int(lagna_sign),
                formation_house=_sign_dist(neecha_planet.d1_sign, int(lagna_sign)) + 1,
                formation_logic=f"{neecha_planet.name} is debilitated; debilitation not cancelled as per BPHS (Neecha Bhanga Raja Yoga).",
                neecha_bhanga_data={"is_rescued": False, "rules_met": []},
            )
        )

    return yogas

"""
Phase 6: Complete Yoga Detection Engine

This is the main yoga engine that combines all yoga detection modules
to provide comprehensive yoga analysis following JHora-style rules.
"""

from typing import Dict, List

from src.jyotish.yogas.planetary_yogas import detect_planetary_yogas
from src.jyotish.yogas.mahapurusha_yogas import detect_mahapurusha_yogas
from src.jyotish.yogas.house_yogas import detect_house_yogas
from src.jyotish.yogas.combination_yogas import detect_combination_yogas
from src.jyotish.yogas.raja_yogas import detect_advanced_raja_yogas
from src.jyotish.yogas.extended_yogas import detect_extended_yogas


def detect_all_yogas(planets: Dict, houses: List[Dict]) -> Dict:
    """
    Phase 6: Detect all yogas in the birth chart.
    
    This function combines all yoga detection modules to provide
    a complete analysis of 250+ classical yogas.
    
    Args:
        planets: Dictionary of planet positions with degrees, signs, houses
        houses: List of house data with signs and degrees
    
    Returns:
        Complete yoga analysis dictionary
    """
    all_yogas = []
    
    # 1. Planetary Placement Yogas
    planetary_yogas = detect_planetary_yogas(planets, houses)
    all_yogas.extend(planetary_yogas)
    
    # 2. Panch Mahapurusha Yogas
    mahapurusha_yogas = detect_mahapurusha_yogas(planets, houses)
    all_yogas.extend(mahapurusha_yogas)
    
    # 3. House-Based Yogas
    house_yogas = detect_house_yogas(planets, houses)
    all_yogas.extend(house_yogas)
    
    # 4. Combination Yogas
    combination_yogas = detect_combination_yogas(planets, houses)
    all_yogas.extend(combination_yogas)
    
    # 5. Advanced Raja Yogas
    advanced_raja_yogas = detect_advanced_raja_yogas(planets, houses)
    all_yogas.extend(advanced_raja_yogas)
    
    # 6. Extended Yogas (250+ total)
    extended_yogas = detect_extended_yogas(planets, houses)
    all_yogas.extend(extended_yogas)
    
    # Categorize yogas
    major_yogas = [y for y in all_yogas if y.get("category") == "Major"]
    moderate_yogas = [y for y in all_yogas if y.get("category") == "Moderate"]
    doshas = [y for y in all_yogas if y.get("category") == "Dosha"]
    
    # Group by type
    planetary = [y for y in all_yogas if y.get("type") == "Planetary"]
    house_based = [y for y in all_yogas if y.get("type") == "House"]
    mahapurusha = [y for y in all_yogas if y.get("type") == "Mahapurusha"]
    combination = [y for y in all_yogas if y.get("type") == "Combination"]
    raja = [y for y in all_yogas if y.get("type") == "Raja Yoga"]
    
    return {
        "total_yogas": len(all_yogas),
        "all_yogas": all_yogas,
        "major_yogas": major_yogas,
        "moderate_yogas": moderate_yogas,
        "doshas": doshas,
        "by_type": {
            "planetary": planetary,
            "house_based": house_based,
            "mahapurusha": mahapurusha,
            "combination": combination,
            "raja_yoga": raja
        },
        "summary": {
            "total": len(all_yogas),
            "major": len(major_yogas),
            "moderate": len(moderate_yogas),
            "doshas": len(doshas)
        }
    }

