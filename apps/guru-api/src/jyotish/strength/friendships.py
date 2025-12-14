"""
Planetary friendship relationships module.

Phase 5: Natural and temporary friendships as per classical Vedic texts.
Used for Shadbala and Ashtakavarga calculations.
"""

from typing import Dict, List


# Phase 5: Natural friendships as per classical texts
NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"]
}

# Phase 5: Natural enemies as per classical texts
NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],  # Moon has no natural enemies
    "Mars": ["Mercury"],
    "Mercury": ["Mars"],
    "Jupiter": ["Venus", "Mercury"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon"]
}

# Phase 5: Neutral relationships (neither friend nor enemy)
NATURAL_NEUTRAL = {
    "Sun": ["Mercury"],
    "Moon": ["Mars", "Jupiter", "Venus", "Saturn"],
    "Mars": ["Venus", "Saturn"],
    "Mercury": ["Moon", "Jupiter", "Saturn"],
    "Jupiter": ["Venus", "Saturn"],
    "Venus": ["Mars", "Jupiter"],
    "Saturn": ["Mars", "Jupiter"]
}


def relationship(planet: str, other: str) -> str:
    """
    Determine relationship between two planets.
    
    Args:
        planet: First planet name
        other: Second planet name
    
    Returns:
        Relationship: "friend", "enemy", or "neutral"
    """
    if planet not in NATURAL_FRIENDS:
        return "neutral"
    
    if other in NATURAL_FRIENDS.get(planet, []):
        return "friend"
    elif other in NATURAL_ENEMIES.get(planet, []):
        return "enemy"
    else:
        return "neutral"


def get_temporary_friendship(planet: str, other_planet: str, other_sign: int) -> str:
    """
    Calculate temporary friendship based on sign position.
    
    Temporary friendship overrides natural friendship when a planet
    is in a sign owned by another planet.
    
    Args:
        planet: Planet name
        other_planet: Other planet name
        other_sign: Sign number (0-11) where other planet is placed
    
    Returns:
        Temporary relationship: "friend", "enemy", or "neutral"
    """
    # Sign lords (natural zodiac)
    sign_lords = {
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
    
    sign_lord = sign_lords.get(other_sign, "")
    
    # If other planet is in its own sign or friend's sign, it's a friend
    if other_planet == sign_lord:
        return "friend"
    elif sign_lord in NATURAL_FRIENDS.get(planet, []):
        return "friend"
    elif sign_lord in NATURAL_ENEMIES.get(planet, []):
        return "enemy"
    else:
        return relationship(planet, other_planet)


def get_combined_friendship(
    planet: str,
    other_planet: str,
    other_sign: int
) -> str:
    """
    Get combined friendship (natural + temporary).
    
    JHora formula: Temporary friendship can override natural.
    
    Args:
        planet: Planet name
        other_planet: Other planet name
        other_sign: Sign number where other planet is placed
    
    Returns:
        Combined relationship: "friend", "enemy", or "neutral"
    """
    natural = relationship(planet, other_planet)
    temporary = get_temporary_friendship(planet, other_planet, other_sign)
    
    # Temporary friendship can override natural
    if temporary == "friend" and natural == "enemy":
        return "friend"
    elif temporary == "enemy" and natural == "friend":
        return "enemy"
    else:
        return natural

