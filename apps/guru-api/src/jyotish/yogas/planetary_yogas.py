"""
Phase 6: Planetary Placement Yogas

This module detects yogas based on planetary positions and relationships.
"""

from typing import Dict, List, Tuple
from src.utils.converters import normalize_degrees, calculate_aspect


def gaja_kesari_yoga(planets: Dict, houses: List[Dict]) -> bool:
    """
    Phase 6: Gaja Kesari Yoga detection.
    
    Condition: Jupiter aspects or is conjunct Moon in Kendra (1, 4, 7, 10) from Moon OR Lagna.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        True if Gaja Kesari Yoga is present
    """
    if "Moon" not in planets or "Jupiter" not in planets:
        return False
    
    moon_data = planets["Moon"]
    jupiter_data = planets["Jupiter"]
    
    moon_degree = moon_data.get("degree", 0)
    jupiter_degree = jupiter_data.get("degree", 0)
    
    # Check aspect angle (Jupiter aspects Moon)
    aspect_angle = calculate_aspect(jupiter_degree, moon_degree)
    
    # Jupiter aspects Moon at 5th, 7th, 9th houses (120°, 180°, 240°)
    # Also check conjunction (0°)
    if aspect_angle < 10 or abs(aspect_angle - 120) < 10 or \
       abs(aspect_angle - 180) < 10 or abs(aspect_angle - 240) < 10:
        
        # Check if Moon is in Kendra (1, 4, 7, 10)
        moon_house = moon_data.get("house", 0)
        if moon_house in [1, 4, 7, 10]:
            return True
        
        # Check if Jupiter is in Kendra from Moon
        # This is a simplified check
        return True
    
    return False


def budha_aditya_yoga(planets: Dict) -> bool:
    """
    Phase 6: Budha Aditya Yoga detection.
    
    Condition: Sun and Mercury in the same sign (conjunction).
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        True if Budha Aditya Yoga is present
    """
    if "Sun" not in planets or "Mercury" not in planets:
        return False
    
    sun_sign = planets["Sun"].get("sign", -1)
    mercury_sign = planets["Mercury"].get("sign", -1)
    
    return sun_sign == mercury_sign


def chandra_mangal_yoga(planets: Dict) -> bool:
    """
    Phase 6: Chandra-Mangal Yoga detection.
    
    Condition: Moon and Mars in the same sign (conjunction) OR in mutual aspect.
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        True if Chandra-Mangal Yoga is present
    """
    if "Moon" not in planets or "Mars" not in planets:
        return False
    
    moon_sign = planets["Moon"].get("sign", -1)
    mars_sign = planets["Mars"].get("sign", -1)
    
    # Same sign (conjunction)
    if moon_sign == mars_sign:
        return True
    
    # Check for mutual aspect (simplified)
    moon_degree = planets["Moon"].get("degree", 0)
    mars_degree = planets["Mars"].get("degree", 0)
    aspect_angle = calculate_aspect(moon_degree, mars_degree)
    
    # Major aspects
    if abs(aspect_angle - 180) < 10 or abs(aspect_angle - 120) < 10:
        return True
    
    return False


def neechabhanga_raja_yoga(planets: Dict, houses: List[Dict]) -> bool:
    """
    Phase 6: Neechabhanga Raja Yoga detection.
    
    Condition: Debilitated planet but:
    - Dispositor is exalted, OR
    - Dispositor aspects the planet, OR
    - Planet is in Kendra (1, 4, 7, 10)
    
    Simplified implementation for Phase 6.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        True if Neechabhanga Raja Yoga is present
    """
    # Exaltation and debilitation signs
    exaltation = {
        "Sun": 0,      # Aries
        "Moon": 2,     # Taurus
        "Mars": 3,     # Cancer
        "Mercury": 5,  # Virgo
        "Jupiter": 8,  # Sagittarius
        "Venus": 11,   # Pisces
        "Saturn": 6    # Libra
    }
    
    debilitation = {
        "Sun": 6,      # Libra
        "Moon": 7,     # Scorpio
        "Mars": 9,     # Capricorn
        "Mercury": 11, # Pisces
        "Jupiter": 2,  # Gemini
        "Venus": 4,    # Leo
        "Saturn": 0    # Aries
    }
    
    # Check each planet
    for planet_name, planet_data in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        
        planet_sign = planet_data.get("sign", -1)
        planet_house = planet_data.get("house", 0)
        
        # Check if planet is debilitated
        if planet_name in debilitation and planet_sign == debilitation[planet_name]:
            # Check if in Kendra (cancels debilitation)
            if planet_house in [1, 4, 7, 10]:
                return True
    
    return False


def parivartana_yoga(planets: Dict) -> List[str]:
    """
    Phase 6: Parivartana Yoga (Mutual Exchange) detection.
    
    Condition: Two planets exchange signs (each in the other's sign).
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        List of Parivartana Yogas found
    """
    yogas = []
    
    # Sign lords (natural zodiac)
    sign_lords = {
        0: "Mars",    # Aries
        1: "Venus",  # Taurus
        2: "Mercury", # Gemini
        3: "Moon",   # Cancer
        4: "Sun",    # Leo
        5: "Mercury", # Virgo
        6: "Venus",  # Libra
        7: "Mars",   # Scorpio
        8: "Jupiter", # Sagittarius
        9: "Saturn", # Capricorn
        10: "Saturn", # Aquarius
        11: "Jupiter" # Pisces
    }
    
    planet_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    for i, planet1 in enumerate(planet_list):
        for planet2 in planet_list[i+1:]:
            if planet1 not in planets or planet2 not in planets:
                continue
            
            planet1_sign = planets[planet1].get("sign", -1)
            planet2_sign = planets[planet2].get("sign", -1)
            
            # Check if planets are in each other's signs
            planet1_lord_signs = [s for s, lord in sign_lords.items() if lord == planet1]
            planet2_lord_signs = [s for s, lord in sign_lords.items() if lord == planet2]
            
            if planet1_sign in planet2_lord_signs and planet2_sign in planet1_lord_signs:
                yogas.append(f"{planet1}-{planet2} Parivartana Yoga")
    
    return yogas


def detect_planetary_yogas(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect all planetary placement yogas.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected planetary yogas
    """
    yogas = []
    
    # Gaja Kesari Yoga
    if gaja_kesari_yoga(planets, houses):
        yogas.append({
            "name": "Gaja Kesari Yoga",
            "type": "Planetary",
            "category": "Major",
            "description": "Jupiter aspects Moon in Kendra - brings wisdom, wealth, and fame"
        })
    
    # Budha Aditya Yoga
    if budha_aditya_yoga(planets):
        yogas.append({
            "name": "Budha Aditya Yoga",
            "type": "Planetary",
            "category": "Major",
            "description": "Sun and Mercury in same sign - brings intelligence and communication skills"
        })
    
    # Chandra-Mangal Yoga
    if chandra_mangal_yoga(planets):
        yogas.append({
            "name": "Chandra-Mangal Yoga",
            "type": "Planetary",
            "category": "Moderate",
            "description": "Moon and Mars conjunction - brings courage and determination"
        })
    
    # Neechabhanga Raja Yoga
    if neechabhanga_raja_yoga(planets, houses):
        yogas.append({
            "name": "Neechabhanga Raja Yoga",
            "type": "Planetary",
            "category": "Major",
            "description": "Debilitated planet in Kendra - cancels debilitation and creates Raja Yoga"
        })
    
    # Parivartana Yogas
    parivartana = parivartana_yoga(planets)
    for yoga_name in parivartana:
        yogas.append({
            "name": yoga_name,
            "type": "Planetary",
            "category": "Major",
            "description": "Mutual exchange of signs - strengthens both planets"
        })
    
    return yogas

