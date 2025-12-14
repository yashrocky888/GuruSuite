"""
Panchang calculation module.

Panchang provides five essential elements of a day:
1. Tithi - Lunar day
2. Nakshatra - Lunar mansion
3. Yoga - Combination of Sun and Moon
4. Karana - Half of a tithi
5. Vaar - Day of the week

Phase 3: Added core nakshatra calculation functions for Vimshottari Dasha.
"""

from typing import Dict, Tuple
from datetime import datetime
from math import floor

from src.ephemeris.planets import calculate_planets_sidereal
from src.utils.timezone import local_to_utc
from src.utils.converters import normalize_degrees, get_nakshatra_name


# Phase 3: Complete Nakshatra list (27 nakshatras)
NAKSHATRA_LIST = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

# Phase 3: Nakshatra Lords in exact order (repeats every 9 nakshatras)
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]


def get_nakshatra(moon_degree: float) -> Tuple[str, int]:
    """
    Phase 3: Get nakshatra name and index from Moon's degree.
    
    Each Nakshatra = 13°20' = 13.333333 degrees
    Formula: nakshatra_index = int(moon_degree / (13 + 20/60))
    
    Args:
        moon_degree: Moon's sidereal longitude in degrees (0-360)
    
    Returns:
        Tuple of (nakshatra_name, nakshatra_index) where index is 0-26
    """
    moon_degree = normalize_degrees(moon_degree)
    part = 13 + 20/60  # 13.333333 degrees
    index = int(moon_degree // part)
    
    # Ensure index is within valid range (0-26)
    if index >= 27:
        index = 26
    elif index < 0:
        index = 0
    
    return NAKSHATRA_LIST[index], index


def get_nakshatra_lord(nak_index: int) -> str:
    """
    Phase 3: Get the lord of a nakshatra by its index.
    
    Nakshatra lords repeat every 9 nakshatras:
    ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
    
    Args:
        nak_index: Nakshatra index (0-26)
    
    Returns:
        Planet name that rules the nakshatra
    """
    return NAKSHATRA_LORDS[nak_index % 9]


def get_nakshatra_pada(moon_degree: float) -> int:
    """
    Phase 3: Get nakshatra pada (quarter) from Moon's degree.
    
    Each nakshatra is divided into 4 padas.
    Each pada = 3°20' = 3.333333 degrees
    
    Args:
        moon_degree: Moon's sidereal longitude in degrees
    
    Returns:
        Pada number (1-4)
    """
    moon_degree = normalize_degrees(moon_degree)
    part = 13 + 20/60  # Full nakshatra span
    pada_size = part / 4  # Each pada = 3.333333 degrees
    
    degrees_in_nakshatra = moon_degree % part
    pada = int(degrees_in_nakshatra / pada_size) + 1
    
    if pada > 4:
        pada = 4
    
    return pada


# Tithi names (30 tithis in a lunar month)
TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
]

# Yoga names (27 yogas)
YOGA_NAMES = [
    "Vishkambha", "Preeti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

# Karana names (11 karanas)
KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara",
    "Vanija", "Visti", "Shakuni", "Chatushpada", "Naga",
    "Kimstughna"
]

# Day names
DAY_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday"
]


def calculate_tithi(sun_longitude: float, moon_longitude: float) -> Dict:
    """
    Calculate Tithi (lunar day).
    
    Tithi is the angular distance between Sun and Moon.
    Each tithi is 12 degrees (360 / 30).
    
    Args:
        sun_longitude: Sun's longitude
        moon_longitude: Moon's longitude
    
    Returns:
        Dictionary with tithi number and name
    """
    # Calculate angular difference
    diff = normalize_degrees(moon_longitude - sun_longitude)
    
    # Tithi number (1-30)
    tithi_number = int(diff / 12) + 1
    
    if tithi_number > 30:
        tithi_number = 30
    
    # Determine if it's Shukla Paksha (waxing) or Krishna Paksha (waning)
    paksha = "Shukla" if tithi_number <= 15 else "Krishna"
    if tithi_number > 15:
        tithi_number = tithi_number - 15
    
    return {
        "number": tithi_number,
        "name": TITHI_NAMES[tithi_number - 1],
        "paksha": paksha,
        "degrees": diff % 12
    }


def calculate_yoga(sun_longitude: float, moon_longitude: float) -> Dict:
    """
    Calculate Yoga (combination of Sun and Moon).
    
    Yoga is the sum of Sun and Moon longitudes divided by 13.33 degrees.
    There are 27 yogas.
    
    Args:
        sun_longitude: Sun's longitude
        moon_longitude: Moon's longitude
    
    Returns:
        Dictionary with yoga number and name
    """
    # Sum of Sun and Moon longitudes
    sum_longitude = normalize_degrees(sun_longitude + moon_longitude)
    
    # Yoga number (1-27)
    yoga_number = int(sum_longitude / (360.0 / 27)) + 1
    
    if yoga_number > 27:
        yoga_number = 27
    
    return {
        "number": yoga_number,
        "name": YOGA_NAMES[yoga_number - 1],
        "degrees": sum_longitude % (360.0 / 27)
    }


def calculate_karana(sun_longitude: float, moon_longitude: float) -> Dict:
    """
    Calculate Karana (half of a tithi).
    
    Each tithi has 2 karanas. There are 11 karanas total.
    First 7 karanas repeat, last 4 occur once per month.
    
    Args:
        sun_longitude: Sun's longitude
        moon_longitude: Moon's longitude
    
    Returns:
        Dictionary with karana number and name
    """
    # Calculate tithi
    diff = normalize_degrees(moon_longitude - sun_longitude)
    tithi_number = int(diff / 12) + 1
    
    # Karana number (1-11)
    # Each tithi has 2 karanas
    karana_in_tithi = int((diff % 12) / 6) + 1
    
    if tithi_number <= 15:
        # Shukla Paksha
        if tithi_number == 1:
            karana_number = 1 if karana_in_tithi == 1 else 2
        elif tithi_number == 15:
            karana_number = 10 if karana_in_tithi == 1 else 11
        else:
            karana_number = ((tithi_number - 1) * 2 + karana_in_tithi - 1) % 7 + 1
    else:
        # Krishna Paksha
        karana_number = ((tithi_number - 16) * 2 + karana_in_tithi) % 7 + 1
    
    return {
        "number": karana_number,
        "name": KARANA_NAMES[karana_number - 1]
    }


def calculate_panchang(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone: str
) -> Dict:
    """
    Calculate complete Panchang for a given date.
    
    Panchang includes:
    - Tithi (lunar day)
    - Nakshatra (lunar mansion)
    - Yoga (Sun-Moon combination)
    - Karana (half tithi)
    - Vaar (day of week)
    
    Args:
        date: Date to calculate panchang for
        latitude: Geographic latitude
        longitude: Geographic longitude
        timezone: Timezone string
    
    Returns:
        Complete panchang data
    """
    # Convert to UTC (use noon for calculations)
    date_noon = date.replace(hour=12, minute=0, second=0, microsecond=0)
    date_utc = local_to_utc(date_noon, timezone)
    
    # Calculate Sun and Moon positions
    planets = calculate_planets_sidereal(date_utc, latitude, longitude)
    sun_data = planets["Sun"]
    moon_data = planets["Moon"]
    
    # Calculate panchang elements
    tithi = calculate_tithi(sun_data["longitude"], moon_data["longitude"])
    nakshatra = {
        "number": moon_data["nakshatra"],
        "name": moon_data["nakshatra_name"],
        "pada": moon_data["pada"]
    }
    yoga = calculate_yoga(sun_data["longitude"], moon_data["longitude"])
    karana = calculate_karana(sun_data["longitude"], moon_data["longitude"])
    
    # Day of week
    day_of_week = date.weekday()
    vaar = DAY_NAMES[day_of_week]
    
    return {
        "date": date.isoformat(),
        "tithi": tithi,
        "nakshatra": nakshatra,
        "yoga": yoga,
        "karana": karana,
        "vaar": vaar,
        "sun": {
            "longitude": sun_data["longitude"],
            "sign": sun_data["sign_name"],
            "degrees": sun_data["degrees_in_sign"]
        },
        "moon": {
            "longitude": moon_data["longitude"],
            "sign": moon_data["sign_name"],
            "degrees": moon_data["degrees_in_sign"]
        }
    }

