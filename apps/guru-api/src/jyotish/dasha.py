"""
Dasha (Planetary Periods) calculation module.

This module provides functions to calculate Vimshottari Dasha system,
which is the most commonly used dasha system in Vedic astrology.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta

from src.ephemeris.planets import calculate_planets_sidereal
from src.utils.timezone import local_to_utc
from src.utils.converters import normalize_degrees, get_nakshatra_name


# Vimshottari Dasha periods (in years)
DASHA_PERIODS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17
}

# Nakshatra lords (in order of 27 nakshatras)
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]


def get_nakshatra_lord(nakshatra_number: int) -> str:
    """
    Get the lord of a nakshatra.
    
    Args:
        nakshatra_number: Nakshatra number (0-26)
    
    Returns:
        Planet name that rules the nakshatra
    """
    return NAKSHATRA_LORDS[nakshatra_number % 27]


def calculate_dasha_start_date(
    birth_date: datetime,
    moon_nakshatra: int,
    moon_longitude: float
) -> datetime:
    """
    Calculate the start date of the current dasha period.
    
    Each nakshatra is 13.333... degrees. We need to find how much
    of the nakshatra has elapsed at birth to determine when the
    dasha started.
    
    Args:
        birth_date: Birth date
        moon_nakshatra: Moon's nakshatra number (0-26)
        moon_longitude: Moon's longitude in degrees
    
    Returns:
        Start date of current dasha period
    """
    # Calculate degrees elapsed in current nakshatra
    nakshatra_start = (moon_nakshatra * 360.0 / 27)
    degrees_elapsed = normalize_degrees(moon_longitude - nakshatra_start)
    
    # Calculate percentage of nakshatra elapsed
    nakshatra_span = 360.0 / 27
    percentage_elapsed = degrees_elapsed / nakshatra_span
    
    # Get dasha lord and period
    dasha_lord = get_nakshatra_lord(moon_nakshatra)
    dasha_period_years = DASHA_PERIODS[dasha_lord]
    
    # Calculate when dasha started
    dasha_duration_days = dasha_period_years * 365.25
    days_elapsed = dasha_duration_days * percentage_elapsed
    
    dasha_start = birth_date - timedelta(days=days_elapsed)
    
    return dasha_start


def calculate_vimshottari_dasha(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str,
    calculation_date: datetime = None
) -> Dict:
    """
    Calculate Vimshottari Dasha periods.
    
    Vimshottari Dasha is a 120-year cycle divided among 9 planets.
    The starting dasha is determined by the Moon's nakshatra at birth.
    
    Args:
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
        calculation_date: Date to calculate dasha for (defaults to current date)
    
    Returns:
        Dictionary with current dasha, antardasha, and full dasha sequence
    """
    if calculation_date is None:
        calculation_date = datetime.now()
    
    # Parse birth time
    hour, minute = map(int, birth_time.split(':'))
    birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    birth_datetime_utc = local_to_utc(birth_datetime, timezone)
    
    # Calculate Moon position
    planets = calculate_planets_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    moon_data = planets["Moon"]
    
    moon_nakshatra = moon_data["nakshatra"]
    moon_longitude = moon_data["longitude"]
    
    # Get starting dasha lord
    dasha_lord = get_nakshatra_lord(moon_nakshatra)
    
    # Calculate dasha start date
    dasha_start = calculate_dasha_start_date(birth_datetime, moon_nakshatra, moon_longitude)
    
    # Calculate all dasha periods
    dasha_sequence = []
    current_date = dasha_start
    current_lord_index = list(DASHA_PERIODS.keys()).index(dasha_lord)
    
    # Generate 120 years of dasha sequence
    for i in range(9):  # 9 planets in sequence
        lord = list(DASHA_PERIODS.keys())[(current_lord_index + i) % 9]
        period_years = DASHA_PERIODS[lord]
        period_days = period_years * 365.25
        
        end_date = current_date + timedelta(days=period_days)
        
        dasha_sequence.append({
            "lord": lord,
            "period_years": period_years,
            "start_date": current_date.isoformat(),
            "end_date": end_date.isoformat()
        })
        
        current_date = end_date
    
    # Find current dasha
    current_dasha = None
    for dasha in dasha_sequence:
        start = datetime.fromisoformat(dasha["start_date"].replace('Z', '+00:00'))
        end = datetime.fromisoformat(dasha["end_date"].replace('Z', '+00:00'))
        if start <= calculation_date <= end:
            current_dasha = dasha
            break
    
    if current_dasha is None:
        # If calculation date is outside sequence, use first dasha
        current_dasha = dasha_sequence[0]
    
    # Calculate antardasha (sub-period)
    antardashas = calculate_antardasha(
        current_dasha["lord"],
        current_dasha["start_date"],
        calculation_date
    )
    
    return {
        "birth_details": {
            "date": birth_datetime.isoformat(),
            "moon_nakshatra": moon_nakshatra,
            "moon_nakshatra_name": get_nakshatra_name(moon_nakshatra),
            "dasha_start_date": dasha_start.isoformat()
        },
        "current_dasha": current_dasha,
        "current_antardasha": antardashas["current"],
        "upcoming_antardashas": antardashas["upcoming"],
        "dasha_sequence": dasha_sequence
    }


def calculate_antardasha(
    maha_dasha_lord: str,
    maha_dasha_start: str,
    calculation_date: datetime
) -> Dict:
    """
    Calculate antardasha (sub-period) within a maha dasha.
    
    Each maha dasha is divided into 9 antardashas, one for each planet.
    The sequence starts with the maha dasha lord itself.
    
    Args:
        maha_dasha_lord: Lord of the maha dasha
        maha_dasha_start: Start date of maha dasha
        calculation_date: Date to calculate for
    
    Returns:
        Dictionary with current and upcoming antardashas
    """
    maha_dasha_start_dt = datetime.fromisoformat(maha_dasha_start.replace('Z', '+00:00'))
    maha_dasha_period = DASHA_PERIODS[maha_dasha_lord]
    maha_dasha_days = maha_dasha_period * 365.25
    
    # Find starting antardasha lord index
    lord_index = list(DASHA_PERIODS.keys()).index(maha_dasha_lord)
    
    # Calculate antardasha periods
    antardashas = []
    current_date = maha_dasha_start_dt
    
    for i in range(9):
        antardasha_lord = list(DASHA_PERIODS.keys())[(lord_index + i) % 9]
        antardasha_period_years = DASHA_PERIODS[antardasha_lord]
        
        # Antardasha period is proportional to maha dasha period
        antardasha_days = (antardasha_period_years / 120.0) * maha_dasha_days
        
        end_date = current_date + timedelta(days=antardasha_days)
        
        antardashas.append({
            "lord": antardasha_lord,
            "start_date": current_date.isoformat(),
            "end_date": end_date.isoformat(),
            "period_days": antardasha_days
        })
        
        current_date = end_date
    
    # Find current antardasha
    current_antardasha = None
    for antardasha in antardashas:
        start = datetime.fromisoformat(antardasha["start_date"].replace('Z', '+00:00'))
        end = datetime.fromisoformat(antardasha["end_date"].replace('Z', '+00:00'))
        if start <= calculation_date <= end:
            current_antardasha = antardasha
            break
    
    if current_antardasha is None:
        current_antardasha = antardashas[0]
    
    # Get upcoming antardashas
    current_index = antardashas.index(current_antardasha)
    upcoming = antardashas[current_index + 1:current_index + 4]  # Next 3
    
    return {
        "current": current_antardasha,
        "upcoming": upcoming
    }

