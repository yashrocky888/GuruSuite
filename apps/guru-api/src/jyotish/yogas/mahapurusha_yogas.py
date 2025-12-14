"""
Phase 6: Panch Mahapurusha Yogas

This module detects the five great person yogas:
- Ruchaka (Mars)
- Bhadra (Mercury)
- Hamsa (Jupiter)
- Malavya (Venus)
- Sasa (Saturn)
"""

from typing import Dict, List


# Phase 6: Own signs for each planet
OWN_SIGNS = {
    "Mars": [0, 7],      # Aries, Scorpio
    "Mercury": [2, 5],   # Gemini, Virgo
    "Jupiter": [8, 11],  # Sagittarius, Pisces
    "Venus": [1, 6],     # Taurus, Libra
    "Saturn": [9, 10]    # Capricorn, Aquarius
}

# Phase 6: Exaltation signs
EXALTATION_SIGNS = {
    "Mars": 3,      # Cancer
    "Mercury": 5,   # Virgo
    "Jupiter": 8,   # Sagittarius
    "Venus": 11,    # Pisces
    "Saturn": 6     # Libra
}


def detect_mahapurusha_yogas(planets: Dict, houses: List[Dict]) -> List[Dict]:
    """
    Phase 6: Detect Panch Mahapurusha Yogas.
    
    Condition: Planet in own or exalted sign in Kendra (1, 4, 7, 10).
    
    Panch Mahapurusha Yogas:
    - Mars in own/exalted sign in Kendra → Ruchaka Yoga
    - Mercury in own/exalted sign in Kendra → Bhadra Yoga
    - Jupiter in own/exalted sign in Kendra → Hamsa Yoga
    - Venus in own/exalted sign in Kendra → Malavya Yoga
    - Saturn in own/exalted sign in Kendra → Sasa Yoga
    
    Args:
        planets: Dictionary of planet positions
        houses: List of house data
    
    Returns:
        List of detected Mahapurusha Yogas
    """
    yogas = []
    
    mahapurusha_planets = {
        "Mars": "Ruchaka",
        "Mercury": "Bhadra",
        "Jupiter": "Hamsa",
        "Venus": "Malavya",
        "Saturn": "Sasa"
    }
    
    for planet_name, yoga_name in mahapurusha_planets.items():
        if planet_name not in planets:
            continue
        
        planet_data = planets[planet_name]
        planet_sign = planet_data.get("sign", -1)
        planet_house = planet_data.get("house", 0)
        
        # Check if planet is in Kendra (1, 4, 7, 10)
        if planet_house not in [1, 4, 7, 10]:
            continue
        
        # Check if planet is in own sign
        own_signs = OWN_SIGNS.get(planet_name, [])
        is_own_sign = planet_sign in own_signs
        
        # Check if planet is in exaltation sign
        exaltation_sign = EXALTATION_SIGNS.get(planet_name, -1)
        is_exalted = planet_sign == exaltation_sign
        
        if is_own_sign or is_exalted:
            yogas.append({
                "name": f"{yoga_name} Yoga",
                "type": "Mahapurusha",
                "category": "Major",
                "planet": planet_name,
                "sign": planet_sign,
                "house": planet_house,
                "description": f"{planet_name} in own/exalted sign in Kendra - brings great qualities"
            })
    
    return yogas

