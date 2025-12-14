"""
Astronomical utility functions for Panchang calculations.

Phase 4: Helper functions for Sun/Moon calculations using Swiss Ephemeris.
"""

import swisseph as swe
from datetime import datetime
from typing import Tuple


def normalize(deg: float) -> float:
    """
    Normalize degrees to 0-360 range.
    
    Args:
        deg: Degree value (can be negative or > 360)
    
    Returns:
        Normalized degrees (0-360)
    """
    deg = deg % 360
    if deg < 0:
        deg += 360
    return deg


def get_sun_moon_longitudes(jd: float) -> Tuple[float, float]:
    """
    Get Sun and Moon tropical longitudes for a given Julian Day.
    
    Uses Swiss Ephemeris for accurate calculations.
    
    Args:
        jd: Julian Day Number
    
    Returns:
        Tuple of (sun_longitude, moon_longitude) in degrees
    """
    # Calculate Sun position
    sun_result = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
    sun_longitude = normalize(sun_result[0][0])
    
    # Calculate Moon position
    moon_result = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
    moon_longitude = normalize(moon_result[0][0])
    
    return sun_longitude, moon_longitude


def get_sun_moon_sidereal(jd: float) -> Tuple[float, float]:
    """
    Get Sun and Moon sidereal longitudes (with ayanamsa correction).
    
    Args:
        jd: Julian Day Number
    
    Returns:
        Tuple of (sun_sidereal, moon_sidereal) in degrees
    """
    # Get ayanamsa
    ayanamsa = swe.get_ayanamsa(jd)
    
    # Get tropical positions
    sun_tropical, moon_tropical = get_sun_moon_longitudes(jd)
    
    # Convert to sidereal
    sun_sidereal = normalize(sun_tropical - ayanamsa)
    moon_sidereal = normalize(moon_tropical - ayanamsa)
    
    return sun_sidereal, moon_sidereal

