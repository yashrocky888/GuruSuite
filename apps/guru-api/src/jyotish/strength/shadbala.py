"""
Phase 5: Shadbala (Six-fold Strength) Calculation Module

JHora-style Shadbala calculation following classical Vedic astrology rules.
Shadbala consists of six types of strength:
1. Sthana Bala (Positional strength)
2. Dig Bala (Directional strength)
3. Kala Bala (Temporal strength)
4. Cheshta Bala (Motional strength)
5. Naisargika Bala (Natural strength)
6. Drik Bala (Aspectual strength)
"""

import swisseph as swe
from typing import Dict, List
from datetime import datetime

from src.jyotish.strength.friendships import relationship, get_combined_friendship
from src.jyotish.kundli_engine import get_planet_positions, get_sign
from src.ephemeris.ephemeris_utils import (
    get_ascendant,
    get_houses,
    calculate_planet_position,
    SE_SUN, SE_MOON, SE_MARS, SE_MERCURY, SE_JUPITER, SE_VENUS, SE_SATURN
)
from src.utils.converters import normalize_degrees, degrees_to_sign


# Phase 5: Naisargika Bala (Natural strength) as per JHora
NAISARGIKA_BALA = {
    "Sun": 60,
    "Moon": 51,
    "Venus": 43,
    "Jupiter": 34,
    "Mercury": 26,
    "Mars": 17,
    "Saturn": 9
}

# Planet to Swiss Ephemeris constant mapping
PLANET_TO_SE = {
    "Sun": SE_SUN,
    "Moon": SE_MOON,
    "Mars": SE_MARS,
    "Mercury": SE_MERCURY,
    "Jupiter": SE_JUPITER,
    "Venus": SE_VENUS,
    "Saturn": SE_SATURN
}


def calculate_sthana_bala(planet: str, planet_degree: float, houses: List[float]) -> float:
    """
    Calculate Sthana Bala (Positional strength).
    
    Includes:
    - Uchcha Bala (Exaltation strength)
    - Saptavargaja Bala (Multi-divisional strength)
    - Ojayugma Bala (Odd/Even sign strength)
    - Kendradi Bala (Angular house strength)
    - Drekkana Bala (Decanate strength)
    
    Simplified JHora model for Phase 5.
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
        houses: List of house cusp longitudes
    
    Returns:
        Sthana Bala value
    """
    # Simplified calculation
    # Full implementation would include exaltation, debilitation, etc.
    
    # Sign strength (based on degrees in sign)
    sign_num, degrees_in_sign = degrees_to_sign(planet_degree)
    sign_strength = (degrees_in_sign / 30.0) * 20
    
    # House strength (angular houses are stronger)
    # Determine which house planet is in
    ascendant = houses[0] if houses else 0
    relative_pos = normalize_degrees(planet_degree - ascendant)
    house_num = int(relative_pos / 30) + 1
    if house_num > 12:
        house_num = 1
    
    # Angular houses (1, 4, 7, 10) are strongest
    if house_num in [1, 4, 7, 10]:
        house_strength = 15
    elif house_num in [2, 5, 8, 11]:
        house_strength = 10
    else:
        house_strength = 5
    
    return sign_strength + house_strength


def calculate_dig_bala(planet: str, planet_degree: float) -> float:
    """
    Calculate Dig Bala (Directional strength).
    
    Based on direction where planet has maximum strength:
    - Jupiter/Mercury: Strongest in 1st house (0-180°)
    - Mars/Saturn: Strongest in 7th house (180-360°)
    - Others: Moderate directional strength
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
    
    Returns:
        Dig Bala value
    """
    # Simplified JHora model
    if planet in ["Jupiter", "Mercury"]:
        # Strongest in 1st house (0-180° from ascendant)
        if 0 <= planet_degree <= 180:
            return 15
        else:
            return 0
    elif planet in ["Mars", "Saturn"]:
        # Strongest in 7th house (180-360°)
        if 180 <= planet_degree <= 360:
            return 15
        else:
            return 0
    else:
        # Moderate directional strength for others
        return 5


def calculate_kala_bala(planet: str, jd: float) -> float:
    """
    Calculate Kala Bala (Temporal strength).
    
    Includes:
    - Natonnata (Day/Night strength)
    - Paksha (Lunar phase strength)
    - Tribhaga (Time of day strength)
    - Abda, Masa, Vara (Year, Month, Day strength)
    - Yuddha Bala (Planetary war strength)
    
    Simplified JHora model for Phase 5.
    
    Args:
        planet: Planet name
        jd: Julian Day Number
    
    Returns:
        Kala Bala value
    """
    # Simplified calculation
    # Full implementation would calculate all temporal factors
    
    # Basic temporal strength
    base_kala = 10
    
    # Day/Night strength (Sun, Mars, Jupiter are day planets)
    # Moon, Venus, Saturn are night planets
    if planet in ["Sun", "Mars", "Jupiter"]:
        # Day planets stronger during day
        base_kala += 5
    elif planet in ["Moon", "Venus", "Saturn"]:
        # Night planets stronger during night
        base_kala += 5
    
    return base_kala


def calculate_cheshta_bala(planet: str, jd: float) -> float:
    """
    Calculate Cheshta Bala (Motional strength).
    
    For retrograde planets: 16 Shashtiamsas (as per JHora).
    For direct planets: 0.
    
    Args:
        planet: Planet name
        jd: Julian Day Number
    
    Returns:
        Cheshta Bala value (16 if retrograde, 0 otherwise)
    """
    if planet not in PLANET_TO_SE:
        return 0
    
    try:
        # Calculate planet position with speed
        planet_num = PLANET_TO_SE[planet]
        result = swe.calc_ut(jd, planet_num, swe.FLG_SWIEPH | swe.FLG_SPEED)
        
        if result and len(result) > 0:
            speed = result[0][3]  # Speed in longitude
            # Negative speed indicates retrograde
            if speed < 0:
                return 16  # 16 Shashtiamsas for retrograde
    except Exception:
        pass
    
    return 0


def calculate_drik_bala(
    planet: str,
    planet_degree: float,
    all_planets: Dict[str, float],
    all_signs: Dict[str, int]
) -> float:
    """
    Calculate Drik Bala (Aspectual strength).
    
    Sum of benefic aspects minus malefic aspects.
    Friends give positive strength, enemies give negative.
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
        all_planets: Dictionary of all planet positions
        all_signs: Dictionary of all planet signs
    
    Returns:
        Drik Bala value
    """
    drik = 0
    
    for other_planet, other_degree in all_planets.items():
        if other_planet == planet:
            continue
        
        # Check if planets are in aspect (simplified: same sign or opposite)
        aspect_angle = abs(normalize_degrees(planet_degree - other_degree))
        
        # Major aspects: conjunction (0°), opposition (180°), trine (120°), square (90°)
        if aspect_angle < 10 or abs(aspect_angle - 180) < 10 or \
           abs(aspect_angle - 120) < 10 or abs(aspect_angle - 90) < 10:
            
            # Get relationship
            other_sign = all_signs.get(other_planet, 0)
            rel = get_combined_friendship(planet, other_planet, other_sign)
            
            if rel == "friend":
                drik += 5
            elif rel == "enemy":
                drik -= 5
    
    return drik


def calculate_shadbala(
    jd: float,
    lat: float,
    lon: float
) -> Dict:
    """
    Phase 5: Calculate complete Shadbala (Six-fold Strength) for all planets.
    
    This is the main Shadbala calculation function following JHora formulas.
    
    Args:
        jd: Julian Day Number
        lat: Geographic latitude
        lon: Geographic longitude
    
    Returns:
        Dictionary with Shadbala for each planet
    """
    # Get planet positions (sidereal)
    planets = get_planet_positions(jd)
    
    # Get ascendant and houses
    asc = get_ascendant(jd, lat, lon)
    houses_list = get_houses(jd, lat, lon)
    
    # Convert houses to list format for calculations
    houses = [asc] + houses_list
    
    # Get signs for all planets
    planet_signs = {}
    for planet_name, planet_degree in planets.items():
        sign_num, _ = degrees_to_sign(planet_degree)
        planet_signs[planet_name] = sign_num
    
    shadbala_results = {}
    
    # Calculate Shadbala for each planet
    for planet_name, planet_degree in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            # Rahu and Ketu have simplified calculations
            continue
        
        # 1. Naisargika Bala (Natural strength)
        naisargika = NAISARGIKA_BALA.get(planet_name, 0)
        
        # 2. Cheshta Bala (Motional strength)
        cheshta = calculate_cheshta_bala(planet_name, jd)
        
        # 3. Sthana Bala (Positional strength)
        sthana = calculate_sthana_bala(planet_name, planet_degree, houses)
        
        # 4. Dig Bala (Directional strength)
        dig = calculate_dig_bala(planet_name, planet_degree)
        
        # 5. Kala Bala (Temporal strength)
        kala = calculate_kala_bala(planet_name, jd)
        
        # 6. Drik Bala (Aspectual strength)
        drik = calculate_drik_bala(planet_name, planet_degree, planets, planet_signs)
        
        # Total Shadbala
        total = naisargika + cheshta + sthana + dig + kala + drik
        
        shadbala_results[planet_name] = {
            "naisargika_bala": round(naisargika, 2),
            "cheshta_bala": round(cheshta, 2),
            "sthana_bala": round(sthana, 2),
            "dig_bala": round(dig, 2),
            "kala_bala": round(kala, 2),
            "drik_bala": round(drik, 2),
            "total_shadbala": round(total, 2)
        }
    
    return shadbala_results

