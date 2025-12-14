"""
Planet calculation module for Vedic astrology.

This module provides functions to calculate planet positions
in the sidereal zodiac (with ayanamsa correction).
"""

from typing import Dict, List
from datetime import datetime

from src.ephemeris.ephemeris_utils import (
    calculate_all_planets,
    get_ayanamsa,
    SE_SUN, SE_MOON, SE_MERCURY, SE_VENUS, SE_MARS,
    SE_JUPITER, SE_SATURN, SE_RAHU
)
from src.utils.timezone import get_julian_day
from src.utils.converters import (
    normalize_degrees,
    degrees_to_sign,
    get_sign_name,
    get_nakshatra_name
)


def calculate_planets_sidereal(
    birth_datetime: datetime,
    latitude: float,
    longitude: float
) -> Dict[str, Dict]:
    """
    Calculate planet positions in sidereal zodiac (Vedic).
    
    This function:
    1. Calculates tropical positions using Swiss Ephemeris
    2. Applies ayanamsa correction to get sidereal positions
    3. Determines sign, nakshatra, and other astrological data
    
    Args:
        birth_datetime: Birth date and time (UTC)
        latitude: Birth latitude
        longitude: Birth longitude
    
    Returns:
        Dictionary with planet data including:
        - longitude: Sidereal longitude
        - sign: Sign number (0-11)
        - sign_name: Sign name
        - degrees_in_sign: Degrees within sign
        - nakshatra: Nakshatra number (0-26)
        - nakshatra_name: Nakshatra name
        - pada: Nakshatra pada (1-4)
    """
    julian_day = get_julian_day(birth_datetime)
    
    # Get ayanamsa (precession correction)
    ayanamsa = get_ayanamsa(julian_day)
    
    # Calculate all planet positions (tropical)
    tropical_positions = calculate_all_planets(julian_day)
    
    # Convert to sidereal by subtracting ayanamsa
    sidereal_positions = {}
    
    for planet_name, position in tropical_positions.items():
        # Convert tropical to sidereal
        tropical_longitude = position["longitude"]
        sidereal_longitude = normalize_degrees(tropical_longitude - ayanamsa)
        
        # Calculate sign and degrees in sign
        sign_num, degrees_in_sign = degrees_to_sign(sidereal_longitude)
        
        # Calculate nakshatra (each nakshatra is 13.333... degrees)
        nakshatra_num = int(sidereal_longitude / (360.0 / 27))
        nakshatra_degrees = sidereal_longitude % (360.0 / 27)
        pada = int(nakshatra_degrees / (360.0 / 27 / 4)) + 1
        
        sidereal_positions[planet_name] = {
            "longitude": sidereal_longitude,
            "latitude": position["latitude"],
            "distance": position["distance"],
            "speed_longitude": position["speed_longitude"],
            "speed_latitude": position["speed_latitude"],
            "speed_distance": position["speed_distance"],
            "sign": sign_num,
            "sign_name": get_sign_name(sign_num),
            "degrees_in_sign": degrees_in_sign,
            "nakshatra": nakshatra_num,
            "nakshatra_name": get_nakshatra_name(nakshatra_num),
            "pada": pada
        }
    
    return sidereal_positions


def get_planet_in_house(
    planet_longitude: float,
    house_cusps: Dict[str, float]
) -> int:
    """
    Determine which house a planet is in.
    
    Args:
        planet_longitude: Planet's sidereal longitude
        house_cusps: Dictionary of house cusp longitudes
    
    Returns:
        House number (1-12)
    """
    planet_longitude = normalize_degrees(planet_longitude)
    ascendant = normalize_degrees(house_cusps["ascendant"])
    
    # Calculate relative position from ascendant
    relative_pos = normalize_degrees(planet_longitude - ascendant)
    
    # Determine house based on relative position
    # Each house is 30 degrees
    house = int(relative_pos / 30) + 1
    
    if house > 12:
        house = 1
    
    return house

