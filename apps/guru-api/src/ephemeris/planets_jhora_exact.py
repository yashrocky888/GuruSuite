"""
EXACT JHORA Planetary Calculation Engine

This module implements EXACT JHORA planetary calculation methodology.
DO NOT MODIFY THE CALCULATION LOGIC - IT MUST MATCH JHORA EXACTLY.
"""

import swisseph as swe
from typing import Dict
import math

from src.utils.converters import normalize_degrees


def init_jhora_exact():
    """Initialize Swiss Ephemeris in EXACT JHORA mode."""
    # Set Lahiri Ayanamsa (SIDM_LAHIRI)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    # Set ephemeris path (if needed)
    # swe.set_ephe_path("./ephe")


def calculate_planet_jhora_exact(julian_day: float, planet_id: int) -> Dict:
    """
    Calculate planet position using EXACT JHORA / DRIK PANCHANG methodology.
    
    Formula (DO NOT MODIFY):
    1. swe.set_sid_mode(swe.SIDM_LAHIRI)
    2. lon, lat, dist = swe.calc_ut(jd_ut, planet, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    3. FLG_SIDEREAL returns sidereal longitude directly - DO NOT subtract ayanamsa
    4. sidereal_lon = lon % 360.0
    
    Args:
        julian_day: Julian Day Number (UTC - jd_ut)
        planet_id: Planet ID (swe.SUN, swe.MOON, etc.)
    
    Returns:
        Complete planet data with exact DMS format
    """
    init_jhora_exact()
    
    # Step 1: Calculate sidereal longitude using calc_ut() with FLG_SIDEREAL
    # FLG_SIDEREAL returns sidereal positions directly (no manual ayanamsa subtraction)
    # FLG_SPEED is needed for retrograde detection
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    xx, ret = swe.calc_ut(julian_day, planet_id, flags)
    
    if ret < 0:
        raise ValueError(f"Error calculating planet {planet_id}: {ret}")
    
    # Extract sidereal longitude (already sidereal due to FLG_SIDEREAL flag)
    sidereal_lon = float(xx[0])
    latitude = float(xx[1])
    distance = float(xx[2])
    speed_longitude = float(xx[3])
    
    # Step 2: Normalize sidereal longitude
    sidereal_lon = sidereal_lon % 360.0
    if sidereal_lon < 0:
        sidereal_lon += 360.0
    
    # Convert to DMS EXACTLY as specified (NO ROUNDING, NO ceil)
    sign_index = int(sidereal_lon // 30.0)
    deg_in_sign = sidereal_lon % 30.0
    
    # Full degree (0-360)
    deg_full = int(sidereal_lon // 1.0)
    minutes_float = (sidereal_lon % 1.0) * 60.0
    minutes_full = int(minutes_float)
    seconds_full = int((minutes_float - minutes_full) * 60.0)
    
    # Degree in sign (0-29)
    deg_in_sign_int = int(deg_in_sign // 1.0)
    minutes_in_sign_float = (deg_in_sign % 1.0) * 60.0
    minutes_in_sign = int(minutes_in_sign_float)
    seconds_in_sign = int((minutes_in_sign_float - minutes_in_sign) * 60.0)
    
    # Retrograde detection
    retro = (speed_longitude < 0)
    
    return {
        "longitude": sidereal_lon,  # Full sidereal longitude (0-360), double precision
        "latitude": latitude,
        "distance": distance,
        "speed": speed_longitude,
        "retro": retro,
        "sign_index": sign_index,
        "degrees_in_sign": deg_in_sign,
        # Full longitude DMS
        "degree": deg_full,
        "arcminutes": minutes_full,
        "arcseconds": seconds_full,
        # Degree in sign DMS
        "degree_in_sign": deg_in_sign_int,
        "minutes_in_sign": minutes_in_sign,
        "seconds_in_sign": seconds_in_sign
    }


def calculate_ascendant_jhora_exact(julian_day: float, latitude: float, longitude: float) -> Dict:
    """
    Calculate Ascendant using EXACT JHORA / DRIK PANCHANG methodology.
    
    Formula (DO NOT MODIFY):
    1. houses = swe.houses_ex(jd_ut, lat, lon, b'P', swe.FLG_SIDEREAL)
    2. FLG_SIDEREAL returns sidereal ascendant directly - DO NOT subtract ayanamsa
    3. asc_sidereal = houses[0][0] % 360.0
    4. Convert to DMS exactly as specified
    
    Args:
        julian_day: Julian Day Number (UTC - jd_ut)
        latitude: Geographic latitude
        longitude: Geographic longitude
    
    Returns:
        Ascendant data with exact DMS format
    """
    init_jhora_exact()
    
    # Step 1: Calculate houses using houses_ex() with FLG_SIDEREAL
    # FLG_SIDEREAL returns sidereal positions directly (no manual ayanamsa subtraction)
    # b'P' = Placidus house system (JHORA style)
    result = swe.houses_ex(julian_day, latitude, longitude, b'P', swe.FLG_SIDEREAL)
    if result is None:
        raise ValueError("Error calculating houses")
    
    cusps, ascmc = result
    sidereal_asc = float(ascmc[0])  # Ascendant (already sidereal due to FLG_SIDEREAL)
    
    # Step 2: Normalize sidereal ascendant
    sidereal_asc = sidereal_asc % 360.0
    if sidereal_asc < 0:
        sidereal_asc += 360.0
    
    # Convert to DMS EXACTLY as specified (NO ROUNDING, NO ceil)
    sign_index = int(sidereal_asc // 30.0)
    deg_in_sign = sidereal_asc % 30.0
    
    # Full degree (0-360)
    deg_full = int(sidereal_asc // 1.0)
    minutes_float = (sidereal_asc % 1.0) * 60.0
    minutes_full = int(minutes_float)
    seconds_full = int((minutes_float - minutes_full) * 60.0)
    
    # Degree in sign (0-29)
    deg_in_sign_int = int(deg_in_sign // 1.0)
    minutes_in_sign_float = (deg_in_sign % 1.0) * 60.0
    minutes_in_sign = int(minutes_in_sign_float)
    seconds_in_sign = int((minutes_in_sign_float - minutes_in_sign) * 60.0)
    
    return {
        "longitude": sidereal_asc,  # Full sidereal longitude, double precision
        "sign_index": sign_index,
        "degrees_in_sign": deg_in_sign,
        # Full longitude DMS
        "degree": deg_full,
        "arcminutes": minutes_full,
        "arcseconds": seconds_full,
        # Degree in sign DMS
        "degree_in_sign": deg_in_sign_int,
        "minutes_in_sign": minutes_in_sign,
        "seconds_in_sign": seconds_in_sign
    }


def calculate_all_planets_jhora_exact(julian_day: float) -> Dict[str, Dict]:
    """
    Calculate all planets using EXACT JHORA / DRIK PANCHANG methodology.
    
    Args:
        julian_day: Julian Day Number (UTC - jd_ut)
    
    Returns:
        Dictionary with all planet data
    """
    init_jhora_exact()
    
    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE  # MEAN NODE (not True Node)
    }
    
    results = {}
    
    # Calculate all planets
    for planet_name, planet_id in planets.items():
        results[planet_name] = calculate_planet_jhora_exact(julian_day, planet_id)
    
    # Calculate Ketu (Rahu + 180 degrees)
    rahu_data = results["Rahu"]
    ketu_longitude = (rahu_data["longitude"] + 180.0) % 360.0
    
    # Convert Ketu to DMS
    sign_index = int(ketu_longitude // 30.0)
    deg_in_sign = ketu_longitude % 30.0
    
    deg_full = int(ketu_longitude // 1.0)
    minutes_float = (ketu_longitude % 1.0) * 60.0
    minutes_full = int(minutes_float)
    seconds_full = int((minutes_float - minutes_full) * 60.0)
    
    deg_in_sign_int = int(deg_in_sign // 1.0)
    minutes_in_sign_float = (deg_in_sign % 1.0) * 60.0
    minutes_in_sign = int(minutes_in_sign_float)
    seconds_in_sign = int((minutes_in_sign_float - minutes_in_sign) * 60.0)
    
    results["Ketu"] = {
        "longitude": ketu_longitude,
        "latitude": -rahu_data["latitude"],
        "distance": rahu_data["distance"],
        "speed": -rahu_data["speed"],
        "retro": True,  # Ketu is always retrograde
        "sign_index": sign_index,
        "degrees_in_sign": deg_in_sign,
        "degree": deg_full,
        "arcminutes": minutes_full,
        "arcseconds": seconds_full,
        "degree_in_sign": deg_in_sign_int,
        "minutes_in_sign": minutes_in_sign,
        "seconds_in_sign": seconds_in_sign
    }
    
    return results

