"""
Kundli (Birth Chart) API routes.

This module provides FastAPI endpoints for calculating and retrieving
birth charts (kundli), including D1, D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsa), D9 (Navamsa), D10 (Dasamsa), and D12 (Dwadasamsa).
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, List
from datetime import datetime
import math
import os
import logging
import swisseph as swe

from src.db.schemas import KundliRequest
from src.db.database import SessionLocal
from src.db.models import BirthDetail
from src.jyotish.kundli import calculate_kundli
from src.jyotish.kundli_engine import generate_kundli
# DEPRECATED: Direct varga imports removed - use varga_engine.py instead
# from src.jyotish.varga import calculate_navamsa, calculate_dasamsa, varga_degree
# All varga calculations now go through varga_engine.py (single source of truth)
# Note: Old calculate_all_yogas replaced by new yoga system
# from src.jyotish.yogas import calculate_all_yogas
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.ai.explanation import add_explanation_to_response
# 🔒 SCOPING SAFETY CONTRACT (FOR ALL FUTURE EDITS / AI AGENTS)
# - get_nakshatra_lord MUST be imported ONLY at module level, NEVER inside kundli_get()
# - kundli_get() and its nested helpers must ONLY CALL get_nakshatra_lord (or a captured alias),
#   they must NOT re-import or reassign it anywhere inside the function body.
# - Violating this rule causes Python to treat get_nakshatra_lord as a local variable
#   and raises: "cannot access local variable 'get_nakshatra_lord' where it is not associated with a value"
#
# 🔒 CRITICAL: Import _normalize_sign_index from canonical source (varga_engine.py)
# This ensures the function is ALWAYS available and prevents scoping errors
from src.jyotish.varga_engine import _normalize_sign_index
# 🔒 CRITICAL: Import get_nakshatra_lord at module level to prevent scoping errors
from src.jyotish.dasha_drik import get_nakshatra_lord

# Planet Functional Strength Engine (Ancient Jyotish logic)
# Backend-only extension: computes functional strength flags from D1 chart
from src.jyotish.strength.planet_functional_strength import (
    calculate_planet_functional_strength,
)

router = APIRouter()


# ⚠️ GRAHA DRISHTI HELPER — PARĀŚARI RULES ONLY (MODULE LEVEL)
# ⚠️ Computes aspects independently for EACH chart using sign_index positions
# ⚠️ This function is shared by kundli_get() and kundli_transits()
def compute_graha_drishti(planets_dict: Dict, houses_array: Optional[List[Dict]] = None, get_sign_name_fn = None) -> list:
    """
    Compute Parāśari Graha Drishti (Planetary Aspects) for a chart.
    
    Args:
        planets_dict: Dictionary of {planet_name: {sign_index: int, ...}}
        houses_array: Optional list of house dictionaries with sign_index and house number
        get_sign_name_fn: Optional function to get sign name from sign_index
    
    Returns:
        List of aspect dictionaries with aspected_house field:
        [{"from": "Mars", "aspect": "4th", "to": "Saturn", "aspected_house": "Mithuna – 2nd house"}, ...]
    """
    # Parāśari Graha Drishti Rules:
    aspect_rules = {
        "Sun": [6],      # 7th only
        "Moon": [6],     # 7th only
        "Mercury": [6],  # 7th only
        "Venus": [6],    # 7th only
        "Mars": [3, 6, 7],        # 4th, 7th, 8th
        "Jupiter": [4, 6, 8],     # 5th, 7th, 9th
        "Saturn": [2, 6, 9],      # 3rd, 7th, 10th
        "Rahu": [4, 6, 8],       # 5th, 7th, 9th
        "Ketu": [4, 6, 8],       # 5th, 7th, 9th
    }
    
    # Aspect offset to aspect name mapping
    aspect_offset_to_name = {
        2: "3rd",
        3: "4th",
        4: "5th",
        6: "7th",
        7: "8th",
        8: "9th",
        9: "10th",
    }
    
    # Reverse mapping: aspect name to offset (for aspected_house computation)
    aspect_name_to_offset = {
        "3rd": 2,
        "4th": 3,
        "5th": 4,
        "7th": 6,
        "8th": 7,
        "9th": 8,
        "10th": 9,
    }
    
    # Build sign_index -> planet_name mapping
    sign_to_planets = {}
    for planet_name, planet_data in planets_dict.items():
        planet_sign_index = planet_data.get("sign_index")
        if planet_sign_index is not None:
            if planet_sign_index not in sign_to_planets:
                sign_to_planets[planet_sign_index] = []
            sign_to_planets[planet_sign_index].append(planet_name)
    
    # Build sign_index -> house mapping (for aspected_house computation)
    sign_to_house = {}
    if houses_array:
        for house_data in houses_array:
            house_sign_index = house_data.get("sign_index")
            house_num = house_data.get("house")
            if house_sign_index is not None and house_num is not None:
                sign_to_house[house_sign_index] = house_data
    
    aspects_list = []
    
    # Helper function to compute aspected_house string
    def get_aspected_house_string(target_sign_index: int) -> str:
        """Compute aspected house string: '<SignName> – <HouseNumber> house'"""
        if houses_array and target_sign_index in sign_to_house:
            house_data = sign_to_house[target_sign_index]
            house_num = house_data.get("house")
            sign_name = house_data.get("sign_sanskrit") or house_data.get("sign")
            if sign_name and house_num:
                return f"{sign_name} – {house_num}{'st' if house_num == 1 else 'nd' if house_num == 2 else 'rd' if house_num == 3 else 'th'} house"
        elif get_sign_name_fn:
            # Fallback: use get_sign_name_fn if houses_array not available
            sign_name = get_sign_name_fn(target_sign_index)
            return f"{sign_name} – -"
        return "-"
    
    # Compute aspects for each planet
    for from_planet_name, planet_data in planets_dict.items():
        from_sign_index = planet_data.get("sign_index")
        if from_sign_index is None:
            continue
        
        # Get aspect offsets for this planet
        aspect_offsets = aspect_rules.get(from_planet_name, [6])  # Default to 7th if not found
        
        # Compute each aspect
        for aspect_offset in aspect_offsets:
            # Calculate target sign_index for this aspect
            target_sign_index = (from_sign_index + aspect_offset) % 12
            
            # Find planets in the target sign
            target_planets = sign_to_planets.get(target_sign_index, [])
            
            aspect_name = aspect_offset_to_name.get(aspect_offset, f"{aspect_offset}th")
            
            # Compute aspected house string (always computed, even for Nil)
            aspected_house_str = get_aspected_house_string(target_sign_index)
            
            # If target sign has planets, emit one row per planet
            if target_planets:
                for to_planet_name in target_planets:
                    # Don't aspect self
                    if to_planet_name == from_planet_name:
                        continue
                    
                    aspects_list.append({
                        "from": from_planet_name,
                        "aspect": aspect_name,
                        "to": to_planet_name,
                        "aspected_house": aspected_house_str
                    })
            else:
                # If target sign is empty, emit one row with "Nil"
                aspects_list.append({
                    "from": from_planet_name,
                    "aspect": aspect_name,
                    "to": "Nil",
                    "aspected_house": aspected_house_str
                })
    
    return aspects_list


@router.post("/kundli")
async def calculate_kundli_endpoint(request: KundliRequest, include_explanation: bool = Query(False)):
    """
    Calculate complete birth chart (Kundli D1).
    
    This endpoint calculates the main birth chart including:
    - Planet positions in signs and houses
    - House cusps
    - Ascendant
    - Nakshatras
    
    Args:
        request: Kundli calculation request with birth details
        include_explanation: Whether to include AI-generated explanation
    
    Returns:
        Complete kundli data
    """
    try:
        kundli_data = calculate_kundli(
            name=request.name,
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_latitude=request.birth_latitude,
            birth_longitude=request.birth_longitude,
            birth_place=request.birth_place,
            timezone=request.timezone
        )
        
        if include_explanation:
            kundli_data = add_explanation_to_response(kundli_data, "kundli")
        
        return kundli_data
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Error calculating kundli",
                "message": str(e),
                "type": type(e).__name__,
                "traceback": error_trace
            }
        )


@router.post("/kundli/planets")
async def get_planets(request: KundliRequest):
    """
    Get only planet positions from birth chart.
    
    Args:
        request: Kundli calculation request
    
    Returns:
        Planet positions data
    """
    try:
        kundli_data = calculate_kundli(
            name=request.name,
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_latitude=request.birth_latitude,
            birth_longitude=request.birth_longitude,
            birth_place=request.birth_place,
            timezone=request.timezone
        )
        
        return {
            "planets": kundli_data["planets"],
            "ascendant": kundli_data["ascendant"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating planets: {str(e)}")


@router.post("/kundli/houses")
async def get_houses(request: KundliRequest):
    """
    Get only house cusps from birth chart.
    
    Args:
        request: Kundli calculation request
    
    Returns:
        House cusps data
    """
    try:
        kundli_data = calculate_kundli(
            name=request.name,
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_latitude=request.birth_latitude,
            birth_longitude=request.birth_longitude,
            birth_place=request.birth_place,
            timezone=request.timezone
        )
        
        return {
            "houses": kundli_data["houses"],
            "ascendant": kundli_data["ascendant"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating houses: {str(e)}")


@router.post("/kundli/navamsa")
async def get_navamsa(request: KundliRequest):
    """
    Calculate Navamsa (D9) chart using authoritative varga engine.
    
    Navamsa is the 9th divisional chart, important for:
    - Marriage and spouse analysis
    - Spiritual matters
    - Final results of planets
    
    Args:
        request: Kundli calculation request
    
    Returns:
        Navamsa chart data
    """
    try:
        # Use authoritative varga engine - single source of truth
        from src.jyotish.varga_engine import build_varga_chart
        from src.jyotish.kundli_engine import generate_kundli
        from src.utils.timezone import local_to_utc
        from src.utils.converters import get_sign_name_sanskrit
        import swisseph as swe
        from datetime import datetime
        
        # Parse birth datetime
        hour, minute = map(int, request.birth_time.split(':'))
        birth_datetime = datetime.combine(request.birth_date, datetime.min.time().replace(hour=hour, minute=minute))
        birth_datetime_utc = local_to_utc(birth_datetime, request.timezone)
        
        jd = swe.julday(
            birth_datetime_utc.year, birth_datetime_utc.month, birth_datetime_utc.day,
            birth_datetime_utc.hour + birth_datetime_utc.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Generate D1 kundli
        base_kundli = generate_kundli(jd, request.birth_latitude, request.birth_longitude)
        
        # 🔒 CRITICAL: Use RAW unrounded sidereal longitudes for varga calculations
        # DO NOT use rounded degrees from D1 output - rounding causes varga mismatches
        from src.ephemeris.planets_jhora_exact import calculate_ascendant_jhora_exact, calculate_all_planets_jhora_exact
        
        # Get RAW ascendant longitude (unrounded, exact sidereal)
        asc_jhora_raw = calculate_ascendant_jhora_exact(jd, lat, lon)
        d1_ascendant = asc_jhora_raw["longitude"]  # Raw unrounded sidereal longitude
        
        # Get RAW planet longitudes (unrounded, exact sidereal)
        planets_jhora_raw = calculate_all_planets_jhora_exact(jd)
        d1_planets = {
            planet_name: planet_data["longitude"]  # Raw unrounded sidereal longitude
            for planet_name, planet_data in planets_jhora_raw.items()
        }
        
        # Build D9 chart using authoritative engine
        d9_chart = build_varga_chart(d1_planets, d1_ascendant, 9)
        
        # Build standardized response matching D1 structure
        # RUNTIME ASSERTION: Lagna house must be 1
        assert d9_chart["ascendant"]["house"] == 1, \
            f"D9 lagna house must be 1, got {d9_chart['ascendant']['house']}"
        
        # Build houses array (Whole Sign: relative to ascendant sign)
        # 🔒 DO NOT MODIFY — JHora compatible
        # Whole Sign: House 1 = Ascendant sign, House 2 = next sign clockwise, etc.
        # Formula: sign_index = (asc_sign_index + house_num - 1) % 12
        asc_sign_index = d9_chart["ascendant"]["sign_index"]
        houses_array = []
        for house_num in range(1, 13):
            sign_index = (asc_sign_index + house_num - 1) % 12
            houses_array.append({
                "house": house_num,
                "sign": get_sign_name(sign_index),
                "sign_sanskrit": get_sign_name_sanskrit(sign_index),
                "sign_index": sign_index,
                "degree": 0.0,
                "degrees_in_sign": 0.0,
                "lord": get_house_lord_from_sign(sign_index)
            })
        
        return {
            "Ascendant": {
                "degree": d9_chart["ascendant"]["degree"],
                "sign": d9_chart["ascendant"]["sign"],
                "sign_sanskrit": get_sign_name_sanskrit(d9_chart["ascendant"]["sign_index"]),
                "sign_index": d9_chart["ascendant"]["sign_index"],
                "degrees_in_sign": d9_chart["ascendant"]["degrees_in_sign"],
                "house": d9_chart["ascendant"]["house"],  # Always 1
                "lord": get_house_lord_from_sign(d9_chart["ascendant"]["sign_index"])
            },
            "Houses": houses_array,
            "Planets": d9_chart["planets"],
            "chartType": "D9"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating navamsa: {str(e)}")


@router.post("/kundli/dasamsa")
async def get_dasamsa(request: KundliRequest):
    """
    Calculate Dasamsa (D10) chart using authoritative varga engine.
    
    Dasamsa is the 10th divisional chart, important for:
    - Career and profession
    - Status and reputation
    - Karma and work
    
    Args:
        request: Kundli calculation request
    
    Returns:
        Dasamsa chart data
    """
    try:
        # Use authoritative varga engine - single source of truth
        from src.jyotish.varga_engine import build_varga_chart
        from src.jyotish.kundli_engine import generate_kundli
        from src.utils.timezone import local_to_utc
        from src.utils.converters import get_sign_name_sanskrit
        import swisseph as swe
        from datetime import datetime
        
        # Parse birth datetime
        hour, minute = map(int, request.birth_time.split(':'))
        birth_datetime = datetime.combine(request.birth_date, datetime.min.time().replace(hour=hour, minute=minute))
        birth_datetime_utc = local_to_utc(birth_datetime, request.timezone)
        
        jd = swe.julday(
            birth_datetime_utc.year, birth_datetime_utc.month, birth_datetime_utc.day,
            birth_datetime_utc.hour + birth_datetime_utc.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Generate D1 kundli
        base_kundli = generate_kundli(jd, request.birth_latitude, request.birth_longitude)
        
        # 🔒 CRITICAL: Use RAW unrounded sidereal longitudes for varga calculations
        # DO NOT use rounded degrees from D1 output - rounding causes varga mismatches
        from src.ephemeris.planets_jhora_exact import calculate_ascendant_jhora_exact, calculate_all_planets_jhora_exact
        
        # Get RAW ascendant longitude (unrounded, exact sidereal)
        asc_jhora_raw = calculate_ascendant_jhora_exact(jd, lat, lon)
        d1_ascendant = asc_jhora_raw["longitude"]  # Raw unrounded sidereal longitude
        
        # Get RAW planet longitudes (unrounded, exact sidereal)
        planets_jhora_raw = calculate_all_planets_jhora_exact(jd)
        d1_planets = {
            planet_name: planet_data["longitude"]  # Raw unrounded sidereal longitude
            for planet_name, planet_data in planets_jhora_raw.items()
        }
        
        # Build D10 chart using authoritative engine (with verified Prokerala/JHora logic)
        d10_chart = build_varga_chart(d1_planets, d1_ascendant, 10)
        
        # Build standardized response matching D1 structure
        # RUNTIME ASSERTION: Lagna house must be 1
        assert d10_chart["ascendant"]["house"] == 1, \
            f"D10 lagna house must be 1, got {d10_chart['ascendant']['house']}"
        
        # Build houses array (Whole Sign: relative to ascendant sign)
        # 🔒 DO NOT MODIFY — JHora compatible
        # Whole Sign: House 1 = Ascendant sign, House 2 = next sign clockwise, etc.
        # Formula: sign_index = (asc_sign_index + house_num - 1) % 12
        asc_sign_index = d10_chart["ascendant"]["sign_index"]
        houses_array = []
        for house_num in range(1, 13):
            sign_index = (asc_sign_index + house_num - 1) % 12
            houses_array.append({
                "house": house_num,
                "sign": get_sign_name(sign_index),
                "sign_sanskrit": get_sign_name_sanskrit(sign_index),
                "sign_index": sign_index,
                "degree": 0.0,
                "degrees_in_sign": 0.0,
                "lord": get_house_lord_from_sign(sign_index)
            })
        
        return {
            "Ascendant": {
                "degree": d10_chart["ascendant"]["degree"],
                "sign": d10_chart["ascendant"]["sign"],
                "sign_sanskrit": get_sign_name_sanskrit(d10_chart["ascendant"]["sign_index"]),
                "sign_index": d10_chart["ascendant"]["sign_index"],
                "degrees_in_sign": d10_chart["ascendant"]["degrees_in_sign"],
                "house": d10_chart["ascendant"]["house"],  # Always 1
                "lord": get_house_lord_from_sign(d10_chart["ascendant"]["sign_index"])
            },
            "Houses": houses_array,
            "Planets": d10_chart["planets"],
            "chartType": "D10"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating dasamsa: {str(e)}")


@router.get("/kundli")
async def kundli_get(
    user_id: Optional[str] = Query(None, description="User ID to lookup birth details from database"),
    dob: Optional[str] = Query(None, description="Date of birth in YYYY-MM-DD format (required if user_id not provided)"),
    time: Optional[str] = Query(None, description="Time of birth in HH:MM format (required if user_id not provided)"),
    lat: Optional[float] = Query(None, description="Latitude (required if user_id not provided)"),
    lon: Optional[float] = Query(None, description="Longitude (required if user_id not provided)"),
    timezone: str = Query("Asia/Kolkata", description="Timezone (default: Asia/Kolkata)"),
    # d24_chart_method parameter REMOVED - D24 is locked to Method 1 (JHora verified)
):
    # 🔥 STEP 5: PROVE WHICH BACKEND IS HIT (MANDATORY LOG)
    print("🔥 KUNDLI HIT — PID:", os.getpid(), flush=True)
    
    # 🔒 CRITICAL: Hard asserts at API entry point - ensures core helpers are callable
    # This forces immediate failure if scoping/shadowing rules are violated
    assert callable(_normalize_sign_index), "_normalize_sign_index is not callable"
    assert callable(get_nakshatra_lord), "get_nakshatra_lord is not callable (scoping violation)"
    
    """
    Calculate complete Kundli (D1) with all varga charts (D2-D60).
    
    Phase 2 Core Kundli Engine endpoint.
    Uses Swiss Ephemeris for all calculations with Lahiri ayanamsa.
    
    Supported varga charts:
    - D1: Rasi (Main birth chart)
    - D2: Hora, D3: Drekkana, D4: Chaturthamsa, D7: Saptamsa
    - D9: Navamsa, D10: Dasamsa, D12: Dwadasamsa
    - D16: Shodasamsa, D20: Vimsamsa, D24: Chaturvimsamsa
    - D27: Saptavimsamsa, D30: Trimsamsa, D40: Khavedamsa
    - D45: Akshavedamsa, D60: Shashtiamsa
    
    Args:
        user_id: Optional user ID to lookup birth details from database
        dob: Date of birth (YYYY-MM-DD) - required if user_id not provided
        time: Time of birth (HH:MM) - required if user_id not provided
        lat: Birth latitude - required if user_id not provided
        lon: Birth longitude - required if user_id not provided
        timezone: Timezone (default: Asia/Kolkata)
    
    Returns:
        Complete Kundli with D1 and all varga charts (D2-D60)
    """
    try:
        # 🔒 BACKEND FIX: Support user_id lookup from database (optional - falls back to query params if DB unavailable)
        # If user_id is provided, try to lookup birth details from database
        # If database is unavailable, fall back to using birth details from query parameters
        if user_id:
            # Try database lookup, but don't fail if DB is unavailable
            try:
                db = SessionLocal()
                # Convert user_id to int if it's a string
                user_id_int = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
                
                # Query birth details from database (this may fail if DB is not connected)
                try:
                    birth_detail = db.query(BirthDetail).filter(BirthDetail.user_id == user_id_int).first()
                    
                    if birth_detail:
                        # Extract birth details from database
                        dob = birth_detail.birth_date.strftime("%Y-%m-%d") if birth_detail.birth_date else dob
                        time = birth_detail.birth_time or time
                        lat = birth_detail.birth_latitude if birth_detail.birth_latitude is not None else lat
                        lon = birth_detail.birth_longitude if birth_detail.birth_longitude is not None else lon
                        timezone = birth_detail.timezone or timezone  # Use stored timezone or fallback to default
                    else:
                        # User not found in database - fall back to query parameters
                        print(f"⚠️  Warning: user_id {user_id} not found in database. Using birth details from query parameters.")
                except Exception as query_error:
                    # Query failed - fall back to query parameters
                    print(f"⚠️  Warning: Database query failed ({type(query_error).__name__}). Using birth details from query parameters.")
                finally:
                    try:
                        db.close()
                    except:
                        pass
            except Exception as db_error:
                # SessionLocal() creation or connection failed - fall back to query parameters
                print(f"⚠️  Warning: Database unavailable ({type(db_error).__name__}). Using birth details from query parameters.")
                # Continue with query parameters (dob, time, lat, lon from function params)
        
        # Validate that we have all required birth details (either from DB or query params)
        if not dob or not time or lat is None or lon is None:
            raise HTTPException(
                status_code=422,
                detail="Missing required birth details. Please provide: dob, time, lat, lon"
            )
        
        # Parse date and time
        from datetime import date
        birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
        
        # Parse time
        time_parts = time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        # Create local datetime
        birth_dt_local = datetime.combine(
            birth_date,
            datetime.min.time().replace(hour=hour, minute=minute, second=second)
        )
        
        # Convert to UTC (Swiss Ephemeris requires UTC)
        from src.utils.timezone import local_to_utc
        birth_dt_utc = local_to_utc(birth_dt_local, timezone)
        
        # Calculate Julian Day with proper UTC conversion
        # Note: calc_ut() requires UTC, so we convert local time to UTC first
        jd = swe.julday(
            birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
            birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0,
            swe.GREG_CAL
        )
        
        # Generate base D1 Kundli using EXACT JHORA engine
        base_kundli = generate_kundli(jd, lat, lon)
        
        # 🔒 D1 NAKSHATRA LORD ATTACHMENT (ASCENDANT)
        # Add nakshatra_lord to D1 Ascendant based on existing nakshatra_index
        if "Ascendant" in base_kundli and "nakshatra_index" in base_kundli["Ascendant"]:
            base_kundli["Ascendant"]["nakshatra_lord"] = get_nakshatra_lord(
                base_kundli["Ascendant"]["nakshatra_index"]
            )
        
        # 🔒 D1 NAKSHATRA LORD ATTACHMENT (PLANETS)
        # Add nakshatra_lord to each D1 planet based on existing nakshatra_index
        for planet_name, pdata in base_kundli.get("Planets", {}).items():
            if "nakshatra_index" in pdata:
                pdata["nakshatra_lord"] = get_nakshatra_lord(pdata["nakshatra_index"])
        
        # Calculate current dasha for dashboard
        current_dasha_info = None
        try:
            from src.jyotish.dasha_drik import calculate_vimshottari_dasha_drik
            from datetime import datetime as dt
            time_str = f"{hour:02d}:{minute:02d}" + (f":{second:02d}" if second > 0 else "")
            dasha_data = calculate_vimshottari_dasha_drik(
                birth_date, time_str, lat, lon, timezone, dt.now()
            )
            # Extract current dasha
            current_mahadasha = dasha_data.get("current_mahadasha", {})
            current_antardasha = dasha_data.get("current_antardasha", {})
            if current_mahadasha:
                mahadasha_lord = current_mahadasha.get("lord", "N/A")
                antardasha_lord = current_antardasha.get("lord", "N/A") if current_antardasha else None
                current_dasha_info = {
                    "mahadasha": mahadasha_lord,
                    "antardasha": antardasha_lord,
                    "mahadasha_start": current_mahadasha.get("start"),
                    "mahadasha_end": current_mahadasha.get("end"),
                    "display": f"{mahadasha_lord} Dasha" + (f" - {antardasha_lord} Antardasha" if antardasha_lord else "")
                }
        except Exception as e:
            # If dasha calculation fails, continue without it
            import traceback
            print(f"Warning: Could not calculate current dasha: {e}")
            traceback.print_exc()
        
        # ============================================================
        # AUTHORITATIVE VARGA COMPUTATION - SINGLE SOURCE OF TRUTH
        # ============================================================
        # API routes MUST use varga_engine.py - NEVER call calculate_varga() directly
        # This ensures consistency across all endpoints and eliminates mismatches
        # ============================================================
        
        from src.jyotish.varga_engine import build_varga_chart, get_varga_ascendant_only, compute_vargottama_flags
        from src.utils.converters import get_sign_name_sanskrit
        
        # 🔒 CRITICAL: Use RAW unrounded sidereal longitudes for varga calculations
        # DO NOT use rounded degrees from D1 output - rounding causes varga mismatches
        # Extract raw longitudes directly from ephemeris calculations
        from src.ephemeris.planets_jhora_exact import calculate_ascendant_jhora_exact, calculate_all_planets_jhora_exact
        
        # Get RAW ascendant longitude (unrounded, exact sidereal)
        asc_jhora_raw = calculate_ascendant_jhora_exact(jd, lat, lon)
        d1_ascendant = asc_jhora_raw["longitude"]  # Raw unrounded sidereal longitude
        
        # 🔍 STEP 1A: RAW D1 ASCENDANT (immediately after ephemeris)
        print("=" * 80)
        print("🔍 STEP 1A: RAW D1 ASCENDANT (kundli_routes.py - after calculate_ascendant_jhora_exact)")
        print("=" * 80)
        print(f"Ascendant longitude = {asc_jhora_raw['longitude']}")
        print(f"Ascendant sign_index = {asc_jhora_raw['sign_index']}")
        print(f"Ascendant degrees_in_sign = {asc_jhora_raw['degrees_in_sign']}")
        print(f"d1_ascendant (extracted) = {d1_ascendant}")
        # 🔒 INVARIANT CHECK: d1_ascendant must equal asc_jhora_raw["longitude"]
        assert abs(d1_ascendant - asc_jhora_raw["longitude"]) < 1e-10, f"d1_ascendant mismatch: {d1_ascendant} != {asc_jhora_raw['longitude']}"
        print("=" * 80)
        
        # Get RAW planet longitudes (unrounded, exact sidereal)
        planets_jhora_raw = calculate_all_planets_jhora_exact(jd)
        d1_planets = {
            planet_name: planet_data["longitude"]  # Raw unrounded sidereal longitude
            for planet_name, planet_data in planets_jhora_raw.items()
        }
        
        # 🔍 STEP 1B: RAW D1 MOON (for comparison)
        if "Moon" in planets_jhora_raw:
            moon_raw = planets_jhora_raw["Moon"]
            moon_d1_longitude = d1_planets["Moon"]
            print("=" * 80)
            print("🔍 STEP 1B: RAW D1 MOON (for comparison)")
            print("=" * 80)
            print(f"Moon longitude = {moon_raw['longitude']}")
            print(f"Moon sign_index = {moon_raw['sign_index']}")
            print(f"Moon degrees_in_sign = {moon_raw['degrees_in_sign']}")
            print(f"moon_d1_longitude (extracted) = {moon_d1_longitude}")
            # 🔒 INVARIANT CHECK: moon_d1_longitude must equal moon_raw["longitude"]
            assert abs(moon_d1_longitude - moon_raw["longitude"]) < 1e-10, f"moon_d1_longitude mismatch: {moon_d1_longitude} != {moon_raw['longitude']}"
            print("=" * 80)
        
        # 🔍 STEP 1C: VALUES PASSED INTO build_varga_chart()
        print("=" * 80)
        print("🔍 STEP 1C: VALUES PASSED INTO build_varga_chart() (kundli_routes.py)")
        print("=" * 80)
        print(f"d1_ascendant (BEFORE build_varga_chart) = {d1_ascendant}")
        if "Moon" in d1_planets:
            print(f"moon_d1_longitude (BEFORE build_varga_chart) = {d1_planets['Moon']}")
        # 🔒 INVARIANT CHECK: No rounding before varga calculation
        assert isinstance(d1_ascendant, float), f"d1_ascendant must be float, got {type(d1_ascendant)}"
        assert 0 <= d1_ascendant < 360, f"d1_ascendant out of range: {d1_ascendant}"
        print("=" * 80)
        
        # 🔒 MANDATORY VALIDATION: Ensure d1_planets is not empty before building varga charts
        if not d1_planets or len(d1_planets) == 0:
            raise ValueError(f"D1 planets dictionary is empty or None. Cannot build varga charts.")
        if d1_ascendant is None:
            raise ValueError(f"D1 ascendant is None. Cannot build varga charts.")
        
        # Build all varga charts using authoritative engine
        # This ensures sign and house are computed together atomically
        # All vargas D1-D60 are supported
        d2_chart = build_varga_chart(d1_planets, d1_ascendant, 2)
        d3_chart = build_varga_chart(d1_planets, d1_ascendant, 3)
        d4_chart = build_varga_chart(d1_planets, d1_ascendant, 4)
        
        # 🔒 MANDATORY D4 VALIDATION: Ensure D4 chart is complete before building response
        if not d4_chart:
            raise ValueError("D4 chart is None or empty")
        if "ascendant" not in d4_chart:
            raise ValueError("D4 chart is incomplete: missing 'ascendant' key")
        if not d4_chart.get("ascendant"):
            raise ValueError("D4 chart ascendant is None or empty")
        if d4_chart["ascendant"].get("sign_index") is None:
            raise ValueError(f"D4 chart ascendant is incomplete: sign_index is None. Ascendant data: {d4_chart.get('ascendant')}")
        if "planets" not in d4_chart:
            raise ValueError("D4 chart is incomplete: missing 'planets' key")
        if not d4_chart["planets"] or len(d4_chart["planets"]) == 0:
            raise ValueError(f"D4 chart is incomplete: planets dictionary is empty. d1_planets had {len(d1_planets)} planets: {list(d1_planets.keys())}")
        
        d7_chart = build_varga_chart(d1_planets, d1_ascendant, 7)
        d9_chart = build_varga_chart(d1_planets, d1_ascendant, 9)
        d10_chart = build_varga_chart(d1_planets, d1_ascendant, 10)
        # Vargottama (D1 sign == D9 sign): attach to D1 planets only; backend single source of truth
        vargottama_flags = compute_vargottama_flags(base_kundli["Planets"], d9_chart["planets"])
        for planet_name, pdata in base_kundli.get("Planets", {}).items():
            pdata["is_vargottama"] = vargottama_flags.get(planet_name, False)
        
        # D12 (Dwadasamsa) - Special handling for ascendant (base formula, no +3 correction)
        # But planets still use standard varga formula
        d12_chart = build_varga_chart(d1_planets, d1_ascendant, 12)
        
        # Additional varga charts (D16-D60)
        d16_chart = build_varga_chart(d1_planets, d1_ascendant, 16)
        d20_chart = build_varga_chart(d1_planets, d1_ascendant, 20)
        # D24 is LOCKED to Method 1 (JHora verified) - no method parameter
        d24_chart = build_varga_chart(d1_planets, d1_ascendant, 24)
        d27_chart = build_varga_chart(d1_planets, d1_ascendant, 27)
        d30_chart = build_varga_chart(d1_planets, d1_ascendant, 30)
        d40_chart = build_varga_chart(d1_planets, d1_ascendant, 40)
        d45_chart = build_varga_chart(d1_planets, d1_ascendant, 45)
        d60_chart = build_varga_chart(d1_planets, d1_ascendant, 60)
        
        # D12 ascendant uses BASE formula (no +3 correction) - recalculate
        d1_asc_sign = int(d1_ascendant / 30)
        d1_asc_deg_in_sign = d1_ascendant % 30
        part = 2.5
        div_index = int(math.floor(d1_asc_deg_in_sign / part))
        if div_index >= 12:
            div_index = 11
        d12_asc_sign = (d1_asc_sign + div_index) % 12
        d12_asc_deg_in_sign = (d1_asc_deg_in_sign * 12) % 30
        d12_asc_longitude = d12_asc_sign * 30 + d12_asc_deg_in_sign
        from src.utils.converters import normalize_degrees, get_sign_name
        d12_asc_longitude = normalize_degrees(d12_asc_longitude)
        
        # Update D12 ascendant with base formula result
        # CRITICAL: Lagna is ALWAYS in House 1 (Whole Sign system rule)
        # DO NOT MODIFY — JHora compatible
        d12_chart["ascendant"] = {
            "degree": round(d12_asc_longitude, 4),
            "sign": get_sign_name(d12_asc_sign),
            "sign_index": d12_asc_sign,
            "degrees_in_sign": round(d12_asc_deg_in_sign, 4),
            "house": 1  # Always 1 for lagna (not sign_index + 1)
        }
        
        # ============================================================
        # STANDARDIZED API RESPONSE STRUCTURE
        # ============================================================
        # D1 and ALL varga charts must return identical structure:
        # {
        #   ascendant: { sign, sign_index, degree, house, sign_sanskrit }
        #   houses: [{ house: 1..12, sign, sign_index, degree, ... }]
        #   planets: { planet: { sign, sign_index, house, degree, ... } }
        # }
        # DO NOT MODIFY — JHora compatible
        # ============================================================
        
        # ⚠️ D1 GRAHA DRISHTI (PLANETARY ASPECTS) — PARĀŚARI RULES ONLY
        # ⚠️ Compute aspects for D1 using D1's sign_index positions
        # ⚠️ D1 aspects are computed independently (not reused for other vargas)
        from src.utils.converters import get_sign_name
        d1_houses = base_kundli.get("Houses")  # D1 houses from generate_kundli
        d1_aspects = compute_graha_drishti(
            base_kundli.get("Planets", {}),
            houses_array=d1_houses,
            get_sign_name_fn=get_sign_name
        )
        base_kundli["Aspects"] = d1_aspects
        
        # Helper function to build standardized varga chart response
        # 🔒 CRITICAL: Explicitly capture get_nakshatra_lord in closure to prevent scoping errors
        # This ensures the nested function can access the module-level import
        _get_nakshatra_lord_fn = get_nakshatra_lord  # Explicit closure binding
        
        def build_standardized_varga_response(varga_chart: Dict, chart_type: str) -> Dict:
            """Build standardized varga chart response matching D1 structure."""
            # Import required functions
            from src.utils.converters import get_sign_name, get_sign_name_sanskrit, get_nakshatra_name, normalize_degrees
            from src.jyotish.kundli_engine import get_house_lord_from_sign
            
            # Extract varga number from chart_type (e.g., "D24" -> 24)
            varga_num = int(chart_type[1:]) if chart_type[1:].isdigit() else 0
            
            # For D24-D60: NO HOUSE LOGIC (pure sign charts)
            # For D1-D20: Build houses array using Whole Sign system
            if varga_num in (24, 27, 30, 40, 45, 60):
                # Pure sign chart - no houses
                houses_array = None
                ascendant_house = None
            else:
                # RUNTIME ASSERTION: Lagna house must be 1 for D1-D20
                assert varga_chart["ascendant"]["house"] == 1, \
                    f"{chart_type} lagna house must be 1, got {varga_chart['ascendant']['house']}"
                
                # Build houses array for varga using Whole Sign system
                # 🔒 DO NOT MODIFY — JHora compatible
                # Whole Sign: House 1 = Varga ascendant sign, House 2 = next sign clockwise, etc.
                # 🔒 MANDATORY: Normalize asc_sign_index to 0-11 range (data integrity fix)
                # This ensures house sign_index is NEVER negative or >= 12
                # Note: sign_index should already be normalized from varga_engine, but we normalize again for safety
                # 🔒 CRITICAL: _normalize_sign_index is imported from varga_engine.py (canonical source)
                # DO NOT redefine it here - use the imported function
                
                # 🔒 MANDATORY: Use ONLY normalized sign_index from build_varga_chart()
                # DO NOT recompute or override - use the engine output directly
                asc_sign_index_raw = varga_chart["ascendant"]["sign_index"]
                asc_sign_index = _normalize_sign_index(asc_sign_index_raw)
                
                # 🔒 CRITICAL ASSERTION: House 1 sign_index MUST equal Ascendant sign_index
                # This proves houses are Lagna-relative (not absolute zodiac)
                # This assertion runs BEFORE response leaves backend
                expected_house1_sign = asc_sign_index
                
                houses_array = []
                for house_num in range(1, 13):
                    # Calculate sign for this house: (asc_sign + house_num - 1) % 12
                    # House 1 = ascendant sign, House 2 = next sign, etc.
                    sign_index = (asc_sign_index + house_num - 1) % 12
                    
                    # 🔒 HARD ASSERTION: House sign_index MUST be 0-11 (API response layer)
                    # This is the FINAL validation before response leaves backend
                    if sign_index < 0 or sign_index >= 12:
                        raise ValueError(
                            f"FATAL API DATA INTEGRITY ERROR: {chart_type} House {house_num} sign_index={sign_index} "
                            f"is OUT OF RANGE [0, 11]. asc_sign_index={asc_sign_index}, house_num={house_num}. "
                            f"This indicates a data integrity violation in the API response layer."
                        )
                    
                    houses_array.append({
                        "house": house_num,
                        "sign": get_sign_name(sign_index),
                        "sign_sanskrit": get_sign_name_sanskrit(sign_index),
                        "sign_index": sign_index,
                        "degree": 0.0,  # Varga houses don't have cusps
                        "degrees_in_sign": 0.0,
                        "lord": get_house_lord_from_sign(sign_index)
                    })
                
                # 🔒 CRITICAL ASSERTION: House 1 sign_index MUST equal Ascendant sign_index
                # This proves houses are constructed correctly from normalized ascendant
                house1_sign = houses_array[0]["sign_index"]
                if house1_sign != expected_house1_sign:
                    raise ValueError(
                        f"FATAL API DATA INTEGRITY ERROR: {chart_type} House-1 sign_index={house1_sign} "
                        f"does NOT equal Ascendant sign_index={expected_house1_sign}. "
                        f"This indicates houses are NOT Lagna-relative or normalization failed."
                    )
                
                # RUNTIME ASSERTION: Must have exactly 12 houses
                assert len(houses_array) == 12, f"{chart_type} must have exactly 12 houses"
                ascendant_house = varga_chart["ascendant"]["house"]  # Always 1 for D1-D20
            
            # Build Ascendant response
            # 🔒 MANDATORY: Use normalized sign_index (same as used for houses)
            # DO NOT use raw varga_chart["ascendant"]["sign_index"] - it may be unnormalized
            # For D1-D20: Use the same normalized asc_sign_index used for houses
            # For D24-D60: Normalize separately (no houses, but still need normalized sign_index)
            if varga_num not in (24, 27, 30, 40, 45, 60):
                asc_sign_index_normalized = asc_sign_index  # Use the same normalized value from houses
            else:
                asc_sign_index_normalized = _normalize_sign_index(varga_chart["ascendant"]["sign_index"])
            
            # ⚠️ NAKSHATRA PER VARGA RULE:
            # ⚠️ Nakshatra MUST be computed from the VARGA longitude (absolute) for each chart.
            # ⚠️ NEVER reuse D1 nakshatra for D2–D60. Each varga has its own longitude and nakshatra.
            
            # Compute absolute varga longitude for Ascendant
            asc_deg_in_sign = varga_chart["ascendant"]["degrees_in_sign"]
            asc_longitude = normalize_degrees(asc_sign_index_normalized * 30.0 + asc_deg_in_sign)
            
            # Compute nakshatra index and pada from VARGA longitude
            nakshatra_span = 13 + 20.0 / 60.0  # 13°20' per nakshatra
            pada_size = nakshatra_span / 4.0   # 4 padas per nakshatra
            
            asc_nak_index = int(asc_longitude // nakshatra_span)
            if asc_nak_index >= 27:
                asc_nak_index = 26
            if asc_nak_index < 0:
                asc_nak_index = 0
            
            asc_degrees_in_nakshatra = asc_longitude % nakshatra_span
            asc_pada = int(asc_degrees_in_nakshatra // pada_size) + 1
            if asc_pada > 4:
                asc_pada = 4
            if asc_pada < 1:
                asc_pada = 1
            
            asc_nak_name = get_nakshatra_name(asc_nak_index)
            asc_nak_lord = _get_nakshatra_lord_fn(asc_nak_index)
            
            ascendant_response = {
                "degree": varga_chart["ascendant"]["degree"],
                "sign": varga_chart["ascendant"]["sign"],
                "sign_sanskrit": get_sign_name_sanskrit(asc_sign_index_normalized),
                "sign_index": asc_sign_index_normalized,  # Use normalized sign_index
                "degrees_in_sign": asc_deg_in_sign,
                "lord": get_house_lord_from_sign(asc_sign_index_normalized),
                # Nakshatra data computed from VARGA longitude (per-chart)
                "nakshatra": asc_nak_name,
                "nakshatra_index": asc_nak_index,
                "pada": asc_pada,
                "nakshatra_lord": asc_nak_lord,
            }
            
            # Only add house field for D1-D20
            if ascendant_house is not None:
                ascendant_response["house"] = ascendant_house
            
            # 🔒 NORMALIZE PLANET KEYS: Ensure all planets use snake_case keys (sign_index, degrees_in_sign)
            # This ensures frontend receives consistent key naming
            normalized_planets = {}
            for planet_name, planet_data in varga_chart["planets"].items():
                # Compute VARGA-based nakshatra for each planet (no D1 reuse)
                planet_sign_index = planet_data.get("sign_index")
                planet_deg_in_sign = planet_data.get("degrees_in_sign")
                
                if planet_sign_index is not None and planet_deg_in_sign is not None:
                    planet_longitude = normalize_degrees(planet_sign_index * 30.0 + planet_deg_in_sign)
                    
                    planet_nak_index = int(planet_longitude // nakshatra_span)
                    if planet_nak_index >= 27:
                        planet_nak_index = 26
                    if planet_nak_index < 0:
                        planet_nak_index = 0
                    
                    planet_degrees_in_nakshatra = planet_longitude % nakshatra_span
                    planet_pada = int(planet_degrees_in_nakshatra // pada_size) + 1
                    if planet_pada > 4:
                        planet_pada = 4
                    if planet_pada < 1:
                        planet_pada = 1
                    
                    planet_nak_name = get_nakshatra_name(planet_nak_index)
                    planet_nak_lord = _get_nakshatra_lord_fn(planet_nak_index)
                else:
                    # Fallback: should not normally happen, but keep structure intact
                    planet_nak_index = 0
                    planet_pada = 1
                    planet_nak_name = ""
                    planet_nak_lord = _get_nakshatra_lord_fn(planet_nak_index)
                
                normalized_planet = {
                    "degree": planet_data.get("degree"),
                    "sign": planet_data.get("sign"),
                    "sign_name": planet_data.get("sign_name") or planet_data.get("sign"),  # Fallback to sign if sign_name missing
                    "sign_index": planet_sign_index,  # Ensure snake_case
                    "degrees_in_sign": planet_deg_in_sign,  # Ensure snake_case
                    # Nakshatra data computed from VARGA longitude (per-chart)
                    "nakshatra": planet_nak_name,
                    "nakshatra_index": planet_nak_index,
                    "pada": planet_pada,
                    "nakshatra_lord": planet_nak_lord,
                }
                # Add optional fields if present
                if "house" in planet_data:
                    normalized_planet["house"] = planet_data["house"]
                if "degree_dms" in planet_data:
                    normalized_planet["degree_dms"] = planet_data["degree_dms"]
                if "arcminutes" in planet_data:
                    normalized_planet["arcminutes"] = planet_data["arcminutes"]
                if "arcseconds" in planet_data:
                    normalized_planet["arcseconds"] = planet_data["arcseconds"]
                if "degree_formatted" in planet_data:
                    normalized_planet["degree_formatted"] = planet_data["degree_formatted"]
                normalized_planets[planet_name] = normalized_planet
            
            # ⚠️ GRAHA DRISHTI (PLANETARY ASPECTS) — PARĀŚARI RULES ONLY
            # ⚠️ Compute aspects independently for EACH varga chart using THAT varga's sign_index positions
            # ⚠️ Each varga is treated as a standalone chart with its own aspect relationships
            # ⚠️ NO reuse of D1 aspects for D2–D60
            aspects_list = compute_graha_drishti(
                normalized_planets,
                houses_array=houses_array,
                get_sign_name_fn=get_sign_name
            )
            
            # 🔒 FINAL API RESPONSE VALIDATION: Assert ALL sign_index values are 0-11
            # This is the LAST check before response leaves backend
            response_data = {
                "Ascendant": ascendant_response,
                "Houses": houses_array,  # None for D24-D60
                "Planets": normalized_planets,  # Use normalized planets with snake_case keys
                "Aspects": aspects_list,  # Graha Drishti computed per varga
                "chartType": chart_type
            }
            
            # Validate Ascendant sign_index
            if response_data["Ascendant"]["sign_index"] < 0 or response_data["Ascendant"]["sign_index"] >= 12:
                raise ValueError(
                    f"FATAL API DATA INTEGRITY ERROR: {chart_type} Ascendant sign_index={response_data['Ascendant']['sign_index']} "
                    f"is OUT OF RANGE [0, 11]. This indicates normalization failed."
                )
            
            # Validate ALL house sign_index values (if houses exist)
            if houses_array is not None:
                for house in houses_array:
                    if house["sign_index"] < 0 or house["sign_index"] >= 12:
                        raise ValueError(
                            f"FATAL API DATA INTEGRITY ERROR: {chart_type} House {house['house']} sign_index={house['sign_index']} "
                            f"is OUT OF RANGE [0, 11]. This indicates a data integrity violation."
                        )
            
            # Validate ALL planet sign_index values
            for planet_name, planet_data in response_data["Planets"].items():
                if planet_data.get("sign_index") is None:
                    raise ValueError(
                        f"FATAL API DATA INTEGRITY ERROR: {chart_type} {planet_name} missing sign_index. "
                        f"Planet data: {planet_data}"
                    )
                if planet_data["sign_index"] < 0 or planet_data["sign_index"] >= 12:
                    raise ValueError(
                        f"FATAL API DATA INTEGRITY ERROR: {chart_type} {planet_name} sign_index={planet_data['sign_index']} "
                        f"is OUT OF RANGE [0, 11]. This indicates normalization failed."
                    )
                if planet_data.get("degrees_in_sign") is None:
                    raise ValueError(
                        f"FATAL API DATA INTEGRITY ERROR: {chart_type} {planet_name} missing degrees_in_sign. "
                        f"Planet data: {planet_data}"
                    )
            
            return response_data
        
        # Build standardized response with consistent structure
        # Include ALL varga charts (D1-D60)
        
        # 🔒 D4: Build response and log separately to avoid lambda issues
        d4_response = build_standardized_varga_response(d4_chart, "D4")
        print("=" * 80)
        print("🔍 MANDATORY D4 PAYLOAD LOG (API BOUNDARY)")
        print("=" * 80)
        print(f"D4 Response Keys: {list(d4_response.keys()) if isinstance(d4_response, dict) else 'NOT A DICT'}")
        print(f"D4 Response Type: {type(d4_response)}")
        print(f"D4 Ascendant: {d4_response.get('Ascendant', {}) if isinstance(d4_response, dict) else 'N/A'}")
        print(f"D4 Ascendant sign_index: {d4_response.get('Ascendant', {}).get('sign_index') if isinstance(d4_response, dict) else 'N/A'}")
        print(f"D4 Houses Count: {len(d4_response.get('Houses', [])) if isinstance(d4_response, dict) else 'N/A'}")
        if isinstance(d4_response, dict) and d4_response.get('Houses'):
            for h in d4_response.get('Houses', []):
                print(f"D4 House {h.get('house')}: sign_index={h.get('sign_index')}, sign={h.get('sign')}")
        print("=" * 80)
        
        # 🔒 PLANET FUNCTIONAL STRENGTH (D1-ONLY, BACKEND-ONLY)
        # Compute ancient Jyotish functional strength flags from the FINAL D1 chart.
        # - Backend-only extension
        # - D1-only input (base_kundli)
        # - NO recomputation of planets
        # - NO prediction logic
        try:
            planet_strength = calculate_planet_functional_strength(base_kundli)
            planet_strength_raw = planet_strength.get("planet_functional_strength", {})
            
            # 🔒 PLANET KEY NORMALIZATION: Ensure canonical keys (Sun, Moon, Mars, etc.)
            # Frontend expects EXACT keys: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
            # This normalization ensures API response shape matches frontend expectations
            CANONICAL_PLANET_KEYS = {
                "Sun": "Sun",
                "Moon": "Moon",
                "Mars": "Mars",
                "Mercury": "Mercury",
                "Jupiter": "Jupiter",
                "Venus": "Venus",
                "Saturn": "Saturn",
                "Rahu": "Rahu",
                "Ketu": "Ketu",
                # Common aliases (if any exist in input)
                "Su": "Sun",
                "Mo": "Moon",
                "Ma": "Mars",
                "Me": "Mercury",
                "Ju": "Jupiter",
                "Ve": "Venus",
                "Sa": "Saturn",
                "Ra": "Rahu",
                "Ke": "Ketu",
            }
            
            # Expected canonical keys (frontend contract)
            EXPECTED_KEYS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
            
            planet_strength_payload = {}
            for raw_key, strength_data in planet_strength_raw.items():
                # Normalize key to canonical format
                canonical_key = CANONICAL_PLANET_KEYS.get(raw_key, raw_key)
                # Only include if it's a canonical key (frontend expects these exact keys)
                if canonical_key in EXPECTED_KEYS:
                    planet_strength_payload[canonical_key] = strength_data
                else:
                    # If key doesn't match any known format, log warning
                    logging.getLogger(__name__).warning(
                        f"Unknown planet key in functional strength: {raw_key} (normalized to: {canonical_key}). Skipping."
                    )
            
        except Exception as e:
            # Fail-safe: Never break main kundli response if strength engine fails
            logging.getLogger(__name__).error(
                "Planet functional strength calculation failed: %s", e
            )
            planet_strength_payload = {}
        
        response = {
            "julian_day": round(jd, 6),
            "D1": base_kundli,
            "D2": build_standardized_varga_response(d2_chart, "D2"),
            "D3": build_standardized_varga_response(d3_chart, "D3"),
            "D4": d4_response,
            "D7": build_standardized_varga_response(d7_chart, "D7"),
            "D9": build_standardized_varga_response(d9_chart, "D9"),
            "D10": build_standardized_varga_response(d10_chart, "D10"),
            "D12": build_standardized_varga_response(d12_chart, "D12"),
            # Additional varga charts (D16-D60)
            "D16": build_standardized_varga_response(d16_chart, "D16"),
            "D20": build_standardized_varga_response(d20_chart, "D20"),
            "D24": build_standardized_varga_response(d24_chart, "D24"),
            "D27": build_standardized_varga_response(d27_chart, "D27"),
            "D30": build_standardized_varga_response(d30_chart, "D30"),
            "D40": build_standardized_varga_response(d40_chart, "D40"),
            "D45": build_standardized_varga_response(d45_chart, "D45"),
            "D60": build_standardized_varga_response(d60_chart, "D60"),
            # Planet Functional Strength (ancient Jyotish engine; D1-only input)
            # This is a BACKEND-ONLY, additive payload. Frontend may ignore safely.
            "planet_functional_strength": planet_strength_payload,
        }
        
        # CRITICAL: Log final payload for D10 verification (Prokerala match)
        logger = logging.getLogger(__name__)
        if "D10" in response:
            d10_data = response["D10"]
            logger.info(f"📊 D10 FINAL PAYLOAD (Authoritative Engine):")
            logger.info(f"   Ascendant: {d10_data.get('Ascendant', {}).get('sign_sanskrit')} (sign_index={d10_data.get('Ascendant', {}).get('sign_index')}) → House {d10_data.get('Ascendant', {}).get('house')}")
            for planet_name in ["Venus", "Mars"]:
                if planet_name in d10_data.get("Planets", {}):
                    planet_data = d10_data["Planets"][planet_name]
                    logger.info(f"   {planet_name}: {planet_data.get('sign')} (sign_index={planet_data.get('sign_index')}) → House {planet_data.get('house')}")
        
        # Log all varga charts included in response
        varga_keys = [key for key in response.keys() if key.startswith("D") and key != "D1"]
        logger.info(f"✅ VARGA CHARTS INCLUDED IN RESPONSE: {sorted(varga_keys, key=lambda x: int(x[1:]) if x[1:].isdigit() else 999)}")
        logger.info(f"   Total varga charts: {len(varga_keys)}")
        
        # Verify D16-D60 are present
        required_vargas = ["D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
        missing_vargas = [v for v in required_vargas if v not in response]
        if missing_vargas:
            logger.warning(f"⚠️  MISSING VARGA CHARTS: {missing_vargas}")
        else:
            logger.info(f"✅ All extended varga charts (D16-D60) are included in response")
        
        # Add current dasha information if available
        if current_dasha_info:
            response["current_dasha"] = current_dasha_info
        
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Invalid date/time format",
                "message": str(e),
                "type": "ValidationError"
            }
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Error calculating kundli",
                "message": str(e),
                "type": type(e).__name__,
                "traceback": error_trace
            }
        )


@router.get("/kundli/transits")
async def kundli_transits(
    user_id: Optional[str] = Query(None, description="User ID to lookup birth details from database"),
    transit_datetime: Optional[str] = Query(None, alias="datetime", description="Transit datetime in ISO format (YYYY-MM-DDTHH:MM:SS). If not provided, uses current time."),
    lat: Optional[float] = Query(None, description="Transit latitude (optional, defaults to birth location)"),
    lon: Optional[float] = Query(None, description="Transit longitude (optional, defaults to birth location)"),
    timezone: str = Query("Asia/Kolkata", description="Timezone (default: Asia/Kolkata)"),
):
    """
    Calculate Transit (Gochar) Chart for specified datetime and location.
    
    This endpoint calculates planetary positions using:
    - Specified datetime (or current time if not provided)
    - Specified location (or birth location if not provided)
    - Same ephemeris + ayanamsa as natal charts (Drik Siddhanta + Lahiri)
    
    Returns transit chart in SAME format as D1, allowing frontend reuse.
    
    Args:
        user_id: Optional user ID to lookup birth details from database
        datetime: Optional transit datetime in ISO format (YYYY-MM-DDTHH:MM:SS). Defaults to current time.
        lat: Optional transit latitude. Defaults to birth location if user_id provided.
        lon: Optional transit longitude. Defaults to birth location if user_id provided.
        timezone: Timezone (default: Asia/Kolkata)
    
    Returns:
        Transit chart with structure matching D1:
        {
            "chartType": "TRANSIT",
            "chartLabel": "Current Transits",
            "Ascendant": { ... },
            "Planets": { ... },
            "Houses": [ ... ],
            "Aspects": [ ... ]
        }
    """
    try:
        # 🔒 BACKEND FIX: Support user_id lookup from database (optional - falls back to query params if DB unavailable)
        if user_id:
            try:
                db = SessionLocal()
                user_id_int = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
                try:
                    birth_detail = db.query(BirthDetail).filter(BirthDetail.user_id == user_id_int).first()
                    if birth_detail:
                        lat = birth_detail.birth_latitude if birth_detail.birth_latitude is not None else lat
                        lon = birth_detail.birth_longitude if birth_detail.birth_longitude is not None else lon
                        timezone = birth_detail.timezone or timezone
                    else:
                        print(f"⚠️  Warning: user_id {user_id} not found in database. Using query parameters.")
                except Exception as query_error:
                    print(f"⚠️  Warning: Database query failed ({type(query_error).__name__}). Using query parameters.")
                finally:
                    try:
                        db.close()
                    except:
                        pass
            except Exception as db_error:
                print(f"⚠️  Warning: Database unavailable ({type(db_error).__name__}). Using query parameters.")
        
        # Store birth location for fallback (from DB lookup or query params)
        birth_lat = lat
        birth_lon = lon
        
        # Validate that we have location (either from DB or query params)
        if lat is None or lon is None:
            raise HTTPException(
                status_code=422,
                detail="Missing required location. Please provide: lat, lon or user_id"
            )
        
        # Use provided transit location (from query params) or fall back to birth location
        # Note: lat/lon query params override birth location if provided
        transit_lat = lat  # Use query param lat if provided, otherwise birth_lat from above
        transit_lon = lon  # Use query param lon if provided, otherwise birth_lon from above
        
        # Parse transit datetime (if provided) or use current time
        from datetime import datetime, timezone as tz
        from src.utils.timezone import local_to_utc
        
        if transit_datetime:
            try:
                # Parse ISO format datetime string
                # Support formats: YYYY-MM-DDTHH:MM:SS, YYYY-MM-DDTHH:MM:SSZ, YYYY-MM-DDTHH:MM:SS+HH:MM
                if transit_datetime.endswith('Z'):
                    transit_dt_utc = datetime.fromisoformat(transit_datetime.replace('Z', '+00:00'))
                elif '+' in transit_datetime or transit_datetime.count('-') > 2:
                    # Has timezone offset
                    transit_dt_utc = datetime.fromisoformat(transit_datetime)
                else:
                    # No timezone, assume local timezone and convert to UTC
                    # Parse as naive datetime first
                    naive_dt = datetime.strptime(transit_datetime, "%Y-%m-%dT%H:%M:%S")
                    # Convert to UTC using provided timezone
                    from src.utils.timezone import get_timezone, local_to_utc
                    local_tz = get_timezone(timezone)
                    local_dt = local_tz.localize(naive_dt)
                    transit_dt_utc = local_dt.astimezone(tz.utc)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid datetime format. Expected ISO format (YYYY-MM-DDTHH:MM:SS), got: {transit_datetime}. Error: {str(e)}"
                )
        else:
            # Default to current UTC time
            transit_dt_utc = datetime.now(tz.utc)
        
        # Calculate Julian Day for transit datetime
        jd = swe.julday(
            transit_dt_utc.year, transit_dt_utc.month, transit_dt_utc.day,
            transit_dt_utc.hour + transit_dt_utc.minute / 60.0 + transit_dt_utc.second / 3600.0,
            swe.GREG_CAL
        )
        
        # Generate transit chart using EXACT JHORA engine (same as D1)
        # Use transit location (provided or birth location fallback)
        transit_kundli = generate_kundli(jd, transit_lat, transit_lon)
        
        # 🔒 TRANSIT NAKSHATRA LORD ATTACHMENT (ASCENDANT)
        if "Ascendant" in transit_kundli and "nakshatra_index" in transit_kundli["Ascendant"]:
            transit_kundli["Ascendant"]["nakshatra_lord"] = get_nakshatra_lord(
                transit_kundli["Ascendant"]["nakshatra_index"]
            )
        
        # 🔒 TRANSIT NAKSHATRA LORD ATTACHMENT (PLANETS)
        for planet_name, pdata in transit_kundli.get("Planets", {}).items():
            if "nakshatra_index" in pdata:
                pdata["nakshatra_lord"] = get_nakshatra_lord(pdata["nakshatra_index"])
        
        # ⚠️ TRANSIT GRAHA DRISHTI (PLANETARY ASPECTS) — PARĀŚARI RULES ONLY
        # ⚠️ Compute aspects for transit chart using transit's sign_index positions
        from src.utils.converters import get_sign_name
        transit_houses = transit_kundli.get("Houses")
        transit_aspects = compute_graha_drishti(
            transit_kundli.get("Planets", {}),
            houses_array=transit_houses,
            get_sign_name_fn=get_sign_name
        )
        transit_kundli["Aspects"] = transit_aspects
        
        # Format response to match D1 structure (for frontend reuse)
        response = {
            "chartType": "TRANSIT",
            "chartLabel": "Current Transits",
            "Ascendant": transit_kundli.get("Ascendant", {}),
            "Planets": transit_kundli.get("Planets", {}),
            "Houses": transit_kundli.get("Houses", []),
            "Aspects": transit_aspects,
        }
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid input",
                "message": str(e),
                "type": "ValidationError"
            }
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error calculating transit chart",
                "message": str(e),
                "type": type(e).__name__,
                "traceback": error_trace
            }
        )


@router.post("/kundli/yogas")
async def get_yogas(request: KundliRequest, include_explanation: bool = Query(False)):
    """
    Calculate all yogas (planetary combinations) in birth chart.
    
    Args:
        request: Kundli calculation request
        include_explanation: Whether to include AI-generated explanation
    
    Returns:
        Yogas data
    """
    try:
        # Use new yoga detection system
        from src.jyotish.kundli_engine import get_planet_positions
        from src.ephemeris.ephemeris_utils import get_ascendant, get_houses, get_ayanamsa
        from src.utils.converters import degrees_to_sign, normalize_degrees
        
        # Parse birth datetime
        birth_dt = datetime.combine(request.birth_date, request.birth_time)
        jd = swe.julday(
            birth_dt.year, birth_dt.month, birth_dt.day,
            birth_dt.hour + birth_dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Prepare planets and houses for yoga detection
        planets_sidereal = get_planet_positions(jd)
        asc = get_ascendant(jd, request.birth_latitude, request.birth_longitude)
        ayanamsa = get_ayanamsa(jd)
        asc_sidereal = normalize_degrees(asc - ayanamsa)
        houses_list = get_houses(jd, request.birth_latitude, request.birth_longitude)
        houses_sidereal = [normalize_degrees(h - ayanamsa) for h in houses_list]
        
        # Prepare planets with house information
        # 🔒 DO NOT MODIFY — JHora compatible
        # Whole Sign House System: house = ((planet_sign_index - ascendant_sign_index + 12) % 12) + 1
        planets = {}
        asc_sign_index = int(asc_sidereal / 30.0)
        for planet_name, planet_degree in planets_sidereal.items():
            if planet_name in ["Rahu", "Ketu"]:
                continue
            sign_num, _ = degrees_to_sign(planet_degree)
            # Get sign indices (0-11) for house calculation
            planet_sign_index = int(planet_degree / 30.0)
            # Whole Sign house calculation using ONLY sign indices
            house_num = ((planet_sign_index - asc_sign_index + 12) % 12) + 1
            # RUNTIME ASSERTION: House must be 1-12
            assert 1 <= house_num <= 12, f"House must be 1-12, got {house_num} (planet_sign={planet_sign_index}, asc_sign={asc_sign_index})"
            planets[planet_name] = {
                "degree": planet_degree,
                "sign": sign_num,
                "house": house_num
            }
        
        # Prepare houses
        houses = []
        asc_sign, _ = degrees_to_sign(asc_sidereal)
        houses.append({"house": 1, "degree": asc_sidereal, "sign": asc_sign})
        for i, house_degree in enumerate(houses_sidereal):
            sign_num, _ = degrees_to_sign(house_degree)
            houses.append({"house": i + 2, "degree": house_degree, "sign": sign_num})
        
        # Detect yogas using new system
        yogas_data = detect_all_yogas(planets, houses)
        
        if include_explanation:
            yogas_data = add_explanation_to_response(yogas_data, "yogas")
        
        return yogas_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating yogas: {str(e)}")

