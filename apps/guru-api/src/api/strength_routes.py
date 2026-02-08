"""
Planetary Strength API routes.

Phase 5: Shadbala and Ashtakavarga calculation endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import swisseph as swe

from src.jyotish.strength.shadbala import calculate_shadbala, SHADBALA_CONFIG
from src.jyotish.strength.ashtakavarga import calculate_ashtakavarga
from src.jyotish.yogas.yoga_engine import detect_yogas, is_dasha_connected, build_d1_sign_map_for_sambandha
from src.jyotish.dasha.vimshottari_engine import calculate_vimshottari_dasha as calculate_vimshottari_dasha_complete
from src.jyotish.kundli_engine import get_planet_positions
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses
from src.utils.timezone import get_julian_day, local_to_utc

router = APIRouter()


@router.get("/shadbala")
def get_shadbala(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    timezone: str = Query("Asia/Kolkata", description="Timezone (default: Asia/Kolkata)")
):
    """
    Phase 5: Calculate Shadbala (Six-fold Strength) for all planets.
    
    Shadbala consists of:
    - Naisargika Bala (Natural strength)
    - Cheshta Bala (Motional strength - retrograde)
    - Sthana Bala (Positional strength) with sub-components:
      - Uchcha Bala (Exaltation strength)
      - Saptavargaja Bala (Seven-fold dignity)
      - Ojhayugmarasiamsa Bala (Odd/Even sign strength)
      - Kendradi Bala (Kendra/Panaphara/Apoklima strength)
      - Drekkana Bala (Decanate strength)
    - Dig Bala (Directional strength)
    - Kala Bala (Temporal strength) with sub-components:
      - Nathonnatha Bala (Day/Night strength)
      - Paksha Bala (Lunar phase strength)
      - Tribhaga Bala (Time division strength)
      - Varsha Bala (Year strength)
      - Masa Bala (Month strength)
      - Dina Bala (Day strength)
      - Hora Bala (Hour strength)
      - Ayana Bala (Solstice strength)
    - Drik Bala (Aspectual strength)
    
    Calculation Mode: PURE BPHS STANDARD
    - Kendradi: 60 / 30 / 15 (Kendra / Panaphara / Apoklima)
    - Dig Bala: Angular Distance / 3 (no planet-specific scaling)
    - Saptavargaja: Raw sum of 7 Vargas (no normalization)
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
        timezone: Timezone string (default: Asia/Kolkata)
    
    Returns:
        Complete Shadbala data for all planets including:
        - All six main Bala components
        - Sthana Bala sub-components
        - Kala Bala sub-components
        - Total Virupas
        - Rupas (Total / 60)
        - Relative Rank (1-7, where 1 is strongest)
    """
    try:
        # Parse date and time
        date_obj = datetime.strptime(dob, "%Y-%m-%d").date()
        time_parts = time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        # Create local datetime
        birth_dt_local = datetime.combine(
            date_obj,
            datetime.min.time().replace(hour=hour, minute=minute, second=second)
        )
        
        # Convert to UTC
        birth_dt_utc = local_to_utc(birth_dt_local, timezone)
        
        # Calculate Julian Day
        jd = get_julian_day(birth_dt_utc)
        
        # Calculate Shadbala
        shadbala_data = calculate_shadbala(jd, lat, lon, timezone=timezone)
        
        return {
            "calculation_mode": "PURE BPHS STANDARD",
            "config": {
                "kendradi_scale": SHADBALA_CONFIG["KENDRADI_SCALE"],
                "dig_bala_sun_multiplier": SHADBALA_CONFIG["DIGBALA_SUN_MULTIPLIER"],
                "saptavargaja_divisor": SHADBALA_CONFIG["SAPTAVARGAJA_DIVISOR"]
            },
            "julian_day": round(jd, 6),
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon,
                "timezone": timezone
            },
            "shadbala": shadbala_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating shadbala: {str(e)}")


@router.get("/ashtakavarga")
def get_ashtakavarga(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Phase 5: Calculate Ashtakavarga (Eight-fold Division).
    
    Ashtakavarga shows house strength based on planetary relationships:
    - Bhinnashtakavarga (BAV): Individual planet's ashtakavarga
    - Sarvashtakavarga (SAV): Combined ashtakavarga of all planets
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        Complete Ashtakavarga data (BAV + SAV)
    """
    try:
        # Parse date and time
        dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        
        # Calculate Julian Day
        jd = swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Get planet positions (sidereal)
        planet_positions = get_planet_positions(jd)
        
        # Get ascendant and houses
        ascendant = get_ascendant(jd, lat, lon)
        houses_list = get_houses(jd, lat, lon)
        
        # Calculate Ashtakavarga
        ashtakavarga_data = calculate_ashtakavarga(
            planet_positions, houses_list, ascendant
        )
        
        return {
            "julian_day": round(jd, 6),
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon
            },
            "ashtakavarga": ashtakavarga_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating ashtakavarga: {str(e)}")


@router.get("/yogas")
def get_yogas(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    timezone: str = Query("Asia/Kolkata", description="Timezone (default: Asia/Kolkata)"),
):
    """
    Phase 1: Yoga Engine (PURE BPHS, Ancient Logic)

    Scope:
    - D1 (Rāśi) + D9 (Navāṁśa) only
    - No heuristics, no normalization, no AI
    - Shadbala ratios are used only for strength gating and base power
    """
    try:
        # Parse date and time
        date_obj = datetime.strptime(dob, "%Y-%m-%d").date()
        time_parts = time.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0

        # Create local datetime
        birth_dt_local = datetime.combine(
            date_obj,
            datetime.min.time().replace(hour=hour, minute=minute, second=second),
        )

        # Convert to UTC
        birth_dt_utc = local_to_utc(birth_dt_local, timezone)

        # Calculate Julian Day
        jd = get_julian_day(birth_dt_utc)

        # Shadbala (source of ratios) — DO NOT modify SHADBALA logic
        shadbala_data = calculate_shadbala(jd, lat, lon, timezone=timezone)

        # Detect Yogas
        yogas = detect_yogas(jd, lat, lon, shadbala_data)

        # ------------------------------------------------------------------
        # API SANITIZATION (STRICT): remove internal/debug token leakage
        # ------------------------------------------------------------------
        def _sanitize_text(value: str) -> str:
            if not isinstance(value, str):
                return value
            t = value
            # Cut debug trailers
            if ";" in t:
                t = t.split(";", 1)[0]
            if "Selected:" in t:
                t = t.split("Selected:", 1)[0]
            # Remove known internal tokens / indices
            import re
            t = re.sub(r"dist_from_lagna\s*=\s*\d+", "", t, flags=re.IGNORECASE)
            t = re.sub(r"\b(?:Moon|Sun|Mars|Mercury|Jupiter|Venus|Saturn)?\s*sign\s*=\s*\d+\b", "", t, flags=re.IGNORECASE)
            t = re.sub(r"\b[a-zA-Z_]+\s*=\s*[a-zA-Z0-9_]+\b", "", t)
            t = re.sub(r"\b[a-zA-Z_]+\s*=\s*-?\d+(?:\.\d+)?\b", "", t)
            # Normalize whitespace/punctuation
            t = re.sub(r"\s{2,}", " ", t).strip()
            t = re.sub(r"\s+,", ",", t)
            t = re.sub(r",\s*,", ",", t)
            t = re.sub(r"\s+\.", ".", t)
            t = t.strip(" ,;")
            return t

        for y in yogas:
            if not isinstance(y, dict):
                continue
            if "formation_logic" in y and isinstance(y.get("formation_logic"), str):
                y["formation_logic"] = _sanitize_text(y["formation_logic"])
            if "explanation" in y and isinstance(y.get("explanation"), str):
                y["explanation"] = _sanitize_text(y["explanation"])

        # Dasha × Yoga activation bridge (PURE BPHS sambandha; diagnostic only)
        dasha_data = calculate_vimshottari_dasha_complete(
            birth_date=dob,
            birth_time=time,
            latitude=lat,
            longitude=lon,
            timezone=timezone,
        )
        current = dasha_data.get("current_dasha", {}) if isinstance(dasha_data, dict) else {}
        md_lord = current.get("mahadasha")
        ad_lord = current.get("antardasha")

        chart_data = {"d1_signs": build_d1_sign_map_for_sambandha(jd)}

        def _activation_for_yoga(yoga: dict) -> dict:
            potency = float(yoga.get("potency_percent", 0.0) or 0.0)
            status = yoga.get("status_label")
            planets = yoga.get("planets_involved", []) or []

            # Absolute law: Mṛta yogas (including "Mṛta (Inactive)") are always Supta
            if isinstance(status, str) and status.startswith("Mṛta"):
                return {
                    "state": "Supta",
                    "state_label": "Supta (Sleeping)",
                    "is_active_now": False,
                    "manifestation_score": 0.0,
                    "connected_lords": {"mahadasha": None, "antardasha": None},
                }

            md_connected = is_dasha_connected(md_lord, planets, chart_data)
            ad_connected = is_dasha_connected(ad_lord, planets, chart_data)

            if md_connected and ad_connected:
                state = "Jāgrata"
                score = potency * 1.0
            elif md_connected ^ ad_connected:
                state = "Swapna"
                score = potency * 0.5
            else:
                state = "Supta"
                score = 0.0

            state_label = f"{state} ({'Awake' if state == 'Jāgrata' else ('Dreaming' if state == 'Swapna' else 'Sleeping')})"
            return {
                "state": state,
                "state_label": state_label,
                "is_active_now": state != "Supta",
                "manifestation_score": round(float(score), 2),
                "connected_lords": {
                    "mahadasha": md_lord if md_connected else None,
                    "antardasha": ad_lord if ad_connected else None,
                },
            }

        for y in yogas:
            if isinstance(y, dict):
                y["activation"] = _activation_for_yoga(y)

        return {
            "calculation_mode": "PURE BPHS (YOGA PHASE 1)",
            "chart_scope": ["D1", "D9"],
            "shadbala_mode": "PURE BPHS STANDARD",
            "config": {
                "kendradi_scale": SHADBALA_CONFIG["KENDRADI_SCALE"],
                "dig_bala_sun_multiplier": SHADBALA_CONFIG["DIGBALA_SUN_MULTIPLIER"],
                "saptavargaja_divisor": SHADBALA_CONFIG["SAPTAVARGAJA_DIVISOR"],
            },
            "julian_day": round(jd, 6),
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon,
                "timezone": timezone,
            },
            "yogas": yogas,
            "transparency_note": "Yogas calculated strictly as per BPHS using D1, D9, and Shadbala. No interpretive scaling.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating yogas: {str(e)}")


def _add_years_safe(dt: datetime, years: int) -> datetime:
    """
    Add years to a datetime without external dependencies.
    If the target date is invalid (e.g., Feb 29), clamp to Feb 28.
    """
    try:
        return dt.replace(year=dt.year + years)
    except ValueError:
        # Feb 29 → Feb 28 fallback
        return dt.replace(month=2, day=28, year=dt.year + years)


def _parse_iso_dt(value: str) -> datetime:
    # Dasha engine sometimes emits naive ISO; be tolerant of 'Z'
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_md_ad_range(start_md: str, start_ad: str, end_md: str, end_ad: str) -> str:
    start = f"{start_md}–{start_ad}"
    end = f"{end_md}–{end_ad}"
    return start if start == end else f"{start} → {end}"


@router.get("/yogas/timeline")
def get_yogas_timeline(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    timezone: str = Query("Asia/Kolkata", description="Timezone (default: Asia/Kolkata)"),
):
    """
    Yoga Activation Timeline (Birth → 100 years) — PURE BPHS.

    This endpoint does NOT change yoga formation or potency.
    It sweeps Vimshottari Mahadasha–Antardasha periods and computes activation_state
    using the authoritative `is_dasha_connected()` logic (identity / yuti / drishti / parivartana).
    """
    try:
        # Parse date and time
        date_obj = datetime.strptime(dob, "%Y-%m-%d").date()
        time_parts = time.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0

        # Birth datetime (local) and UTC for JD
        birth_dt_local = datetime.combine(
            date_obj,
            datetime.min.time().replace(hour=hour, minute=minute, second=second),
        )
        birth_dt_utc = local_to_utc(birth_dt_local, timezone)
        jd = get_julian_day(birth_dt_utc)

        range_start = birth_dt_local
        range_end = _add_years_safe(birth_dt_local, 100)

        # Detect yogas once (formation + potency are locked)
        shadbala_data = calculate_shadbala(jd, lat, lon, timezone=timezone)
        yogas = detect_yogas(jd, lat, lon, shadbala_data)

        # Compute full Vimshottari tree once (authoritative)
        dasha_data = calculate_vimshottari_dasha_complete(
            birth_date=dob,
            birth_time=time,
            latitude=lat,
            longitude=lon,
            timezone=timezone,
            calculation_date=range_start,  # deterministic anchor (timeline itself ignores "now")
        )
        mahadashas = dasha_data.get("mahadashas", []) if isinstance(dasha_data, dict) else []
        antardashas_dict = dasha_data.get("antardashas", {}) if isinstance(dasha_data, dict) else {}

        # Precompute chart data once for sambandha checks
        chart_data = {"d1_signs": build_d1_sign_map_for_sambandha(jd)}

        # Build a single linear MD–AD list (clipped to 100-year range)
        ad_periods = []
        for md in mahadashas:
            md_lord = md.get("planet")
            if not md_lord:
                continue
            for ad in antardashas_dict.get(md_lord, []) or []:
                ad_lord = ad.get("planet")
                start_raw = ad.get("start")
                end_raw = ad.get("end")
                if not ad_lord or not start_raw or not end_raw:
                    continue
                start_dt = _parse_iso_dt(start_raw)
                end_dt = _parse_iso_dt(end_raw)

                # clip to [range_start, range_end] (inclusive semantics preserved)
                start_dt = max(start_dt, range_start)
                end_dt = min(end_dt, range_end)
                if start_dt > end_dt:
                    continue

                ad_periods.append(
                    {
                        "md": md_lord,
                        "ad": ad_lord,
                        "start": start_dt,
                        "end": end_dt,
                    }
                )

        ad_periods.sort(key=lambda x: x["start"])

        def activation_state_for(md_lord: str, ad_lord: str, yoga: dict) -> tuple[str, float, float]:
            """
            Returns (state, multiplier, manifestation_score).
            """
            potency = float(yoga.get("potency_percent", 0.0) or 0.0)
            status = yoga.get("status_label")
            yoga_planets = yoga.get("planets_involved", []) or []

            # 1) Mṛta safeguard (includes "Mṛta (Inactive)")
            if isinstance(status, str) and status.startswith("Mṛta"):
                return "Supta", 0.0, 0.0

            md_connected = is_dasha_connected(md_lord, yoga_planets, chart_data)
            ad_connected = is_dasha_connected(ad_lord, yoga_planets, chart_data)

            if md_connected and ad_connected:
                return "Jāgrata", 1.0, potency * 1.0
            if md_connected ^ ad_connected:
                return "Swapna", 0.5, potency * 0.5
            return "Supta", 0.0, 0.0

        def consolidate(rows: list[dict]) -> list[dict]:
            """
            Merge consecutive AD blocks if yoga/state/multiplier are identical.
            """
            if not rows:
                return rows
            merged = [rows[0]]
            for r in rows[1:]:
                prev = merged[-1]
                if (
                    r["state"] == prev["state"]
                    and r["multiplier"] == prev["multiplier"]
                    and r["start_date"] <= prev["end_date"]  # no-gap requirement (allows overlap)
                ):
                    # extend
                    prev["end_date"] = max(prev["end_date"], r["end_date"])
                    prev["end_md"] = r["end_md"]
                    prev["end_ad"] = r["end_ad"]
                else:
                    merged.append(r)

            # finalize dasha_period string
            for m in merged:
                m["dasha_period"] = _format_md_ad_range(m["start_md"], m["start_ad"], m["end_md"], m["end_ad"])
                # cleanup internal
                del m["start_md"]
                del m["start_ad"]
                del m["end_md"]
                del m["end_ad"]

            return merged

        response_yogas = []
        for y in yogas:
            yoga_name = y.get("yoga_name", "Unknown Yoga")
            potency = float(y.get("potency_percent", 0.0) or 0.0)
            status = y.get("status_label")

            raw_rows = []
            for p in ad_periods:
                state, mult, score = activation_state_for(p["md"], p["ad"], y)
                raw_rows.append(
                    {
                        "start_date": p["start"].date().isoformat(),
                        "end_date": p["end"].date().isoformat(),
                        "state": state,
                        "state_label": f"{state} ({'Awake' if state == 'Jāgrata' else ('Dreaming' if state == 'Swapna' else 'Sleeping')})",
                        "manifestation_score": round(float(score), 2),
                        "multiplier": mult,
                        "start_md": p["md"],
                        "start_ad": p["ad"],
                        "end_md": p["md"],
                        "end_ad": p["ad"],
                    }
                )

            response_yogas.append(
                {
                    "yoga_name": yoga_name,
                    "timeline": consolidate(raw_rows),
                    # keep potency/status stable but do not duplicate fields at top level beyond spec
                }
            )

        return {
            "birth_range": {
                "from": range_start.date().isoformat(),
                "to": range_end.date().isoformat(),
            },
            "yogas": response_yogas,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating yoga timeline: {str(e)}")

