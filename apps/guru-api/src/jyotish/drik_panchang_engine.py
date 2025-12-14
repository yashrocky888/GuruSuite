"""
Drik Panchang & JHORA Compatible Astrology Engine

This is the master engine that ensures ALL calculations match Drik Panchang and JHORA exactly.

Global Requirements:
- Swiss Ephemeris ONLY
- FLG_SWIEPH | FLG_SIDEREAL | FLG_TRUEPOS | FLG_SPEED
- Lahiri Ayanamsa (SE_SIDM_LAHIRI)
- TRUE NODE (not mean node)
- Proper IST → UTC → JD UT conversion
- All longitudes normalized 0-360
- All degrees converted to zodiac correctly
- All nakshatra logic: 13.333333333 degrees per nakshatra
- All padas: 3.333333333 degrees
"""

import swisseph as swe
from typing import Dict, List, Tuple
from datetime import datetime

from src.utils.converters import normalize_degrees
from src.utils.timezone import local_to_utc


# Global Drik Panchang Configuration
DRIK_FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TRUEPOS | swe.FLG_SPEED
DRIK_AYANAMSA = swe.SIDM_LAHIRI
DRIK_NODE = swe.TRUE_NODE  # Not mean node!

# Nakshatra constants (JHORA/Drik Panchang standard)
NAKSHATRA_SIZE = 360.0 / 27.0  # 13.333333333 degrees
PADA_SIZE = NAKSHATRA_SIZE / 4.0  # 3.333333333 degrees

# Rashi (Sign) names in Sanskrit (JHORA order)
RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]

# Nakshatra names (27 nakshatras, JHORA order)
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]


def init_drik_mode():
    """Initialize Swiss Ephemeris in Drik Panchang mode."""
    swe.set_sid_mode(DRIK_AYANAMSA, 0, 0)


def get_julian_day_utc(birth_date: datetime, birth_time: str, timezone: str) -> float:
    """
    Calculate Julian Day in UTC with exact precision (Drik Panchang method).
    
    Args:
        birth_date: Birth date
        birth_time: Birth time (HH:MM or HH:MM:SS)
        timezone: Timezone string (e.g., "Asia/Kolkata")
    
    Returns:
        Julian Day Number (UTC)
    """
    # Parse time with seconds precision
    time_parts = birth_time.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    second = int(time_parts[2]) if len(time_parts) > 2 else 0
    
    # Create local datetime
    birth_dt_local = datetime.combine(
        birth_date,
        datetime.min.time().replace(hour=hour, minute=minute, second=second, microsecond=0)
    )
    
    # Convert to UTC (India has NO DST)
    birth_dt_utc = local_to_utc(birth_dt_local, timezone)
    
    # Calculate Julian Day with full precision
    jd = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0,
        swe.GREG_CAL
    )
    
    return jd


def calculate_planet_drik(julian_day: float, planet_id: int) -> Dict:
    """
    Calculate planet position using Drik Panchang methodology.
    
    Args:
        julian_day: Julian Day Number (UTC)
        planet_id: Planet ID (SE_SUN, SE_MOON, etc.)
    
    Returns:
        Complete planet data with rashi, nakshatra, pada, retrograde
    """
    init_drik_mode()
    
    # Calculate with proper flags
    xx, ret = swe.calc_ut(julian_day, planet_id, DRIK_FLAGS)
    
    if ret < 0:
        raise ValueError(f"Error calculating planet {planet_id}: {ret}")
    
    # Extract data (already sidereal due to FLG_SIDEREAL)
    longitude = normalize_degrees(xx[0])
    latitude = xx[1]
    distance = xx[2]
    speed_longitude = xx[3]
    speed_latitude = xx[4]
    speed_distance = xx[5]
    
    # Get Rashi
    rashi_index = int(longitude / 30)
    degree_in_rashi = longitude % 30
    
    # Get Nakshatra and Pada (JHORA method)
    nakshatra_index = int(longitude / NAKSHATRA_SIZE)
    degree_in_nakshatra = longitude % NAKSHATRA_SIZE
    pada = int(degree_in_nakshatra / PADA_SIZE) + 1
    if pada > 4:
        pada = 4
    
    # Retrograde detection
    retro = (speed_longitude < 0)
    
    return {
        "longitude": longitude,
        "latitude": latitude,
        "distance": distance,
        "speed": speed_longitude,
        "rashi_index": rashi_index,
        "rashi": RASHI_NAMES[rashi_index],
        "degree_in_rashi": degree_in_rashi,
        "nakshatra_index": nakshatra_index,
        "nakshatra": NAKSHATRA_NAMES[nakshatra_index],
        "pada": pada,
        "retro": retro
    }


def calculate_all_planets_drik(julian_day: float) -> Dict[str, Dict]:
    """
    Calculate all planets using Drik Panchang methodology.
    
    Args:
        julian_day: Julian Day Number (UTC)
    
    Returns:
        Dictionary with all planet data
    """
    init_drik_mode()
    
    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": DRIK_NODE  # TRUE NODE
    }
    
    results = {}
    
    # Calculate all planets
    for planet_name, planet_id in planets.items():
        results[planet_name] = calculate_planet_drik(julian_day, planet_id)
    
    # Calculate Ketu (Rahu + 180 degrees, normalized)
    rahu_data = results["Rahu"]
    ketu_longitude = normalize_degrees(rahu_data["longitude"] + 180)
    
    # Get Ketu's Rashi and Nakshatra
    ketu_rashi_index = int(ketu_longitude / 30)
    ketu_degree_in_rashi = ketu_longitude % 30
    ketu_nakshatra_index = int(ketu_longitude / NAKSHATRA_SIZE)
    ketu_degree_in_nakshatra = ketu_longitude % NAKSHATRA_SIZE
    ketu_pada = int(ketu_degree_in_nakshatra / PADA_SIZE) + 1
    if ketu_pada > 4:
        ketu_pada = 4
    
    results["Ketu"] = {
        "longitude": ketu_longitude,
        "latitude": -rahu_data["latitude"],
        "distance": rahu_data["distance"],
        "speed": -rahu_data["speed"],  # Ketu speed is opposite
        "rashi_index": ketu_rashi_index,
        "rashi": RASHI_NAMES[ketu_rashi_index],
        "degree_in_rashi": ketu_degree_in_rashi,
        "nakshatra_index": ketu_nakshatra_index,
        "nakshatra": NAKSHATRA_NAMES[ketu_nakshatra_index],
        "pada": ketu_pada,
        "retro": True  # Ketu is always retrograde
    }
    
    return results


def calculate_houses_drik(julian_day: float, latitude: float, longitude: float, house_system: bytes = b'P') -> Dict:
    """
    Calculate houses using Drik Panchang methodology.
    
    Args:
        julian_day: Julian Day Number (UTC)
        latitude: Geographic latitude
        longitude: Geographic longitude
        house_system: House system ('P' for Placidus, 'W' for Whole Sign)
    
    Returns:
        Dictionary with ascendant and house cusps (sidereal)
    """
    init_drik_mode()
    
    # Calculate houses (tropical)
    result = swe.houses_ex(julian_day, latitude, longitude, house_system)
    
    if result is None or len(result) < 2:
        raise ValueError("Error calculating houses")
    
    cusps, ascmc = result
    
    # Get ayanamsa for sidereal conversion
    ayanamsa = swe.get_ayanamsa(julian_day)
    
    # Convert to sidereal
    asc_tropical = ascmc[0]
    asc_sidereal = normalize_degrees(asc_tropical - ayanamsa)
    
    # Convert house cusps to sidereal
    # cusps[0] is typically 0 or unused, cusps[1] through cusps[12] are house cusps
    houses_sidereal = []
    if len(cusps) >= 13:
        # Standard case: indices 1-12 are houses
        for i in range(1, 13):
            house_tropical = cusps[i]
            house_sidereal = normalize_degrees(house_tropical - ayanamsa)
            houses_sidereal.append(house_sidereal)
    elif len(cusps) == 12:
        # Alternative: indices 0-11 are houses
        for i in range(12):
            house_tropical = cusps[i]
            house_sidereal = normalize_degrees(house_tropical - ayanamsa)
            houses_sidereal.append(house_sidereal)
    else:
        raise ValueError(f"Unexpected cusps length: {len(cusps)}")
    
    return {
        "ascendant": asc_sidereal,
        "houses": houses_sidereal
    }

