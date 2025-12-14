"""
Phase 6: Advanced Raja Yoga Detection

This module provides enhanced Raja Yoga detection with multiple variations.
"""

from typing import Dict, List
from src.jyotish.yogas.house_yogas import get_house_lord, SIGN_LORDS


def detect_dharma_karmadhipati_yoga(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect Dharma-Karmadhipati Yoga.
    
    Condition: 9th house lord (Dharma) and 10th house lord (Karma) combine.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected Dharma-Karmadhipati Yogas
    """
    yogas = []
    
    # Get house lords
    house_lords = {}
    for house_data in houses:
        house_num = house_data.get("house", 0)
        house_sign = house_data.get("sign", 0)
        house_lords[house_num] = get_house_lord(house_sign)
    
    house9_lord = house_lords.get(9, "")
    house10_lord = house_lords.get(10, "")
    
    if house9_lord and house10_lord and house9_lord in planets and house10_lord in planets:
        # Check if lords are in each other's houses or aspect each other
        lord9_house = planets[house9_lord].get("house", 0)
        lord10_house = planets[house10_lord].get("house", 0)
        
        if lord9_house == 10 or lord10_house == 9:
            yogas.append({
                "name": "Dharma-Karmadhipati Yoga",
                "type": "Raja Yoga",
                "category": "Major",
                "description": "9th and 10th house lords combine - brings dharma and karma fulfillment"
            })
    
    return yogas


def detect_lakshmi_yoga(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect Lakshmi Yoga.
    
    Condition: 9th house lord in 11th house, or 11th house lord in 9th house.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected Lakshmi Yogas
    """
    yogas = []
    
    # Get house lords
    house_lords = {}
    for house_data in houses:
        house_num = house_data.get("house", 0)
        house_sign = house_data.get("sign", 0)
        house_lords[house_num] = get_house_lord(house_sign)
    
    house9_lord = house_lords.get(9, "")
    house11_lord = house_lords.get(11, "")
    
    if house9_lord and house11_lord and house9_lord in planets and house11_lord in planets:
        lord9_house = planets[house9_lord].get("house", 0)
        lord11_house = planets[house11_lord].get("house", 0)
        
        if lord9_house == 11 or lord11_house == 9:
            yogas.append({
                "name": "Lakshmi Yoga",
                "type": "Raja Yoga",
                "category": "Major",
                "description": "9th and 11th house lords combine - brings wealth and fortune"
            })
    
    return yogas


def detect_advanced_raja_yogas(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect advanced Raja Yogas.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected advanced Raja Yogas
    """
    yogas = []
    
    # Dharma-Karmadhipati Yoga
    yogas.extend(detect_dharma_karmadhipati_yoga(planets, houses))
    
    # Lakshmi Yoga
    yogas.extend(detect_lakshmi_yoga(planets, houses))
    
    return yogas

