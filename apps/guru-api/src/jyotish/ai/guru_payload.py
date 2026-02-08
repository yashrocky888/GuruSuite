"""
Guru Context payload builder for AI predictions.

Builds the single JSON payload (natal, strength, time, transit, quality, panchanga)
and attaches dynamic horizon keys: transit_events (daily), monthly_transits (monthly).
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import swisseph as swe

from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha.vimshottari_engine import calculate_vimshottari_dasha
from src.jyotish.transits.gochar import get_transits
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.jyotish.varga_engine import build_varga_chart, compute_vargottama_flags
from src.utils.converters import normalize_degrees, degrees_to_sign, longitude_to_sign_index
from src.utils.timezone import get_julian_day, local_to_utc
from src.ephemeris.ephemeris_utils import get_ascendant, get_ayanamsa, get_houses
from src.ephemeris.planets_drik import get_nakshatra_pada
from src.jyotish.dasha.vimshottari_engine import get_nakshatra_lord
from src.jyotish.strength.avastha import get_transit_avastha, get_transit_dignity
from src.monthly.monthly_transit_map import generate_month_transit_positions, identify_major_shifts

# Sign names for numeric mapping (0-11)
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _sign_name_to_index(name: str) -> int:
    """Map sign name to 0-11. Numeric only."""
    for i, s in enumerate(SIGN_NAMES):
        if s.lower() == (name or "").lower():
            return i
    return 0


def _moon_longitude_at_jd(jd: float) -> float:
    """Return Moon longitude 0–360 at given JD."""
    planets = get_planet_positions(jd)
    moon = planets.get("Moon")
    if moon is None:
        return 0.0
    return normalize_degrees(float(moon))


def _house_from_lagna_sign(transit_sign_index: int, lagna_sign_index: int) -> int:
    """
    House 1–12 from Lagna using sign-based formula only.
    LOCK: house_number = ((transit_sign_index - lagna_sign_index) % 12) + 1
    No degree-based calculation. No frontend override.
    """
    return ((transit_sign_index - lagna_sign_index) % 12) + 1


def _find_moon_sign_change_jd(
    jd_start: float,
    jd_end: float,
    from_sign_index: int,
    to_sign_index: int,
    max_iter: int = 25,
) -> float:
    """Binary search: JD at which Moon sign changes from from_sign to to_sign."""
    low, high = jd_start, jd_end
    for _ in range(max_iter):
        if high - low < 1e-6:
            break
        jd_mid = (low + high) / 2.0
        lon = _moon_longitude_at_jd(jd_mid)
        sign_here = longitude_to_sign_index(lon)
        if sign_here == from_sign_index:
            low = jd_mid
        elif sign_here == to_sign_index:
            high = jd_mid
        else:
            low = jd_mid
    return (low + high) / 2.0


def _daily_moon_shift(
    calculation_date: datetime,
    timezone: str,
    transit_jd: float,
    natal_asc_degree: float,
) -> List[Dict[str, Any]]:
    """
    Daily horizon: same-day Moon sign change only.
    Returns one event with from_sign_index, from_house, to_sign_index, to_house, time_local.
    If no sign change that day, returns [].
    """
    try:
        day_start = calculation_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        tz_start = local_to_utc(day_start, timezone)
        tz_end = local_to_utc(day_end, timezone)
        jd_start = get_julian_day(tz_start)
        jd_end = get_julian_day(tz_end)

        moon_start = _moon_longitude_at_jd(jd_start)
        moon_end = _moon_longitude_at_jd(jd_end)
        current_sign_index = longitude_to_sign_index(moon_start)
        next_sign_index = longitude_to_sign_index(moon_end)

        if current_sign_index == next_sign_index:
            return []

        change_jd = _find_moon_sign_change_jd(
            jd_start, jd_end, current_sign_index, next_sign_index
        )

        lagna_sign_index = longitude_to_sign_index(natal_asc_degree)
        from_house = ((current_sign_index - lagna_sign_index) % 12) + 1
        to_house = ((next_sign_index - lagna_sign_index) % 12) + 1

        if current_sign_index != next_sign_index and from_house == to_house:
            raise RuntimeError("INVALID MOON HOUSE TRANSITION")

        from src.jyotish.panchanga.panchanga_engine import _jd_to_datetime
        change_dt = _jd_to_datetime(change_jd, timezone)
        change_time_iso = change_dt.strftime("%Y-%m-%dT%H:%M:%S")

        return [
            {
                "planet": "Moon",
                "event": "sign_change",
                "from_sign_index": current_sign_index,
                "from_house": from_house,
                "to_sign_index": next_sign_index,
                "to_house": to_house,
                "time_local": change_time_iso,
            }
        ]
    except RuntimeError:
        raise
    except Exception:
        return []


def _monthly_planet_shifts(
    calculation_date: datetime,
    timezone: str,
    transit_jd: float,
) -> List[Dict[str, Any]]:
    """
    Deterministic JD-based monthly sign change detection.
    Detects ALL sign changes within the calendar month.
    Numeric-only payload.
    """
    try:
        from src.utils.timezone import local_to_utc, get_julian_day
        from src.jyotish.kundli_engine import get_planet_positions
        from src.utils.converters import normalize_degrees
        from src.jyotish.panchanga.panchanga_engine import _jd_to_datetime

        year = calculation_date.year
        month = calculation_date.month

        month_start = calculation_date.replace(day=1, hour=12, minute=0, second=0, microsecond=0)

        if month == 12:
            next_month = month_start.replace(year=year + 1, month=1)
        else:
            next_month = month_start.replace(month=month + 1)

        tz_start = local_to_utc(month_start, timezone)
        tz_end = local_to_utc(next_month, timezone)

        jd_start = get_julian_day(tz_start)
        jd_end = get_julian_day(tz_end)

        planets_to_track = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

        result: List[Dict[str, Any]] = []

        # initial sign snapshot
        prev_positions = get_planet_positions(jd_start)

        prev_signs = {}
        for p in planets_to_track:
            lon = normalize_degrees(prev_positions.get(p, 0))
            prev_signs[p] = int(lon // 30) % 12

        jd = jd_start + 1  # start stepping day by day

        while jd < jd_end:
            positions = get_planet_positions(jd)

            for p in planets_to_track:
                lon = normalize_degrees(positions.get(p, 0))
                current_sign = int(lon // 30) % 12

                if current_sign != prev_signs[p]:
                    dt_shift = _jd_to_datetime(jd, timezone)
                    date_str = dt_shift.strftime("%b %d")  # Example: "Feb 08"
                    from_lon = normalize_degrees(prev_positions.get(p, 0))
                    to_lon = normalize_degrees(positions.get(p, 0))
                    from_nak = get_nakshatra_pada(from_lon).get("name", "")
                    to_nak = get_nakshatra_pada(to_lon).get("name", "")
                    is_retro = (current_sign == (prev_signs[p] - 1) % 12)

                    result.append({
                        "planet": p,
                        "date": date_str,
                        "from_sign_index": prev_signs[p],
                        "to_sign_index": current_sign,
                        "from_nakshatra": from_nak,
                        "to_nakshatra": to_nak,
                        "is_retrograde": is_retro,
                    })

                    prev_signs[p] = current_sign

            jd += 1  # step 1 day

        return result

    except Exception:
        return []


def _yearly_planet_shifts(
    calculation_date: datetime,
    timezone: str,
    transit_jd: float,
) -> List[Dict[str, Any]]:
    """
    Deterministic 12-month sign change detection.
    Tracks Jupiter and Saturn only.
    Numeric-only payload.
    """
    try:
        from src.utils.timezone import local_to_utc, get_julian_day
        from src.jyotish.kundli_engine import get_planet_positions
        from src.utils.converters import normalize_degrees
        from src.jyotish.panchanga.panchanga_engine import _jd_to_datetime

        # 12-month rolling window
        start_dt = calculation_date.replace(hour=12, minute=0, second=0, microsecond=0)
        end_dt = start_dt.replace(year=start_dt.year + 1)

        tz_start = local_to_utc(start_dt, timezone)
        tz_end = local_to_utc(end_dt, timezone)

        jd_start = get_julian_day(tz_start)
        jd_end = get_julian_day(tz_end)

        planets_to_track = ["Jupiter", "Saturn"]

        result: List[Dict[str, Any]] = []

        prev_positions = get_planet_positions(jd_start)

        prev_signs = {}
        for p in planets_to_track:
            lon = normalize_degrees(prev_positions.get(p, 0))
            prev_signs[p] = int(lon // 30) % 12

        jd = jd_start + 5  # step 5 days for performance

        while jd < jd_end:
            positions = get_planet_positions(jd)

            for p in planets_to_track:
                lon = normalize_degrees(positions.get(p, 0))
                current_sign = int(lon // 30) % 12

                if current_sign != prev_signs[p]:
                    dt_shift = _jd_to_datetime(jd, timezone)
                    date_str = dt_shift.strftime("%b %d")
                    from_lon = normalize_degrees(prev_positions.get(p, 0))
                    to_lon = normalize_degrees(positions.get(p, 0))
                    from_nak = get_nakshatra_pada(from_lon).get("name", "")
                    to_nak = get_nakshatra_pada(to_lon).get("name", "")
                    is_retro = (current_sign == (prev_signs[p] - 1) % 12)

                    result.append({
                        "planet": p,
                        "date": date_str,
                        "from_sign_index": prev_signs[p],
                        "to_sign_index": current_sign,
                        "from_nakshatra": from_nak,
                        "to_nakshatra": to_nak,
                        "is_retrograde": is_retro,
                    })

                    prev_signs[p] = current_sign

            jd += 5  # 5-day step

        return result

    except Exception:
        return []


def build_guru_context(
    birth_details: Dict[str, Any],
    timescale: str = "daily",
    calculation_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Build complete Guru Context JSON (natal, strength, time, transit, quality, panchanga).
    After computing transit_jd and base transit data, attaches dynamic horizon keys:
    - daily: result["transit_events"] = _daily_moon_shift(...)
    - monthly: result["monthly_transits"] = _monthly_planet_shifts(...)
    """
    dob = birth_details.get("dob") or birth_details.get("birth_date") or ""
    time_str = birth_details.get("time") or birth_details.get("birth_time") or "12:00"
    lat = float(birth_details.get("lat") or birth_details.get("birth_latitude") or 0)
    lon = float(birth_details.get("lon") or birth_details.get("birth_longitude") or 0)
    timezone = birth_details.get("timezone") or "Asia/Kolkata"

    if calculation_date is None:
        calculation_date = datetime.now()

    # Birth JD
    try:
        dt_birth = datetime.strptime(f"{dob} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            dt_birth = datetime.strptime(f"{dob} {time_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt_birth = datetime.strptime(str(dob)[:10], "%Y-%m-%d").replace(hour=12, minute=0, second=0, microsecond=0)
    tz_birth = local_to_utc(dt_birth.replace(tzinfo=None), timezone)
    birth_jd = get_julian_day(tz_birth)

    # Transit JD (noon on calculation_date for stability)
    calc_noon = calculation_date.replace(hour=12, minute=0, second=0, microsecond=0)
    tz_calc = local_to_utc(calc_noon, timezone)
    transit_jd = get_julian_day(tz_calc)

    # Natal: D1 + D9 vargottama + yogas
    kundli = generate_kundli(birth_jd, lat, lon)
    planets_d1 = kundli.get("Planets") or {}
    houses_d1 = kundli.get("Houses") or []
    ascendant = kundli.get("Ascendant") or {}
    d1_lons = {p: planets_d1[p].get("degree") for p in planets_d1 if planets_d1[p].get("degree") is not None}
    d1_asc = ascendant.get("degree") or 0
    vargottama_flags = {}
    try:
        d9 = build_varga_chart(d1_lons, d1_asc, 9)
        d9_planets = d9.get("planets") or d9.get("Planets") or {}
        vargottama_flags = compute_vargottama_flags(planets_d1, d9_planets)
    except Exception:
        pass
    planets_for_natal = {}
    for p, data in planets_d1.items():
        rec = dict(data) if isinstance(data, dict) else {}
        rec["is_vargottama"] = vargottama_flags.get(p, False)
        planets_for_natal[p] = rec
    planets_list = list(planets_d1.keys())
    houses_list = [{"house": h.get("house"), "sign": h.get("sign"), "sign_index": h.get("sign_index")} for h in houses_d1]
    try:
        yoga_analysis = detect_all_yogas(
            {p: planets_d1[p] for p in planets_list if p in planets_d1},
            houses_d1,
        )
        all_yogas = yoga_analysis.get("all_yogas") or []
    except Exception:
        all_yogas = []
    # Natal planets: explicit payload for AI (sign_index, degree, house, nakshatra, pada, is_retrograde, is_combust)
    # All values from already-computed planets_d1 — no new calculation.
    natal_planets = {}
    for pname, data in planets_d1.items():
        rec = data if isinstance(data, dict) else {}
        deg = rec.get("degree")
        if deg is None:
            continue
        sign_idx = rec.get("sign_index")
        if sign_idx is None:
            sign_idx = int(float(deg) // 30) % 12
        house = rec.get("house")
        if house is None:
            house = 1
        nakshatra = rec.get("nakshatra")
        pada = rec.get("pada", 1)
        if nakshatra is None or nakshatra == "":
            nak_pada = get_nakshatra_pada(float(deg))
            nakshatra = nak_pada.get("name", "")
            pada = nak_pada.get("pada", 1)
        is_retrograde = bool(rec.get("retro", False))
        natal_planets[pname] = {
            "sign_index": sign_idx,
            "degree": round(float(deg), 4),
            "house": house,
            "nakshatra": nakshatra,
            "pada": pada,
            "is_retrograde": is_retrograde,
        }
        if rec.get("is_combust") is not None:
            natal_planets[pname]["is_combust"] = rec["is_combust"]
        elif rec.get("combust") is not None:
            natal_planets[pname]["is_combust"] = rec["combust"]

    natal = {
        "planets_d1": planets_for_natal,
        "planets": natal_planets,
        "ascendant": ascendant,
        "yogas": all_yogas,
    }

    # Strength: Shadbala (stub if not available)
    strength = {}
    try:
        from src.jyotish.strength.shadbala import calculate_shadbala
        shadbala_result = calculate_shadbala(birth_jd, lat, lon)
        for p, data in (shadbala_result.get("planets") or {}).items():
            strength[p] = {
                "rupas": data.get("shadbala_in_rupas") or data.get("rupas"),
                "total_virupas": data.get("total_virupas"),
                "status": data.get("status"),
            }
    except Exception:
        pass

    # Time: Dasha + permission
    time_block = {"permission_granted": True, "mahadasha_lord": None, "antardasha_lord": None, "active_yogas_count": 0}
    try:
        dasha = calculate_vimshottari_dasha(
            dob, time_str, lat, lon, timezone,
            calculation_date=calculation_date,
        )
        current = dasha.get("current_dasha") or {}
        time_block["mahadasha_lord"] = current.get("mahadasha")
        time_block["antardasha_lord"] = current.get("antardasha")
        time_block["dasha_end"] = current.get("end")
    except Exception:
        pass
    try:
        from src.jyotish.transits.yoga_activation_engine import evaluate_current_activation
        activations = evaluate_current_activation(dob, time_str, lat, lon, timezone, calculation_date=calculation_date)
        active = [a for a in activations if a.get("status") == "Active"]
        time_block["active_yogas_count"] = len(active)
        if not active and time_block.get("mahadasha_lord"):
            time_block["permission_granted"] = True
    except Exception:
        pass

    # Transit: positions + house_from_lagna, house_from_moon, nakshatra, pada, is_retrograde
    # Same transit degree used for Ashtakavarga/strength — enrich with nakshatra/retro only.
    transit_block = {}
    try:
        from src.ephemeris.planets_jhora_exact import calculate_all_planets_jhora_exact

        natal_asc = ascendant.get("degree") or 0
        natal_moon = planets_d1.get("Moon", {}).get("degree") or 0
        lagna_sign_index = longitude_to_sign_index(natal_asc)
        moon_sign_index = longitude_to_sign_index(natal_moon)
        transits_data = get_transits(transit_jd, lat, lon)
        transits_dict = transits_data.get("transits") or transits_data
        transit_full = calculate_all_planets_jhora_exact(transit_jd)
        for pname, pdata in (transits_dict or {}).items():
            deg = pdata.get("degree") if isinstance(pdata, dict) else pdata
            if deg is None:
                continue
            deg = float(deg)
            if deg >= 360.0:
                deg = deg % 360.0
            sign_num, _ = degrees_to_sign(deg)
            house_lagna = _house_from_lagna_sign(sign_num, lagna_sign_index)
            house_moon = _house_from_lagna_sign(sign_num, moon_sign_index)
            nak_pada = get_nakshatra_pada(deg)
            is_retro = bool(transit_full.get(pname, {}).get("retro", False))
            dignity = get_transit_dignity(pname, sign_num) if pname not in ("Rahu", "Ketu") else "neutral"
            entry = {
                "degree": round(deg, 4),
                "sign_index": sign_num,
                "house_from_lagna": house_lagna,
                "house_from_moon": house_moon,
                "transit_house": house_lagna,
                "dignity": dignity,
                "nakshatra": nak_pada.get("name", ""),
                "pada": nak_pada.get("pada", 1),
                "is_retrograde": is_retro,
            }
            if isinstance(pdata, dict) and pdata.get("aspects") is not None:
                entry["aspects"] = pdata["aspects"]
            pfull = transit_full.get(pname, {})
            if pfull.get("is_combust") is not None:
                entry["is_combust"] = pfull["is_combust"]
            # Avastha: tone modifier only (Rahu/Ketu excluded—no Deeptadi/Sayanadi)
            if pname not in ("Rahu", "Ketu"):
                try:
                    avastha = get_transit_avastha(pname, deg, calculation_date=calculation_date)
                    if avastha and avastha.get("modifier_suggestion"):
                        mod = avastha["modifier_suggestion"]
                        if not (dignity == "debilitated" and mod == "Strength amplified."):
                            entry["avastha"] = avastha
                except Exception:
                    pass
            if pname in ("Rahu", "Ketu"):
                nak_idx = nak_pada.get("index", int(deg / (360.0 / 27.0)) % 27)
                entry["nakshatra_lord"] = get_nakshatra_lord(nak_idx)
            transit_block[pname] = entry
    except Exception:
        pass

    # Quality: Ashtakavarga bindus (stub if not available)
    quality = {}
    try:
        from src.jyotish.strength.ashtakavarga import calculate_bhinnashtakavarga
        from src.jyotish.strength.ashtakavarga import PLANETS as BAV_PLANETS
        asc_tropical = get_ascendant(transit_jd, lat, lon)
        ayanamsa = get_ayanamsa(transit_jd)
        asc_sidereal = normalize_degrees(asc_tropical - ayanamsa)
        houses_list_tropical = get_houses(transit_jd, lat, lon)
        house_cusps = [normalize_degrees(h - ayanamsa) for h in (houses_list_tropical or [])[1:12]]
        all_planets = get_planet_positions(transit_jd)
        for pname in transit_block:
            if pname not in BAV_PLANETS:
                continue
            house_num = transit_block[pname].get("house_from_lagna", 1)
            bav = calculate_bhinnashtakavarga(
                pname, all_planets.get(pname, 0), all_planets, house_cusps, asc_sidereal
            )
            idx = house_num - 1
            if 0 <= idx < len(bav):
                quality[pname] = {"bindu": bav[idx], "transit_house": house_num}
    except Exception:
        pass

    # Panchanga (stub if not available)
    panchanga = {}
    try:
        from src.jyotish.panchanga.panchanga_engine import calculate_panchanga
        date_str = calculation_date.strftime("%Y-%m-%d")
        panchanga = calculate_panchanga(date_str, lat, lon, timezone) or {}
    except Exception:
        try:
            from src.jyotish.panchang import calculate_panchang
            panchanga = calculate_panchang(transit_jd, calculation_date, lat, lon) or {}
        except Exception:
            pass

    # Janma Nakshatra: explicit block so AI does not derive manually (Moon natal nakshatra/pada/degree)
    moon_natal = planets_d1.get("Moon") or {}
    janma_nakshatra = {
        "name": moon_natal.get("nakshatra") or get_nakshatra_pada(float(moon_natal.get("degree", 0))).get("name", ""),
        "pada": moon_natal.get("pada", 1),
        "degree": round(float(moon_natal.get("degree", 0)), 4),
    }

    # Tara Bala: transit Moon nakshatra vs Janma nakshatra (0-26 indices)
    tara_bala_block = {}
    try:
        from src.jyotish.math.suitability import calculate_tara_bala
        moon_transit = transit_block.get("Moon") or {}
        transit_moon_nak = moon_transit.get("nakshatra")
        janma_name = janma_nakshatra.get("name") or ""
        if transit_moon_nak and janma_name:
            nakshatra_span = 360.0 / 27.0
            birth_moon_deg = float(moon_natal.get("degree", 0))
            transit_moon_deg = float(moon_transit.get("degree", 0))
            birth_nak_idx = int(birth_moon_deg / nakshatra_span) % 27
            transit_nak_idx = int(transit_moon_deg / nakshatra_span) % 27
            tara_result = calculate_tara_bala(birth_nak_idx, transit_nak_idx)
            tara_bala_block["tara_category"] = tara_result.get("tara_name", "")
            tara_bala_block["quality"] = tara_result.get("quality", "")
    except Exception:
        pass

    # Lordship: house lords, per-planet flags (for zero-hardcode interpretation engine)
    lordship_block = {}
    try:
        from src.jyotish.kundli_engine import SIGN_LORDS
        from src.jyotish.strength.planet_functional_strength import calculate_functional_nature

        lagna_sign_index = longitude_to_sign_index(d1_asc)
        DUSTHANA = {6, 8, 12}
        KENDRAS = {1, 4, 7, 10}
        TRIKONAS = {1, 5, 9}

        house_lords = {}
        for h in range(1, 13):
            house_sign_index = (lagna_sign_index + h - 1) % 12
            house_lords[h] = SIGN_LORDS.get(house_sign_index, "Unknown")

        for pname in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            lordships = [h for h, lord in house_lords.items() if lord == pname]
            if not lordships and pname == "Rahu":
                lordships = [h for h in range(1, 13) if (lagna_sign_index + h - 1) % 12 == 10]
            if not lordships and pname == "Ketu":
                lordships = [h for h in range(1, 13) if (lagna_sign_index + h - 1) % 12 == 7]
            owned = set(lordships)
            is_dusthana_lord = bool(owned & DUSTHANA)
            is_kendra_lord = bool(owned & KENDRAS)
            is_trikona_lord = bool(owned & TRIKONAS)
            is_yogakaraka = is_kendra_lord and is_trikona_lord
            func_nature = "neutral"
            if pname not in ("Rahu", "Ketu"):
                func_nature = calculate_functional_nature(pname, lagna_sign_index)
            lordship_block[pname] = {
                "lordships": lordships,
                "is_dusthana_lord": is_dusthana_lord,
                "is_kendra_lord": is_kendra_lord,
                "is_yogakaraka": is_yogakaraka,
                "functional_nature": func_nature,
            }
        lordship_block["_house_lords"] = house_lords
    except Exception:
        pass

    # Most afflicted house: debilitated planet's transit house, or lowest bindu
    most_afflicted_house = None
    afflicted_reason = ""
    try:
        for pname, pdata in (transit_block or {}).items():
            if isinstance(pdata, dict) and pdata.get("dignity") == "debilitated":
                most_afflicted_house = int(pdata.get("transit_house") or pdata.get("house_from_lagna", 1))
                afflicted_reason = "debilitated_planet"
                break
        if most_afflicted_house is None and quality:
            min_bindu, min_house = 999, None
            for pname, qdata in quality.items():
                if isinstance(qdata, dict):
                    b = qdata.get("bindu")
                    h = qdata.get("transit_house")
                    if b is not None and h is not None and int(b) < min_bindu:
                        min_bindu, min_house = int(b), int(h)
            if min_house is not None and min_bindu < 4:
                most_afflicted_house = min_house
                afflicted_reason = "low_bindu"
    except Exception:
        pass

    # Stress flags for remedy gating (LLM must obey)
    stress_flags = {}
    try:
        from src.jyotish.ai.interpretation_engine import compute_stress_flags
        temp_result = {
            "janma_nakshatra": janma_nakshatra,
            "transit": transit_block,
            "quality": quality,
            "time": time_block,
            "tara_bala": tara_bala_block,
            "lordship": lordship_block,
        }
        stress_flags = compute_stress_flags(temp_result)
    except Exception:
        stress_flags = {"severe_stress": False, "moderate_stress": False}

    result = {
        "janma_nakshatra": janma_nakshatra,
        "natal": natal,
        "strength": strength,
        "time": time_block,
        "transit": transit_block,
        "quality": quality,
        "panchanga": panchanga,
        "tara_bala": tara_bala_block,
        "lordship": lordship_block,
        "most_afflicted_house": most_afflicted_house,
        "afflicted_reason": afflicted_reason,
        "calculation_date": calculation_date.replace(tzinfo=None).isoformat() if calculation_date else None,
        "severe_stress": stress_flags.get("severe_stress", False),
        "moderate_stress": stress_flags.get("moderate_stress", False),
    }

    # --- DYNAMIC HORIZON VISIBILITY (additive only) ---
    # DAILY: attach transit_events so AI + API see daily Moon sign-change (from/to + time_local)
    if timescale == "daily":
        events = _daily_moon_shift(
            calculation_date, timezone, transit_jd, natal_asc_degree=d1_asc
        )
        result["transit_events"] = events if events else []

    # MONTHLY: attach monthly_transits so AI + API see Mercury/Sun shifts
    if timescale == "monthly":
        shifts = _monthly_planet_shifts(calculation_date, timezone, transit_jd)
        result["monthly_transits"] = shifts if shifts else []

    # YEARLY: attach Jupiter/Saturn sign changes
    if timescale == "yearly":
        yearly_shifts = _yearly_planet_shifts(calculation_date, timezone, transit_jd)
        result["yearly_transits"] = yearly_shifts if yearly_shifts else []

    # Gita: contextual verse for dharmic guidance (daily only)
    if timescale == "daily":
        try:
            from src.jyotish.ai.gita_engine import get_contextual_gita
            result["gita"] = get_contextual_gita(result)
        except Exception:
            result["gita"] = {}

    return result
