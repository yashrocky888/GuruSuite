"""
Kundli (Birth Chart) API routes.

This module provides FastAPI endpoints for calculating and retrieving
birth charts (kundli), including D1, D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsa), D9 (Navamsa), D10 (Dasamsa), and D12 (Dwadasamsa).
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict
from datetime import datetime
import math
import os
import logging
import swisseph as swe

from src.db.schemas import KundliRequest
from src.jyotish.kundli import calculate_kundli
from src.jyotish.kundli_engine import generate_kundli
# DEPRECATED: Direct varga imports removed - use varga_engine.py instead
# from src.jyotish.varga import calculate_navamsa, calculate_dasamsa, varga_degree
# All varga calculations now go through varga_engine.py (single source of truth)
# Note: Old calculate_all_yogas replaced by new yoga system
# from src.jyotish.yogas import calculate_all_yogas
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.ai.explanation import add_explanation_to_response

router = APIRouter()


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
        
        # Prepare D1 data for varga engine
        d1_ascendant = base_kundli["Ascendant"]["degree"]
        d1_planets = {
            planet_name: planet_info["degree"]
            for planet_name, planet_info in base_kundli["Planets"].items()
        }
        
        # Build D9 chart using authoritative engine
        d9_chart = build_varga_chart(d1_planets, d1_ascendant, 9)
        
        # Build standardized response matching D1 structure
        # RUNTIME ASSERTION: Lagna house must be 1
        assert d9_chart["ascendant"]["house"] == 1, \
            f"D9 lagna house must be 1, got {d9_chart['ascendant']['house']}"
        
        # Build houses array (Whole Sign: fixed sign grid)
        houses_array = []
        for house_num in range(1, 13):
            sign_index = house_num - 1
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
        
        # Prepare D1 data for varga engine
        d1_ascendant = base_kundli["Ascendant"]["degree"]
        d1_planets = {
            planet_name: planet_info["degree"]
            for planet_name, planet_info in base_kundli["Planets"].items()
        }
        
        # Build D10 chart using authoritative engine (with verified Prokerala/JHora logic)
        d10_chart = build_varga_chart(d1_planets, d1_ascendant, 10)
        
        # Build standardized response matching D1 structure
        # RUNTIME ASSERTION: Lagna house must be 1
        assert d10_chart["ascendant"]["house"] == 1, \
            f"D10 lagna house must be 1, got {d10_chart['ascendant']['house']}"
        
        # Build houses array (Whole Sign: fixed sign grid)
        houses_array = []
        for house_num in range(1, 13):
            sign_index = house_num - 1
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
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    timezone: str = Query("Asia/Kolkata", description="Timezone (default: Asia/Kolkata)")
):
    """
    Calculate complete Kundli (D1) with D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsa), D9 (Navamsa), D10 (Dasamsa), and D12 (Dwadasamsa) varga charts.
    
    Phase 2 Core Kundli Engine endpoint.
    Uses Swiss Ephemeris for all calculations with Lahiri ayanamsa.
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
        timezone: Timezone (default: Asia/Kolkata)
    
    Returns:
        Complete Kundli with D1, D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsa), D9 (Navamsa), D10 (Dasamsa), and D12 (Dwadasamsa)
    """
    try:
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
        
        from src.jyotish.varga_engine import build_varga_chart, get_varga_ascendant_only
        from src.utils.converters import get_sign_name_sanskrit
        
        # Prepare D1 planet longitudes for varga engine
        d1_ascendant = base_kundli["Ascendant"]["degree"]
        d1_planets = {
            planet_name: planet_info["degree"]
            for planet_name, planet_info in base_kundli["Planets"].items()
        }
        
        # Build all varga charts using authoritative engine
        # This ensures sign and house are computed together atomically
        d2_chart = build_varga_chart(d1_planets, d1_ascendant, 2)
        d3_chart = build_varga_chart(d1_planets, d1_ascendant, 3)
        d4_chart = build_varga_chart(d1_planets, d1_ascendant, 4)
        d7_chart = build_varga_chart(d1_planets, d1_ascendant, 7)
        d9_chart = build_varga_chart(d1_planets, d1_ascendant, 9)
        d10_chart = build_varga_chart(d1_planets, d1_ascendant, 10)
        
        # D12 (Dwadasamsa) - Special handling for ascendant (base formula, no +3 correction)
        # But planets still use standard varga formula
        d12_chart = build_varga_chart(d1_planets, d1_ascendant, 12)
        
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
        
        # Helper function to build standardized varga chart response
        def build_standardized_varga_response(varga_chart: Dict, chart_type: str) -> Dict:
            """Build standardized varga chart response matching D1 structure."""
            # RUNTIME ASSERTION: Lagna house must be 1
            assert varga_chart["ascendant"]["house"] == 1, \
                f"{chart_type} lagna house must be 1, got {varga_chart['ascendant']['house']}"
            
            # Import required functions
            from src.utils.converters import get_sign_name
            from src.jyotish.kundli_engine import get_house_lord_from_sign
            
            # Build houses array for varga (Whole Sign: house = sign, fixed grid)
            # House 1 = Mesha, House 2 = Vrishabha, ..., House 12 = Meena
            houses_array = []
            for house_num in range(1, 13):
                sign_index = house_num - 1  # 0-11
                houses_array.append({
                    "house": house_num,
                    "sign": get_sign_name(sign_index),
                    "sign_sanskrit": get_sign_name_sanskrit(sign_index),
                    "sign_index": sign_index,
                    "degree": 0.0,  # Varga houses don't have cusps
                    "degrees_in_sign": 0.0,
                    "lord": get_house_lord_from_sign(sign_index)
                })
            
            # RUNTIME ASSERTION: Must have exactly 12 houses
            assert len(houses_array) == 12, f"{chart_type} must have exactly 12 houses"
            
            return {
                "Ascendant": {
                    "degree": varga_chart["ascendant"]["degree"],
                    "sign": varga_chart["ascendant"]["sign"],
                    "sign_sanskrit": get_sign_name_sanskrit(varga_chart["ascendant"]["sign_index"]),
                    "sign_index": varga_chart["ascendant"]["sign_index"],
                    "degrees_in_sign": varga_chart["ascendant"]["degrees_in_sign"],
                    "house": varga_chart["ascendant"]["house"],  # Always 1
                    "lord": get_house_lord_from_sign(varga_chart["ascendant"]["sign_index"])
                },
                "Houses": houses_array,
                "Planets": varga_chart["planets"],
                "chartType": chart_type
            }
        
        # Build standardized response with consistent structure
        response = {
            "julian_day": round(jd, 6),
            "D1": base_kundli,
            "D2": build_standardized_varga_response(d2_chart, "D2"),
            "D3": build_standardized_varga_response(d3_chart, "D3"),
            "D4": build_standardized_varga_response(d4_chart, "D4"),
            "D7": build_standardized_varga_response(d7_chart, "D7"),
            "D9": build_standardized_varga_response(d9_chart, "D9"),
            "D10": build_standardized_varga_response(d10_chart, "D10"),
            "D12": build_standardized_varga_response(d12_chart, "D12")
        }
        
        # CRITICAL: Log final payload for D10 verification (Prokerala match)
        logger = logging.getLogger(__name__)
        if "D10" in response:
            d10_data = response["D10"]
            logger.info(f"📊 D10 FINAL PAYLOAD (Authoritative Engine):")
            logger.info(f"   Ascendant: {d10_data.get('ascendant_sign_sanskrit')} (sign_index={d10_data.get('ascendant_sign')}) → House {d10_data.get('ascendant_house')}")
            for planet_name in ["Venus", "Mars"]:
                if planet_name in d10_data.get("planets", {}):
                    planet_data = d10_data["planets"][planet_name]
                    logger.info(f"   {planet_name}: {planet_data.get('sign')} (sign_index={planet_data.get('sign_index')}) → House {planet_data.get('house')} [house==sign: {planet_data.get('house') == planet_data.get('sign_index') + 1}]")
        
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
        planets = {}
        for planet_name, planet_degree in planets_sidereal.items():
            if planet_name in ["Rahu", "Ketu"]:
                continue
            sign_num, _ = degrees_to_sign(planet_degree)
            relative_pos = normalize_degrees(planet_degree - asc_sidereal)
            house_num = int(relative_pos / 30) + 1
            if house_num > 12:
                house_num = 1
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

