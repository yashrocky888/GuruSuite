"""
Conversion utility functions for astrological calculations.

Provides functions to convert between different coordinate systems,
angles, and astrological units.
"""

import math
from typing import Tuple


def longitude_to_sign_index(longitude: float) -> int:
    """
    LOCK: Sign index 0-11 from longitude. Uses floor. Never round.
    Guard: longitude normalized to 0-360.
    29.999° → 0, 30.000° → 1, 359.999° → 11, 360.000° → 0.
    """
    lon = float(longitude)
    if lon >= 360.0:
        lon = lon % 360.0
    lon = lon % 360.0
    if lon < 0:
        lon += 360.0
    return int(math.floor(lon / 30.0)) % 12


def degrees_to_dms(degrees: float) -> Tuple[int, int, float]:
    """
    Convert decimal degrees to degrees, minutes, seconds.
    
    Args:
        degrees: Decimal degrees
    
    Returns:
        Tuple of (degrees, minutes, seconds)
    """
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return (d, m, s)


def dms_to_degrees(degrees: int, minutes: int, seconds: float) -> float:
    """
    Convert degrees, minutes, seconds to decimal degrees.
    
    Args:
        degrees: Degrees component
        minutes: Minutes component
        seconds: Seconds component
    
    Returns:
        Decimal degrees
    """
    return degrees + minutes / 60.0 + seconds / 3600.0


def normalize_degrees(degrees: float) -> float:
    """
    Normalize degrees to 0-360 range.
    
    Args:
        degrees: Degrees value (can be negative or > 360)
    
    Returns:
        Normalized degrees (0-360)
    """
    degrees = degrees % 360
    if degrees < 0:
        degrees += 360
    return degrees


def degrees_to_sign(degrees: float) -> Tuple[int, float]:
    """
    Convert absolute degrees to sign and degrees within sign.
    LOCK: Uses floor for sign. Guard longitude normalization.
    
    Args:
        degrees: Absolute degrees (0-360)
    
    Returns:
        Tuple of (sign_number (0-11), degrees_in_sign (0-30))
    """
    degrees = normalize_degrees(degrees)
    if degrees >= 360.0:
        degrees = degrees % 360.0
    sign = longitude_to_sign_index(degrees)
    degrees_in_sign = degrees % 30.0
    return (sign, degrees_in_sign)


def get_sign_name(sign_number: int) -> str:
    """
    Get sign name from sign number (0-11).
    
    Args:
        sign_number: Sign number (0 = Aries, 11 = Pisces)
    
    Returns:
        Sign name in English
    """
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    return signs[sign_number % 12]


def get_sign_name_sanskrit(sign_number: int) -> str:
    """
    Get Sanskrit sign name from sign number (0-11).
    
    Args:
        sign_number: Sign number (0 = Mesha, 11 = Meena)
    
    Returns:
        Sign name in Sanskrit (Vedic)
    """
    signs_sanskrit = [
        "Mesha", "Vrishabha", "Mithuna", "Karka",
        "Simha", "Kanya", "Tula", "Vrishchika",
        "Dhanu", "Makara", "Kumbha", "Meena"
    ]
    return signs_sanskrit[sign_number % 12]


def get_nakshatra_name(nakshatra_number: int) -> str:
    """
    Get nakshatra name from nakshatra number (0-26).
    
    Args:
        nakshatra_number: Nakshatra number (0-26)
    
    Returns:
        Nakshatra name in English
    """
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    return nakshatras[nakshatra_number % 27]


def get_planet_name(planet_number: int) -> str:
    """
    Get planet name from planet number (Swiss Ephemeris numbering).
    
    Args:
        planet_number: Planet number (0 = Sun, 1 = Moon, etc.)
    
    Returns:
        Planet name in English
    """
    planets = [
        "Sun", "Moon", "Mercury", "Venus", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
    ]
    if 0 <= planet_number < len(planets):
        return planets[planet_number]
    return "Unknown"


def calculate_aspect(planet1_longitude: float, planet2_longitude: float) -> float:
    """
    Calculate the aspect angle between two planets.
    
    Args:
        planet1_longitude: Longitude of first planet
        planet2_longitude: Longitude of second planet
    
    Returns:
        Aspect angle in degrees (0-180)
    """
    diff = abs(planet1_longitude - planet2_longitude)
    if diff > 180:
        diff = 360 - diff
    return diff

