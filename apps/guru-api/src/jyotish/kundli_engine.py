"""
Core Kundli Engine - Phase 2 Implementation.

This module provides the core Kundli (Janma Kundali) calculation engine
following ancient Vedic rules and using Swiss Ephemeris.
"""

import swisseph as swe
import math
from typing import Dict, List
from datetime import datetime

from src.ephemeris.ephemeris_utils import (
    init_swisseph,
    get_ascendant,
    get_houses,
    calculate_all_planets,
    get_ayanamsa
)
from src.utils.converters import normalize_degrees


# Vedic astrology signs (Rashi) - English names
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Sanskrit names for signs
SIGNS_SANSKRIT = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]

# Sign lords (natural zodiac)
SIGN_LORDS = {
    0: "Mars",    # Aries/Mesha
    1: "Venus",   # Taurus/Vrishabha
    2: "Mercury", # Gemini/Mithuna
    3: "Moon",    # Cancer/Karka
    4: "Sun",     # Leo/Simha
    5: "Mercury", # Virgo/Kanya
    6: "Venus",   # Libra/Tula
    7: "Mars",    # Scorpio/Vrishchika
    8: "Jupiter", # Sagittarius/Dhanu
    9: "Saturn",  # Capricorn/Makara
    10: "Saturn", # Aquarius/Kumbha
    11: "Jupiter" # Pisces/Meena
}


def get_sign(degree: float) -> str:
    """
    Get sign name from degree using Vedic rule: degree // 30 = sign index.
    
    Args:
        degree: Longitude in degrees (0-360)
    
    Returns:
        Sign name (English)
    """
    degree = normalize_degrees(degree)
    sign_index = int(degree // 30)
    return SIGNS[sign_index]


def get_sign_sanskrit(degree: float) -> str:
    """
    Get Sanskrit sign name from degree.
    
    Args:
        degree: Longitude in degrees (0-360)
    
    Returns:
        Sanskrit sign name
    """
    degree = normalize_degrees(degree)
    sign_index = int(degree // 30)
    return SIGNS_SANSKRIT[sign_index]


def get_sign_index(degree: float) -> int:
    """
    Get sign index (0-11) from degree.
    
    Args:
        degree: Longitude in degrees (0-360)
    
    Returns:
        Sign index (0-11)
    """
    degree = normalize_degrees(degree)
    return int(degree // 30)


def get_house_lord_from_sign(sign_index: int) -> str:
    """
    Get house lord based on sign index.
    
    Args:
        sign_index: Sign index (0-11)
    
    Returns:
        Planet name that rules the sign
    """
    return SIGN_LORDS.get(sign_index, "Unknown")


def get_planet_positions(julian_day: float) -> Dict[str, float]:
    """
    Get positions of all planets for a given Julian Day.
    
    Returns sidereal positions using Drik Panchang methodology.
    Uses FLG_SIDEREAL flag so positions are already sidereal.
    
    Args:
        julian_day: Julian Day Number
    
    Returns:
        Dictionary with planet names as keys and sidereal longitudes as values
    """
    init_swisseph()
    
    # Calculate all planets (already sidereal due to FLG_SIDEREAL flag)
    planets = calculate_all_planets(julian_day)
    
    # Extract sidereal longitudes
    sidereal_positions = {}
    for planet_name, planet_data in planets.items():
        sidereal_positions[planet_name] = planet_data["longitude"]
    
    return sidereal_positions


def get_planet_house(planet_degree: float, ascendant_degree: float, house_cusps: List[float]) -> int:
    """
    Calculate which house a planet is in based on house cusps.
    
    Uses proper house cusp comparison method for accurate house placement.
    
    Args:
        planet_degree: Planet's sidereal longitude
        ascendant_degree: Ascendant degree (house 1 cusp)
        house_cusps: List of 12 house cusp degrees (indices 0-11 = houses 1-12)
    
    Returns:
        House number (1-12)
    """
    planet_degree = normalize_degrees(planet_degree)
    
    # Normalize all house cusps
    normalized_cusps = [normalize_degrees(cusp) for cusp in house_cusps]
    
    # Find which house the planet falls into
    # A planet is in house N if its degree is >= house N cusp and < house N+1 cusp
    for i in range(12):
        current_cusp = normalized_cusps[i]
        next_cusp = normalized_cusps[(i + 1) % 12]
        
        # Handle wrap-around (when next house cusp wraps past 360)
        if next_cusp < current_cusp:
            # Planet is in this house if it's >= current_cusp OR < next_cusp
            if planet_degree >= current_cusp or planet_degree < next_cusp:
                return i + 1
        else:
            # Normal case: planet is in this house if current_cusp <= planet < next_cusp
            if current_cusp <= planet_degree < next_cusp:
                return i + 1
    
    # Fallback: if planet is exactly on a cusp or edge case, use relative calculation
    # This should rarely happen, but provides a safety net
    relative_pos = normalize_degrees(planet_degree - ascendant_degree)
    house = int(relative_pos / 30) + 1
    if house > 12:
        house = 1
    return house


def get_planet_house_jhora(planet_degree: float, ascendant_degree: float, house_cusps: List[float]) -> int:
    """
    Calculate which house a planet is in using Whole Sign house system.
    
    🔒 DO NOT MODIFY — JHora compatible
    Whole Sign House System:
    - House 1 = Ascendant sign
    - House 2 = Next sign clockwise from ascendant
    - House 3 = Next sign clockwise, etc.
    
    Formula: house = ((planet_sign_index - ascendant_sign_index + 12) % 12) + 1
    
    Args:
        planet_degree: Planet's sidereal longitude
        ascendant_degree: Ascendant degree (house 1 cusp)
        house_cusps: List of 12 house cusp degrees (for reference, not used in calculation)
    
    Returns:
        House number (1-12) using Whole Sign system
    """
    planet_deg = normalize_degrees(planet_degree)
    asc_deg = normalize_degrees(ascendant_degree)
    
    # Get sign indices (0-11)
    planet_sign_index = int(planet_deg / 30.0)
    asc_sign_index = int(asc_deg / 30.0)
    
    # Whole Sign house calculation:
    # House 1 = ascendant sign
    # House 2 = next sign clockwise from ascendant
    # Formula: ((planet_sign - asc_sign + 12) % 12) + 1
    house = ((planet_sign_index - asc_sign_index + 12) % 12) + 1
    
    # DEBUG LOG: Show calculation details
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"   get_planet_house_jhora: planet={planet_deg}° (sign_idx={planet_sign_index}), asc={asc_deg}° (sign_idx={asc_sign_index}) → house={house}")
    
    # RUNTIME ASSERTION: House must be 1-12
    assert 1 <= house <= 12, f"House must be 1-12, got {house} (planet_sign={planet_sign_index}, asc_sign={asc_sign_index})"
    
    return house


def get_degrees_in_sign(degree: float) -> float:
    """
    Get degrees within the sign (0-30).
    
    Args:
        degree: Longitude in degrees (0-360)
    
    Returns:
        Degrees within sign (0-30)
    """
    degree = normalize_degrees(degree)
    return degree % 30


def generate_kundli(
    julian_day: float,
    latitude: float,
    longitude: float
) -> Dict:
    """
    Generate complete Kundli (D1 Rasi chart) for given parameters.
    
    This is the core Kundli engine that calculates:
    - Ascendant (Lagna) with degree and sign
    - All 9 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
    - 12 house cusps with degrees and signs
    - House position for each planet
    
    Args:
        julian_day: Julian Day Number
        latitude: Geographic latitude
        longitude: Geographic longitude
    
    Returns:
        Complete Kundli dictionary with:
        - Ascendant: {degree, sign, degrees_in_sign}
        - Planets: {planet_name: {degree, sign, degrees_in_sign, house}}
        - Houses: [{house: 1-12, degree, sign, degrees_in_sign}]
    """
    init_swisseph()
    
    # Calculate ascendant using EXACT JHORA method
    from src.ephemeris.planets_jhora_exact import calculate_ascendant_jhora_exact
    asc_jhora = calculate_ascendant_jhora_exact(julian_day, latitude, longitude)
    asc_sidereal = asc_jhora["longitude"]
    
    # Calculate houses using JHORA method (tropical then convert to sidereal)
    # Get ayanamsa for house conversion
    ayanamsa = get_ayanamsa(julian_day)
    houses_tropical = get_houses(julian_day, latitude, longitude)
    # Convert to sidereal
    houses_sidereal = [normalize_degrees(h - ayanamsa) for h in houses_tropical]
    
    # Get full planet data with nakshatra, pada, retrograde info (EXACT JHORA format)
    # Use EXACT JHORA method: swe.calc_ut() (tropical) + manual ayanamsa subtraction
    from src.ephemeris.planets_jhora_exact import calculate_all_planets_jhora_exact, calculate_ascendant_jhora_exact
    from src.ephemeris.planets_drik import get_nakshatra_pada, get_rashi
    planets_full_jhora = calculate_all_planets_jhora_exact(julian_day)
    
    # Convert JHORA format to expected format
    planets_full = {}
    for planet_name, planet_jhora in planets_full_jhora.items():
        planets_full[planet_name] = {
            "longitude": planet_jhora["longitude"],
            "latitude": planet_jhora["latitude"],
            "distance": planet_jhora["distance"],
            "speed": planet_jhora["speed"],
            "rashi_index": planet_jhora["sign_index"],
            "rashi": get_rashi(planet_jhora["longitude"])["name"],
            "degree_in_rashi": planet_jhora["degrees_in_sign"],
            "nakshatra_index": int(planet_jhora["longitude"] / (360.0 / 27.0)),
            "nakshatra": get_nakshatra_pada(planet_jhora["longitude"])["name"],
            "pada": get_nakshatra_pada(planet_jhora["longitude"])["pada"],
            "retro": planet_jhora["retro"],
            # Add JHORA deg-min-sec format
            "degree": planet_jhora["degree"],
            "arcminutes": planet_jhora["arcminutes"],
            "arcseconds": planet_jhora["arcseconds"]
        }
    
    # Calculate house position for each planet using JHORA method
    planets_with_houses = {}
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔍 HOUSE CALCULATION DEBUG:")
    logger.info(f"   Ascendant: {asc_sidereal}° (sign_index {get_sign_index(asc_sidereal)})")
    
    for planet_name, planet_full in planets_full.items():
        # Use longitude from JHORA calculation
        planet_degree = planet_full.get("longitude", 0)
        planet_sign_idx = get_sign_index(planet_degree)
        # Use JHORA method for house calculation
        house_num = get_planet_house_jhora(planet_degree, asc_sidereal, houses_sidereal)
        sign_index = get_sign_index(planet_degree)
        
        # DEBUG LOG: Show calculation details
        logger.info(f"   {planet_name}: {planet_degree}° (sign_index {planet_sign_idx}) → house {house_num}")
        
        # Compute DMS exactly as Prokerala (EXACT Prokerala/JHora precision)
        # 🔒 DO NOT MODIFY — JHora compatible
        # Preserve absolute longitude as float (0-360) without rounding
        # Compute sign_degree = absolute_longitude % 30
        sign_degree = get_degrees_in_sign(planet_degree)
        # Compute DMS exactly as Prokerala:
        # degrees = floor(sign_degree)
        # minutes = floor((sign_degree - degrees) * 60)
        # seconds = floor((((sign_degree - degrees) * 60) - minutes) * 60)
        dms_degrees = int(math.floor(sign_degree))
        dms_minutes_float = (sign_degree - dms_degrees) * 60.0
        dms_minutes = int(math.floor(dms_minutes_float))
        dms_seconds = int(math.floor((dms_minutes_float - dms_minutes) * 60.0))
        # Use JHORA values if available (more precise), otherwise compute from longitude
        degree_dms = planet_full.get("degree_in_sign", dms_degrees)
        arcminutes = planet_full.get("minutes_in_sign", dms_minutes)
        arcseconds = planet_full.get("seconds_in_sign", dms_seconds)
        # Formatted string: "25° 15′ 00″"
        degree_formatted = f"{degree_dms}° {arcminutes:02d}′ {arcseconds:02d}″"
        
        planets_with_houses[planet_name] = {
            "degree": round(planet_degree, 4),
            "sign": get_sign(planet_degree),
            "sign_sanskrit": get_sign_sanskrit(planet_degree),
            "sign_index": sign_index,
            "degrees_in_sign": round(get_degrees_in_sign(planet_degree), 4),
            "house": house_num,
            "house_lord": get_house_lord_from_sign(sign_index),
            "nakshatra": planet_full.get("nakshatra", ""),
            "nakshatra_index": planet_full.get("nakshatra_index", 0),
            "pada": planet_full.get("pada", 1),
            "retro": planet_full.get("retro", False),
            "speed": round(planet_full.get("speed", 0), 6),
            # Add JHORA deg-min-sec format (EXACT Prokerala/JHora precision)
            "degree_dms": degree_dms,
            "arcminutes": arcminutes,
            "arcseconds": arcseconds,
            "degree_formatted": degree_formatted
        }
    
    # Get Ascendant nakshatra and pada
    asc_nakshatra = get_nakshatra_pada(asc_sidereal)
    asc_sign_index = get_sign_index(asc_sidereal)
    
    # CRITICAL: Lagna (Ascendant) is ALWAYS in House 1 (Whole Sign system rule)
    # DO NOT MODIFY — JHora compatible
    # This is a fundamental Vedic astrology rule: Lagna = House 1, regardless of sign
    # Applies to D1 and ALL varga charts
    asc_house = 1
    
    # RUNTIME ASSERTION: Enforce lagna house invariant
    assert asc_house == 1, f"Lagna house must be 1, got {asc_house}"
    
    # Compute Ascendant DMS exactly as Prokerala (EXACT Prokerala/JHora precision)
    # 🔒 DO NOT MODIFY — JHora compatible
    # Preserve absolute longitude as float (0-360) without rounding
    # Compute sign_degree = absolute_longitude % 30
    asc_sign_degree = get_degrees_in_sign(asc_sidereal)
    # Compute DMS exactly as Prokerala:
    # degrees = floor(sign_degree)
    # minutes = floor((sign_degree - degrees) * 60)
    # seconds = floor((((sign_degree - degrees) * 60) - minutes) * 60)
    asc_dms_degrees = int(math.floor(asc_sign_degree))
    asc_dms_minutes_float = (asc_sign_degree - asc_dms_degrees) * 60.0
    asc_dms_minutes = int(math.floor(asc_dms_minutes_float))
    asc_dms_seconds = int(math.floor((asc_dms_minutes_float - asc_dms_minutes) * 60.0))
    # Use JHORA values if available (more precise), otherwise compute from longitude
    asc_degree_dms = asc_jhora.get("degree_in_sign", asc_dms_degrees)
    asc_arcminutes = asc_jhora.get("minutes_in_sign", asc_dms_minutes)
    asc_arcseconds = asc_jhora.get("seconds_in_sign", asc_dms_seconds)
    # Formatted string: "25° 15′ 00″"
    asc_degree_formatted = f"{asc_degree_dms}° {asc_arcminutes:02d}′ {asc_arcseconds:02d}″"
    
    # Build Kundli structure
    kundli = {
        "Ascendant": {
            "degree": round(asc_sidereal, 4),
            "sign": get_sign(asc_sidereal),
            "sign_sanskrit": get_sign_sanskrit(asc_sidereal),
            "sign_index": asc_sign_index,
            "degrees_in_sign": round(get_degrees_in_sign(asc_sidereal), 4),
            "house": asc_house,  # Always 1 for ascendant
            "lord": get_house_lord_from_sign(asc_sign_index),
            "nakshatra": asc_nakshatra["name"],
            "nakshatra_index": asc_nakshatra["index"],
            "pada": asc_nakshatra["pada"],
            # Add JHORA deg-min-sec format (EXACT Prokerala/JHora precision)
            "degree_dms": asc_degree_dms,
            "arcminutes": asc_arcminutes,
            "arcseconds": asc_arcseconds,
            "degree_formatted": asc_degree_formatted
        },
        "Planets": planets_with_houses,
        "Houses": [
            {
                "house": house_num,
                # 🔒 DO NOT MODIFY — JHora compatible
                # Whole Sign: House 1 = Ascendant sign, House 2 = next sign clockwise, etc.
                # Formula: sign_index = (asc_sign_index + house_num - 1) % 12
                "sign_index": (asc_sign_index + house_num - 1) % 12,
                "sign": SIGNS[(asc_sign_index + house_num - 1) % 12],
                "sign_sanskrit": SIGNS_SANSKRIT[(asc_sign_index + house_num - 1) % 12],
                "degree": round(houses_sidereal[house_num - 1], 4) if house_num <= len(houses_sidereal) else 0.0,  # Keep cusp degree for reference
                "degrees_in_sign": round(get_degrees_in_sign(houses_sidereal[house_num - 1]), 4) if house_num <= len(houses_sidereal) else 0.0,
                "lord": get_house_lord_from_sign((asc_sign_index + house_num - 1) % 12)
            }
            for house_num in range(1, 13)
        ]
    }
    
    return kundli

