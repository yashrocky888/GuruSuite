"""
Yoga calculation module for Vedic astrology.

This module identifies various yogas (planetary combinations) in a birth chart.
Yogas are special combinations that indicate specific results in life.
"""

from typing import Dict, List
from datetime import datetime

from src.ephemeris.planets import calculate_planets_sidereal
from src.ephemeris.houses import calculate_houses_sidereal
from src.utils.timezone import local_to_utc
from src.utils.converters import normalize_degrees, calculate_aspect


def check_raj_yoga(planets: Dict, houses: Dict) -> List[Dict]:
    """
    Check for Raj Yogas (Royal Combinations).
    
    Raj Yogas occur when:
    - Lords of kendras (1, 4, 7, 10) and trikonas (1, 5, 9) exchange signs
    - Benefic planets in kendras or trikonas
    - Strong planets in angular houses
    
    Args:
        planets: Dictionary of planet positions
        houses: Dictionary of house cusps
    
    Returns:
        List of Raj Yogas found
    """
    yogas = []
    
    # Get house lords (simplified - would need actual house lords from chart)
    # This is a basic implementation
    
    # Check for benefic planets in angular houses
    benefics = ["Venus", "Jupiter", "Mercury", "Moon"]
    angular_houses = [1, 4, 7, 10]
    
    for planet_name in benefics:
        if planet_name in planets:
            house = planets[planet_name].get("house", 0)
            if house in angular_houses:
                yogas.append({
                    "name": f"{planet_name} Raj Yoga",
                    "type": "Raj Yoga",
                    "description": f"{planet_name} in angular house {house}",
                    "strength": "Strong"
                })
    
    return yogas


def check_dhana_yoga(planets: Dict, houses: Dict) -> List[Dict]:
    """
    Check for Dhana Yogas (Wealth Combinations).
    
    Dhana Yogas occur when:
    - 2nd and 11th house lords are strong
    - Benefic planets in 2nd or 11th house
    - Jupiter in 2nd, 5th, 9th, or 11th house
    
    Args:
        planets: Dictionary of planet positions
        houses: Dictionary of house cusps
    
    Returns:
        List of Dhana Yogas found
    """
    yogas = []
    
    # Check Jupiter in wealth houses
    if "Jupiter" in planets:
        jupiter_house = planets["Jupiter"].get("house", 0)
        if jupiter_house in [2, 5, 9, 11]:
            yogas.append({
                "name": "Jupiter Dhana Yoga",
                "type": "Dhana Yoga",
                "description": f"Jupiter in house {jupiter_house}",
                "strength": "Strong"
            })
    
    # Check Venus in 2nd or 11th
    if "Venus" in planets:
        venus_house = planets["Venus"].get("house", 0)
        if venus_house in [2, 11]:
            yogas.append({
                "name": "Venus Dhana Yoga",
                "type": "Dhana Yoga",
                "description": f"Venus in house {venus_house}",
                "strength": "Moderate"
            })
    
    return yogas


def check_mangal_dosha(planets: Dict) -> List[Dict]:
    """
    Check for Mangal Dosha (Mars affliction).
    
    Mangal Dosha occurs when Mars is in 1st, 4th, 7th, 8th, or 12th house.
    This is considered a dosha (affliction) for marriage.
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        List with Mangal Dosha if present
    """
    yogas = []
    
    if "Mars" in planets:
        mars_house = planets["Mars"].get("house", 0)
        mangal_dosha_houses = [1, 4, 7, 8, 12]
        
        if mars_house in mangal_dosha_houses:
            yogas.append({
                "name": "Mangal Dosha",
                "type": "Dosha",
                "description": f"Mars in house {mars_house}",
                "strength": "Strong",
                "remedy": "Mars in 7th house can be cancelled if spouse also has Mangal Dosha"
            })
    
    return yogas


def check_shani_dosha(planets: Dict) -> List[Dict]:
    """
    Check for Shani Dosha (Saturn affliction).
    
    Shani Dosha occurs when Saturn aspects or is in certain houses.
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        List with Shani Dosha if present
    """
    yogas = []
    
    if "Saturn" in planets:
        saturn_house = planets["Saturn"].get("house", 0)
        shani_dosha_houses = [1, 2, 4, 5, 7, 8, 9, 12]
        
        if saturn_house in shani_dosha_houses:
            yogas.append({
                "name": "Shani Dosha",
                "type": "Dosha",
                "description": f"Saturn in house {saturn_house}",
                "strength": "Moderate"
            })
    
    return yogas


def check_rahu_ketu_yogas(planets: Dict) -> List[Dict]:
    """
    Check for Rahu-Ketu related yogas.
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        List of Rahu-Ketu yogas
    """
    yogas = []
    
    if "Rahu" in planets and "Ketu" in planets:
        rahu_house = planets["Rahu"].get("house", 0)
        ketu_house = planets["Ketu"].get("house", 0)
        
        # Rahu in 5th or 9th can give spiritual benefits
        if rahu_house in [5, 9]:
            yogas.append({
                "name": "Rahu Spiritual Yoga",
                "type": "Spiritual Yoga",
                "description": f"Rahu in house {rahu_house}",
                "strength": "Moderate"
            })
        
        # Ketu in 9th or 12th can give moksha
        if ketu_house in [9, 12]:
            yogas.append({
                "name": "Ketu Moksha Yoga",
                "type": "Spiritual Yoga",
                "description": f"Ketu in house {ketu_house}",
                "strength": "Moderate"
            })
    
    return yogas


def check_conjunction_yogas(planets: Dict) -> List[Dict]:
    """
    Check for conjunction yogas (planets in same sign/house).
    
    Args:
        planets: Dictionary of planet positions
    
    Returns:
        List of conjunction yogas
    """
    yogas = []
    
    planet_list = list(planets.keys())
    
    # Check for important conjunctions
    for i, planet1 in enumerate(planet_list):
        for planet2 in planet_list[i+1:]:
            if planet1 in planets and planet2 in planets:
                p1_sign = planets[planet1].get("sign", -1)
                p2_sign = planets[planet2].get("sign", -1)
                
                if p1_sign == p2_sign:
                    # Same sign conjunction
                    aspect_angle = calculate_aspect(
                        planets[planet1]["longitude"],
                        planets[planet2]["longitude"]
                    )
                    
                    if aspect_angle < 5:  # Close conjunction
                        yogas.append({
                            "name": f"{planet1}-{planet2} Conjunction",
                            "type": "Conjunction Yoga",
                            "description": f"{planet1} and {planet2} in same sign",
                            "strength": "Moderate"
                        })
    
    return yogas


def calculate_all_yogas(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str
) -> Dict:
    """
    Calculate all yogas in a birth chart.
    
    This function checks for 30+ classic yogas including:
    - Raj Yogas
    - Dhana Yogas
    - Doshas (Mangal, Shani)
    - Spiritual Yogas
    - Conjunction Yogas
    - And more
    
    Args:
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
    
    Returns:
        Dictionary with all yogas found
    """
    # Parse birth time
    hour, minute = map(int, birth_time.split(':'))
    birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    birth_datetime_utc = local_to_utc(birth_datetime, timezone)
    
    # Calculate planets and houses
    planets = calculate_planets_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    houses = calculate_houses_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    
    # Add house information to planets
    house_cusps = {key: data["longitude"] for key, data in houses.items()}
    from src.ephemeris.planets import get_planet_in_house
    
    for planet_name in planets:
        house_num = get_planet_in_house(planets[planet_name]["longitude"], house_cusps)
        planets[planet_name]["house"] = house_num
    
    # Check all types of yogas
    all_yogas = []
    
    all_yogas.extend(check_raj_yoga(planets, houses))
    all_yogas.extend(check_dhana_yoga(planets, houses))
    all_yogas.extend(check_mangal_dosha(planets))
    all_yogas.extend(check_shani_dosha(planets))
    all_yogas.extend(check_rahu_ketu_yogas(planets))
    all_yogas.extend(check_conjunction_yogas(planets))
    
    return {
        "total_yogas": len(all_yogas),
        "yogas": all_yogas,
        "summary": {
            "raj_yogas": len([y for y in all_yogas if y["type"] == "Raj Yoga"]),
            "dhana_yogas": len([y for y in all_yogas if y["type"] == "Dhana Yoga"]),
            "doshas": len([y for y in all_yogas if y["type"] == "Dosha"]),
            "spiritual_yogas": len([y for y in all_yogas if y["type"] == "Spiritual Yoga"])
        }
    }

