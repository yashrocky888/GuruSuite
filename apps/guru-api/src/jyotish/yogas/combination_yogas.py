"""
Phase 6: Combination Yogas

This module detects complex yogas involving multiple planets and conditions.
"""

from typing import Dict, List
from src.utils.converters import calculate_aspect, normalize_degrees


# Benefic planets
BENEFICS = ["Venus", "Jupiter", "Mercury", "Moon"]

# Malefic planets
MALEFICS = ["Mars", "Saturn", "Sun", "Rahu", "Ketu"]


def detect_chatusagara_yoga(planets: Dict, houses: List[Dict]) -> bool:
    """
    Phase 6: Chatusagara Yoga detection.
    
    Condition: All four benefics (Venus, Jupiter, Mercury, Moon) in Kendra (1, 4, 7, 10).
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        True if Chatusagara Yoga is present
    """
    kendra_planets = []
    
    for planet_name, planet_data in planets.items():
        if planet_name in BENEFICS:
            planet_house = planet_data.get("house", 0)
            if planet_house in [1, 4, 7, 10]:
                kendra_planets.append(planet_name)
    
    # Check if all 4 benefics are in Kendra
    return len(kendra_planets) == 4


def detect_veshi_yoga(planets: Dict) -> bool:
    """
    Phase 6: Veshi Yoga detection.
    
    Condition: Planet in 2nd house from Moon.
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        True if Veshi Yoga is present
    """
    if "Moon" not in planets:
        return False
    
    moon_house = planets["Moon"].get("house", 0)
    house2_from_moon = (moon_house % 12) + 1
    
    # Check if any planet is in 2nd from Moon
    for planet_name, planet_data in planets.items():
        if planet_name == "Moon":
            continue
        if planet_data.get("house", 0) == house2_from_moon:
            return True
    
    return False


def detect_vashi_yoga(planets: Dict) -> bool:
    """
    Phase 6: Vashi Yoga detection.
    
    Condition: Planet in 12th house from Moon.
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        True if Vashi Yoga is present
    """
    if "Moon" not in planets:
        return False
    
    moon_house = planets["Moon"].get("house", 0)
    house12_from_moon = ((moon_house - 2) % 12) + 1
    
    # Check if any planet is in 12th from Moon
    for planet_name, planet_data in planets.items():
        if planet_name == "Moon":
            continue
        if planet_data.get("house", 0) == house12_from_moon:
            return True
    
    return False


def detect_anapha_yoga(planets: Dict) -> bool:
    """
    Phase 6: Anapha Yoga detection.
    
    Condition: Planet in 12th house from Moon (same as Vashi, but different interpretation).
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        True if Anapha Yoga is present
    """
    return detect_vashi_yoga(planets)


def detect_sunapha_yoga(planets: Dict) -> bool:
    """
    Phase 6: Sunapha Yoga detection.
    
    Condition: Planet in 2nd house from Moon (same as Veshi, but different interpretation).
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        True if Sunapha Yoga is present
    """
    return detect_veshi_yoga(planets)


def detect_durudhara_yoga(planets: Dict) -> bool:
    """
    Phase 6: Durudhara Yoga detection.
    
    Condition: Planets in both 2nd and 12th from Moon.
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        True if Durudhara Yoga is present
    """
    if "Moon" not in planets:
        return False
    
    moon_house = planets["Moon"].get("house", 0)
    house2_from_moon = (moon_house % 12) + 1
    house12_from_moon = ((moon_house - 2) % 12) + 1
    
    has_planet_in_2nd = False
    has_planet_in_12th = False
    
    for planet_name, planet_data in planets.items():
        if planet_name == "Moon":
            continue
        planet_house = planet_data.get("house", 0)
        if planet_house == house2_from_moon:
            has_planet_in_2nd = True
        if planet_house == house12_from_moon:
            has_planet_in_12th = True
    
    return has_planet_in_2nd and has_planet_in_12th


def detect_kalpadruma_yoga(planets: Dict, houses: List[Dict]) -> bool:
    """
    Phase 6: Kalpadruma Yoga detection.
    
    Condition: All planets in Kendra (1, 4, 7, 10) or Trikona (1, 5, 9).
    
    Simplified implementation.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        True if Kalpadruma Yoga is present
    """
    kendra_trikona_houses = [1, 4, 5, 7, 9, 10]
    
    planets_in_kendra_trikona = 0
    total_planets = 0
    
    for planet_name, planet_data in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        
        total_planets += 1
        planet_house = planet_data.get("house", 0)
        if planet_house in kendra_trikona_houses:
            planets_in_kendra_trikona += 1
    
    # If most planets are in Kendra/Trikona
    return planets_in_kendra_trikona >= (total_planets * 0.7)


def detect_sanyasa_yoga(planets: Dict, houses: List[Dict]) -> bool:
    """
    Phase 6: Sanyasa Yoga detection.
    
    Condition: All planets in 3rd, 6th, 9th, or 12th houses (Dusthana).
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        True if Sanyasa Yoga is present
    """
    dusthana_houses = [3, 6, 9, 12]
    
    planets_in_dusthana = 0
    total_planets = 0
    
    for planet_name, planet_data in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        
        total_planets += 1
        planet_house = planet_data.get("house", 0)
        if planet_house in dusthana_houses:
            planets_in_dusthana += 1
    
    # If most planets are in Dusthana
    return planets_in_dusthana >= (total_planets * 0.7)


def detect_combination_yogas(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect all combination yogas.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected combination yogas
    """
    yogas = []
    
    # Chatusagara Yoga
    if detect_chatusagara_yoga(planets, houses):
        yogas.append({
            "name": "Chatusagara Yoga",
            "type": "Combination",
            "category": "Major",
            "description": "All four benefics in Kendra - brings great fortune"
        })
    
    # Veshi Yoga
    if detect_veshi_yoga(planets):
        yogas.append({
            "name": "Veshi Yoga",
            "type": "Combination",
            "category": "Moderate",
            "description": "Planet in 2nd house from Moon"
        })
    
    # Vashi Yoga
    if detect_vashi_yoga(planets):
        yogas.append({
            "name": "Vashi Yoga",
            "type": "Combination",
            "category": "Moderate",
            "description": "Planet in 12th house from Moon"
        })
    
    # Anapha Yoga
    if detect_anapha_yoga(planets):
        yogas.append({
            "name": "Anapha Yoga",
            "type": "Combination",
            "category": "Moderate",
            "description": "Planet in 12th house from Moon"
        })
    
    # Sunapha Yoga
    if detect_sunapha_yoga(planets):
        yogas.append({
            "name": "Sunapha Yoga",
            "type": "Combination",
            "category": "Moderate",
            "description": "Planet in 2nd house from Moon"
        })
    
    # Durudhara Yoga
    if detect_durudhara_yoga(planets):
        yogas.append({
            "name": "Durudhara Yoga",
            "type": "Combination",
            "category": "Moderate",
            "description": "Planets in both 2nd and 12th from Moon"
        })
    
    # Kalpadruma Yoga
    if detect_kalpadruma_yoga(planets, houses):
        yogas.append({
            "name": "Kalpadruma Yoga",
            "type": "Combination",
            "category": "Major",
            "description": "Most planets in Kendra or Trikona - brings fulfillment of desires"
        })
    
    # Sanyasa Yoga
    if detect_sanyasa_yoga(planets, houses):
        yogas.append({
            "name": "Sanyasa Yoga",
            "type": "Combination",
            "category": "Moderate",
            "description": "Most planets in Dusthana - indicates spiritual inclination"
        })
    
    return yogas

