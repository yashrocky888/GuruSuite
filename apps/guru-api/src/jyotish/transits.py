"""
Transit (Gochar) calculation module.

This module calculates planetary transits - where planets are currently
positioned relative to the birth chart.
"""

from typing import Dict, List
from datetime import datetime

from src.ephemeris.planets import calculate_planets_sidereal
from src.ephemeris.houses import calculate_houses_sidereal
from src.utils.timezone import local_to_utc
from src.utils.converters import normalize_degrees, calculate_aspect
from src.ephemeris.planets import get_planet_in_house


def calculate_transits(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str,
    transit_date: datetime = None
) -> Dict:
    """
    Calculate planetary transits for a given date.
    
    Transits show where planets are currently positioned and how they
    aspect the birth chart planets and houses.
    
    Args:
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
        transit_date: Date to calculate transits for (defaults to current date)
    
    Returns:
        Dictionary with transit data
    """
    if transit_date is None:
        transit_date = datetime.now()
    
    # Parse birth time
    hour, minute = map(int, birth_time.split(':'))
    birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    birth_datetime_utc = local_to_utc(birth_datetime, timezone)
    
    # Calculate birth chart
    birth_planets = calculate_planets_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    birth_houses = calculate_houses_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    
    # Calculate transit positions (use noon for transit date)
    transit_datetime = transit_date.replace(hour=12, minute=0, second=0, microsecond=0)
    transit_datetime_utc = local_to_utc(transit_datetime, timezone)
    
    transit_planets = calculate_planets_sidereal(transit_datetime_utc, birth_latitude, birth_longitude)
    
    # Calculate transit houses
    transit_houses = calculate_houses_sidereal(transit_datetime_utc, birth_latitude, birth_longitude)
    
    # Determine which birth house each transit planet is in
    birth_house_cusps = {key: data["longitude"] for key, data in birth_houses.items()}
    birth_house_cusps["ascendant"] = birth_houses["ascendant"]["longitude"]
    
    transit_data = {}
    
    for planet_name in transit_planets:
        transit_pos = transit_planets[planet_name]
        birth_pos = birth_planets.get(planet_name, {})
        
        # Calculate which birth house the transit planet is in
        transit_house = get_planet_in_house(transit_pos["longitude"], birth_house_cusps)
        
        # Calculate aspect to birth position
        if birth_pos:
            aspect_angle = calculate_aspect(
                transit_pos["longitude"],
                birth_pos.get("longitude", 0)
            )
        else:
            aspect_angle = None
        
        # Determine transit effect
        effect = determine_transit_effect(planet_name, transit_house, aspect_angle)
        
        transit_data[planet_name] = {
            "transit_longitude": transit_pos["longitude"],
            "transit_sign": transit_pos["sign_name"],
            "transit_house": transit_house,
            "birth_longitude": birth_pos.get("longitude"),
            "birth_sign": birth_pos.get("sign_name"),
            "aspect_angle": aspect_angle,
            "effect": effect,
            "description": get_transit_description(planet_name, transit_house, effect)
        }
    
    return {
        "transit_date": transit_date.isoformat(),
        "birth_date": birth_datetime.isoformat(),
        "transits": transit_data,
        "summary": {
            "favorable_transits": len([t for t in transit_data.values() if t["effect"] == "Favorable"]),
            "challenging_transits": len([t for t in transit_data.values() if t["effect"] == "Challenging"]),
            "neutral_transits": len([t for t in transit_data.values() if t["effect"] == "Neutral"])
        }
    }


def determine_transit_effect(
    planet_name: str,
    transit_house: int,
    aspect_angle: float = None
) -> str:
    """
    Determine the effect of a planet's transit.
    
    Args:
        planet_name: Name of the planet
        transit_house: House number where planet is transiting
        aspect_angle: Angle to birth position (if applicable)
    
    Returns:
        Effect description: "Favorable", "Challenging", or "Neutral"
    """
    # Benefic planets
    benefics = ["Venus", "Jupiter", "Mercury", "Moon"]
    # Malefic planets
    malefics = ["Mars", "Saturn", "Rahu", "Ketu", "Sun"]
    
    # Favorable houses for transits
    favorable_houses = [1, 2, 3, 4, 5, 9, 10, 11]
    # Challenging houses
    challenging_houses = [6, 8, 12]
    
    if planet_name in benefics:
        if transit_house in favorable_houses:
            return "Favorable"
        elif transit_house in challenging_houses:
            return "Challenging"
        else:
            return "Neutral"
    elif planet_name in malefics:
        if transit_house in challenging_houses:
            return "Challenging"
        elif transit_house in favorable_houses:
            return "Neutral"  # Malefics in good houses are less challenging
        else:
            return "Neutral"
    
    return "Neutral"


def get_transit_description(
    planet_name: str,
    transit_house: int,
    effect: str
) -> str:
    """
    Get a descriptive text for the transit.
    
    Args:
        planet_name: Name of the planet
        transit_house: House number
        effect: Effect type
    
    Returns:
        Description string
    """
    house_meanings = {
        1: "self, personality, health",
        2: "wealth, family, speech",
        3: "siblings, courage, communication",
        4: "mother, home, property",
        5: "children, creativity, education",
        6: "health, enemies, service",
        7: "spouse, partnerships, marriage",
        8: "longevity, transformation",
        9: "father, dharma, fortune",
        10: "career, reputation, status",
        11: "gains, income, friends",
        12: "losses, expenses, foreign lands"
    }
    
    house_meaning = house_meanings.get(transit_house, "unknown")
    
    if effect == "Favorable":
        return f"{planet_name} transiting {transit_house}th house ({house_meaning}) - favorable period"
    elif effect == "Challenging":
        return f"{planet_name} transiting {transit_house}th house ({house_meaning}) - challenging period"
    else:
        return f"{planet_name} transiting {transit_house}th house ({house_meaning}) - neutral period"

