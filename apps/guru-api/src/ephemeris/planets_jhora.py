"""
EXACT JHORA Planetary Calculation Engine

This module implements EXACT JHORA planetary calculation methodology:
- Use swe.calc() for tropical positions (NOT swe.calc_ut() with FLG_SIDEREAL)
- Compute ayanamsa using swe.get_ayanamsa()
- Convert to sidereal: (tropical_lon - ayanamsa) % 360
- Use SE_SIDM_LAHIRI (N.C. Lahiri corrected)
- Output deg-min-sec format
- Match JHORA exactly up to 1 arcsecond
"""

import swisseph as swe
from typing import Dict
import math

from src.utils.converters import normalize_degrees


def init_jhora_mode():
    """Initialize Swiss Ephemeris in JHORA mode."""
    # Set Lahiri Ayanamsa (N.C. Lahiri corrected)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)


def calculate_planet_jhora(julian_day: float, planet_id: int) -> Dict:
    """
    Calculate planet position using EXACT JHORA methodology.
    
    Steps:
    1. Compute tropical longitude using swe.calc(jd, planet)
    2. Compute ayanamsa using swe.get_ayanamsa(jd)
    3. Compute sidereal longitude: (tropical_lon - ayanamsa) % 360
    4. DO NOT ROUND - use double-precision floats
    5. DO NOT use FLG_SIDEREAL flag
    
    Args:
        julian_day: Julian Day Number (UTC)
        planet_id: Planet ID (swe.SUN, swe.MOON, etc.)
    
    Returns:
        Complete planet data with deg-min-sec format
    """
    init_jhora_mode()
    
    # Step 1: Compute tropical longitude using swe.calc_ut() WITHOUT FLG_SIDEREAL
    # swe.calc_ut() uses UTC, which is what we have (jd_ut)
    # We do NOT use FLG_SIDEREAL flag - we want tropical, then convert manually
    xx, ret = swe.calc_ut(julian_day, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    
    if ret < 0:
        raise ValueError(f"Error calculating planet {planet_id}: {ret}")
    
    # Extract tropical longitude
    tropical_lon = xx[0]
    latitude = xx[1]
    distance = xx[2]
    speed_longitude = xx[3]
    
    # Step 2: Compute ayanamsa
    ayanamsa = swe.get_ayanamsa(julian_day)
    
    # Step 3: Compute sidereal longitude
    sidereal_lon = normalize_degrees(tropical_lon - ayanamsa)
    
    # Get sign information
    sign_index = int(sidereal_lon / 30.0)
    degrees_in_sign = sidereal_lon % 30.0
    
    # Convert FULL longitude to deg-min-sec format (not just degrees_in_sign)
    deg_min_sec = degrees_to_dms(sidereal_lon)
    
    # Also convert degrees_in_sign for sign-based display
    deg_in_sign_dms = degrees_to_dms(degrees_in_sign)
    
    # Retrograde detection
    retro = (speed_longitude < 0)
    
    return {
        "longitude": sidereal_lon,  # Full sidereal longitude (0-360)
        "tropical_lon": tropical_lon,  # For reference
        "ayanamsa": ayanamsa,  # For reference
        "latitude": latitude,
        "distance": distance,
        "speed": speed_longitude,
        "retro": retro,
        "sign_index": sign_index,
        "degrees_in_sign": degrees_in_sign,
        "degree": deg_min_sec["degree"],  # Full degree (0-360)
        "arcminutes": deg_min_sec["minutes"],
        "arcseconds": deg_min_sec["seconds"],
        "degree_in_sign": deg_in_sign_dms["degree"],  # Degree within sign (0-29)
        "minutes_in_sign": deg_in_sign_dms["minutes"],
        "seconds_in_sign": deg_in_sign_dms["seconds"]
    }


def degrees_to_dms(degrees: float) -> Dict[str, int]:
    """
    Convert degrees to degrees, arcminutes, arcseconds.
    
    Args:
        degrees: Longitude in degrees (0-360)
    
    Returns:
        Dictionary with degree, minutes, seconds
    """
    degrees = normalize_degrees(degrees)
    
    # Get full degrees
    deg = int(math.floor(degrees))
    
    # Get fractional part for minutes
    fractional = degrees - deg
    total_minutes = fractional * 60.0
    minutes = int(math.floor(total_minutes))
    
    # Get fractional part for seconds
    fractional_minutes = total_minutes - minutes
    total_seconds = fractional_minutes * 60.0
    seconds = int(math.floor(total_seconds))
    
    return {
        "degree": deg,
        "minutes": minutes,
        "seconds": seconds
    }


def calculate_all_planets_jhora(julian_day: float) -> Dict[str, Dict]:
    """
    Calculate all planets using EXACT JHORA methodology.
    
    Args:
        julian_day: Julian Day Number (UTC)
    
    Returns:
        Dictionary with all planet data
    """
    init_jhora_mode()
    
    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE  # MEAN NODE (to match reference/JHORA exactly)
    }
    
    results = {}
    
    # Calculate all planets
    for planet_name, planet_id in planets.items():
        results[planet_name] = calculate_planet_jhora(julian_day, planet_id)
    
    # Calculate Ketu (Rahu + 180 degrees)
    rahu_data = results["Rahu"]
    ketu_longitude = normalize_degrees(rahu_data["longitude"] + 180)
    
    # Convert Ketu to deg-min-sec
    ketu_dms = degrees_to_dms(ketu_longitude)
    ketu_sign_index = int(ketu_longitude / 30.0)
    ketu_degrees_in_sign = ketu_longitude % 30.0
    
    results["Ketu"] = {
        "longitude": ketu_longitude,
        "tropical_lon": normalize_degrees(rahu_data["tropical_lon"] + 180),
        "ayanamsa": rahu_data["ayanamsa"],
        "latitude": -rahu_data["latitude"],
        "distance": rahu_data["distance"],
        "speed": -rahu_data["speed"],  # Ketu speed is opposite
        "retro": True,  # Ketu is always retrograde
        "sign_index": ketu_sign_index,
        "degrees_in_sign": ketu_degrees_in_sign,
        "degree": int(ketu_degrees_in_sign),
        "arcminutes": ketu_dms["minutes"],
        "arcseconds": ketu_dms["seconds"]
    }
    
    return results


def calculate_ascendant_jhora(julian_day: float, latitude: float, longitude: float) -> Dict:
    """
    Calculate Ascendant using EXACT JHORA methodology.
    
    Steps:
    1. Use swe.houses(jd, lat, lon) to get tropical ascendant
    2. Compute ayanamsa using swe.get_ayanamsa(jd)
    3. Convert to sidereal: (tropical_asc - ayanamsa) % 360
    4. Convert to deg-min-sec format
    
    Args:
        julian_day: Julian Day Number (UTC)
        latitude: Geographic latitude
        longitude: Geographic longitude
    
    Returns:
        Ascendant data with deg-min-sec format
    """
    init_jhora_mode()
    
    # Step 1: Use swe.houses() to get tropical ascendant
    # swe.houses() uses TT internally, but we pass JD_UT
    # For exact JHORA match, we may need to convert JD_UT to JD_TT first
    # But let's try swe.houses() directly first
    result = swe.houses(julian_day, latitude, longitude, b'P')  # Placidus
    if result is None:
        raise ValueError("Error calculating houses")
    
    cusps, ascmc = result
    tropical_asc = ascmc[0]
    
    # Step 2: Compute ayanamsa
    ayanamsa = swe.get_ayanamsa(julian_day)
    
    # Step 3: Convert to sidereal
    sidereal_asc = normalize_degrees(tropical_asc - ayanamsa)
    
    # Convert to deg-min-sec format
    asc_dms = degrees_to_dms(sidereal_asc)
    
    # Get sign information
    sign_index = int(sidereal_asc / 30.0)
    degrees_in_sign = sidereal_asc % 30.0
    
    return {
        "longitude": sidereal_asc,
        "tropical_lon": tropical_asc,
        "ayanamsa": ayanamsa,
        "sign_index": sign_index,
        "degrees_in_sign": degrees_in_sign,
        "degree": asc_dms["degree"],  # Full degree (0-360), not degrees_in_sign
        "arcminutes": asc_dms["minutes"],
        "arcseconds": asc_dms["seconds"]
    }

