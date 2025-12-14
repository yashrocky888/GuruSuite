"""
Phase 6: House-Based Yogas

This module detects yogas based on house positions and house lord combinations.
"""

from typing import Dict, List, Tuple
from src.utils.converters import normalize_degrees, calculate_aspect


# Phase 6: Sign lords (natural zodiac)
SIGN_LORDS = {
    0: "Mars",    # Aries
    1: "Venus",   # Taurus
    2: "Mercury", # Gemini
    3: "Moon",    # Cancer
    4: "Sun",     # Leo
    5: "Mercury", # Virgo
    6: "Venus",   # Libra
    7: "Mars",    # Scorpio
    8: "Jupiter", # Sagittarius
    9: "Saturn",  # Capricorn
    10: "Saturn", # Aquarius
    11: "Jupiter" # Pisces
}

# Benefic planets
BENEFICS = ["Venus", "Jupiter", "Mercury", "Moon"]

# Malefic planets
MALEFICS = ["Mars", "Saturn", "Sun", "Rahu", "Ketu"]


def get_house_lord(house_sign: int) -> str:
    """
    Get the lord of a house based on its sign.
    
    Args:
        house_sign: Sign number (0-11)
    
    Returns:
        Planet name that rules the sign
    """
    return SIGN_LORDS.get(house_sign, "Unknown")


def detect_raja_yogas(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect Raja Yogas (Royal Combinations).
    
    Condition: Lords of Kendra (1, 4, 7, 10) and Trikona (1, 5, 9) exchange or combine.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected Raja Yogas
    """
    yogas = []
    
    # Get house lords
    house_lords = {}
    for house_data in houses:
        house_num = house_data.get("house", 0)
        house_sign = house_data.get("sign", 0)
        house_lords[house_num] = get_house_lord(house_sign)
    
    # Kendra houses: 1, 4, 7, 10
    # Trikona houses: 1, 5, 9
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]
    
    # Check for combinations
    for kendra_house in kendra_houses:
        kendra_lord = house_lords.get(kendra_house, "")
        if not kendra_lord or kendra_lord not in planets:
            continue
        
        for trikona_house in trikona_houses:
            if kendra_house == trikona_house:
                continue
            
            trikona_lord = house_lords.get(trikona_house, "")
            if not trikona_lord or trikona_lord not in planets:
                continue
            
            # Check if lords are in each other's houses or aspect each other
            kendra_lord_house = planets[kendra_lord].get("house", 0)
            trikona_lord_house = planets[trikona_lord].get("house", 0)
            
            if kendra_lord_house == trikona_house or trikona_lord_house == kendra_house:
                yogas.append({
                    "name": f"Raja Yoga ({kendra_lord}-{trikona_lord})",
                    "type": "House",
                    "category": "Major",
                    "description": f"Kendra lord {kendra_lord} and Trikona lord {trikona_lord} combination"
                })
    
    return yogas


def detect_dhana_yogas(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect Dhana Yogas (Wealth Combinations).
    
    Conditions:
    - 2nd and 11th house lords are strong
    - Benefic planets in 2nd or 11th house
    - Jupiter in 2nd, 5th, 9th, or 11th house
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected Dhana Yogas
    """
    yogas = []
    
    # Check Jupiter in wealth houses
    if "Jupiter" in planets:
        jupiter_house = planets["Jupiter"].get("house", 0)
        if jupiter_house in [2, 5, 9, 11]:
            yogas.append({
                "name": "Jupiter Dhana Yoga",
                "type": "House",
                "category": "Major",
                "description": f"Jupiter in house {jupiter_house} - brings wealth and prosperity"
            })
    
    # Check Venus in 2nd or 11th
    if "Venus" in planets:
        venus_house = planets["Venus"].get("house", 0)
        if venus_house in [2, 11]:
            yogas.append({
                "name": "Venus Dhana Yoga",
                "type": "House",
                "category": "Moderate",
                "description": f"Venus in house {venus_house} - brings material comforts"
            })
    
    # Check 2nd and 11th house lords
    house_lords = {}
    for house_data in houses:
        house_num = house_data.get("house", 0)
        house_sign = house_data.get("sign", 0)
        house_lords[house_num] = get_house_lord(house_sign)
    
    house2_lord = house_lords.get(2, "")
    house11_lord = house_lords.get(11, "")
    
    if house2_lord in BENEFICS and house11_lord in BENEFICS:
        yogas.append({
            "name": "Dhana Yoga (2nd-11th Lords)",
            "type": "House",
            "category": "Major",
            "description": "Benefic lords of 2nd and 11th houses - strong wealth combination"
        })
    
    return yogas


def detect_kemdrum_yoga(planets: Dict, houses: List[Dict]) -> bool:
    """
    Phase 6: Detect Kemdrum Yoga (Moon Isolation).
    
    Condition: Moon has no planets in 2nd and 12th houses from Moon.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        True if Kemdrum Yoga is present
    """
    if "Moon" not in planets:
        return False
    
    moon_house = planets["Moon"].get("house", 0)
    
    # Calculate 2nd and 12th houses from Moon
    house2_from_moon = (moon_house % 12) + 1
    house12_from_moon = ((moon_house - 2) % 12) + 1
    
    # Check if any planets are in these houses
    for planet_name, planet_data in planets.items():
        if planet_name == "Moon":
            continue
        
        planet_house = planet_data.get("house", 0)
        if planet_house == house2_from_moon or planet_house == house12_from_moon:
            return False  # Moon is not isolated
    
    return True  # Moon is isolated


def detect_shubha_kartari_yoga(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect Shubha Kartari Yoga (Benefic Hemming).
    
    Condition: Benefic planets on both sides of a house or planet.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected Shubha Kartari Yogas
    """
    yogas = []
    
    # Check for benefics hemming houses
    for house_data in houses:
        house_num = house_data.get("house", 0)
        
        # Get previous and next houses
        prev_house = ((house_num - 2) % 12) + 1
        next_house = (house_num % 12) + 1
        
        # Check planets in adjacent houses
        prev_house_planets = [p for p, data in planets.items() if data.get("house", 0) == prev_house]
        next_house_planets = [p for p, data in planets.items() if data.get("house", 0) == next_house]
        
        prev_benefics = [p for p in prev_house_planets if p in BENEFICS]
        next_benefics = [p for p in next_house_planets if p in BENEFICS]
        
        if len(prev_benefics) > 0 and len(next_benefics) > 0:
            yogas.append({
                "name": f"Shubha Kartari Yoga (House {house_num})",
                "type": "House",
                "category": "Moderate",
                "description": f"Benefics on both sides of house {house_num}"
            })
    
    return yogas


def detect_paap_kartari_yoga(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect Paap Kartari Yoga (Malefic Hemming).
    
    Condition: Malefic planets on both sides of a house or planet.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected Paap Kartari Yogas
    """
    yogas = []
    
    # Check for malefics hemming houses
    for house_data in houses:
        house_num = house_data.get("house", 0)
        
        # Get previous and next houses
        prev_house = ((house_num - 2) % 12) + 1
        next_house = (house_num % 12) + 1
        
        # Check planets in adjacent houses
        prev_house_planets = [p for p, data in planets.items() if data.get("house", 0) == prev_house]
        next_house_planets = [p for p, data in planets.items() if data.get("house", 0) == next_house]
        
        prev_malefics = [p for p in prev_house_planets if p in MALEFICS]
        next_malefics = [p for p in next_house_planets if p in MALEFICS]
        
        if len(prev_malefics) > 0 and len(next_malefics) > 0:
            yogas.append({
                "name": f"Paap Kartari Yoga (House {house_num})",
                "type": "House",
                "category": "Dosha",
                "description": f"Malefics on both sides of house {house_num} - creates obstacles"
            })
    
    return yogas


def detect_vipareeta_raja_yogas(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect Vipareeta Raja Yogas (Reverse Royal Combinations).
    
    Condition: Lords of 6, 8, 12 in each other's houses or placed together.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected Vipareeta Raja Yogas
    """
    yogas = []
    
    # Get house lords
    house_lords = {}
    for house_data in houses:
        house_num = house_data.get("house", 0)
        house_sign = house_data.get("sign", 0)
        house_lords[house_num] = get_house_lord(house_sign)
    
    # Houses 6, 8, 12
    vipareeta_houses = [6, 8, 12]
    
    for house1 in vipareeta_houses:
        lord1 = house_lords.get(house1, "")
        if not lord1 or lord1 not in planets:
            continue
        
        for house2 in vipareeta_houses:
            if house1 == house2:
                continue
            
            lord2 = house_lords.get(house2, "")
            if not lord2 or lord2 not in planets:
                continue
            
            # Check if lords are in each other's houses
            lord1_house = planets[lord1].get("house", 0)
            lord2_house = planets[lord2].get("house", 0)
            
            if lord1_house == house2 or lord2_house == house1:
                yogas.append({
                    "name": f"Vipareeta Raja Yoga ({lord1}-{lord2})",
                    "type": "House",
                    "category": "Major",
                    "description": f"Lords of houses {house1} and {house2} in each other's houses"
                })
    
    return yogas


def detect_house_yogas(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect all house-based yogas.
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of all detected house-based yogas
    """
    yogas = []
    
    # Raja Yogas
    yogas.extend(detect_raja_yogas(planets, houses))
    
    # Dhana Yogas
    yogas.extend(detect_dhana_yogas(planets, houses))
    
    # Kemdrum Yoga
    if detect_kemdrum_yoga(planets, houses):
        yogas.append({
            "name": "Kemdrum Yoga",
            "type": "House",
            "category": "Dosha",
            "description": "Moon isolated - no planets in 2nd and 12th from Moon"
        })
    
    # Shubha Kartari
    yogas.extend(detect_shubha_kartari_yoga(planets, houses))
    
    # Paap Kartari
    yogas.extend(detect_paap_kartari_yoga(planets, houses))
    
    # Vipareeta Raja Yogas
    yogas.extend(detect_vipareeta_raja_yogas(planets, houses))
    
    return yogas

