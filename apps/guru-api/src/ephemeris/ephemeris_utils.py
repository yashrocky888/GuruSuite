"""
Swiss Ephemeris utility functions for astronomical calculations.

This module provides wrapper functions around pyswisseph (Swiss Ephemeris)
for calculating planetary positions, houses, and other astronomical data.
"""

import swisseph as swe
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from src.utils.timezone import get_julian_day
from src.utils.converters import normalize_degrees, degrees_to_sign, get_sign_name


# Swiss Ephemeris planet constants
SE_SUN = swe.SUN
SE_MOON = swe.MOON
SE_MERCURY = swe.MERCURY
SE_VENUS = swe.VENUS
SE_MARS = swe.MARS
SE_JUPITER = swe.JUPITER
SE_SATURN = swe.SATURN
SE_URANUS = swe.URANUS
SE_NEPTUNE = swe.NEPTUNE
SE_PLUTO = swe.PLUTO
SE_RAHU = swe.TRUE_NODE  # North Node (Rahu)
SE_KETU = swe.TRUE_NODE  # South Node (Ketu) - calculated as opposite of Rahu

# House system constants
SE_HOUSE_PLACIDUS = b'P'  # Placidus house system
SE_HOUSE_KOCH = b'K'  # Koch house system
SE_HOUSE_EQUAL = b'E'  # Equal house system
SE_HOUSE_WHOLE = b'W'  # Whole sign house system

# Ayanamsa constants
SE_SIDM_LAHIRI = swe.SIDM_LAHIRI  # Lahiri ayanamsa (most common in India)

# Ephemeris path (Swiss Ephemeris will auto-download if needed)
EPHE_PATH = os.path.abspath("ephe") if os.path.exists("ephe") else None


def init_swisseph():
    """
    Initialize Swiss Ephemeris library.
    Sets the ephemeris path and ayanamsa.
    """
    # Set ayanamsa to Lahiri (Chitra Paksha) for Vedic astrology
    swe.set_sid_mode(SE_SIDM_LAHIRI, 0, 0)
    
    # Set ephemeris path if directory exists
    if EPHE_PATH and os.path.exists(EPHE_PATH):
        swe.set_ephe_path(EPHE_PATH)


def initialize_ephemeris():
    """
    Initialize Swiss Ephemeris library (alias for init_swisseph).
    Sets the ephemeris path and ayanamsa.
    """
    init_swisseph()


def calculate_planet_position(
    julian_day: float,
    planet: int,
    latitude: float = 0.0,
    longitude: float = 0.0
) -> Dict[str, float]:
    """
    Calculate planet position for a given Julian Day.
    
    Uses Drik Panchang methodology with proper SWE flags:
    - SEFLG_SWIEPH | SEFLG_SIDEREAL | SEFLG_TRUEPOS | SEFLG_SPEED
    
    Args:
        julian_day: Julian Day Number
        planet: Planet number (SE_SUN, SE_MOON, etc.)
        latitude: Geographic latitude (for some calculations)
        longitude: Geographic longitude (for some calculations)
    
    Returns:
        Dictionary with planet position data:
        - longitude: Ecliptic longitude in degrees (sidereal)
        - latitude: Ecliptic latitude in degrees
        - distance: Distance from Earth in AU
        - speed_longitude: Speed in longitude (degrees/day)
        - speed_latitude: Speed in latitude (degrees/day)
        - speed_distance: Speed in distance (AU/day)
    """
    # Initialize Drik mode (Lahiri Ayanamsa)
    swe.set_sid_mode(SE_SIDM_LAHIRI, 0, 0)
    
    # Use proper flags for Drik Panchang calculation
    # FLG_SIDEREAL returns sidereal positions directly (no manual ayanamsa subtraction needed)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TRUEPOS | swe.FLG_SPEED
    
    # Calculate position (already in sidereal due to FLG_SIDEREAL flag)
    xx, ret = swe.calc_ut(julian_day, planet, flag)
    
    if ret < 0:
        raise ValueError(f"Error calculating planet {planet}: {ret}")
    
    longitude = normalize_degrees(xx[0])  # Already sidereal
    latitude = xx[1]
    distance = xx[2]
    speed_longitude = xx[3]
    speed_latitude = xx[4]
    speed_distance = xx[5]
    
    return {
        "longitude": longitude,
        "latitude": latitude,
        "distance": distance,
        "speed_longitude": speed_longitude,
        "speed_latitude": speed_latitude,
        "speed_distance": speed_distance
    }


def calculate_all_planets(julian_day: float) -> Dict[str, Dict[str, float]]:
    """
    Calculate positions of all planets (including Rahu and Ketu).
    
    Uses Drik Panchang methodology:
    - Lahiri Ayanamsa
    - TRUE NODE (not mean node)
    - Proper SWE flags
    
    Args:
        julian_day: Julian Day Number
    
    Returns:
        Dictionary with planet names as keys and position data as values
    """
    # Initialize Drik mode
    swe.set_sid_mode(SE_SIDM_LAHIRI, 0, 0)
    
    planets = {
        "Sun": SE_SUN,
        "Moon": SE_MOON,
        "Mercury": SE_MERCURY,
        "Venus": SE_VENUS,
        "Mars": SE_MARS,
        "Jupiter": SE_JUPITER,
        "Saturn": SE_SATURN,
        "Rahu": SE_RAHU,  # TRUE NODE (not mean node)
    }
    
    results = {}
    
    for planet_name, planet_num in planets.items():
        pos = calculate_planet_position(julian_day, planet_num)
        results[planet_name] = pos
    
    # Calculate Ketu (Rahu + 180 degrees, normalized)
    rahu_pos = results["Rahu"]["longitude"]
    ketu_longitude = normalize_degrees(rahu_pos + 180)
    results["Ketu"] = {
        "longitude": ketu_longitude,
        "latitude": -results["Rahu"]["latitude"],
        "distance": results["Rahu"]["distance"],
        "speed_longitude": -results["Rahu"]["speed_longitude"],  # Ketu speed is opposite
        "speed_latitude": -results["Rahu"]["speed_latitude"],
        "speed_distance": results["Rahu"]["speed_distance"]
    }
    
    return results


def calculate_houses(
    julian_day: float,
    latitude: float,
    longitude: float,
    house_system: bytes = SE_HOUSE_PLACIDUS
) -> Dict[str, float]:
    """
    Calculate house cusps (ascendant and 12 houses).
    
    Args:
        julian_day: Julian Day Number
        latitude: Geographic latitude
        longitude: Geographic longitude
        house_system: House system to use (default: Placidus)
    
    Returns:
        Dictionary with house cusps:
        - ascendant: Ascendant longitude
        - house_1 through house_12: House cusp longitudes
    """
    # Calculate houses using houses_ex for more control
    cusps, ascmc = swe.houses_ex(julian_day, latitude, longitude, house_system)
    
    if cusps is None:
        raise ValueError("Error calculating houses")
    
    # Extract ascendant and house cusps
    ascendant = normalize_degrees(ascmc[0])  # Ascendant
    
    results = {
        "ascendant": ascendant,
        "house_1": normalize_degrees(cusps[1]),
        "house_2": normalize_degrees(cusps[2]),
        "house_3": normalize_degrees(cusps[3]),
        "house_4": normalize_degrees(cusps[4]),
        "house_5": normalize_degrees(cusps[5]),
        "house_6": normalize_degrees(cusps[6]),
        "house_7": normalize_degrees(cusps[7]),
        "house_8": normalize_degrees(cusps[8]),
        "house_9": normalize_degrees(cusps[9]),
        "house_10": normalize_degrees(cusps[10]),
        "house_11": normalize_degrees(cusps[11]),
        "house_12": normalize_degrees(cusps[12]),
    }
    
    return results


def get_ascendant(julian_day: float, latitude: float, longitude: float) -> float:
    """
    Get ascendant (Lagna) for given coordinates and time.
    
    Args:
        julian_day: Julian Day Number
        latitude: Geographic latitude
        longitude: Geographic longitude
    
    Returns:
        Ascendant longitude in degrees
    """
    _, ascmc = swe.houses(julian_day, latitude, longitude, SE_HOUSE_PLACIDUS)
    return normalize_degrees(ascmc[0])


def get_houses(julian_day: float, latitude: float, longitude: float) -> List[float]:
    """
    Get all 12 house cusps.
    
    Args:
        julian_day: Julian Day Number
        latitude: Geographic latitude
        longitude: Geographic longitude
    
    Returns:
        List of 12 house cusp longitudes (indices 0-11 correspond to houses 1-12)
    """
    # Use houses() - returns tuple where cusps[1] through cusps[12] are house cusps
    cusps, ascmc = swe.houses(julian_day, latitude, longitude, SE_HOUSE_PLACIDUS)
    # cusps is a tuple/list where indices 1-12 are house cusps (index 0 is typically 0 or unused)
    # Handle both cases: if cusps[0] exists and is valid, or if we start from index 1
    if len(cusps) >= 13:
        # Standard case: indices 1-12 are houses
        return [normalize_degrees(cusps[i]) for i in range(1, 13)]
    elif len(cusps) == 12:
        # Alternative: indices 0-11 are houses
        return [normalize_degrees(cusps[i]) for i in range(12)]
    else:
        raise ValueError(f"Unexpected cusps length: {len(cusps)}")


def get_ayanamsa(julian_day: float) -> float:
    """
    Get ayanamsa (precession) value for given Julian Day.
    
    Args:
        julian_day: Julian Day Number
    
    Returns:
        Ayanamsa in degrees
    """
    ayanamsa = swe.get_ayanamsa(julian_day)
    return ayanamsa


# Initialize ephemeris on module import
init_swisseph()
