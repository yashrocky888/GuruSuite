"""
House calculation module for Vedic astrology.

This module provides functions to calculate house cusps
and determine planetary house positions.
"""

from typing import Dict, List
from datetime import datetime

from src.ephemeris.ephemeris_utils import calculate_houses, SE_HOUSE_PLACIDUS
from src.utils.timezone import get_julian_day
from src.utils.converters import (
    normalize_degrees,
    degrees_to_sign,
    get_sign_name
)


def calculate_houses_sidereal(
    birth_datetime: datetime,
    latitude: float,
    longitude: float
) -> Dict[str, Dict]:
    """
    Calculate house cusps in sidereal zodiac (Vedic).
    
    This function:
    1. Calculates tropical house cusps using Swiss Ephemeris
    2. Applies ayanamsa correction to get sidereal positions
    3. Determines sign for each house cusp
    
    Args:
        birth_datetime: Birth date and time (UTC)
        latitude: Birth latitude
        longitude: Birth longitude
    
    Returns:
        Dictionary with house data including:
        - ascendant: Ascendant longitude and sign
        - house_1 through house_12: House cusp data
    """
    julian_day = get_julian_day(birth_datetime)
    
    # Calculate houses (tropical)
    tropical_houses = calculate_houses(julian_day, latitude, longitude, SE_HOUSE_PLACIDUS)
    
    # Get ayanamsa for sidereal conversion
    from src.ephemeris.ephemeris_utils import get_ayanamsa
    ayanamsa = get_ayanamsa(julian_day)
    
    # Convert to sidereal
    sidereal_houses = {}
    
    for house_key, tropical_longitude in tropical_houses.items():
        # Convert tropical to sidereal
        sidereal_longitude = normalize_degrees(tropical_longitude - ayanamsa)
        
        # Calculate sign
        sign_num, degrees_in_sign = degrees_to_sign(sidereal_longitude)
        
        sidereal_houses[house_key] = {
            "longitude": sidereal_longitude,
            "sign": sign_num,
            "sign_name": get_sign_name(sign_num),
            "degrees_in_sign": degrees_in_sign
        }
    
    return sidereal_houses


def get_house_lord(house_number: int) -> str:
    """
    Get the lord (ruler) of a house.
    
    House lords in Vedic astrology:
    1: Aries (Mars), 2: Taurus (Venus), 3: Gemini (Mercury),
    4: Cancer (Moon), 5: Leo (Sun), 6: Virgo (Mercury),
    7: Libra (Venus), 8: Scorpio (Mars), 9: Sagittarius (Jupiter),
    10: Capricorn (Saturn), 11: Aquarius (Saturn), 12: Pisces (Jupiter)
    
    Args:
        house_number: House number (1-12)
    
    Returns:
        Planet name that rules the house
    """
    # House lords based on natural zodiac
    house_lords = {
        1: "Mars",    # Aries
        2: "Venus",   # Taurus
        3: "Mercury", # Gemini
        4: "Moon",    # Cancer
        5: "Sun",     # Leo
        6: "Mercury", # Virgo
        7: "Venus",   # Libra
        8: "Mars",    # Scorpio
        9: "Jupiter", # Sagittarius
        10: "Saturn", # Capricorn
        11: "Saturn", # Aquarius
        12: "Jupiter" # Pisces
    }
    
    return house_lords.get(house_number, "Unknown")


def get_house_meanings() -> Dict[int, str]:
    """
    Get traditional meanings of houses in Vedic astrology.
    
    Returns:
        Dictionary mapping house numbers to their meanings
    """
    return {
        1: "Self, personality, appearance, health",
        2: "Wealth, family, speech, food, face",
        3: "Siblings, courage, communication, short journeys",
        4: "Mother, home, property, education, vehicles",
        5: "Children, creativity, education, speculation",
        6: "Health, enemies, service, debts, obstacles",
        7: "Spouse, partnerships, marriage, business",
        8: "Longevity, transformation, occult, sudden events",
        9: "Father, dharma, fortune, higher learning, guru",
        10: "Career, reputation, status, karma",
        11: "Gains, income, friends, aspirations",
        12: "Losses, expenses, foreign lands, moksha, bed pleasures"
    }

