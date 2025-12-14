"""
Phase 7: Planetary Aspects (Graha Drishti) Calculation

This module calculates planetary aspects following JHora-style rules.
"""

from typing import Dict
from src.utils.converters import normalize_degrees


def aspect_points(planet: str, planet_degree: float, other_degree: float) -> int:
    """
    Phase 7: Calculate aspect points between two planets.
    
    Following JHora-style Graha Drishti rules:
    - All planets have 7th house aspect (180°) = 5 points
    - Jupiter aspects 5th (150°) and 9th (210°) = 4 points each
    - Saturn aspects 3rd (90°) and 10th (300°) = 4 points each
    - Mars aspects 4th (120°) and 8th (240°) = 4 points each
    
    Args:
        planet: Planet name doing the aspecting
        planet_degree: Degree of the aspecting planet
        other_degree: Degree of the planet being aspected
    
    Returns:
        Aspect points (0-5)
    """
    diff = abs(normalize_degrees(other_degree - planet_degree))
    
    # 7th house aspect (180°) - all planets
    if abs(diff - 180) < 5:
        return 5
    
    # Jupiter aspects 5th (150°) and 9th (210°)
    if planet == "Jupiter":
        if abs(diff - 150) < 5 or abs(diff - 210) < 5:
            return 4
    
    # Saturn aspects 3rd (90°) and 10th (300°)
    if planet == "Saturn":
        if abs(diff - 90) < 5 or abs(diff - 300) < 5:
            return 4
    
    # Mars aspects 4th (120°) and 8th (240°)
    if planet == "Mars":
        if abs(diff - 120) < 5 or abs(diff - 240) < 5:
            return 4
    
    return 0


def get_planet_aspects(planet: str, planet_degree: float, all_planets: Dict[str, float]) -> Dict[str, int]:
    """
    Phase 7: Get all aspects for a planet.
    
    Args:
        planet: Planet name
        planet_degree: Planet's degree
        all_planets: Dictionary of all planet degrees
    
    Returns:
        Dictionary of aspect points for each planet
    """
    aspects = {}
    
    for other_planet, other_degree in all_planets.items():
        if other_planet == planet:
            continue
        
        points = aspect_points(planet, planet_degree, other_degree)
        if points > 0:
            aspects[other_planet] = points
    
    return aspects


def calculate_aspect_strength(aspects: Dict[str, int], benefics: list, malefics: list) -> Dict:
    """
    Phase 7: Calculate benefic/malefic aspect strength.
    
    Args:
        aspects: Dictionary of aspect points
        benefics: List of benefic planets
        malefics: List of malefic planets
    
    Returns:
        Dictionary with benefic and malefic strength
    """
    benefic_strength = sum(aspects.get(p, 0) for p in benefics)
    malefic_strength = sum(aspects.get(p, 0) for p in malefics)
    
    return {
        "benefic_strength": benefic_strength,
        "malefic_strength": malefic_strength,
        "net_strength": benefic_strength - malefic_strength
    }

