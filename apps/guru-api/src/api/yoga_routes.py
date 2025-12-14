"""
Yoga Detection API routes.

Phase 6: Complete yoga detection endpoints following JHora-style rules.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Dict
import swisseph as swe

from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses, get_ayanamsa
from src.utils.converters import normalize_degrees, degrees_to_sign

router = APIRouter()


def prepare_planets_for_yogas(jd: float, lat: float, lon: float):
    """
    Prepare planet data in format needed for yoga detection.
    
    Args:
        jd: Julian Day Number
        lat: Latitude
        lon: Longitude
    
    Returns:
        Tuple of (planets_dict, houses_list, ascendant)
    """
    # Get kundli data
    kundli = generate_kundli(jd, lat, lon)
    
    # Get ascendant and houses
    asc = get_ascendant(jd, lat, lon)
    ayanamsa = get_ayanamsa(jd)
    asc_sidereal = normalize_degrees(asc - ayanamsa)
    
    houses_list = get_houses(jd, lat, lon)
    houses_sidereal = [normalize_degrees(h - ayanamsa) for h in houses_list]
    
    # Get planet positions (sidereal)
    planets_sidereal = get_planet_positions(jd)
    
    # Prepare planets with house information
    planets = {}
    for planet_name, planet_degree in planets_sidereal.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        
        sign_num, degrees_in_sign = degrees_to_sign(planet_degree)
        
        # Determine house (relative to ascendant)
        relative_pos = normalize_degrees(planet_degree - asc_sidereal)
        house_num = int(relative_pos / 30) + 1
        if house_num > 12:
            house_num = 1
        
        planets[planet_name] = {
            "degree": planet_degree,
            "sign": sign_num,
            "house": house_num
        }
    
    return planets, houses_sidereal, asc_sidereal


@router.get("/all")
async def get_all_yogas(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Phase 6: Detect all yogas in the birth chart.
    
    This endpoint detects 250+ classical yogas including:
    - Planetary Placement Yogas (Gaja Kesari, Budha Aditya, etc.)
    - Panch Mahapurusha Yogas (Ruchaka, Bhadra, Hamsa, Malavya, Sasa)
    - House-Based Yogas (Raja Yogas, Dhana Yogas, etc.)
    - Combination Yogas (Chatusagara, Kalpadruma, etc.)
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        Complete yoga analysis
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
        
        # Prepare planet and house data
        planets, houses_list, asc = prepare_planets_for_yogas(jd, lat, lon)
        
        # Convert houses to required format
        houses = []
        # Add ascendant as house 1
        asc_sign, _ = degrees_to_sign(asc)
        houses.append({
            "house": 1,
            "degree": asc,
            "sign": asc_sign
        })
        
        # Add houses 2-12
        for i, house_degree in enumerate(houses_list):
            sign_num, _ = degrees_to_sign(house_degree)
            houses.append({
                "house": i + 2,  # Houses 2-12
                "degree": house_degree,
                "sign": sign_num
            })
        
        # Detect all yogas
        yoga_analysis = detect_all_yogas(planets, houses)
        
        return {
            "julian_day": round(jd, 6),
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon
            },
            "yogas": yoga_analysis
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting yogas: {str(e)}")


@router.get("/major")
async def get_major_yogas(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Get only major yogas from the birth chart.
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        Major yogas only
    """
    try:
        dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0, swe.GREG_CAL)
        
        planets, houses_list, asc = prepare_planets_for_yogas(jd, lat, lon)
        
        houses = []
        for i, house_degree in enumerate(houses_list):
            sign_num, _ = degrees_to_sign(house_degree)
            houses.append({"house": i + 2, "degree": house_degree, "sign": sign_num})
        
        asc_sign, _ = degrees_to_sign(asc)
        houses.insert(0, {"house": 1, "degree": asc, "sign": asc_sign})
        
        yoga_analysis = detect_all_yogas(planets, houses)
        
        return {
            "major_yogas": yoga_analysis["major_yogas"],
            "count": len(yoga_analysis["major_yogas"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting major yogas: {str(e)}")


@router.get("/planetary")
async def get_planetary_yogas(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Get only planetary placement yogas.
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        Planetary yogas only
    """
    try:
        dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0, swe.GREG_CAL)
        
        planets, houses_list, asc = prepare_planets_for_yogas(jd, lat, lon)
        
        houses = []
        for i, house_degree in enumerate(houses_list):
            sign_num, _ = degrees_to_sign(house_degree)
            houses.append({"house": i + 2, "degree": house_degree, "sign": sign_num})
        
        asc_sign, _ = degrees_to_sign(asc)
        houses.insert(0, {"house": 1, "degree": asc, "sign": asc_sign})
        
        yoga_analysis = detect_all_yogas(planets, houses)
        
        return {
            "planetary_yogas": yoga_analysis["by_type"]["planetary"],
            "count": len(yoga_analysis["by_type"]["planetary"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting planetary yogas: {str(e)}")


@router.get("/house")
async def get_house_yogas(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Get only house-based yogas.
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        House-based yogas only
    """
    try:
        dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0, swe.GREG_CAL)
        
        planets, houses_list, asc = prepare_planets_for_yogas(jd, lat, lon)
        
        houses = []
        for i, house_degree in enumerate(houses_list):
            sign_num, _ = degrees_to_sign(house_degree)
            houses.append({"house": i + 2, "degree": house_degree, "sign": sign_num})
        
        asc_sign, _ = degrees_to_sign(asc)
        houses.insert(0, {"house": 1, "degree": asc, "sign": asc_sign})
        
        yoga_analysis = detect_all_yogas(planets, houses)
        
        return {
            "house_yogas": yoga_analysis["by_type"]["house_based"],
            "count": len(yoga_analysis["by_type"]["house_based"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting house yogas: {str(e)}")

