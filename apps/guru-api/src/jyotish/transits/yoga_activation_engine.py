"""
Yoga Transit Activation Engine — BPHS-correct, minimal surface area.

ARCHITECTURAL PRINCIPLE (locked):
  "Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort."
Transit NEVER creates or alters natal yogas. Transit is a SECONDARY SWITCH only.

Responsibilities ONLY:
A) Evaluate CURRENT transit activation of natal yogas
B) Evaluate FUTURE activation windows (Next N years, up to 100)
C) Qualify strength using Ashtakavarga (Bindus) — Bhinnashtakavarga for transit quality

Optimized forecast: Dasha windows first; slow planets (Saturn, Jupiter, Mars) by sign ingress;
skip fast planets if window < 6 months.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import swisseph as swe

from src.jyotish.yogas.yoga_engine import detect_all_yogas, YOGA_LEAD_RULES
from src.jyotish.dasha.vimshottari_engine import calculate_vimshottari_dasha
from src.jyotish.transits.gochar import get_transits
from src.jyotish.kundli_engine import get_planet_positions as _get_planet_positions
from src.jyotish.strength.ashtakavarga import (
    calculate_bhinnashtakavarga,
    PLANETS as BAV_PLANETS,
)
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses
from src.utils.converters import normalize_degrees, degrees_to_sign
from src.utils.timezone import get_julian_day, local_to_utc
from src.ephemeris.ephemeris_utils import get_ayanamsa

# Transit contact: same sign (0), 7th (6), 5th (4), 9th (8) from natal = Conjunction, Opposition, Trikona
TRANSIT_CONTACT_DISTS = {0, 4, 6, 8}

# Ashtakavarga quality (BPHS)
BINDU_KASHTA = (0, 3)   # 0-3: Weak / Painful
BINDU_SAMA = 4          # 4: Average
BINDU_SHUBHA = (5, 8)   # 5-8: Strong / Excellent

# Slow planets: scan by sign ingress for forecast (no per-day loops)
SLOW_PLANETS = {"Saturn", "Jupiter", "Mars"}
# Fast planets: only if window >= 6 months, step by 7 days (Moon ignored for long-range)
FAST_PLANETS_FORECAST = {"Sun", "Venus", "Mercury"}
MIN_WINDOW_DAYS_FOR_FAST = 182  # ~6 months


def _get_yoga_participants(yoga: Dict) -> List[str]:
    """Extract planet participants from a yoga dict. Used for Dasha + Transit filters."""
    participants = []
    if yoga.get("planet"):
        participants.append(yoga["planet"])
    if yoga.get("planets"):
        participants.extend(yoga["planets"] if isinstance(yoga["planets"], list) else [yoga["planets"]])
    name = yoga.get("name", "")
    if not participants and name in YOGA_LEAD_RULES:
        lead = YOGA_LEAD_RULES[name].get("lead_planets", [])
        participants.extend(lead)
    return list(dict.fromkeys(participants))


def _is_transit_contact(natal_sign: int, transit_sign: int) -> bool:
    """True if transit planet is in Conjunction (0), Opposition (6), or Trikona (4, 8) from natal sign."""
    dist = (transit_sign - natal_sign + 12) % 12
    return dist in TRANSIT_CONTACT_DISTS


def _bindu_quality(bindus: int) -> str:
    """BPHS: 0-3 Kashta, 4 Sama, 5-8 Shubha."""
    if bindus is None or bindus < 0:
        return "Sama"
    if bindus <= BINDU_KASHTA[1]:
        return "Kashta"
    if bindus == BINDU_SAMA:
        return "Sama"
    if BINDU_SHUBHA[0] <= bindus <= BINDU_SHUBHA[1]:
        return "Shubha"
    return "Sama"


def _prepare_planets_and_houses(jd: float, lat: float, lon: float) -> Tuple[Dict, List[Dict], float]:
    """Prepare planet and house data for yoga detection (same logic as yoga_routes)."""
    asc = get_ascendant(jd, lat, lon)
    ayanamsa = get_ayanamsa(jd)
    asc_sidereal = normalize_degrees(asc - ayanamsa)
    houses_list = get_houses(jd, lat, lon)
    houses_sidereal = [normalize_degrees(h - ayanamsa) for h in houses_list]
    planets_sidereal = _get_planet_positions(jd)
    planets = {}
    for planet_name, planet_degree in planets_sidereal.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        sign_num, _ = degrees_to_sign(planet_degree)
        relative_pos = normalize_degrees(planet_degree - asc_sidereal)
        house_num = int(relative_pos / 30) + 1
        if house_num > 12:
            house_num = 1
        planets[planet_name] = {"degree": planet_degree, "sign": sign_num, "house": house_num}
    houses = []
    asc_sign, _ = degrees_to_sign(asc_sidereal)
    houses.append({"house": 1, "degree": asc_sidereal, "sign": asc_sign})
    for i, house_degree in enumerate(houses_sidereal):
        sign_num, _ = degrees_to_sign(house_degree)
        houses.append({"house": i + 2, "degree": house_degree, "sign": sign_num})
    return planets, houses, asc_sidereal


def _prepare_natal_yogas(dob: str, time: str, lat: float, lon: float, timezone: str) -> Tuple[float, Dict, List[Dict], Dict[str, int]]:
    """
    Get birth JD, yoga analysis, list of natal yogas (non-Dosha, non-Mrita), and natal planet sign map.
    Mrita: exclude Dosha category; exclude yogas with no participants.
    """
    dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0, swe.GREG_CAL)
    planets, houses, _ = _prepare_planets_and_houses(jd, lat, lon)
    yoga_analysis = detect_all_yogas(planets, houses)
    all_yogas = yoga_analysis.get("all_yogas", [])
    natal_yogas = [y for y in all_yogas if y.get("category") != "Dosha" and _get_yoga_participants(y)]
    natal_sign_map = {}
    for pname, pdata in planets.items():
        if isinstance(pdata, dict) and "sign" in pdata:
            natal_sign_map[pname] = int(pdata["sign"])
        elif isinstance(pdata, (int, float)):
            s, _ = degrees_to_sign(float(pdata))
            natal_sign_map[pname] = s
    return jd, yoga_analysis, natal_yogas, natal_sign_map


def _find_sign_ingresses(
    planet_name: str,
    start_dt: datetime,
    end_dt: datetime,
    timezone: str,
    lat: float,
    lon: float,
    step_days: int,
) -> List[Tuple[datetime, int]]:
    """
    Find approximate sign-ingress dates for a planet in [start_dt, end_dt].
    Returns list of (datetime, sign_index) at each sign change. Ingress-based scanning.
    """
    out: List[Tuple[datetime, int]] = []
    try:
        current = start_dt
        jd_prev = get_julian_day(local_to_utc(current.replace(tzinfo=None), timezone))
        transits_prev = get_transits(jd_prev, lat, lon).get("transits") or {}
        sign_prev = transits_prev.get(planet_name, {}).get("sign")
        if sign_prev is None:
            return out
        if isinstance(sign_prev, dict):
            sign_prev = sign_prev.get("sign_index", sign_prev.get("sign", 0))
        sign_prev = int(sign_prev)
        while current <= end_dt:
            current = current + timedelta(days=step_days)
            jd = get_julian_day(local_to_utc(current.replace(tzinfo=None), timezone))
            transits = get_transits(jd, lat, lon).get("transits") or {}
            t_sign = transits.get(planet_name, {}).get("sign")
            if t_sign is None:
                continue
            if isinstance(t_sign, dict):
                t_sign = t_sign.get("sign_index", t_sign.get("sign", 0))
            t_sign = int(t_sign)
            if t_sign != sign_prev:
                out.append((current, t_sign))
                sign_prev = t_sign
    except Exception:
        pass
    return out


def _get_bindu_at_transit(
    transit_jd: float,
    lat: float,
    lon: float,
    planet_name: str,
    transit_house: int,
) -> Optional[int]:
    """
    Bhinnashtakavarga at transit time for the transit planet in its transit house.
    Returns bindu count (0-8) or None if not calculable.
    """
    if planet_name not in BAV_PLANETS or transit_house < 1 or transit_house > 12:
        return None
    try:
        asc_tropical = get_ascendant(transit_jd, lat, lon)
        ayanamsa = swe.get_ayanamsa_ut(transit_jd)
        asc_sidereal = normalize_degrees(asc_tropical - ayanamsa)
        houses_list = get_houses(transit_jd, lat, lon)
        houses_sidereal = [normalize_degrees(h - ayanamsa) for h in houses_list]
        # BAV expects house_cusps = [house2, house3, ..., house12] (11 elements)
        house_cusps = houses_sidereal[1:12] if len(houses_sidereal) >= 12 else houses_sidereal
        all_planets = _get_planet_positions(transit_jd)
        planet_degree = all_planets.get(planet_name)
        if planet_degree is None:
            return None
        bav = calculate_bhinnashtakavarga(
            planet_name, float(planet_degree), all_planets, house_cusps, asc_sidereal
        )
        idx = transit_house - 1
        return bav[idx] if 0 <= idx < len(bav) else None
    except Exception:
        return None


def evaluate_current_activation(
    dob: str,
    time: str,
    lat: float,
    lon: float,
    timezone: str,
    calculation_date: Optional[datetime] = None,
) -> List[Dict]:
    """
    Evaluate CURRENT transit activation of natal yogas.
    Filter 1: Natal seed (yoga exists, not Mrita).
    Filter 2: Dasha permission (MD or AD lord is yoga participant) -> else Dormant.
    Filter 3: Transit contact (transit planet in same/7th/5th/9th from natal) -> Active.
    Ashtakavarga: Bindu in transit house for quality (Kashta/Sama/Shubha).
    """
    if calculation_date is None:
        calculation_date = datetime.now()
    try:
        _, _, natal_yogas, natal_sign_map = _prepare_natal_yogas(dob, time, lat, lon, timezone)
    except Exception:
        return []

    # Current transit JD (noon for stability)
    calc_dt = calculation_date.replace(hour=12, minute=0, second=0, microsecond=0)
    tz = local_to_utc(calc_dt, timezone) if timezone else calc_dt
    transit_jd = get_julian_day(tz)

    # Current dasha
    dasha = calculate_vimshottari_dasha(dob, time, lat, lon, timezone, calculation_date=calculation_date)
    current = dasha.get("current_dasha") or {}
    md_lord = current.get("mahadasha")
    ad_lord = current.get("antardasha")

    # Current transits
    transit_data = get_transits(transit_jd, lat, lon)
    transits = transit_data.get("transits") or {}

    result = []
    for yoga in natal_yogas:
        participants = _get_yoga_participants(yoga)
        if not participants:
            continue
        # Filter 2: Dasha permission
        dasha_lords = {md_lord, ad_lord} - {None}
        if not (dasha_lords & set(participants)):
            result.append({
                "yoga_name": yoga.get("name", ""),
                "status": "Dormant",
                "reason": "Dasha lord not a yoga participant",
                "dasha_md": md_lord,
                "dasha_ad": ad_lord,
                "participants": participants,
                "bindus": None,
                "quality": None,
                "trigger_planet": None,
                "transit_sign": None,
            })
            continue

        # Filter 3: Transit contact
        active_trigger = None
        trigger_sign = None
        bindus = None
        for p in participants:
            if p not in transits or p not in natal_sign_map:
                continue
            natal_sign = natal_sign_map[p]
            transit_sign = transits[p].get("sign")
            if transit_sign is None:
                continue
            if isinstance(transit_sign, dict):
                transit_sign = transit_sign.get("sign_index", transit_sign.get("sign", 0))
            if _is_transit_contact(natal_sign, int(transit_sign)):
                active_trigger = p
                trigger_sign = int(transit_sign)
                transit_house = transits[p].get("house", 1)
                bindus = _get_bindu_at_transit(transit_jd, lat, lon, p, transit_house)
                break

        if active_trigger is None:
            result.append({
                "yoga_name": yoga.get("name", ""),
                "status": "Dormant",
                "reason": "No transit contact (conjunction/opposition/trikona)",
                "dasha_md": md_lord,
                "dasha_ad": ad_lord,
                "participants": participants,
                "bindus": None,
                "quality": None,
                "trigger_planet": None,
                "transit_sign": None,
            })
        else:
            quality = _bindu_quality(bindus) if bindus is not None else "Sama"
            result.append({
                "yoga_name": yoga.get("name", ""),
                "status": "Active",
                "reason": "Transit contact",
                "dasha_md": md_lord,
                "dasha_ad": ad_lord,
                "participants": participants,
                "bindus": bindus,
                "quality": quality,
                "trigger_planet": active_trigger,
                "transit_sign": trigger_sign,
            })

    return result


# Alias for API / documentation: same as evaluate_current_activation
evaluate_transit_activation_summary = evaluate_current_activation


def evaluate_transit_activation_forecast(
    dob: str,
    time: str,
    lat: float,
    lon: float,
    timezone: str,
    years: int = 100,
) -> List[Dict]:
    """
    Next N-year activation windows (default 100 years). Optimized strategy:
    A) Vimshottari windows from today -> today + years
    B) Keep only windows where MD or AD lord is a yoga participant
    C) Slow planets (Saturn, Jupiter, Mars): sign-ingress-based scanning (no per-day loops)
    D) Fast planets (Sun, Venus, Mercury): only if window >= 6 months, step by 7 days; Moon ignored
    E) When transit hits conjunction/opposition/trikona, evaluate bindus; >= 5 -> MAJOR, < 4 -> weak
    """
    today = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    end_date = today + timedelta(days=years * 365)
    try:
        _, _, natal_yogas, natal_sign_map = _prepare_natal_yogas(dob, time, lat, lon, timezone)
    except Exception:
        return []

    yoga_participants = {y.get("name", ""): _get_yoga_participants(y) for y in natal_yogas}
    participants_set = set()
    for plist in yoga_participants.values():
        participants_set.update(plist)

    dasha = calculate_vimshottari_dasha(dob, time, lat, lon, timezone, calculation_date=today)
    mahadashas = dasha.get("mahadashas") or []
    antardashas_dict = dasha.get("antardashas") or {}
    windows: List[Tuple[datetime, datetime, str, str]] = []
    for m in mahadashas:
        ms = datetime.fromisoformat(m["start"].replace("Z", "+00:00"))
        me = datetime.fromisoformat(m["end"].replace("Z", "+00:00"))
        if me < today or ms > end_date:
            continue
        md_lord = m["planet"]
        if md_lord not in participants_set:
            continue
        for ad in antardashas_dict.get(md_lord, []):
            astart = datetime.fromisoformat(ad["start"].replace("Z", "+00:00"))
            aend = datetime.fromisoformat(ad["end"].replace("Z", "+00:00"))
            if aend < today or astart > end_date:
                continue
            ad_lord = ad["planet"]
            if ad_lord not in participants_set:
                continue
            w_start = max(astart, today)
            w_end = min(aend, end_date)
            if w_start < w_end:
                windows.append((w_start, w_end, md_lord, ad_lord))

    forecast: List[Dict] = []
    seen: set = set()
    # Ingress step days: Saturn ~30, Jupiter ~15, Mars ~7
    ingress_steps = {"Saturn": 30, "Jupiter": 15, "Mars": 7}

    for w_start, w_end, md_lord, ad_lord in windows:
        window_days = (w_end - w_start).days
        use_fast = window_days >= MIN_WINDOW_DAYS_FOR_FAST

        for yoga_name, participants in yoga_participants.items():
            if md_lord not in participants and ad_lord not in participants:
                continue

            # Slow planets: ingress-based
            for p in participants:
                if p not in SLOW_PLANETS or p not in natal_sign_map:
                    continue
                step_d = ingress_steps.get(p, 7)
                ingresses = _find_sign_ingresses(p, w_start, w_end, timezone, lat, lon, step_d)
                for dt, t_sign in ingresses:
                    natal_sign = natal_sign_map[p]
                    if not _is_transit_contact(natal_sign, t_sign):
                        continue
                    key = (yoga_name, dt.date().isoformat(), p)
                    if key in seen:
                        continue
                    seen.add(key)
                    jd = get_julian_day(local_to_utc(dt.replace(tzinfo=None), timezone))
                    transits = get_transits(jd, lat, lon).get("transits") or {}
                    house = transits.get(p, {}).get("house", 1)
                    bindus = _get_bindu_at_transit(jd, lat, lon, p, house)
                    if bindus is not None and bindus >= 5:
                        activation_type = "MAJOR_ACTIVATION"
                    elif bindus is not None and bindus < 4:
                        activation_type = "weak"
                    else:
                        activation_type = "activation"
                    forecast.append({
                        "yoga_name": yoga_name,
                        "window_start": w_start.isoformat(),
                        "window_end": w_end.isoformat(),
                        "date_approx": dt.date().isoformat(),
                        "trigger_planet": p,
                        "activation_type": activation_type,
                        "bindus": bindus,
                        "dasha_md": md_lord,
                        "dasha_ad": ad_lord,
                    })

            # Fast planets: only if window >= 6 months, step 7 days
            if not use_fast:
                continue
            step_days = 7
            current = w_start
            while current <= w_end:
                try:
                    jd = get_julian_day(local_to_utc(current.replace(tzinfo=None), timezone))
                    transits = get_transits(jd, lat, lon).get("transits") or {}
                    for p in participants:
                        if p not in FAST_PLANETS_FORECAST or p not in transits or p not in natal_sign_map:
                            continue
                        natal_sign = natal_sign_map[p]
                        t_sign = transits[p].get("sign")
                        if t_sign is None:
                            continue
                        if isinstance(t_sign, dict):
                            t_sign = t_sign.get("sign_index", t_sign.get("sign", 0))
                        if not _is_transit_contact(natal_sign, int(t_sign)):
                            continue
                        key = (yoga_name, current.date().isoformat(), p)
                        if key in seen:
                            current += timedelta(days=step_days)
                            continue
                        seen.add(key)
                        house = transits[p].get("house", 1)
                        bindus = _get_bindu_at_transit(jd, lat, lon, p, house)
                        if bindus is not None and bindus >= 5:
                            activation_type = "MAJOR_ACTIVATION"
                        elif bindus is not None and bindus < 4:
                            activation_type = "weak"
                        else:
                            activation_type = "activation"
                        forecast.append({
                            "yoga_name": yoga_name,
                            "window_start": w_start.isoformat(),
                            "window_end": w_end.isoformat(),
                            "date_approx": current.date().isoformat(),
                            "trigger_planet": p,
                            "activation_type": activation_type,
                            "bindus": bindus,
                            "dasha_md": md_lord,
                            "dasha_ad": ad_lord,
                        })
                except Exception:
                    pass
                current += timedelta(days=step_days)

    return forecast
