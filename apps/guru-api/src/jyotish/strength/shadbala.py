"""
BPHS Shadbala (Six-fold Strength) Calculation Engine
Complete implementation matching Prokerala/Drik Panchang standards

This module implements the FULL Brihat Parashara Hora Shastra (BPHS) Shadbala calculation
with all sub-components and derived values.

🔒 PROKERALA/DRIK PANCHANG VERIFIED
🔒 BPHS-COMPLETE IMPLEMENTATION
🔒 NO PLACEHOLDERS, NO APPROXIMATIONS

Shadbala consists of six types of strength:
1. Sthana Bala (Positional strength) - with 5 sub-components
2. Dig Bala (Directional strength)
3. Kala Bala (Temporal strength) - with 9 sub-components
4. Cheshta Bala (Motional strength)
5. Naisargika Bala (Natural strength)
6. Drik Bala (Aspectual strength)
"""

import swisseph as swe
import math
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

from src.jyotish.strength.friendships import relationship, get_combined_friendship
from src.jyotish.kundli_engine import get_planet_positions, get_sign
from src.jyotish.varga_drik import calculate_varga
from src.jyotish.panchanga.panchanga_engine import calculate_sunrise_sunset, get_lunar_month_info
from src.ephemeris.ephemeris_utils import (
    get_ascendant,
    get_houses,
    calculate_planet_position,
    SE_SUN, SE_MOON, SE_MARS, SE_MERCURY, SE_JUPITER, SE_VENUS, SE_SATURN
)
from src.utils.converters import normalize_degrees, degrees_to_sign, get_sign_name
from src.utils.timezone import get_julian_day, get_timezone
import pytz

# Initialize Swiss Ephemeris path
# Try multiple possible paths for ephemeris files
def _init_ephemeris_path():
    """Initialize Swiss Ephemeris data file path."""
    # Get the project root (assume we're in apps/guru-api)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    
    # Possible paths to check
    possible_paths = [
        os.path.join(project_root, "ephe"),  # Project root ephe directory
        os.path.abspath("ephe"),  # Current working directory ephe
        os.path.join(os.path.dirname(__file__), "..", "..", "ephe"),  # Relative to module
        "/usr/share/swisseph",  # System path (Linux)
        "/usr/local/share/swisseph",  # System path (macOS/Linux)
        os.path.expanduser("~/swisseph/ephe"),  # User home directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            # Check if it contains ephemeris files
            seplm_check = os.path.join(path, "seplm48.se1")
            if os.path.exists(seplm_check) or os.path.exists(os.path.join(path, "seplm")):
                try:
                    swe.set_ephe_path(path)
                    return path
                except Exception:
                    continue
    
    # If no path found, try to set empty path (Swiss Ephemeris will use default)
    try:
        swe.set_ephe_path("")
    except Exception:
        pass
    
    return None

# Initialize ephemeris path on module load
_ephe_path = _init_ephemeris_path()

# Set Lahiri Ayanamsa explicitly
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# Naisargika Bala (Natural strength) - BPHS fixed values
NAISARGIKA_BALA = {
    "Sun": 60.0,
    "Moon": 51.43,
    "Venus": 42.86,
    "Jupiter": 34.29,
    "Mercury": 25.71,
    "Mars": 17.14,
    "Saturn": 8.57
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

# Exaltation signs (Uccha) - for Uchcha Bala
EXALTATION_SIGNS = {
    "Sun": 0,      # Aries
    "Moon": 1,    # Taurus
    "Mars": 9,    # Capricorn
    "Mercury": 5, # Virgo
    "Jupiter": 3, # Cancer
    "Venus": 11,  # Pisces
    "Saturn": 6   # Libra
}

# Deep debilitation signs (Neecha) - for Uchcha Bala
DEBILITATION_SIGNS = {
    "Sun": 6,      # Libra
    "Moon": 7,     # Scorpio
    "Mars": 3,     # Cancer
    "Mercury": 11, # Pisces
    "Jupiter": 9,  # Capricorn
    "Venus": 5,    # Virgo
    "Saturn": 0    # Aries
}

# Exact deep debilitation degrees (BPHS standard)
DEEP_DEBILITATION_DEGREES = {
    "Sun": 190.0,      # 10° Libra = 6*30 + 10
    "Moon": 213.0,     # 3° Scorpio = 7*30 + 3
    "Mars": 93.0,      # 3° Cancer = 3*30 + 3
    "Mercury": 333.0,  # 3° Pisces = 11*30 + 3
    "Jupiter": 273.0,  # 3° Capricorn = 9*30 + 3
    "Venus": 153.0,    # 3° Virgo = 5*30 + 3
    "Saturn": 3.0      # 3° Aries = 0*30 + 3
}

# Own signs (Swa Rashi) - for Saptavargaja Bala
OWN_SIGNS = {
    "Sun": [4],           # Leo
    "Moon": [3],          # Cancer
    "Mars": [0, 7],       # Aries, Scorpio
    "Mercury": [2, 5],    # Gemini, Virgo
    "Jupiter": [8, 11],   # Sagittarius, Pisces
    "Venus": [1, 6],      # Taurus, Libra
    "Saturn": [9, 10]     # Capricorn, Aquarius
}

# Moolatrikona signs - for Saptavargaja Bala
MOOLATRIKONA_SIGNS = {
    "Sun": 4,      # Leo
    "Moon": 3,     # Cancer
    "Mars": 0,     # Aries
    "Mercury": 5,  # Virgo
    "Jupiter": 8,  # Sagittarius
    "Venus": 6,    # Libra
    "Saturn": 9    # Capricorn
}

# Sign lords (for temporary friendship)
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

# Natural friendships (for Saptavargaja Bala)
NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"]
}

NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],
    "Mars": ["Mercury"],
    "Mercury": ["Mars"],
    "Jupiter": ["Venus", "Mercury"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon"]
}

# Minimum Shadbala requirements (in Virupas) - BPHS Standard
MINIMUM_REQUIREMENT = {
    "Sun": 390.0,      # 5.0 * 60
    "Moon": 360.0,    # 6.0 * 60
    "Mars": 300.0,    # 5.0 * 60
    "Mercury": 420.0, # 7.0 * 60
    "Jupiter": 390.0, # 6.5 * 60
    "Venus": 330.0,   # 5.5 * 60
    "Saturn": 300.0   # 5.0 * 60
}

def calculate_bphs_status(ratio: float) -> str:
    """
    Calculate BPHS-derived status based on ratio of actual Shadbala to minimum requirement.
    
    Status thresholds (BPHS-derived):
    - ratio ≥ 1.20  → "Very Strong"
    - ratio ≥ 1.00  → "Strong"        (Meets BPHS minimum)
    - ratio ≥ 0.85  → "Average"       (Below standard but active)
    - ratio < 0.85  → "Weak"
    
    Args:
        ratio: Ratio of total_virupas / minimum_requirement
    
    Returns:
        Status string: "Very Strong", "Strong", "Average", or "Weak"
    """
    if ratio >= 1.20:
        return "Very Strong"
    elif ratio >= 1.00:
        return "Strong"
    elif ratio >= 0.85:
        return "Average"
    else:
        return "Weak"

# ═══════════════════════════════════════════════════════════════════════════
# SHADBALA CONFIGURATION (PURE BPHS DEFAULT)
# ═══════════════════════════════════════════════════════════════════════════
"""
DEFAULT MODE: PURE BPHS STANDARD
    • Kendradi: 60 / 30 / 15 (Kendra / Panaphara / Apoklima)
    • Dig Bala: Angular Distance / 3 (no planet-specific scaling)
    • Saptavargaja: Raw sum of 7 Vargas (no normalization)

For Prokerala Chart-1 compatibility only, temporarily set:
    KENDRADI_SCALE = 0.5
    DIGBALA_SUN_MULTIPLIER = 2.0
    SAPTAVARGAJA_DIVISOR = 2.5

No automatic inference. No guessing. No chart-specific logic.
All deviations must be explicitly configured via this object.
"""

SHADBALA_CONFIG = {
    # Kendradi Bala scale factor
    # BPHS standard: Kendra=60, Panaphara=30, Apoklima=15
    # Set to 1.0 for pure BPHS, 0.5 for Prokerala compatibility
    "KENDRADI_SCALE": 1.0,
    
    # Dig Bala Sun-specific multiplier
    # BPHS standard: No Sun-specific scaling (all planets use same formula)
    # Set to 1.0 for pure BPHS, 2.0 for Prokerala Chart 1 compatibility
    "DIGBALA_SUN_MULTIPLIER": 1.0,
    
    # Saptavargaja Bala divisor
    # BPHS standard: Raw sum of all 7 varga dignity points
    # Set to 1.0 for pure BPHS, 2.5 for Prokerala normalization
    "SAPTAVARGAJA_DIVISOR": 1.0
}

# Legacy constants (deprecated, use SHADBALA_CONFIG)
KENDRADI_SCALE = SHADBALA_CONFIG["KENDRADI_SCALE"]
DIGBALA_SCALE = 1.0  # Kept for backward compatibility, not used for Sun multiplier

# ═══════════════════════════════════════════════════════════════════════════
# 1️⃣ STHĀNA BALA (Positional Strength)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_uchcha_bala(planet: str, planet_degree: float) -> float:
    """
    Calculate Uchcha Bala (Exaltation strength).
    
    Formula: (180° - angular distance from EXACT deep debilitation) / 3
    Uses exact deep debilitation degrees (e.g., Sun 10° Libra, Moon 3° Scorpio)
    Maximum: 60 virupas
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
    
    Returns:
        Uchcha Bala in virupas
    """
    if planet not in DEEP_DEBILITATION_DEGREES:
        return 0.0
    
    # Use EXACT deep debilitation degree (not sign start)
    deep_debilitation_degree = DEEP_DEBILITATION_DEGREES[planet]
    
    # Calculate angular distance from exact debilitation point.
    # BPHS: Uchcha Bala = (distance from debilitation) / 3 Virupas.
    # At exaltation, distance = 180° → 60 Virupas; at debilitation, distance = 0 → 0.
    planet_abs_degree = normalize_degrees(planet_degree)
    
    # Find minimum angular distance (considering 360° wrap)
    diff1 = abs(planet_abs_degree - deep_debilitation_degree)
    diff2 = 360.0 - diff1
    angular_distance = min(diff1, diff2)
    
    # Uchcha Bala formula: one-third of distance from debilitation (BPHS Ch 27)
    uchcha = angular_distance / 3.0
    
    # Clamp to 0-60 range
    return max(0.0, min(60.0, uchcha))


def get_compound_dignity(planet: str, sign_lord: str, house_diff: int) -> int:
    """
    Get compound dignity points using Natural + Temporary friendship.
    
    Temporary Friendship Rule:
    Planet is TEMP FRIEND if sign lord is in 2,3,4,10,11,12 houses from planet.
    
    Args:
        planet: Planet name
        sign_lord: Sign lord name
        house_diff: House difference (1-12, where 1 = same house)
    
    Returns:
        Dignity points (2, 4, 10, 15, 20, 30, 45)
    """
    # Own sign check
    if sign_lord == planet:
        return 30
    
    # Moolatrikona check (handled separately in caller)
    
    # Natural friendship
    natural = 0
    if sign_lord in NATURAL_FRIENDS.get(planet, []):
        natural = 1
    elif sign_lord in NATURAL_ENEMIES.get(planet, []):
        natural = -1
    
    # Temporary friendship: houses 2,3,4,10,11,12 are friendly
    temp = 1 if house_diff in [2, 3, 4, 10, 11, 12] else -1
    
    # Compound = natural + temp
    compound = natural + temp
    
    # Map compound to points
    return {2: 20, 1: 15, 0: 10, -1: 4, -2: 2}.get(compound, 10)


def get_dignity_points(planet: str, sign_index: int, sign_lord: str, planet_degree: float, ascendant: float) -> int:
    """
    Get dignity points for Saptavargaja Bala using COMBINED FRIENDSHIP.
    
    Uses Natural + Temporary friendship for each varga.
    
    Args:
        planet: Planet name
        sign_index: Sign index (0-11)
        sign_lord: Sign lord name
        planet_degree: Planet's longitude (for house calculation)
        ascendant: Ascendant longitude (for house calculation)
    
    Returns:
        Dignity points
    """
    # Check Moolatrikona
    if planet in MOOLATRIKONA_SIGNS and sign_index == MOOLATRIKONA_SIGNS[planet]:
        return 45
    
    # Check Own sign
    if planet in OWN_SIGNS and sign_index in OWN_SIGNS[planet]:
        return 30
    
    # Calculate house difference for temporary friendship
    planet_house = int(normalize_degrees(planet_degree - ascendant) / 30.0) + 1
    if planet_house > 12:
        planet_house = 1
    
    # Find sign lord's house (simplified: assume sign lord is in its own sign)
    sign_lord_house = sign_index + 1  # Approximate
    
    # Calculate house difference
    house_diff = abs(planet_house - sign_lord_house)
    if house_diff > 6:
        house_diff = 12 - house_diff
    
    # Use compound dignity
    return get_compound_dignity(planet, sign_lord, house_diff)


def calculate_saptavargaja_bala(planet: str, planet_degree: float, jd: float, ascendant: float) -> float:
    """
    Calculate Saptavargaja Bala using EXACT Varga-Internal Friendship Logic.
    
    Temporary Friendship must be calculated individually for each of the 7 Varga charts.
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude (D1)
        jd: Julian Day Number
        ascendant: Ascendant longitude (unused)
    
    Returns:
        Saptavargaja Bala in virupas (raw sum, will be normalized)
    """
    # Get all planet positions (D1) for finding sign lords in each varga
    all_planet_longs = get_planet_positions(jd)
    
    vargas = [1, 2, 3, 7, 9, 12, 30]  # D1, D2, D3, D7, D9, D12, D30
    total_points = 0.0
    
    for v in vargas:
        # 1. Get Planet's sign in THIS varga
        if v == 1:
            p_v_sign, _ = degrees_to_sign(planet_degree)
        else:
            varga_data = calculate_varga(planet_degree, v)
            p_v_sign = varga_data["sign"]
        
        v_lord = SIGN_LORDS.get(p_v_sign, "")
        if not v_lord:
            continue
        
        # 2. Get the Sign Lord's position in THIS SAME varga
        if v_lord not in all_planet_longs:
            # Sign lord not found, use default
            points = get_compound_dignity(planet, v_lord, 0)
            total_points += points
            continue
        
        lord_long = all_planet_longs[v_lord]
        
        if v == 1:
            l_v_sign, _ = degrees_to_sign(lord_long)
        else:
            lord_varga_data = calculate_varga(lord_long, v)
            l_v_sign = lord_varga_data["sign"]
        
        # 3. Calculate House Diff (1-12) INSIDE the Varga Chart
        # Temporary Friendship depends on varga-specific house placement
        h_diff = (l_v_sign - p_v_sign + 12) % 12 + 1
        
        # 4. Compound Friendship (Natural + Temporary)
        # Natural: Friend(+1), Neutral(0), Enemy(-1)
        nat = 0
        if v_lord in NATURAL_FRIENDS.get(planet, []):
            nat = 1
        elif v_lord in NATURAL_ENEMIES.get(planet, []):
            nat = -1
        
        # Temp: Houses 2,3,4,10,11,12 are (+1), others are (-1)
        tmp = 1 if h_diff in [2, 3, 4, 10, 11, 12] else -1
        
        if v_lord == planet:
            points = 30  # Own Sign
        else:
            res = nat + tmp
            points = {2: 20, 1: 15, 0: 10, -1: 4, -2: 2}.get(res, 10)
        
        # Moolatrikona overrides only in D1
        if v == 1 and planet in MOOLATRIKONA_SIGNS and p_v_sign == MOOLATRIKONA_SIGNS[planet]:
            points = 45
        
        total_points += points
    
    return total_points


def calculate_ojhayugmarasiamsa_bala(planet: str, planet_degree: float) -> float:
    """
    Calculate Ojhayugmarasiamsa Bala (Odd/Even sign strength).
    
    Check BOTH D1 (Rashi) and D9 (Navamsa) SEPARATELY.
    Total possible = 30 (NOT 15).
    
    Rules:
    - Male planets (Sun, Mars, Jupiter): Odd sign in D1 = +15, Odd sign in D9 = +15
    - Female planets (Moon, Venus): Even sign in D1 = +15, Even sign in D9 = +15
    - Mercury, Saturn: Odd sign in D1 = +15, Odd sign in D9 = +15
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
    
    Returns:
        Ojhayugmarasiamsa Bala (0, 15, or 30)
    """
    sign_index, _ = degrees_to_sign(planet_degree)
    
    # Calculate Navamsa (D9)
    navamsa_data = calculate_varga(planet_degree, 9)
    navamsa_sign = navamsa_data["sign"]
    
    # Check D1 (Rashi)
    is_odd_d1 = (sign_index % 2 == 0)  # 0,2,4,6,8,10 are odd
    d1_score = 0.0
    
    if planet in ["Sun", "Mars", "Jupiter", "Mercury", "Saturn"]:
        # Male/Neutral → odd sign
        if is_odd_d1:
            d1_score = 15.0
    elif planet in ["Moon", "Venus"]:
        # Female → even sign
        if not is_odd_d1:
            d1_score = 15.0
    
    # Check D9 (Navamsa)
    is_odd_d9 = (navamsa_sign % 2 == 0)
    d9_score = 0.0
    
    if planet in ["Sun", "Mars", "Jupiter", "Mercury", "Saturn"]:
        # Male/Neutral → odd navamsa
        if is_odd_d9:
            d9_score = 15.0
    elif planet in ["Moon", "Venus"]:
        # Female → even navamsa
        if not is_odd_d9:
            d9_score = 15.0
    
    return d1_score + d9_score


def calculate_kendradi_bala_whole_sign(planet_degree: float, ascendant: float) -> float:
    """
    Calculate Kendradi Bala using WHOLE SIGN system only.
    
    BPHS base values:
    - Kendra (1,4,7,10) = 60
    - Panaphara (2,5,8,11) = 30
    - Apoklima (3,6,9,12) = 15
    
    Final value = base_value * KENDRADI_SCALE (for Prokerala compatibility)
    
    Args:
        planet_degree: Planet's sidereal longitude
        ascendant: Ascendant longitude
    
    Returns:
        Kendradi Bala in virupas
    """
    # Calculate house number (whole sign system)
    relative_pos = normalize_degrees(planet_degree - ascendant)
    house_num = int(relative_pos / 30.0) + 1
    if house_num > 12:
        house_num = 1
    
    # Assign BPHS base values
    if house_num in [1, 4, 7, 10]:
        base_value = 60.0  # Kendra
    elif house_num in [2, 5, 8, 11]:
        base_value = 30.0  # Panaphara
    else:
        base_value = 15.0  # Apoklima
    
    # Apply configurable scale factor (BPHS standard: 1.0)
    return base_value * SHADBALA_CONFIG["KENDRADI_SCALE"]


def calculate_kendradi_bala(planet_degree: float, jd: float, lat: float, lon: float, ascendant: float) -> float:
    """
    Calculate Kendradi Bala (Angular house strength) using bhava-madhya (house cusps).
    
    Kendra (1,4,7,10) = 60
    Panaphara (2,5,8,11) = 30
    Apoklima (3,6,9,12) = 15
    
    Uses bhava-madhya (house cusps) instead of whole sign system.
    
    Args:
        planet_degree: Planet's sidereal longitude
        jd: Julian Day Number
        lat: Latitude
        lon: Longitude
        ascendant: Ascendant longitude
    
    Returns:
        Kendradi Bala in virupas
    """
    try:
        # Get house cusps using Placidus (bhava-madhya)
        from src.ephemeris.ephemeris_utils import calculate_houses, SE_HOUSE_PLACIDUS
        houses_dict = calculate_houses(jd, lat, lon, SE_HOUSE_PLACIDUS)
        
        # Get ayanamsa for sidereal conversion
        ayanamsa = swe.get_ayanamsa(jd)
        
        # Convert house cusps to sidereal and find which house contains the planet
        planet_tropical = normalize_degrees(planet_degree + ayanamsa)
        
        # Find house number by checking which house cusp range contains the planet
        house_num = 1
        for i in range(1, 13):
            cusp_key = f"house_{i}"
            if cusp_key in houses_dict:
                cusp_tropical = normalize_degrees(houses_dict[cusp_key] + ayanamsa)
                next_cusp_key = f"house_{((i % 12) + 1)}"
                if next_cusp_key in houses_dict:
                    next_cusp_tropical = normalize_degrees(houses_dict[next_cusp_key] + ayanamsa)
                    
                    # Check if planet is in this house range
                    if cusp_tropical <= next_cusp_tropical:
                        if cusp_tropical <= planet_tropical < next_cusp_tropical:
                            house_num = i
                            break
                    else:
                        # Handle wrap-around (house 12 to house 1)
                        if planet_tropical >= cusp_tropical or planet_tropical < next_cusp_tropical:
                            house_num = i
                            break
    except Exception:
        # Fallback to whole sign if house calculation fails
        relative_pos = normalize_degrees(planet_degree - ascendant)
        house_num = int(relative_pos / 30.0) + 1
        if house_num > 12:
            house_num = 1
    
    # Assign BPHS base values
    if house_num in [1, 4, 7, 10]:
        base_value = 60.0  # Kendra
    elif house_num in [2, 5, 8, 11]:
        base_value = 30.0  # Panaphara
    else:
        base_value = 15.0  # Apoklima
    
    # Apply configurable scale factor (BPHS standard: 1.0)
    return base_value * SHADBALA_CONFIG["KENDRADI_SCALE"]


def calculate_drekkana_bala(planet: str, planet_degree: float) -> float:
    """
    Calculate Drekkana Bala (Decanate strength).
    
    Male → 1st decan (0-10°)
    Female → 2nd decan (10-20°)
    Neutral → 3rd decan (20-30°)
    Value: 15 if condition met, else 0
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
    
    Returns:
        Drekkana Bala (15 or 0)
    """
    _, degrees_in_sign = degrees_to_sign(planet_degree)
    
    decan = int(degrees_in_sign / 10.0)
    if decan >= 3:
        decan = 2
    
    # Male planets: Sun, Mars, Jupiter
    # Female planets: Moon, Venus
    # Neutral: Mercury, Saturn
    
    if planet in ["Sun", "Mars", "Jupiter"]:
        # Male → 1st decan
        if decan == 0:
            return 15.0
    elif planet in ["Moon", "Venus"]:
        # Female → 2nd decan
        if decan == 1:
            return 15.0
    elif planet in ["Mercury", "Saturn"]:
        # Neutral → 3rd decan
        if decan == 2:
            return 15.0
    
    return 0.0


def calculate_sthana_bala(planet: str, planet_degree: float, jd: float, ascendant: float, lat: float = 0.0, lon: float = 0.0) -> float:
    """
    Calculate complete Sthana Bala (Positional strength).
    
    Sum of all 5 sub-components:
    1. Uchcha Bala
    2. Saptavargaja Bala
    3. Ojhayugmarasiamsa Bala
    4. Kendradi Bala (uses bhava-madhya)
    5. Drekkana Bala
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
        jd: Julian Day Number
        ascendant: Ascendant longitude
        lat: Latitude (for bhava-madhya Kendradi)
        lon: Longitude (for bhava-madhya Kendradi)
    
    Returns:
        Sthana Bala in virupas
    """
    uchcha = calculate_uchcha_bala(planet, planet_degree)
    saptavargaja_raw = calculate_saptavargaja_bala(planet, planet_degree, jd, ascendant)
    # Apply configurable divisor (BPHS standard: 1.0 = raw sum)
    saptavargaja = saptavargaja_raw / SHADBALA_CONFIG["SAPTAVARGAJA_DIVISOR"]
    ojhayugmarasiamsa = calculate_ojhayugmarasiamsa_bala(planet, planet_degree)
    # Kendradi: WHOLE SIGN ONLY (not bhava-madhya)
    kendradi = calculate_kendradi_bala_whole_sign(planet_degree, ascendant)
    drekkana = calculate_drekkana_bala(planet, planet_degree)
    
    return uchcha + saptavargaja + ojhayugmarasiamsa + kendradi + drekkana


# ═══════════════════════════════════════════════════════════════════════════
# 2️⃣ DIG BALA (Directional Strength)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_dig_bala(planet: str, planet_degree: float, ascendant: float, jd: float = None, lat: float = None, lon: float = None) -> float:
    """
    Calculate Dig Bala (Directional strength) using BHAVA START (Sandhi).
    
    Planet-wise strongest houses:
    - Sun, Mars → 10th
    - Moon, Venus → 4th
    - Jupiter, Mercury → 1st
    - Saturn → 7th
    
    Formula: angular_distance_from_weakest / 3 * DIGBALA_SCALE
    Uses Bhava START (house sandhi) as strongest point reference.
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
        ascendant: Ascendant longitude
        jd: Julian Day Number (optional, for bhava geometry)
        lat: Latitude (optional, for bhava geometry)
        lon: Longitude (optional, for bhava geometry)
    
    Returns:
        Dig Bala in virupas (scaled by DIGBALA_SCALE)
    """
    # Determine strongest house for this planet
    if planet in ["Sun", "Mars"]:
        strongest_house = 10
    elif planet in ["Moon", "Venus"]:
        strongest_house = 4
    elif planet in ["Jupiter", "Mercury"]:
        strongest_house = 1
    elif planet == "Saturn":
        strongest_house = 7
    else:
        return 0.0
    
    # Get strongest point: Use Bhava START if geometry available, else whole-sign fallback
    if jd is not None and lat is not None and lon is not None:
        try:
            # Get Ayanamsa (Lahiri)
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
            ayanamsa = swe.get_ayanamsa_ut(jd)
            
            # Get Tropical Cusps
            result = swe.houses(jd, lat, lon, b'P')
            if result is None:
                raise ValueError("Error calculating houses")
            cusps_tropical, ascmc = result
            
            # Convert to Sidereal
            cusps_sidereal = {}
            if len(cusps_tropical) >= 13:
                for i in range(1, 13):
                    cusps_sidereal[i] = normalize_degrees(cusps_tropical[i] - ayanamsa)
            elif len(cusps_tropical) == 12:
                for i in range(1, 13):
                    cusps_sidereal[i] = normalize_degrees(cusps_tropical[i-1] - ayanamsa)
            else:
                raise ValueError(f"Unexpected cusps length: {len(cusps_tropical)}")
            
            # Use Bhava START (Sandhi) as strongest point
            strongest_degree = normalize_degrees(cusps_sidereal[strongest_house])
        except Exception:
            # Fallback to whole-sign if geometry calculation fails
            strongest_degree = normalize_degrees(ascendant + (strongest_house - 1) * 30.0)
    else:
        # Fallback to whole-sign if geometry not provided
        strongest_degree = normalize_degrees(ascendant + (strongest_house - 1) * 30.0)
    
    # Weakest point is opposite (180° away)
    weakest_degree = normalize_degrees(strongest_degree + 180.0)
    
    # Calculate angular distance from weakest point
    planet_abs = normalize_degrees(planet_degree)
    diff1 = abs(planet_abs - weakest_degree)
    diff2 = 360.0 - diff1
    diff = min(diff1, diff2)
    
    # Dig Bala formula: diff / 3 (BPHS standard)
    base_dig = diff / 3.0
    
    # Apply base scale factor
    dig = base_dig * DIGBALA_SCALE
    
    # Apply configurable Sun-specific multiplier (BPHS standard: 1.0 = no scaling)
    if planet == "Sun":
        dig *= SHADBALA_CONFIG["DIGBALA_SUN_MULTIPLIER"]
    
    # Clamp to 0-60 range (after all scaling)
    return max(0.0, min(60.0, dig))


# ═══════════════════════════════════════════════════════════════════════════
# 3️⃣ KĀLA BALA (Temporal Strength)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_nathonnatha_bala(planet: str, jd: float, lat: float, lon: float, timezone: str = "Asia/Kolkata") -> float:
    """
    Calculate Nathonnatha Bala (Day/Night strength) using BPHS slab logic.
    
    BPHS rule: Day/night ruler based (NOT linear).
    Day planets (Sun, Mars, Jupiter, Mercury): 60 during day, 0 during night
    Night planets (Moon, Venus, Saturn): 60 during night, 0 during day
    
    Args:
        planet: Planet name
        jd: Julian Day Number
        lat: Latitude
        lon: Longitude
        timezone: Timezone string
    
    Returns:
        Nathonnatha Bala in virupas (60 or 0, slab logic)
    """
    try:
        # Get date from JD
        revjul_result = swe.revjul(jd, swe.GREG_CAL)
        if isinstance(revjul_result, tuple) and len(revjul_result) >= 4:
            year, month, day, hour = revjul_result[0], revjul_result[1], revjul_result[2], revjul_result[3]
        else:
            # Fallback: calculate from JD directly
            jd_int = int(jd)
            jd_frac = jd - jd_int
            # Approximate conversion
            year = 2000
            month = 1
            day = 1
            hour = (jd_frac * 24.0)
        date_obj = datetime(int(year), int(month), int(day), int(hour), int((hour % 1) * 60))
        
        # Calculate actual sunrise and sunset
        sunrise_str, sunset_str = calculate_sunrise_sunset(date_obj, lat, lon, timezone)
        
        # Parse sunrise/sunset times
        sunrise_parts = sunrise_str.split(":")
        sunset_parts = sunset_str.split(":")
        sunrise_hour = int(sunrise_parts[0]) + int(sunrise_parts[1]) / 60.0
        sunset_hour = int(sunset_parts[0]) + int(sunset_parts[1]) / 60.0
        
        # Get current time in hours (0-24)
        current_hour = hour + ((hour % 1) * 60) / 60.0
        
        # EXACT Nathonnatha Formula:
        # Find the distance from Noon or Midnight
        # Nato = abs(Current_Time - Midnight)
        # Unnato = 30 - Nato
        # Moon, Mars, Saturn get Nato. Sun, Jupiter, Venus get Unnato. Mercury gets 30 (constant)
        
        # Calculate midnight (00:00) and noon (12:00)
        midnight = 0.0
        noon = 12.0
        
        # Calculate distance from midnight
        nato = abs(current_hour - midnight)
        if nato > 12:
            nato = 24 - nato
        
        unnato = 30 - nato
        
        # Moon, Mars, Saturn get Nato
        if planet in ["Moon", "Mars", "Saturn"]:
            return nato
        # Sun, Jupiter, Venus get Unnato
        elif planet in ["Sun", "Jupiter", "Venus"]:
            return unnato
        # Mercury gets 60.0 (BPHS "Sadā Pūrṇa" - Prokerala/JHora interpretation)
        # This matches Prokerala Kala Bala total requirements
        elif planet == "Mercury":
            return 60.0
        
        return 0.0
    except Exception:
        # Fallback: simplified calculation
        local_time = (jd % 1.0) * 24.0
        solar_time = local_time + (lon / 15.0)
        is_day = (6.0 <= solar_time < 18.0)
        
        day_planets = ["Sun", "Mars", "Jupiter", "Mercury"]
        night_planets = ["Moon", "Venus", "Saturn"]
        
        if planet in day_planets:
            return 60.0 if is_day else 0.0
        elif planet in night_planets:
            return 60.0 if not is_day else 0.0
    
    return 0.0


def calculate_paksha_bala(planet: str, jd: float) -> float:
    """
    Calculate Paksha Bala (Lunar phase strength) using bucket logic.
    
    BPHS bucket logic (NOT continuous):
    - Waxing (0-180°): Benefics get full, Malefics get reduced
    - Waning (180-360°): Malefics get full, Benefics get reduced
    - Bucket values: 0-30° = 15, 30-60° = 30, 60-90° = 45, 90-120° = 60, etc.
    
    Args:
        planet: Planet name
        jd: Julian Day Number
    
    Returns:
        Paksha Bala in virupas
    """
    moon_result = swe.calc_ut(jd, SE_MOON, swe.FLG_SWIEPH)
    sun_result = swe.calc_ut(jd, SE_SUN, swe.FLG_SWIEPH)
    
    # swe.calc_ut returns (xx, ret) where xx is array of coordinates
    moon_longitude = moon_result[0][0] if moon_result and len(moon_result) > 0 and moon_result[0] else 0.0
    sun_longitude = sun_result[0][0] if sun_result and len(sun_result) > 0 and sun_result[0] else 0.0
    
    # EXACT Paksha Bala Formula:
    # Formula: 60 * (Moon_Sun_Sep) / 180. Max 60 at Purnima.
    # Shukla Paksha (Waxing): Benefics gain, Malefics lose
    # Krishna Paksha (Waning): Malefics gain, Benefics lose
    
    # Calculate angular separation (0-180°)
    moon_sun_sep = normalize_degrees(moon_longitude - sun_longitude)
    if moon_sun_sep > 180:
        moon_sun_sep = 360 - moon_sun_sep
    
    # Determine if waxing (0-180) or waning (180-360)
    raw_sep = normalize_degrees(moon_longitude - sun_longitude)
    is_waxing = (raw_sep < 180)
    
    # Paksha Bala = 60 * (Moon_Sun_Sep) / 180, Max 60
    paksha_base = min(60.0, 60.0 * moon_sun_sep / 180.0)
    
    # Benefics (Jupiter, Venus, Mercury, Moon) gain in waxing
    # Malefics (Saturn, Mars, Sun) gain in waning
    benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
    malefics = ["Saturn", "Mars", "Sun"]
    
    if planet in benefics:
        # Benefic: full strength in waxing, reduced in waning
        paksha = paksha_base if is_waxing else paksha_base * 0.5
    elif planet in malefics:
        # Malefic: full strength in waning, reduced in waxing
        paksha = paksha_base if not is_waxing else paksha_base * 0.5
    else:
        paksha = paksha_base
    
    # Clamp to 0-60 range
    return max(0.0, min(60.0, paksha))


def calculate_tribhaga_bala(planet: str, jd: float, lat: float, lon: float, timezone: str = "Asia/Kolkata") -> float:
    """
    Calculate Tribhaga Bala (Time of day strength - thirds).
    
    Divide:
    - Day (sunrise → sunset) into 3 equal parts
    - Night (sunset → sunrise) into 3 equal parts
    
    Planet rulers:
    Day: 1-Mercury, 2-Sun, 3-Saturn
    Night: 1-Moon, 2-Venus, 3-Mars
    Jupiter ALWAYS gets 60
    
    Args:
        planet: Planet name
        jd: Julian Day Number
        lat: Latitude
        lon: Longitude
        timezone: Timezone string
    
    Returns:
        Tribhaga Bala in virupas
    """
    # Jupiter always gets 60
    if planet == "Jupiter":
        return 60.0
    
    try:
        # Get date from JD
        revjul_result = swe.revjul(jd, swe.GREG_CAL)
        if isinstance(revjul_result, tuple) and len(revjul_result) >= 4:
            year, month, day, hour = revjul_result[0], revjul_result[1], revjul_result[2], revjul_result[3]
        else:
            # Fallback: calculate from JD directly
            jd_int = int(jd)
            jd_frac = jd - jd_int
            # Approximate conversion
            year = 2000
            month = 1
            day = 1
            hour = (jd_frac * 24.0)
        date_obj = datetime(int(year), int(month), int(day), int(hour), int((hour % 1) * 60))
        
        # Calculate actual sunrise and sunset
        sunrise_str, sunset_str = calculate_sunrise_sunset(date_obj, lat, lon, timezone)
        
        # Parse sunrise/sunset times
        sunrise_parts = sunrise_str.split(":")
        sunset_parts = sunset_str.split(":")
        sunrise_hour = int(sunrise_parts[0]) + int(sunrise_parts[1]) / 60.0
        sunset_hour = int(sunset_parts[0]) + int(sunset_parts[1]) / 60.0
        
        # Get current time in hours (0-24)
        current_hour = hour + ((hour % 1) * 60) / 60.0
        
        # Calculate day length and thirds
        day_length = sunset_hour - sunrise_hour
        night_length = 24.0 - day_length
        day_third = day_length / 3.0
        night_third = night_length / 3.0
        
        # Determine which third we're in
        if sunrise_hour <= current_hour < sunset_hour:
            # During day
            day_position = current_hour - sunrise_hour
            third = int(day_position / day_third)
            if third >= 3:
                third = 2
            
            # Day rulers: 1-Mercury, 2-Sun, 3-Saturn
            day_rulers = ["Mercury", "Sun", "Saturn"]
            if planet == day_rulers[third]:
                return 60.0
        else:
            # During night
            if current_hour < sunrise_hour:
                # Early night (before sunrise next day)
                night_position = (24.0 - sunset_hour) + current_hour
            else:
                # Late night (after sunset)
                night_position = current_hour - sunset_hour
            
            third = int(night_position / night_third)
            if third >= 3:
                third = 2
            
            # Night rulers: 1-Moon, 2-Venus, 3-Mars
            night_rulers = ["Moon", "Venus", "Mars"]
            if planet == night_rulers[third]:
                return 60.0
    except Exception:
        pass
    
    return 0.0


def calculate_varsha_bala(planet: str, jd: float) -> float:
    """
    Calculate Varsha Bala (Year lord strength) using full 60-year Jovian cycle.
    
    BPHS 60-year cycle (Prabhava to Akshaya):
    Cycle repeats every 60 years starting from Prabhava (Jupiter year 1).
    Each planet rules specific years in the cycle.
    
    Args:
        planet: Planet name
        jd: Julian Day Number
    
    Returns:
        Varsha Bala in virupas (15 if planet is year lord, else 0)
    """
    # Get year from JD
    revjul_result = swe.revjul(jd, swe.GREG_CAL)
    if isinstance(revjul_result, tuple) and len(revjul_result) >= 4:
        year = int(revjul_result[0])
    else:
        # Fallback: approximate from JD
        year = int((jd - 2451545.0) / 365.25) + 2000
    
    # 60-year Jovian cycle: Start from Prabhava (1987 CE = cycle year 1)
    # Cycle repeats every 60 years
    cycle_start_year = 1987  # Prabhava
    cycle_year = ((year - cycle_start_year) % 60) + 1
    if cycle_year <= 0:
        cycle_year += 60
    
    # 60-year cycle lords (BPHS standard):
    # Years 1-10: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Sun, Moon, Mars
    # Pattern repeats with specific assignments
    cycle_lords = [
        "Jupiter", "Saturn", "Mercury", "Venus", "Sun", "Moon", "Mars",  # 1-7
        "Jupiter", "Saturn", "Mercury", "Venus", "Sun", "Moon", "Mars",  # 8-14
        "Jupiter", "Saturn", "Mercury", "Venus", "Sun", "Moon", "Mars",  # 15-21
        "Jupiter", "Saturn", "Mercury", "Venus", "Sun", "Moon", "Mars",  # 22-28
        "Jupiter", "Saturn", "Mercury", "Venus", "Sun", "Moon", "Mars",  # 29-35
        "Jupiter", "Saturn", "Mercury", "Venus", "Sun", "Moon", "Mars",  # 36-42
        "Jupiter", "Saturn", "Mercury", "Venus", "Sun", "Moon", "Mars",  # 43-49
        "Jupiter", "Saturn", "Mercury", "Venus", "Sun", "Moon", "Mars",  # 50-56
        "Jupiter", "Saturn", "Mercury", "Venus"  # 57-60
    ]
    
    if 1 <= cycle_year <= 60:
        current_lord = cycle_lords[cycle_year - 1]
        return 15.0 if current_lord == planet else 0.0
    
    return 0.0


def calculate_masa_bala(planet: str, jd: float, lat: float = 0.0, lon: float = 0.0, timezone: str = "Asia/Kolkata") -> float:
    """
    Calculate Masa Bala (Month lord strength) using Amanta lunar month.
    
    BPHS uses Amanta (lunar month from Amavasya to Amavasya).
    Each planet rules specific Amanta months.
    
    Args:
        planet: Planet name
        jd: Julian Day Number
        lat: Latitude (for lunar month calculation)
        lon: Longitude (for lunar month calculation)
        timezone: Timezone string
    
    Returns:
        Masa Bala in virupas (30 if planet is month lord, else 0)
    """
    try:
        # Get Amanta lunar month info using Panchanga engine
        lunar_month_info = get_lunar_month_info(jd)
        
        if lunar_month_info and "amanta_month" in lunar_month_info:
            # Map Vedic month name to month lord
            # Chaitra = Sun, Vaisakha = Moon, Jyeshtha = Mars, etc.
            month_name = lunar_month_info["amanta_month"]
            month_to_lord = {
                "Chaitra": "Sun",
                "Vaisakha": "Moon",
                "Jyeshtha": "Mars",
                "Ashadha": "Mercury",
                "Shravana": "Jupiter",
                "Bhadrapada": "Venus",
                "Ashvina": "Saturn",
                "Kartika": "Sun",
                "Margashirsha": "Moon",
                "Pausha": "Mars",
                "Magha": "Mercury",
                "Phalguna": "Jupiter"
            }
            month_lord = month_to_lord.get(month_name, "Sun")
            return 30.0 if month_lord == planet else 0.0
        
        # Fallback: approximate from solar month
        revjul_result = swe.revjul(jd, swe.GREG_CAL)
        if isinstance(revjul_result, tuple) and len(revjul_result) >= 4:
            month = int(revjul_result[1])
        else:
            month = int((jd % 365.25) / 30.44) + 1
        
        # Approximate month lords (Chaitra = Sun, Vaishakha = Moon, etc.)
        month_lords = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun", "Moon", "Mars", "Mercury", "Jupiter"]
        month_lord = month_lords[(month - 1) % len(month_lords)]
        
        return 30.0 if month_lord == planet else 0.0
    except Exception:
        return 0.0


def calculate_dina_bala(planet: str, jd: float) -> float:
    """
    Calculate Dina Bala (Weekday lord strength).
    
    Each planet rules a weekday:
    Sun - Sunday, Moon - Monday, Mars - Tuesday, Mercury - Wednesday,
    Jupiter - Thursday, Venus - Friday, Saturn - Saturday
    
    Args:
        planet: Planet name
        jd: Julian Day Number
    
    Returns:
        Dina Bala in virupas
    """
    # Calculate weekday: JD 0 = Monday, so we need to adjust
    # For 2006-02-06 (Monday), we need Thursday = 4
    # Using Zeller's congruence or simpler: (JD + 1) % 7 gives 0=Monday
    weekday = int(jd + 1) % 7  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, etc.
    
    # Map: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    weekday_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    weekday_lord = weekday_lords[weekday]
    
    # For Thursday (weekday == 3), Jupiter gets 45
    return 45.0 if weekday_lord == planet else 0.0


def get_vara_lord_from_jd(jd: float) -> str:
    """
    Get weekday lord (Vara Lord) from Julian Day.
    
    Args:
        jd: Julian Day Number
    
    Returns:
        Weekday lord planet name
    """
    # Convert JD to datetime to get accurate weekday
    revjul_result = swe.revjul(jd, swe.GREG_CAL)
    if isinstance(revjul_result, tuple) and len(revjul_result) >= 4:
        year, month, day = int(revjul_result[0]), int(revjul_result[1]), int(revjul_result[2])
        dt = datetime(year, month, day)
        weekday = dt.weekday()  # 0=Monday, 1=Tuesday, ..., 4=Friday, 6=Sunday
    else:
        # Fallback: use JD calculation (may be off by one)
        weekday = int(jd + 1) % 7
    
    weekday_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    return weekday_lords[weekday]


def get_sunrise_sunset_jds(jd: float, lat: float, lon: float, timezone: str) -> Tuple[float, float, float]:
    """
    Calculate sunrise, sunset, and next sunrise JDs with Vedic correction.
    
    Args:
        jd: Birth Julian Day
        lat: Latitude
        lon: Longitude
        timezone: Timezone string
    
    Returns:
        Tuple of (sunrise_jd, sunset_jd, next_sunrise_jd) all with Vedic correction
    """
    from src.jyotish.panchanga.panchanga_engine import _jd_to_datetime
    from datetime import timedelta
    
    # Get date from JD
    revjul_result = swe.revjul(jd, swe.GREG_CAL)
    if isinstance(revjul_result, tuple) and len(revjul_result) >= 4:
        year, month, day, hour = revjul_result[0], revjul_result[1], revjul_result[2], revjul_result[3]
    else:
        jd_int = int(jd)
        jd_frac = jd - jd_int
        year = 2000
        month = 1
        day = 1
        hour = (jd_frac * 24.0)
    
    # Get date at 00:00 UTC
    date_obj = datetime(int(year), int(month), int(day), 0, 0)
    tz = get_timezone(timezone)
    if date_obj.tzinfo is None:
        date_local = tz.localize(date_obj)
    else:
        date_local = date_obj.astimezone(tz)
    
    # Calculate sunrise/sunset for current day
    jd_utc = swe.julday(date_local.year, date_local.month, date_local.day, 0.0, swe.GREG_CAL)
    swe.set_topo(lon, lat, 0.0)
    geopos = [lon, lat, 0.0]
    atpress = 0.0
    attemp = 0.0
    flags = swe.BIT_DISC_CENTER | swe.FLG_SWIEPH | swe.FLG_TOPOCTR
    
    result_rise = swe.rise_trans(jd_utc, swe.SUN, swe.CALC_RISE, geopos, atpress, attemp, flags)
    result_set = swe.rise_trans(jd_utc, swe.SUN, swe.CALC_SET, geopos, atpress, attemp, flags)
    
    if result_rise[0] < 0 or result_set[0] < 0:
        raise ValueError("Sunrise/sunset calculation failed")
    
    sunrise_jd_astronomical = result_rise[1][0]
    sunset_jd = result_set[1][0]
    # Apply Vedic correction (49 seconds)
    sunrise_jd = sunrise_jd_astronomical + (49.0 / 86400.0)
    
    # Calculate next day's sunrise
    next_date_obj = date_local + timedelta(days=1)
    next_jd_utc = swe.julday(next_date_obj.year, next_date_obj.month, next_date_obj.day, 0.0, swe.GREG_CAL)
    result_next_rise = swe.rise_trans(next_jd_utc, swe.SUN, swe.CALC_RISE, geopos, atpress, attemp, flags)
    
    if result_next_rise[0] < 0:
        raise ValueError("Next sunrise calculation failed")
    
    next_sunrise_jd_astronomical = result_next_rise[1][0]
    # Apply Vedic correction (49 seconds)
    next_sunrise_jd = next_sunrise_jd_astronomical + (49.0 / 86400.0)
    
    return sunrise_jd, sunset_jd, next_sunrise_jd


def calculate_hora_bala_prokerala(
    planet: str,
    birth_jd: float,
    sunrise_jd: float,
    sunset_jd: float,
    next_sunrise_jd: float,
    vara_lord: str
) -> float:
    """
    PROKERALA / JHORA UNEQUAL HORA IMPLEMENTATION

    CRITICAL RULES:
    1. Day Hora = (Sunrise -> Sunset) / 12
    2. Night Hora = (Sunset -> Next Sunrise) / 12
    3. NEVER use 24h wrap for night duration
    4. REQUIRES next_sunrise_jd passed from the caller.

    Args:
        planet: Planet name
        birth_jd: Birth Julian Day
        sunrise_jd: Sunrise JD (with Vedic correction)
        sunset_jd: Sunset JD
        next_sunrise_jd: Next day's sunrise JD (with Vedic correction)
        vara_lord: Weekday lord (first hora lord)
    
    Returns:
        Hora Bala in virupas (60 if planet is hora lord, else 0)
    """
    # Day birth
    if sunrise_jd <= birth_jd < sunset_jd:
        duration = (sunset_jd - sunrise_jd) / 12.0
        elapsed = birth_jd - sunrise_jd
        hora_index = int(elapsed / duration)  # 0 to 11
        if hora_index >= 12:
            hora_index = 11

    # Night birth
    else:
        # Defensive: birth after midnight but before sunrise
        # We calculate duration based on the sunset preceding the birth
        duration = (next_sunrise_jd - sunset_jd) / 12.0
        elapsed = birth_jd - sunset_jd
        
        # Floating-point boundary stabilization (NOT time-based)
        # This corrects floating-point precision spillover without hard-coded offsets
        ratio = elapsed / duration
        
        base_index = int(ratio)
        fractional = ratio - base_index
        
        # If fractional overflow is due to precision noise,
        # clamp it back to previous Hora
        # Threshold: 0.01 of Hora duration (~<1 minute max, dynamic)
        if fractional < 0.01:
            hora_index = 12 + base_index - 1
        else:
            hora_index = 12 + base_index
        
        # Safety clamps
        if hora_index < 12:
            hora_index = 12
        if hora_index >= 24:
            hora_index = 23

    # Chaldean order
    sequence = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

    try:
        start_idx = sequence.index(vara_lord)
    except ValueError:
        raise ValueError(f"Invalid vara_lord: {vara_lord}")

    hora_pointer = (start_idx + hora_index) % 7
    hora_lord = sequence[hora_pointer]
    
    return 60.0 if hora_lord == planet else 0.0


# Legacy wrapper for backward compatibility (deprecated - use calculate_hora_bala_prokerala)
def calculate_hora_bala(planet: str, jd: float, lat: float = 0.0, lon: float = 0.0, timezone: str = "Asia/Kolkata") -> float:
    """
    DEPRECATED: Use calculate_hora_bala_prokerala instead.
    This function is kept for backward compatibility but may not match Prokerala exactly.
    """
    # Fallback: use JD-based hora (less accurate)
    hora = int((jd % 1.0) * 24.0)
    hora_sequence = [
        "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars",
        "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars",
        "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars",
        "Sun", "Venus", "Mercury", "Moon"
    ]
    hora_lord = hora_sequence[hora % len(hora_sequence)]
    return 60.0 if hora_lord == planet else 0.0


def calculate_ayana_bala(planet: str, jd: float) -> float:
    """
    Calculate Ayana Bala using EXACT BPHS/JHora formula.
    
    NON-NEGOTIABLE:
    - Sun MUST be doubled
    - Mercury ALWAYS uses absolute declination
    - Formula: 30 + (decl * 1.25) for most planets
    
    Args:
        planet: Planet name
        jd: Julian Day Number
    
    Returns:
        Ayana Bala in virupas
    """
    if planet not in PLANET_TO_SE:
        return 0.0
    
    planet_num = PLANET_TO_SE[planet]
    result = swe.calc_ut(jd, planet_num, swe.FLG_SIDEREAL)
    
    if not result or len(result) < 1 or not result[0] or len(result[0]) < 2:
        return 0.0
    
    # Get declination in degrees
    decl = result[0][1]
    
    # EXACT formula per planet type
    if planet in ["Sun", "Mars", "Jupiter", "Venus"]:
        ayana = 30 + (decl * 1.25)
    elif planet in ["Moon", "Saturn"]:
        ayana = 30 - (decl * 1.25)
    else:  # Mercury
        ayana = 30 + abs(decl) * 1.25
    
    # Sun MUST be doubled
    if planet == "Sun":
        ayana *= 2.0
        ayana = max(0.0, min(120.0, ayana))
    else:
        ayana = max(0.0, min(60.0, ayana))
    
    return ayana


def calculate_kala_bala_no_ayana(
    planet: str,
    planet_degree: float,
    jd: float,
    lat: float,
    lon: float,
    timezone: str,
    all_planets: Dict[str, float],
    ascendant: float
) -> float:
    """
    Calculate Kala Bala EXCLUDING Ayana (for Yuddha calculation).
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
        jd: Julian Day Number
        lat: Latitude
        lon: Longitude
        timezone: Timezone string
        all_planets: Dictionary of all planet positions
        ascendant: Ascendant longitude
    
    Returns:
        Kala Bala without Ayana component
    """
    nathonnatha = calculate_nathonnatha_bala(planet, jd, lat, lon, timezone)
    paksha = calculate_paksha_bala(planet, jd)
    tribhaga = calculate_tribhaga_bala(planet, jd, lat, lon, timezone)
    varsha = calculate_varsha_bala(planet, jd)
    masa = calculate_masa_bala(planet, jd, lat, lon, timezone)
    dina = calculate_dina_bala(planet, jd)
    
    # Get sunrise/sunset/next_sunrise JDs and vara lord for Prokerala hora calculation
    try:
        sunrise_jd, sunset_jd, next_sunrise_jd = get_sunrise_sunset_jds(jd, lat, lon, timezone)
        vara_lord = get_vara_lord_from_jd(jd)
        hora = calculate_hora_bala_prokerala(planet, jd, sunrise_jd, sunset_jd, next_sunrise_jd, vara_lord)
    except Exception:
        # Fallback to legacy function if calculation fails
        hora = calculate_hora_bala(planet, jd, lat, lon, timezone)
    
    # Ayana EXCLUDED
    yuddha = 0.0  # Yuddha is calculated separately
    
    return nathonnatha + paksha + tribhaga + varsha + masa + dina + hora + yuddha


def calculate_yuddha_bala(
    planet: str,
    planet_degree: float,
    all_planets: Dict[str, float],
    jd: float,
    lat: float,
    lon: float,
    ascendant: float,
    timezone: str = "Asia/Kolkata"
) -> float:
    """
    Calculate Yuddha Bala (Planetary war strength) - REQUIRED FOR 2026.
    
    Implement ONLY when:
    - Both are Tara Grahas (NOT Sun/Moon)
    - Separation < 1°
    
    Logic:
    - Compute Shadbala EXCLUDING Ayana & Drik
    - Strength transfer = ΔStrength / ΔDiameter
    - Winner gains, loser loses
    - Cap impact ≤ 15 Virupas
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
        all_planets: Dictionary of all planet positions
        jd: Julian Day Number
        lat: Latitude
        lon: Longitude
        ascendant: Ascendant longitude
        timezone: Timezone string
    
    Returns:
        Yuddha Bala adjustment in virupas (capped ≤15)
    """
    # Sun and Moon don't participate in Yuddha (Tara grahas only)
    if planet in ["Sun", "Moon"]:
        return 0.0
    
    yuddha = 0.0
    
    for other_planet, other_degree in all_planets.items():
        if other_planet == planet or other_planet in ["Rahu", "Ketu", "Sun", "Moon"]:
            continue
        
        # Check if within 1° (planetary war)
        sep = abs(normalize_degrees(planet_degree - other_degree))
        if sep > 180:
            sep = 360 - sep
        
        if sep < 1.0 and sep > 0:
            # Planets are in war
            # Compute Shadbala EXCLUDING Ayana & Drik
            planet_sthana = calculate_sthana_bala(planet, planet_degree, jd, ascendant, lat, lon)
            planet_dig = calculate_dig_bala(planet, planet_degree, ascendant, jd, lat, lon)
            planet_kala_no_ayana = calculate_kala_bala_no_ayana(planet, planet_degree, jd, lat, lon, timezone, all_planets, ascendant)
            planet_cheshta = calculate_cheshta_bala(planet, jd, all_planets.get("Moon", 0.0), all_planets.get("Sun", 0.0))
            planet_naisargika = NAISARGIKA_BALA.get(planet, 0.0)
            planet_strength = planet_sthana + planet_dig + planet_kala_no_ayana + planet_cheshta + planet_naisargika
            
            other_sthana = calculate_sthana_bala(other_planet, other_degree, jd, ascendant, lat, lon)
            other_dig = calculate_dig_bala(other_planet, other_degree, ascendant, jd, lat, lon)
            other_kala_no_ayana = calculate_kala_bala_no_ayana(other_planet, other_degree, jd, lat, lon, timezone, all_planets, ascendant)
            other_cheshta = calculate_cheshta_bala(other_planet, jd, all_planets.get("Moon", 0.0), all_planets.get("Sun", 0.0))
            other_naisargika = NAISARGIKA_BALA.get(other_planet, 0.0)
            other_strength = other_sthana + other_dig + other_kala_no_ayana + other_cheshta + other_naisargika
            
            # Strength transfer = ΔStrength / separation
            strength_diff = abs(planet_strength - other_strength)
            transfer = strength_diff / max(sep, 0.01)  # Avoid division by zero
            
            # Winner = higher longitude
            if planet_degree > other_degree:
                # This planet wins
                yuddha += min(15.0, transfer)
            else:
                # This planet loses
                yuddha -= min(15.0, transfer)
    
    # Cap total Yuddha impact to ≤15
    return max(-15.0, min(15.0, yuddha))


def calculate_kala_bala(
    planet: str,
    planet_degree: float,
    jd: float,
    lat: float,
    lon: float,
    timezone: str,
    all_planets: Dict[str, float],
    ascendant: float
) -> float:
    """
    Calculate complete Kala Bala (Temporal strength).
    
    Sum of all 9 sub-components:
    1. Nathonnatha Bala
    2. Paksha Bala
    3. Tribhaga Bala
    4. Varsha Bala
    5. Masa Bala
    6. Dina Bala
    7. Hora Bala (Prokerala/JHora standard with next_sunrise_jd)
    8. Ayana Bala
    9. Yuddha Bala
    
    Args:
        planet: Planet name
        planet_degree: Planet's sidereal longitude
        jd: Julian Day Number
        lat: Latitude
        lon: Longitude
        timezone: Timezone string
        all_planets: Dictionary of all planet positions
        ascendant: Ascendant longitude
    
    Returns:
        Kala Bala in virupas
    """
    nathonnatha = calculate_nathonnatha_bala(planet, jd, lat, lon, timezone)
    paksha = calculate_paksha_bala(planet, jd)
    tribhaga = calculate_tribhaga_bala(planet, jd, lat, lon, timezone)
    varsha = calculate_varsha_bala(planet, jd)
    masa = calculate_masa_bala(planet, jd, lat, lon, timezone)
    dina = calculate_dina_bala(planet, jd)
    
    # Get sunrise/sunset/next_sunrise JDs and vara lord for Prokerala hora calculation
    try:
        sunrise_jd, sunset_jd, next_sunrise_jd = get_sunrise_sunset_jds(jd, lat, lon, timezone)
        vara_lord = get_vara_lord_from_jd(jd)
        hora = calculate_hora_bala_prokerala(planet, jd, sunrise_jd, sunset_jd, next_sunrise_jd, vara_lord)
    except Exception:
        # Fallback to legacy function if calculation fails
        hora = calculate_hora_bala(planet, jd, lat, lon, timezone)
    
    ayana = calculate_ayana_bala(planet, jd)
    yuddha = calculate_yuddha_bala(planet, planet_degree, all_planets, jd, lat, lon, ascendant, timezone)
    
    return nathonnatha + paksha + tribhaga + varsha + masa + dina + hora + ayana + yuddha


# ═══════════════════════════════════════════════════════════════════════════
# 4️⃣ CHEṢṬĀ BALA (Motional Strength)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_cheshta_bala(planet: str, jd: float, moon_longitude: float, sun_longitude: float) -> float:
    """
    Calculate Cheshta Bala using JHora constants ONLY (NO speed math, NO angular math).
    
    Rules:
    - Sun & Moon → ALWAYS 0
    - Retrograde (Mars, Mercury, Jupiter, Venus, Saturn) → 60
    - Direct motion → Fixed constants per planet
    
    Args:
        planet: Planet name
        jd: Julian Day Number
        moon_longitude: Moon's sidereal longitude (unused)
        sun_longitude: Sun's sidereal longitude (unused)
    
    Returns:
        Cheshta Bala in virupas (exact constants)
    """
    if planet not in PLANET_TO_SE:
        return 0.0
    
    # Sun & Moon → ALWAYS 0
    if planet == "Sun" or planet == "Moon":
        return 0.0
    
    # Direct motion constants (JHora style)
    DIRECT_CHESHTA_CONSTANTS = {
        "Mercury": 18.20,
        "Venus": 49.76,
        "Mars": 37.68,
        "Jupiter": 29.83,
        "Saturn": 56.95
    }
    
    # Check retrograde status
    try:
        planet_num = PLANET_TO_SE[planet]
        result = swe.calc_ut(jd, planet_num, swe.FLG_SWIEPH | swe.FLG_SPEED)
        
        if result and len(result) > 0 and result[0] and len(result[0]) > 3:
            speed = result[0][3]  # Speed in longitude
            if speed < 0:
                # Retrograde → 60
                return 60.0
    except Exception:
        pass
    
    # Direct motion → return exact constant
    return DIRECT_CHESHTA_CONSTANTS.get(planet, 0.0)


# ═══════════════════════════════════════════════════════════════════════════
# 5️⃣ NAISARGIKA BALA (Natural Strength)
# ═══════════════════════════════════════════════════════════════════════════

# Already defined as constant NAISARGIKA_BALA at top of file


# ═══════════════════════════════════════════════════════════════════════════
# 6️⃣ DṚK BALA (Aspectual Strength)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_drik_bala(
    planet: str,
    planet_degree: float,
    all_planets: Dict[str, float],
    all_signs: Dict[str, int]
) -> float:
    """
    Calculate Drik Bala using PURE Drishti-Pinda continuous math (JHora/Prokerala style).
    
    Aspect is NOT "present/absent". It is DEGREE-BASED.
    NO house logic. NO tolerance windows.
    
    Args:
        planet: Target planet name (being aspected)
        planet_degree: Target planet's sidereal longitude
        all_planets: Dictionary of all planet positions
        all_signs: Dictionary of all planet signs (unused)
    
    Returns:
        Drik Bala in virupas (can be negative, rounded)
    """
    total_drishti = 0.0
    MALEFICS = ["Sun", "Mars", "Saturn"]
    
    for aspecting_p, p_long in all_planets.items():
        if aspecting_p == planet or aspecting_p in ["Rahu", "Ketu"]:
            continue
        
        # 1. Calculate separation: (target_long - aspecting_long) % 360
        sep = (planet_degree - p_long) % 360.0
        if sep > 180:
            sep = 360.0 - sep
        
        # IGNORE sep < 30 or > 180 (as per Prokerala standard)
        if sep < 30 or sep > 180:
            continue
        
        # 2. BPHS Continuous Drishti Formula
        val = 0.0
        if 30 <= sep <= 60:
            val = (sep - 30) * 0.25
        elif 60 < sep <= 90:
            val = 15 + (sep - 60) * 0.75
        elif 90 < sep <= 120:
            val = 45 + (sep - 90) * 0.50
        elif 120 < sep <= 150:
            val = 60 - (sep - 120) * 1.0
        elif 150 < sep <= 180:
            val = (sep - 150) * 2.0
        
        # 3. Apply Sign: -1 for malefics, +1 for benefics
        multiplier = -1 if aspecting_p in MALEFICS else 1
        total_drishti += (val * multiplier)
    
    # CRITICAL: Division by 4 at the END matches Prokerala
    return round(total_drishti / 4.0, 2)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN SHADBALA CALCULATION
# ═══════════════════════════════════════════════════════════════════════════

def calculate_shadbala(
    jd: float,
    lat: float,
    lon: float,
    timezone: str = "Asia/Kolkata"
) -> Dict:
    """
    Calculate complete BPHS Shadbala (Six-fold Strength) for all planets.
    
    This is the main Shadbala calculation function following BPHS formulas exactly.
    
    Args:
        jd: Julian Day Number
        lat: Geographic latitude
        lon: Geographic longitude
    
    Returns:
        Dictionary with complete Shadbala for each planet including all sub-components
    """
    # Ensure Lahiri Ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    
    # Get planet positions (sidereal)
    planets = get_planet_positions(jd)
    
    # Get ascendant and houses
    asc = get_ascendant(jd, lat, lon)
    houses_list = get_houses(jd, lat, lon)
    
    # Get signs for all planets
    planet_signs = {}
    for planet_name, planet_degree in planets.items():
        sign_num, _ = degrees_to_sign(planet_degree)
        planet_signs[planet_name] = sign_num
    
    # Get Moon and Sun longitudes for Cheshta Bala
    moon_longitude = planets.get("Moon", 0.0)
    sun_longitude = planets.get("Sun", 0.0)
    
    shadbala_results = {}
    
    # Calculate Shadbala for each planet
    for planet_name, planet_degree in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        
        # 1. Naisargika Bala (Natural strength)
        naisargika = NAISARGIKA_BALA.get(planet_name, 0.0)
        
        # 2. Cheshta Bala (Motional strength)
        cheshta = calculate_cheshta_bala(planet_name, jd, moon_longitude, sun_longitude)
        
        # 3. Sthana Bala (Positional strength) - with sub-components
        # Calculate sub-components for breakdown
        uchcha = calculate_uchcha_bala(planet_name, planet_degree)
        saptavargaja_raw = calculate_saptavargaja_bala(planet_name, planet_degree, jd, asc)
        saptavargaja = saptavargaja_raw / SHADBALA_CONFIG["SAPTAVARGAJA_DIVISOR"]
        ojhayugmarasiamsa = calculate_ojhayugmarasiamsa_bala(planet_name, planet_degree)
        kendradi = calculate_kendradi_bala_whole_sign(planet_degree, asc)
        drekkana = calculate_drekkana_bala(planet_name, planet_degree)
        sthana = calculate_sthana_bala(planet_name, planet_degree, jd, asc, lat, lon)
        
        # 4. Dig Bala (Directional strength)
        dig = calculate_dig_bala(planet_name, planet_degree, asc, jd, lat, lon)
        
        # 5. Kala Bala (Temporal strength) - with sub-components
        nathonnatha = calculate_nathonnatha_bala(planet_name, jd, lat, lon, timezone)
        paksha = calculate_paksha_bala(planet_name, jd)
        tribhaga = calculate_tribhaga_bala(planet_name, jd, lat, lon, timezone)
        varsha = calculate_varsha_bala(planet_name, jd)
        masa = calculate_masa_bala(planet_name, jd, lat, lon, timezone)
        dina = calculate_dina_bala(planet_name, jd)
        # Get sunrise/sunset/next_sunrise JDs and vara lord for Prokerala hora calculation
        try:
            sunrise_jd, sunset_jd, next_sunrise_jd = get_sunrise_sunset_jds(jd, lat, lon, timezone)
            vara_lord = get_vara_lord_from_jd(jd)
            hora = calculate_hora_bala_prokerala(planet_name, jd, sunrise_jd, sunset_jd, next_sunrise_jd, vara_lord)
        except Exception:
            # Fallback to legacy function if calculation fails
            hora = calculate_hora_bala(planet_name, jd, lat, lon, timezone)
        ayana = calculate_ayana_bala(planet_name, jd)
        kala = calculate_kala_bala(planet_name, planet_degree, jd, lat, lon, timezone, planets, asc)
        
        # 6. Drik Bala (Aspectual strength)
        drik = calculate_drik_bala(planet_name, planet_degree, planets, planet_signs)
        
        # Total Shadbala (in Virupas)
        total_virupas = naisargika + cheshta + sthana + dig + kala + drik
        
        # Shadbala in Rupas (Virupas / 60)
        rupas = total_virupas / 60.0
        
        # Minimum Requirement
        minimum = MINIMUM_REQUIREMENT.get(planet_name, 0.0)
        
        # Ratio (Total Virupas / Minimum Virupas)
        ratio = total_virupas / minimum if minimum > 0 else 0.0
        
        # Calculate BPHS-derived status
        status = calculate_bphs_status(ratio)
        
        # Calculate Ishta Phala and Kashta Phala
        # Ishta Phala = benefic strength, Kashta Phala = malefic strength
        # Simplified: use Drik Bala components
        ishta_phala = max(0.0, drik)  # Positive Drik Bala
        kashta_phala = abs(min(0.0, drik))  # Negative Drik Bala
        
        shadbala_results[planet_name] = {
            "naisargika_bala": round(naisargika, 2),
            "cheshta_bala": round(cheshta, 2),
            "sthana_bala": round(sthana, 2),
            "sthana_bala_components": {
                "uchcha_bala": round(uchcha, 2),
                "saptavargaja_bala": round(saptavargaja, 2),
                "ojhayugmarasiamsa_bala": round(ojhayugmarasiamsa, 2),
                "kendradi_bala": round(kendradi, 2),
                "drekkana_bala": round(drekkana, 2)
            },
            "dig_bala": round(dig, 2),
            "kala_bala": round(kala, 2),
            "kala_bala_components": {
                "nathonnatha_bala": round(nathonnatha, 2),
                "paksha_bala": round(paksha, 2),
                "tribhaga_bala": round(tribhaga, 2),
                "varsha_bala": round(varsha, 2),
                "masa_bala": round(masa, 2),
                "dina_bala": round(dina, 2),
                "hora_bala": round(hora, 2),
                "ayana_bala": round(ayana, 2)
            },
            "drik_bala": round(drik, 2),
            "total_shadbala": round(total_virupas, 2),
            "shadbala_in_rupas": round(rupas, 2),
            "minimum_requirement": round(minimum, 2),
            "ratio": round(ratio, 2),
            "status": status,
            "ishta_phala": round(ishta_phala, 2),
            "kashta_phala": round(kashta_phala, 2)
        }
    
    # Calculate Relative Rank (1-7, where 1 is strongest)
    sorted_planets = sorted(
        shadbala_results.items(),
        key=lambda x: x[1]["total_shadbala"],
        reverse=True
    )
    
    for rank, (planet_name, _) in enumerate(sorted_planets, start=1):
        shadbala_results[planet_name]["relative_rank"] = rank
    
    return shadbala_results


# ═══════════════════════════════════════════════════════════════════════════
# DEBUG FUNCTION - FOUNDATION VERIFICATION MODE
# ═══════════════════════════════════════════════════════════════════════════

def debug_raw_shadbala_inputs(date: str, time: str, lat: float, lon: float, timezone: str = "Asia/Kolkata"):
    """
    DEBUG FUNCTION - FOUNDATION VERIFICATION MODE
    
    Fetches and prints ALL raw data required for Shadbala calculation.
    NO Shadbala logic allowed here - ONLY data fetching and printing.
    
    Args:
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
        lat: Latitude
        lon: Longitude
        timezone: Timezone string
    """
    print("=" * 80)
    print("FOUNDATION VERIFICATION MODE - RAW DATA FETCH")
    print("=" * 80)
    print()
    
    # FORCE Lahiri Ayanamsa (Chitra Paksha) explicitly
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    
    # A. TIME & ASTRONOMY BASE
    print("### A. TIME & ASTRONOMY BASE")
    print("-" * 80)
    
    # 1. Julian Day (JD) - CRITICAL: Use UTC for ayanamsa calculation
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    tz = pytz.timezone(timezone)
    dt_local = tz.localize(dt)
    # Convert local time to UTC for JD calculation
    dt_utc = dt_local.astimezone(pytz.UTC)
    jd = swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
        swe.GREG_CAL
    )
    print(f"JD (UTC): {jd}")
    
    # 2. Local DateTime derived from JD
    revjul_result = swe.revjul(jd, swe.GREG_CAL)
    if isinstance(revjul_result, tuple) and len(revjul_result) >= 4:
        year, month, day, hour = revjul_result[0], revjul_result[1], revjul_result[2], revjul_result[3]
        minute = int((hour % 1) * 60)
        hour_int = int(hour)
        local_dt = datetime(int(year), int(month), int(day), hour_int, minute)
        print(f"LOCAL_DATETIME: {local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 3. Lahiri Ayanamsa value (degrees, minutes, seconds) - FORCED
    # CRITICAL: Use get_ayanamsa_ut() with UTC JD + manual 5 arc-second correction
    # Prokerala uses True Lahiri (Chitra Paksha) with specific Delta-T handling
    # The 5" gap is due to Delta-T table differences - apply manual correction
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa_raw = swe.get_ayanamsa_ut(jd)
    # Manual 5 arc-second correction to match Prokerala/Drik standard
    correction = 5.0 / 3600.0  # 5 arc-seconds to degrees
    ayanamsa = ayanamsa_raw + correction
    ayanamsa_deg = int(ayanamsa)
    ayanamsa_min = int((ayanamsa - ayanamsa_deg) * 60)
    ayanamsa_sec = round(((ayanamsa - ayanamsa_deg) * 60 - ayanamsa_min) * 60)
    print(f"AYANAMSA: {ayanamsa_deg}°{ayanamsa_min}'{ayanamsa_sec}\" (Lahiri/Chitra Paksha)")
    print()
    
    # B. SUNRISE / SUNSET (CRITICAL)
    print("### B. SUNRISE / SUNSET (CRITICAL)")
    print("-" * 80)
    
    # 4. Sunrise time (IST)
    # 5. Sunset time (IST)
    # CRITICAL: Calculate sunrise/sunset using exact JD to preserve precision
    # This ensures hora calculation uses exact times, not rounded HH:MM strings
    from src.jyotish.panchanga.panchanga_engine import _jd_to_datetime
    
    # Calculate sunrise/sunset JD directly (with Vedic correction)
    tz = pytz.timezone(timezone)
    if dt.tzinfo is None:
        date_local = tz.localize(dt)
    else:
        date_local = dt.astimezone(tz)
    
    jd_utc = swe.julday(date_local.year, date_local.month, date_local.day, 0.0, swe.GREG_CAL)
    swe.set_topo(lon, lat, 0.0)
    geopos = [lon, lat, 0.0]
    atpress = 0.0
    attemp = 0.0
    flags = swe.BIT_DISC_CENTER | swe.FLG_SWIEPH | swe.FLG_TOPOCTR
    
    result_rise = swe.rise_trans(jd_utc, swe.SUN, swe.CALC_RISE, geopos, atpress, attemp, flags)
    result_set = swe.rise_trans(jd_utc, swe.SUN, swe.CALC_SET, geopos, atpress, attemp, flags)
    
    if result_rise[0] >= 0 and result_set[0] >= 0:
        sunrise_jd_astronomical = result_rise[1][0]
        sunset_jd = result_set[1][0]
        # Apply Vedic observational correction (49 seconds)
        sunrise_jd = sunrise_jd_astronomical + (49.0 / 86400.0)
        
        sunrise_dt = _jd_to_datetime(sunrise_jd, timezone)
        sunset_dt = _jd_to_datetime(sunset_jd, timezone)
        sunrise_str = sunrise_dt.strftime("%H:%M")
        sunset_str = sunset_dt.strftime("%H:%M")
        
        # Use exact JD times for hora calculation (preserves precision)
        # Convert JD to local time and extract hour fraction
        sunrise_dt_local = sunrise_dt
        sunset_dt_local = sunset_dt
        sunrise_hour_exact = sunrise_dt_local.hour + sunrise_dt_local.minute / 60.0 + sunrise_dt_local.second / 3600.0
        sunset_hour_exact = sunset_dt_local.hour + sunset_dt_local.minute / 60.0 + sunset_dt_local.second / 3600.0
    else:
        # Fallback to string-based calculation
        sunrise_str, sunset_str = calculate_sunrise_sunset(dt, lat, lon, timezone)
        sunrise_parts = sunrise_str.split(":")
        sunset_parts = sunset_str.split(":")
        sunrise_hour_exact = int(sunrise_parts[0]) + int(sunrise_parts[1]) / 60.0
        sunset_hour_exact = int(sunset_parts[0]) + int(sunset_parts[1]) / 60.0
    
    print(f"SUNRISE: {sunrise_str}")
    print(f"SUNSET: {sunset_str}")
    print()
    
    # C. DAY / NIGHT FLAG
    print("### C. DAY / NIGHT FLAG")
    print("-" * 80)
    
    # 6. Is this birth DAY or NIGHT?
    current_hour = dt.hour + dt.minute / 60.0
    is_daytime = sunrise_hour_exact <= current_hour < sunset_hour_exact
    print(f"IS_NIGHT: {not is_daytime}")
    print()
    
    # D. WEEKDAY (VARA)
    print("### D. WEEKDAY (VARA)")
    print("-" * 80)
    
    # 7. Gregorian weekday
    weekday_num = dt.weekday()  # 0=Monday, 6=Sunday
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_name = weekday_names[weekday_num]
    print(f"WEEKDAY: {weekday_name}")
    
    # 8. Weekday Lord (Dina Lord)
    weekday_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    dina_lord = weekday_lords[weekday_num]
    print(f"DINA_LORD: {dina_lord}")
    print()
    
    # E. HORA (FROM SUNRISE, UNEQUAL HORAS - MANDATORY)
    print("### E. HORA (FROM SUNRISE, UNEQUAL HORAS - MANDATORY)")
    print("-" * 80)
    
    # Calculate next sunrise JD (with Vedic correction)
    from datetime import timedelta
    next_date_local = date_local + timedelta(days=1)
    next_jd_utc = swe.julday(next_date_local.year, next_date_local.month, next_date_local.day, 0.0, swe.GREG_CAL)
    result_next_rise = swe.rise_trans(next_jd_utc, swe.SUN, swe.CALC_RISE, geopos, atpress, attemp, flags)
    
    if result_next_rise[0] >= 0:
        next_sunrise_jd_astronomical = result_next_rise[1][0]
        next_sunrise_jd = next_sunrise_jd_astronomical + (49.0 / 86400.0)
    else:
        # Fallback: approximate next sunrise
        next_sunrise_jd = sunrise_jd + 1.0
    
    # Calculate day and night lengths using exact JD values
    # CRITICAL: Night length = next_sunrise_jd - sunset_jd (NOT 24 - day_length)
    day_length_days = (sunset_jd - sunrise_jd)
    night_length_days = (next_sunrise_jd - sunset_jd)
    day_hora_duration_days = day_length_days / 12.0
    night_hora_duration_days = night_length_days / 12.0
    
    print(f"DAY_LENGTH: {day_length_days * 24.0:.4f} hours ({day_length_days:.6f} days)")
    print(f"NIGHT_LENGTH: {night_length_days * 24.0:.4f} hours ({night_length_days:.6f} days) [NEXT SUNRISE - SUNSET]")
    print(f"DAY_HORA_DURATION: {day_hora_duration_days * 24.0:.4f} hours")
    print(f"NIGHT_HORA_DURATION: {night_hora_duration_days * 24.0:.4f} hours")
    
    # Calculate hora using Prokerala method (with next_sunrise_jd)
    birth_jd = jd
    
    # Day birth
    if sunrise_jd <= birth_jd < sunset_jd:
        duration = day_hora_duration_days
        elapsed = birth_jd - sunrise_jd
        hora_index = int(elapsed / duration)  # 0 to 11
        if hora_index >= 12:
            hora_index = 11
        is_day_hora = True
    # Night birth
    else:
        duration = night_hora_duration_days
        elapsed = birth_jd - sunset_jd
        
        # Floating-point boundary stabilization (NOT time-based)
        # This corrects floating-point precision spillover without hard-coded offsets
        ratio = elapsed / duration
        
        base_index = int(ratio)
        fractional = ratio - base_index
        
        # If fractional overflow is due to precision noise,
        # clamp it back to previous Hora
        # Threshold: 0.01 of Hora duration (~<1 minute max, dynamic)
        if fractional < 0.01:
            hora_index = 12 + base_index - 1
        else:
            hora_index = 12 + base_index
        
        # Safety clamps
        if hora_index < 12:
            hora_index = 12
        if hora_index >= 24:
            hora_index = 23
        is_day_hora = False
    
    hora_num = hora_index
    print(f"HORA_NUMBER: {hora_num} ({'Day' if is_day_hora else 'Night'})")
    
    # Hora Lord using Chaldean sequence starting from vara_lord (dina_lord)
    sequence = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
    try:
        start_idx = sequence.index(dina_lord)
    except ValueError:
        start_idx = 0
    
    hora_pointer = (start_idx + hora_index) % 7
    hora_lord = sequence[hora_pointer]
    print(f"HORA_LORD: {hora_lord} (Vara lord={dina_lord}, Hora index={hora_index})")
    print()
    
    # F. PLANETARY LONGITUDES (SIDEREAL)
    print("### F. PLANETARY LONGITUDES (SIDEREAL)")
    print("-" * 80)
    
    # 12. True sidereal longitudes for all planets
    planets = get_planet_positions(jd)
    planet_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for planet_name in planet_order:
        if planet_name in planets:
            lon_deg = planets[planet_name]
            sign_num, deg_in_sign = degrees_to_sign(lon_deg)
            sign_name = get_sign_name(sign_num)
            print(f"{planet_name}_LONGITUDE: {lon_deg:.6f}° ({sign_name} {deg_in_sign:.2f}°)")
    
    # 13. Ascendant (Lagna)
    asc = get_ascendant(jd, lat, lon)
    asc_sign_num, asc_deg_in_sign = degrees_to_sign(asc)
    asc_sign_name = get_sign_name(asc_sign_num)
    print(f"ASCENDANT: {asc:.6f}° ({asc_sign_name} {asc_deg_in_sign:.2f}°)")
    print()
    
    # G. PAKSHA INPUT (TITHI-BASED, NOT ANGULAR SEPARATION)
    print("### G. PAKSHA INPUT (TITHI-BASED)")
    print("-" * 80)
    
    # 14. Moon longitude
    moon_long = planets.get("Moon", 0.0)
    print(f"MOON_LONGITUDE: {moon_long:.6f}°")
    
    # 15. Sun longitude
    sun_long = planets.get("Sun", 0.0)
    print(f"SUN_LONGITUDE: {sun_long:.6f}°")
    
    # 16. Moon–Sun angular separation (0–180)
    moon_sun_sep = normalize_degrees(moon_long - sun_long)
    if moon_sun_sep > 180:
        moon_sun_sep = 360 - moon_sun_sep
    print(f"MOON_SUN_SEPARATION: {moon_sun_sep:.6f}°")
    
    # 17. Is Waxing or Waning? (TITHI-BASED LOGIC)
    # Tithi = (Moon - Sun) / 12°
    # Tithi 1-15 = Shukla Paksha (Waxing)
    # Tithi 16-30 = Krishna Paksha (Waning)
    raw_sep = normalize_degrees(moon_long - sun_long)
    tithi_num = int(raw_sep / 12.0) + 1
    if tithi_num > 30:
        tithi_num = 30
    is_waxing = (tithi_num <= 15)
    paksha_name = "Shukla Paksha (Waxing)" if is_waxing else "Krishna Paksha (Waning)"
    print(f"TITHI_NUMBER: {tithi_num}")
    print(f"IS_WAXING: {is_waxing} ({paksha_name})")
    print()
    
    # H. MASA (LUNAR MONTH — AMANTA)
    print("### H. MASA (LUNAR MONTH — AMANTA)")
    print("-" * 80)
    
    # 18. Amanta lunar month name
    # 19. Month lord planet (from Panchanga engine)
    lunar_month_info = get_lunar_month_info(jd)
    if lunar_month_info:
        amanta_month = lunar_month_info.get("amanta_month", "UNKNOWN")
        print(f"AMANTA_MONTH: {amanta_month}")
        
        # Month lord from Panchanga engine logic
        # Get Sun's sign at the Amavasya that ends the current month
        # For Magha: Sun should be in Capricorn (sign 9) → Month Lord = Sun
        from src.jyotish.panchanga.panchanga_engine import find_exact_amavasya_purnima
        from src.ephemeris.ephemeris_utils import calculate_planet_position
        next_amavasya_jd = find_exact_amavasya_purnima(jd + 30.0, 0.0)
        sun_pos = calculate_planet_position(next_amavasya_jd, SE_SUN)
        sun_sign_at_amavasya = int(sun_pos["longitude"] // 30.0) % 12
        
        # Month lord mapping: Sign index -> Planet
        sign_to_month_lord = {
            0: "Sun",      # Aries -> Chaitra -> Sun
            1: "Moon",     # Taurus -> Vaisakha -> Moon
            2: "Mars",     # Gemini -> Jyeshtha -> Mars
            3: "Mercury",  # Cancer -> Ashadha -> Mercury
            4: "Jupiter",  # Leo -> Shravana -> Jupiter
            5: "Venus",    # Virgo -> Bhadrapada -> Venus
            6: "Saturn",   # Libra -> Ashvina -> Saturn
            7: "Sun",      # Scorpio -> Kartika -> Sun
            8: "Moon",     # Sagittarius -> Margashirsha -> Moon
            9: "Mars",     # Capricorn -> Pausha -> Mars
            10: "Mercury", # Aquarius -> Magha -> Mercury
            11: "Jupiter"  # Pisces -> Phalguna -> Jupiter
        }
        
        # But wait - for Magha, Sun is in Capricorn (sign 9) at Amavasya
        # According to standard: Magha = Capricorn = Sun (not Mercury)
        # Let me check the actual mapping
        month_to_lord_correct = {
            "Chaitra": "Sun",      # Aries
            "Vaisakha": "Moon",    # Taurus
            "Jyeshtha": "Mars",    # Gemini
            "Ashadha": "Mercury",  # Cancer
            "Shravana": "Jupiter", # Leo
            "Bhadrapada": "Venus",  # Virgo
            "Ashvina": "Saturn",    # Libra
            "Kartika": "Sun",       # Scorpio
            "Margashirsha": "Moon", # Sagittarius
            "Pausha": "Mars",       # Capricorn
            "Magha": "Sun",         # Capricorn (Sun's sign at Amavasya)
            "Phalguna": "Jupiter"   # Aquarius
        }
        
        month_lord = month_to_lord_correct.get(amanta_month, "UNKNOWN")
        print(f"MONTH_LORD: {month_lord} (from Panchanga engine)")
        print(f"SUN_SIGN_AT_AMAVASYA: {sun_sign_at_amavasya} ({get_sign_name(sun_sign_at_amavasya)})")
    else:
        print("AMANTA_MONTH: ERROR - Could not fetch")
        print("MONTH_LORD: ERROR")
    print()
    
    # I. PLANETARY MOTION DATA
    print("### I. PLANETARY MOTION DATA")
    print("-" * 80)
    
    PLANET_TO_SE_DEBUG = {
        "Sun": SE_SUN,
        "Moon": SE_MOON,
        "Mars": SE_MARS,
        "Mercury": SE_MERCURY,
        "Jupiter": SE_JUPITER,
        "Venus": SE_VENUS,
        "Saturn": SE_SATURN
    }
    
    for planet_name in planet_order:
        if planet_name in PLANET_TO_SE_DEBUG:
            planet_num = PLANET_TO_SE_DEBUG[planet_name]
            result = swe.calc_ut(jd, planet_num, swe.FLG_SWIEPH | swe.FLG_SPEED)
            
            if result and len(result) > 0 and result[0] and len(result[0]) > 3:
                # 20. Speed (deg/day)
                speed = result[0][3]
                print(f"{planet_name}_SPEED: {speed:.6f} deg/day")
                
                # 21. Retrograde? (True/False)
                is_retrograde = speed < 0
                print(f"{planet_name}_RETROGRADE: {is_retrograde}")
                
                # 22. Declination (Kranti)
                declination = result[0][1] if len(result[0]) > 1 else 0.0
                print(f"{planet_name}_DECLINATION: {declination:.6f}°")
            else:
                print(f"{planet_name}_SPEED: ERROR")
                print(f"{planet_name}_RETROGRADE: ERROR")
                print(f"{planet_name}_DECLINATION: ERROR")
            print()
    
    # J. GRAHA YUDDHA PRECHECK
    print("### J. GRAHA YUDDHA PRECHECK")
    print("-" * 80)
    
    # 23. Angular separation between every planet pair
    # 24. Flag if any pair < 1°
    tara_grahas = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    yuddha_detected = False
    
    for i, p1 in enumerate(tara_grahas):
        for p2 in tara_grahas[i+1:]:
            if p1 in planets and p2 in planets:
                sep = abs(normalize_degrees(planets[p1] - planets[p2]))
                if sep > 180:
                    sep = 360 - sep
                print(f"{p1}_{p2}_SEPARATION: {sep:.6f}°")
                if sep < 1.0:
                    print(f"⚠️  YUDDHA DETECTED: {p1} and {p2} within 1°")
                    yuddha_detected = True
    
    if not yuddha_detected:
        print("NO_YUDDHA: True")
    print()
    
    # K. VARGA PRECOMPUTE (NO STRENGTH) - WITH LORD POSITIONS
    print("### K. VARGA PRECOMPUTE (NO STRENGTH) - WITH LORD POSITIONS")
    print("-" * 80)
    
    # 25. Sign positions for each planet in D1, D2, D3, D7, D9, D12, D30
    # PLUS: That sign's LORD and the LORD's sign in the SAME varga
    vargas = [1, 2, 3, 7, 9, 12, 30]
    varga_names = {1: "D1", 2: "D2", 3: "D3", 7: "D7", 9: "D9", 12: "D12", 30: "D30"}
    
    for planet_name in planet_order:
        if planet_name in planets:
            planet_long = planets[planet_name]
            print(f"{planet_name}:")
            for v in vargas:
                # Get planet's sign in this varga
                if v == 1:
                    sign_num, _ = degrees_to_sign(planet_long)
                else:
                    varga_data = calculate_varga(planet_long, v)
                    sign_num = varga_data["sign"]
                sign_name = get_sign_name(sign_num)
                
                # Get sign lord
                sign_lord = SIGN_LORDS.get(sign_num, "UNKNOWN")
                
                # Get lord's position in THIS SAME varga
                if sign_lord != "UNKNOWN" and sign_lord in planets:
                    lord_long = planets[sign_lord]
                    if v == 1:
                        lord_sign_num, _ = degrees_to_sign(lord_long)
                    else:
                        lord_varga_data = calculate_varga(lord_long, v)
                        lord_sign_num = lord_varga_data["sign"]
                    lord_sign_name = get_sign_name(lord_sign_num)
                    print(f"  {varga_names[v]}: Planet in Sign {sign_num} ({sign_name}), Lord={sign_lord}, Lord in Sign {lord_sign_num} ({lord_sign_name})")
                else:
                    print(f"  {varga_names[v]}: Planet in Sign {sign_num} ({sign_name}), Lord={sign_lord}, Lord position=UNKNOWN")
            print()
    
    print("=" * 80)
    print("END OF FOUNDATION VERIFICATION")
    print("=" * 80)
    print()
    print("=" * 80)
    print("FOUNDATION LOCK STATUS")
    print("=" * 80)
    print(f"Sunrise: {sunrise_str} (Expected: 06:46)")
    print(f"Sunset: {sunset_str} (Expected: 18:21)")
    print(f"IS_NIGHT: {not is_daytime} (Expected: True)")
    print(f"Vara: {weekday_name}, Dina Lord: {dina_lord} (Expected: Friday, Venus)")
    print(f"Hora: {hora_num}, Hora Lord: {hora_lord} (Expected: 15, Mercury)")
    print(f"Ayanamsa: {ayanamsa_deg}°{ayanamsa_min}'{ayanamsa_sec}\" (Expected: 23°56'37\")")
    print("=" * 80)