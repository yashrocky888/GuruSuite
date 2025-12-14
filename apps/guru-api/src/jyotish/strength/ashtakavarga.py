"""
Phase 5: Ashtakavarga Calculation Module

JHora-style Ashtakavarga (Eight-fold Division) calculation.
Ashtakavarga shows the strength of houses based on planetary relationships.

Two types:
1. Bhinnashtakavarga (BAV) - Individual planet's ashtakavarga
2. Sarvashtakavarga (SAV) - Combined ashtakavarga of all planets
"""

from typing import Dict, List
from src.jyotish.strength.friendships import relationship, get_combined_friendship
from src.utils.converters import degrees_to_sign, normalize_degrees


# Phase 5: Planets that have Ashtakavarga (excluding Rahu/Ketu)
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def get_planet_in_house(planet_degree: float, house_cusps: List[float], ascendant: float) -> int:
    """
    Determine which house a planet is in.
    
    Args:
        planet_degree: Planet's sidereal longitude
        house_cusps: List of house cusp longitudes
        ascendant: Ascendant longitude
    
    Returns:
        House number (1-12)
    """
    planet_degree = normalize_degrees(planet_degree)
    ascendant = normalize_degrees(ascendant)
    
    # Calculate relative position from ascendant
    relative_pos = normalize_degrees(planet_degree - ascendant)
    
    # Determine house (each house is 30 degrees)
    house = int(relative_pos / 30) + 1
    
    if house > 12:
        house = 1
    
    return house


def calculate_bhinnashtakavarga(
    planet: str,
    planet_degree: float,
    all_planets: Dict[str, float],
    house_cusps: List[float],
    ascendant: float
) -> List[int]:
    """
    Calculate Bhinnashtakavarga (BAV) for a specific planet.
    
    BAV shows which houses are favorable for a planet based on
    the positions of other planets relative to it.
    
    Args:
        planet: Planet name for which to calculate BAV
        planet_degree: Planet's sidereal longitude
        all_planets: Dictionary of all planet positions
        house_cusps: List of house cusp longitudes
        ascendant: Ascendant longitude
    
    Returns:
        List of 12 bindus (0-8) for each house
    """
    bav = [0] * 12
    
    # Get planet's sign
    planet_sign, _ = degrees_to_sign(planet_degree)
    
    # For each house
    for house_num in range(1, 13):
        # Calculate house cusp longitude
        if house_num == 1:
            house_cusp = ascendant
        else:
            house_cusp = house_cusps[house_num - 2] if house_num > 1 else ascendant
        
        house_sign, _ = degrees_to_sign(house_cusp)
        
        # Check each other planet's influence on this house
        for other_planet, other_degree in all_planets.items():
            if other_planet == planet or other_planet in ["Rahu", "Ketu"]:
                continue
            
            # Get other planet's sign
            other_sign, _ = degrees_to_sign(other_degree)
            
            # Determine relationship
            rel = get_combined_friendship(planet, other_planet, other_sign)
            
            # Calculate aspect from other planet to house
            aspect_angle = abs(normalize_degrees(other_degree - house_cusp))
            
            # Check if planet aspects the house
            # Major aspects: conjunction (0°), opposition (180°), trine (120°), square (90°)
            is_aspecting = (
                aspect_angle < 10 or
                abs(aspect_angle - 180) < 10 or
                abs(aspect_angle - 120) < 10 or
                abs(aspect_angle - 90) < 10
            )
            
            # If planet is in the house or aspects it
            other_house = get_planet_in_house(other_degree, house_cusps, ascendant)
            if other_house == house_num or is_aspecting:
                if rel == "friend":
                    bav[house_num - 1] += 1
                elif rel == "enemy":
                    # Enemies can reduce bindus (simplified)
                    pass
    
    return bav


def calculate_ashtakavarga(
    planet_positions: Dict[str, float],
    house_cusps: List[float],
    ascendant: float
) -> Dict:
    """
    Phase 5: Calculate complete Ashtakavarga (BAV + SAV).
    
    This function calculates:
    1. Bhinnashtakavarga (BAV) for each planet
    2. Sarvashtakavarga (SAV) - sum of all BAVs
    
    Args:
        planet_positions: Dictionary of planet sidereal longitudes
        house_cusps: List of house cusp longitudes
        ascendant: Ascendant longitude
    
    Returns:
        Dictionary with BAV and SAV data
    """
    bav = {}
    sav = [0] * 12
    
    # Calculate BAV for each planet
    for planet in PLANETS:
        if planet in planet_positions:
            planet_degree = planet_positions[planet]
            bav[planet] = calculate_bhinnashtakavarga(
                planet, planet_degree, planet_positions, house_cusps, ascendant
            )
            
            # Add to SAV
            for house in range(12):
                sav[house] += bav[planet][house]
    
    # Format SAV as house numbers
    sav_dict = {}
    for house in range(12):
        sav_dict[f"house_{house + 1}"] = sav[house]
    
    return {
        "BAV": bav,
        "SAV": sav_dict,
        "SAV_total": sum(sav),
        "SAV_average": round(sum(sav) / 12, 2)
    }

