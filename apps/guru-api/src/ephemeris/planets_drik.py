"""
Drik Panchang-compatible planetary calculation engine.

This module provides EXACT calculations matching Drik Panchang methodology:
- Lahiri Ayanamsa
- TRUE Node (not mean node)
- Proper SWE flags
- Correct Rashi, Nakshatra, Pada calculations
- Retrograde detection
"""

import swisseph as swe
from typing import Dict, List
from datetime import datetime

from src.utils.converters import normalize_degrees


# Rashi (Sign) names in Sanskrit order
RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]

# Rashi names in English
RASHI_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Nakshatra names (27 nakshatras)
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Planet constants
SE_SUN = swe.SUN
SE_MOON = swe.MOON
SE_MERCURY = swe.MERCURY
SE_VENUS = swe.VENUS
SE_MARS = swe.MARS
SE_JUPITER = swe.JUPITER
SE_SATURN = swe.SATURN
SE_RAHU = swe.TRUE_NODE  # TRUE NODE (not mean node)


def init_drik_mode():
    """Initialize Swiss Ephemeris in Drik Panchang mode."""
    # Set Lahiri Ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)


def get_rashi(longitude: float) -> Dict[str, any]:
    """
    Get Rashi (sign) from longitude.
    
    Args:
        longitude: Ecliptic longitude in degrees (0-360)
    
    Returns:
        Dictionary with rashi info
    """
    longitude = normalize_degrees(longitude)
    rashi_index = int(longitude / 30)
    degree_in_rashi = longitude % 30
    
    return {
        "index": rashi_index,
        "name": RASHI_NAMES[rashi_index],
        "name_en": RASHI_NAMES_EN[rashi_index],
        "degree": degree_in_rashi
    }


def get_nakshatra_pada(longitude: float) -> Dict[str, any]:
    """
    Get Nakshatra and Pada from longitude.
    
    Args:
        longitude: Ecliptic longitude in degrees (0-360)
    
    Returns:
        Dictionary with nakshatra and pada info
    """
    longitude = normalize_degrees(longitude)
    
    # Each nakshatra = 13.3333333333 degrees (360/27)
    nakshatra_size = 360.0 / 27.0
    nakshatra_index = int(longitude / nakshatra_size)
    
    # Each pada = 3.3333333333 degrees (13.3333333333/4)
    pada_size = nakshatra_size / 4.0
    degree_in_nakshatra = longitude % nakshatra_size
    pada = int(degree_in_nakshatra / pada_size) + 1
    
    if pada > 4:
        pada = 4
    
    return {
        "index": nakshatra_index,
        "name": NAKSHATRA_NAMES[nakshatra_index],
        "pada": pada
    }


def calculate_planet_drik(julian_day: float, planet_id: int) -> Dict[str, any]:
    """
    Calculate planet position using Drik Panchang methodology.
    
    Uses proper SWE flags:
    - SEFLG_SWIEPH | SEFLG_SIDEREAL | SEFLG_TRUEPOS | SEFLG_SPEED
    
    Args:
        julian_day: Julian Day Number (UTC)
        planet_id: Planet ID (SE_SUN, SE_MOON, etc.)
    
    Returns:
        Complete planet data matching Drik Panchang format
    """
    init_drik_mode()
    
    # Set proper flags for Drik Panchang calculation
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TRUEPOS | swe.FLG_SPEED
    
    # Calculate position (already in sidereal due to FLG_SIDEREAL flag)
    xx, ret = swe.calc_ut(julian_day, planet_id, flags)
    
    if ret < 0:
        raise ValueError(f"Error calculating planet {planet_id}: {ret}")
    
    # Extract data
    longitude = normalize_degrees(xx[0])  # Already sidereal
    latitude = xx[1]
    distance = xx[2]
    speed_longitude = xx[3]
    speed_latitude = xx[4]
    speed_distance = xx[5]
    
    # Get Rashi
    rashi = get_rashi(longitude)
    
    # Get Nakshatra and Pada
    nakshatra_data = get_nakshatra_pada(longitude)
    
    # Retrograde detection
    retro = (speed_longitude < 0)
    
    return {
        "planet": _get_planet_name(planet_id),
        "fullDegree": longitude,
        "degree": longitude % 30,
        "rashi": rashi["name"],
        "rashi_en": rashi["name_en"],
        "rashi_index": rashi["index"],
        "nakshatra": nakshatra_data["name"],
        "nakshatra_index": nakshatra_data["index"],
        "pada": nakshatra_data["pada"],
        "retro": retro,
        "speed": speed_longitude,
        "latitude": latitude,
        "distance": distance
    }


def _get_planet_name(planet_id: int) -> str:
    """Get planet name from ID."""
    planet_map = {
        SE_SUN: "Sun",
        SE_MOON: "Moon",
        SE_MERCURY: "Mercury",
        SE_VENUS: "Venus",
        SE_MARS: "Mars",
        SE_JUPITER: "Jupiter",
        SE_SATURN: "Saturn",
        SE_RAHU: "Rahu"
    }
    return planet_map.get(planet_id, "Unknown")


def calculate_all_planets_drik(julian_day: float) -> Dict[str, Dict[str, any]]:
    """
    Calculate all planets using Drik Panchang methodology.
    
    Args:
        julian_day: Julian Day Number (UTC)
    
    Returns:
        Dictionary with all planet data
    """
    init_drik_mode()
    
    planets = {
        "Sun": SE_SUN,
        "Moon": SE_MOON,
        "Mars": SE_MARS,
        "Mercury": SE_MERCURY,
        "Jupiter": SE_JUPITER,
        "Venus": SE_VENUS,
        "Saturn": SE_SATURN,
        "Rahu": SE_RAHU  # TRUE NODE
    }
    
    results = {}
    
    # Calculate all planets
    for planet_name, planet_id in planets.items():
        results[planet_name] = calculate_planet_drik(julian_day, planet_id)
    
    # Calculate Ketu (Rahu + 180 degrees)
    rahu_data = results["Rahu"]
    ketu_longitude = normalize_degrees(rahu_data["fullDegree"] + 180)
    
    # Get Ketu's Rashi and Nakshatra
    ketu_rashi = get_rashi(ketu_longitude)
    ketu_nakshatra = get_nakshatra_pada(ketu_longitude)
    
    # Ketu is always retrograde (opposite of Rahu)
    ketu_speed = -rahu_data["speed"] if rahu_data["speed"] != 0 else 0
    
    results["Ketu"] = {
        "planet": "Ketu",
        "fullDegree": ketu_longitude,
        "degree": ketu_longitude % 30,
        "rashi": ketu_rashi["name"],
        "rashi_en": ketu_rashi["name_en"],
        "rashi_index": ketu_rashi["index"],
        "nakshatra": ketu_nakshatra["name"],
        "nakshatra_index": ketu_nakshatra["index"],
        "pada": ketu_nakshatra["pada"],
        "retro": True,  # Ketu is always retrograde
        "speed": ketu_speed,
        "latitude": -rahu_data["latitude"],
        "distance": rahu_data["distance"]
    }
    
    return results

