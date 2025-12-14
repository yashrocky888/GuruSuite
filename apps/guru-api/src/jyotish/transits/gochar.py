"""
Phase 7: Transit (Gochar) Calculation Engine

This module calculates planetary transits and their effects on houses.
"""

from math import floor
from typing import Dict, List
from src.jyotish.kundli_engine import get_planet_positions
from src.ephemeris.ephemeris_utils import get_ascendant, get_ayanamsa
from src.jyotish.transits.aspects import get_planet_aspects, calculate_aspect_strength
from src.utils.converters import normalize_degrees, degrees_to_sign

# Benefic and malefic planets
BENEFICS = ["Venus", "Jupiter", "Mercury", "Moon"]
MALEFICS = ["Mars", "Saturn", "Sun", "Rahu", "Ketu"]


def calculate_transit_house(planet_degree: float, ascendant_degree: float) -> int:
    """
    Phase 7: Calculate which house a transit planet is occupying.
    
    Formula: house = floor((planet_degree - ascendant_degree) / 30) + 1
    
    Args:
        planet_degree: Transit planet's sidereal degree
        ascendant_degree: Ascendant's sidereal degree
    
    Returns:
        House number (1-12)
    """
    relative_pos = normalize_degrees(planet_degree - ascendant_degree)
    house = int(relative_pos // 30) + 1
    
    if house > 12:
        house = 1
    
    return house


def get_transits(jd: float, lat: float, lon: float) -> Dict:
    """
    Phase 7: Calculate all planetary transits (Gochar).
    
    This function calculates:
    - Current positions of all planets
    - Which house each planet is transiting
    - Aspects (Graha Drishti) from each planet
    - Benefic/malefic strength per house
    
    Args:
        jd: Julian Day Number (for current date/time)
        lat: Geographic latitude
        lon: Geographic longitude
    
    Returns:
        Complete transit data dictionary
    """
    # Get ascendant and ayanamsa
    asc_tropical = get_ascendant(jd, lat, lon)
    ayanamsa = get_ayanamsa(jd)
    asc_sidereal = normalize_degrees(asc_tropical - ayanamsa)
    
    # Get planet positions (sidereal)
    planets = get_planet_positions(jd)
    
    transits = {}
    
    # Calculate transit for each planet
    for planet_name, planet_degree in planets.items():
        # Calculate house
        house = calculate_transit_house(planet_degree, asc_sidereal)
        
        # Get sign
        sign_num, degrees_in_sign = degrees_to_sign(planet_degree)
        
        # Get aspects
        aspects = get_planet_aspects(planet_name, planet_degree, planets)
        
        # Calculate aspect strength
        aspect_strength = calculate_aspect_strength(aspects, BENEFICS, MALEFICS)
        
        transits[planet_name] = {
            "degree": round(planet_degree, 4),
            "sign": sign_num,
            "house": house,
            "aspects": aspects,
            "aspect_strength": aspect_strength,
            "is_benefic": planet_name in BENEFICS,
            "is_malefic": planet_name in MALEFICS
        }
    
    # Calculate house impacts
    house_impacts = {}
    for house_num in range(1, 13):
        house_impacts[house_num] = {
            "transiting_planets": [],
            "benefic_aspects": 0,
            "malefic_aspects": 0,
            "net_strength": 0
        }
    
    # Fill house impacts
    for planet_name, transit_data in transits.items():
        house = transit_data["house"]
        house_impacts[house]["transiting_planets"].append(planet_name)
        
        # Add aspect strengths
        aspect_strength = transit_data["aspect_strength"]
        house_impacts[house]["benefic_aspects"] += aspect_strength["benefic_strength"]
        house_impacts[house]["malefic_aspects"] += aspect_strength["malefic_strength"]
        house_impacts[house]["net_strength"] += aspect_strength["net_strength"]
    
    return {
        "julian_day": round(jd, 6),
        "ascendant": round(asc_sidereal, 4),
        "transits": transits,
        "house_impacts": house_impacts
    }

