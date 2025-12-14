"""
Kundli (Birth Chart) calculation module.

This module provides functions to calculate the main birth chart (D1)
including planets, houses, and their relationships.
"""

from typing import Dict, List
from datetime import datetime

from src.ephemeris.planets import calculate_planets_sidereal, get_planet_in_house
from src.ephemeris.houses import calculate_houses_sidereal, get_house_lord
from src.utils.timezone import local_to_utc


def calculate_kundli(
    name: str,
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    birth_place: str,
    timezone: str
) -> Dict:
    """
    Calculate complete kundli (birth chart) D1.
    
    This is the main birth chart showing:
    - Planet positions in signs and houses
    - House cusps
    - Planetary aspects and relationships
    
    Args:
        name: Name of the person
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        birth_place: Birth place name
        timezone: Timezone string
    
    Returns:
        Complete kundli data dictionary
    """
    # Parse birth time
    hour, minute = map(int, birth_time.split(':'))
    birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Convert to UTC
    birth_datetime_utc = local_to_utc(birth_datetime, timezone)
    
    # Calculate planets
    planets = calculate_planets_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    
    # Calculate houses
    houses = calculate_houses_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    
    # Determine which house each planet is in
    house_cusps = {key: data["longitude"] for key, data in houses.items()}
    house_cusps["ascendant"] = houses["ascendant"]["longitude"]
    
    planets_in_houses = {}
    for planet_name, planet_data in planets.items():
        house_num = get_planet_in_house(planet_data["longitude"], house_cusps)
        planets_in_houses[planet_name] = {
            **planet_data,
            "house": house_num,
            "house_lord": get_house_lord(house_num)
        }
    
    # Build complete kundli response
    kundli = {
        "name": name,
        "birth_details": {
            "date": birth_datetime.isoformat(),
            "time": birth_time,
            "place": birth_place,
            "latitude": birth_latitude,
            "longitude": birth_longitude,
            "timezone": timezone
        },
        "ascendant": {
            "longitude": houses["ascendant"]["longitude"],
            "sign": houses["ascendant"]["sign"],
            "sign_name": houses["ascendant"]["sign_name"],
            "degrees": houses["ascendant"]["degrees_in_sign"]
        },
        "planets": planets_in_houses,
        "houses": houses,
        "chart_type": "D1 (Rashi Chart)"
    }
    
    return kundli


def get_planet_strength(planet_data: Dict, house_data: Dict) -> str:
    """
    Determine planet strength based on house position.
    
    In Vedic astrology:
    - Own sign: Very strong
    - Exalted: Very strong
    - Mooltrikona: Strong
    - Friendly sign: Moderate
    - Neutral sign: Moderate
    - Enemy sign: Weak
    - Debilitated: Very weak
    
    Args:
        planet_data: Planet position data
        house_data: House data
    
    Returns:
        Strength description
    """
    # Simplified strength calculation
    # Full implementation would check exaltation, debilitation, etc.
    house_num = planet_data.get("house", 0)
    
    # Angular houses (1, 4, 7, 10) are strong
    if house_num in [1, 4, 7, 10]:
        return "Strong"
    # Succedent houses (2, 5, 8, 11) are moderate
    elif house_num in [2, 5, 8, 11]:
        return "Moderate"
    # Cadent houses (3, 6, 9, 12) are weak
    else:
        return "Weak"

