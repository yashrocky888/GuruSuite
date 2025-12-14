"""
Kundli (Birth Chart) API routes.

This module provides FastAPI endpoints for calculating and retrieving
birth charts (kundli), including D1, D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsa), D9 (Navamsa), D10 (Dasamsa), and D12 (Dwadasamsa).
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import math
import os
import logging
import swisseph as swe

from src.db.schemas import KundliRequest
from src.jyotish.kundli import calculate_kundli
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.varga import calculate_navamsa, calculate_dasamsa, varga_degree
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
    Calculate Navamsa (D9) chart.
    
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
        navamsa_data = calculate_navamsa(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_latitude=request.birth_latitude,
            birth_longitude=request.birth_longitude,
            timezone=request.timezone
        )
        
        return navamsa_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating navamsa: {str(e)}")


@router.post("/kundli/dasamsa")
async def get_dasamsa(request: KundliRequest):
    """
    Calculate Dasamsa (D10) chart.
    
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
        dasamsa_data = calculate_dasamsa(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_latitude=request.birth_latitude,
            birth_longitude=request.birth_longitude,
            timezone=request.timezone
        )
        
        return dasamsa_data
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
        
        # Calculate all divisional charts using unified calculate_varga function
        from src.jyotish.varga_drik import calculate_varga
        from src.jyotish.kundli_engine import get_planet_house_jhora
        from src.jyotish.varga_houses import calculate_varga_houses
        from src.jyotish.drik_panchang_engine import calculate_houses_drik
        
        # Get D1 ascendant and houses for house calculations
        d1_ascendant = base_kundli["Ascendant"]["degree"]
        d1_houses_data = calculate_houses_drik(jd, lat, lon)
        d1_houses = d1_houses_data["houses"]
        
        # D2 (Hora) - Whole Sign House system (house = sign)
        d2_planets = {}
        d2_asc = calculate_varga(d1_ascendant, 2)
        for planet_name, planet_info in base_kundli["Planets"].items():
            main_degree = planet_info["degree"]
            varga_data = calculate_varga(main_degree, 2)
            # CRITICAL: For varga charts, house = sign (Whole Sign system)
            house_num = varga_data["sign"] + 1
            d2_planets[planet_name] = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_data["sign"],
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                "house": house_num  # house = sign (Whole Sign system)
            }
        
        # D3 (Drekkana) - Whole Sign House system (house = sign)
        d3_planets = {}
        d3_asc = calculate_varga(d1_ascendant, 3)
        for planet_name, planet_info in base_kundli["Planets"].items():
            main_degree = planet_info["degree"]
            varga_data = calculate_varga(main_degree, 3)
            # CRITICAL: For varga charts, house = sign (Whole Sign system)
            house_num = varga_data["sign"] + 1
            d3_planets[planet_name] = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_data["sign"],
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                "house": house_num  # house = sign (Whole Sign system)
            }
        
        # D4 (Chaturthamsa) - Whole Sign House system (house = sign)
        d4_planets = {}
        d4_asc = calculate_varga(d1_ascendant, 4)
        for planet_name, planet_info in base_kundli["Planets"].items():
            main_degree = planet_info["degree"]
            varga_data = calculate_varga(main_degree, 4)
            # CRITICAL: For varga charts, house = sign (Whole Sign system)
            house_num = varga_data["sign"] + 1
            d4_planets[planet_name] = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_data["sign"],
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                "house": house_num  # house = sign (Whole Sign system)
            }
        
        # D7 (Saptamsa) - Whole Sign House system (house = sign)
        d7_planets = {}
        d7_asc = calculate_varga(d1_ascendant, 7)
        for planet_name, planet_info in base_kundli["Planets"].items():
            main_degree = planet_info["degree"]
            varga_data = calculate_varga(main_degree, 7)
            # CRITICAL: For varga charts, house = sign (Whole Sign system)
            house_num = varga_data["sign"] + 1
            d7_planets[planet_name] = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_data["sign"],
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                "house": house_num  # house = sign (Whole Sign system)
            }
        
        # D9 (Navamsa) - Whole Sign House system (house = sign)
        d9_planets = {}
        d9_asc = calculate_varga(d1_ascendant, 9)
        for planet_name, planet_info in base_kundli["Planets"].items():
            main_degree = planet_info["degree"]
            varga_data = calculate_varga(main_degree, 9)
            # CRITICAL: For varga charts, house = sign (Whole Sign system)
            house_num = varga_data["sign"] + 1
            d9_planets[planet_name] = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_data["sign"],
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                "house": house_num  # house = sign (Whole Sign system)
            }
        
        # D10 (Dasamsa) - Whole Sign House system (house = sign)
        d10_planets = {}
        d10_asc = calculate_varga(d1_ascendant, 10)
        for planet_name, planet_info in base_kundli["Planets"].items():
            main_degree = planet_info["degree"]
            varga_data = calculate_varga(main_degree, 10)
            # CRITICAL: For varga charts, house = sign (Whole Sign system)
            # sign_index is 0-11, house is 1-12
            house_num = varga_data["sign"] + 1
            d10_planets[planet_name] = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_data["sign"],
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                "house": house_num  # house = sign (Whole Sign system)
            }
        
        # D12 (Dwadasamsa) - Whole Sign House system (house = sign)
        # CRITICAL FIX: D12 ascendant uses BASE formula WITHOUT +3 correction
        # Planets use calculate_varga which applies +3 correction
        d12_planets = {}
        
        # Calculate D12 ascendant using BASE formula (no correction)
        d1_asc_sign = int(d1_ascendant / 30)
        d1_asc_deg_in_sign = d1_ascendant % 30
        part = 2.5
        div_index = int(math.floor(d1_asc_deg_in_sign / part))
        if div_index >= 12:
            div_index = 11
        # Base formula: start from same sign, no correction
        d12_asc_sign = (d1_asc_sign + div_index) % 12
        d12_asc_deg_in_sign = (d1_asc_deg_in_sign * 12) % 30
        d12_asc_longitude = d12_asc_sign * 30 + d12_asc_deg_in_sign
        from src.utils.converters import normalize_degrees
        d12_asc_longitude = normalize_degrees(d12_asc_longitude)
        
        # Create d12_asc dict in same format as calculate_varga
        from src.utils.converters import get_sign_name
        d12_asc = {
            "longitude": d12_asc_longitude,
            "sign": d12_asc_sign,
            "sign_name": get_sign_name(d12_asc_sign),
            "degrees_in_sign": d12_asc_deg_in_sign,
            "division": div_index + 1
        }
        
        for planet_name, planet_info in base_kundli["Planets"].items():
            main_degree = planet_info["degree"]
            varga_data = calculate_varga(main_degree, 12)
            # CRITICAL: For varga charts, house = sign (Whole Sign system)
            house_num = varga_data["sign"] + 1
            d12_planets[planet_name] = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_data["sign"],
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                "house": house_num  # house = sign (Whole Sign system)
            }
        
        # Add ascendant information for divisional charts
        # Make all divisional charts have consistent structure: {ascendant, ascendant_sign, ascendant_sign_sanskrit, planets}
        from src.utils.converters import get_sign_name_sanskrit
        
        # CRITICAL: Runtime validation - enforce house = sign for ALL varga charts
        # This is a NON-NEGOTIABLE architectural requirement
        varga_charts = {
            "D2": {"planets": d2_planets, "asc": d2_asc},
            "D3": {"planets": d3_planets, "asc": d3_asc},
            "D4": {"planets": d4_planets, "asc": d4_asc},
            "D7": {"planets": d7_planets, "asc": d7_asc},
            "D9": {"planets": d9_planets, "asc": d9_asc},
            "D10": {"planets": d10_planets, "asc": d10_asc},
            "D12": {"planets": d12_planets, "asc": d12_asc},
        }
        
        validation_errors = []
        for chart_type, chart_data in varga_charts.items():
            # Validate planets: house MUST equal sign
            for planet_name, planet_data in chart_data["planets"].items():
                planet_sign_index = planet_data.get("sign_index")
                planet_house = planet_data.get("house")
                expected_house = planet_sign_index + 1 if planet_sign_index is not None else None
                
                if planet_house != expected_house:
                    error_msg = f"{chart_type} VARGA VIOLATION: {planet_name} - house ({planet_house}) must equal sign ({expected_house})"
                    validation_errors.append(error_msg)
                    # Force correction
                    if planet_sign_index is not None:
                        chart_data["planets"][planet_name]["house"] = planet_sign_index + 1
            
            # Validate ascendant: house MUST equal sign
            asc_sign_index = chart_data["asc"].get("sign")
            asc_house = chart_data["asc"].get("sign") + 1 if chart_data["asc"].get("sign") is not None else None
            # Note: ascendant_house is set in response, validate it matches
            if asc_house is not None and asc_sign_index is not None:
                expected_asc_house = asc_sign_index + 1
                if asc_house != expected_asc_house:
                    error_msg = f"{chart_type} VARGA VIOLATION: Ascendant - house ({asc_house}) must equal sign ({expected_asc_house})"
                    validation_errors.append(error_msg)
        
        if validation_errors:
            logger = logging.getLogger(__name__)
            for error in validation_errors:
                logger.error(f"❌ {error}")
            # Raise error in production, but continue in development
            if os.getenv("DEPLOYMENT_ENV") == "production":
                raise ValueError(f"VARGA CHART VALIDATION FAILED: {'; '.join(validation_errors)}")
        
        response = {
            "julian_day": round(jd, 6),
            "D1": base_kundli,
            "D2": {
                "ascendant": round(d2_asc["longitude"], 4),
                "ascendant_sign": d2_asc["sign_name"],
                "ascendant_sign_sanskrit": get_sign_name_sanskrit(d2_asc["sign"]),
                "ascendant_house": d2_asc["sign"] + 1,  # house = sign (Whole Sign system)
                "chartType": "D2",  # Add chartType for UI detection
                "planets": d2_planets
            },
            "D3": {
                "ascendant": round(d3_asc["longitude"], 4),
                "ascendant_sign": d3_asc["sign_name"],
                "ascendant_sign_sanskrit": get_sign_name_sanskrit(d3_asc["sign"]),
                "ascendant_house": d3_asc["sign"] + 1,  # house = sign (Whole Sign system)
                "chartType": "D3",  # Add chartType for UI detection
                "planets": d3_planets
            },
            "D4": {
                "ascendant": round(d4_asc["longitude"], 4),
                "ascendant_sign": d4_asc["sign_name"],
                "ascendant_sign_sanskrit": get_sign_name_sanskrit(d4_asc["sign"]),
                "ascendant_house": d4_asc["sign"] + 1,  # house = sign (Whole Sign system)
                "chartType": "D4",  # Add chartType for UI detection
                "planets": d4_planets
            },
            "D7": {
                "ascendant": round(d7_asc["longitude"], 4),
                "ascendant_sign": d7_asc["sign_name"],
                "ascendant_sign_sanskrit": get_sign_name_sanskrit(d7_asc["sign"]),
                "ascendant_house": d7_asc["sign"] + 1,  # house = sign (Whole Sign system)
                "chartType": "D7",  # Add chartType for UI detection
                "planets": d7_planets
            },
            "D9": {
                "ascendant": round(d9_asc["longitude"], 4),
                "ascendant_sign": d9_asc["sign_name"],
                "ascendant_sign_sanskrit": get_sign_name_sanskrit(d9_asc["sign"]),
                "ascendant_house": d9_asc["sign"] + 1,  # house = sign (Whole Sign system)
                "chartType": "D9",  # Add chartType for UI detection
                "planets": d9_planets
            },
            "D10": {
                "ascendant": round(d10_asc["longitude"], 4),
                "ascendant_sign": d10_asc["sign_name"],
                "ascendant_sign_sanskrit": get_sign_name_sanskrit(d10_asc["sign"]),
                "ascendant_house": d10_asc["sign"] + 1,  # house = sign (Whole Sign system)
                "chartType": "D10",  # Add chartType for UI detection
                "planets": d10_planets
            },
            "D12": {
                "ascendant": round(d12_asc["longitude"], 4),
                "ascendant_sign": d12_asc["sign_name"],
                "ascendant_sign_sanskrit": get_sign_name_sanskrit(d12_asc["sign"]),
                "ascendant_house": d12_asc["sign"] + 1,  # house = sign (Whole Sign system)
                "chartType": "D12",  # Add chartType for UI detection
                "planets": d12_planets
            }
        }
        
        # CRITICAL: Log final payload for D10, D7, D12 before returning (as per requirements)
        logger = logging.getLogger(__name__)
        for chart_type in ["D10", "D7", "D12"]:
            if chart_type in response:
                chart_data = response[chart_type]
                logger.info(f"📊 {chart_type} FINAL PAYLOAD:")
                logger.info(f"   Ascendant: {chart_data.get('ascendant_sign_sanskrit')} → House {chart_data.get('ascendant_house')}")
                for planet_name, planet_data in chart_data.get("planets", {}).items():
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

