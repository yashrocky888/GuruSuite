"""
Drik Panchang & JHORA Compatible Vimshottari Dasha Engine

This module provides EXACT dasha calculations matching JHORA.

Vimshottari Dasha Rules:
- 120-year cycle divided among 9 planets
- Starting dasha determined by Moon's nakshatra at birth
- Balance calculation: remaining fraction of nakshatra at birth
- Antardasha: (Mahadasha years * Antardasha lord years) / 120
- Pratyantardasha: (Antardasha years * Pratyantardasha lord years) / (Mahadasha years)
"""

from datetime import datetime, timedelta
from typing import Dict, List
from src.jyotish.drik_panchang_engine import (
    calculate_all_planets_drik,
    get_julian_day_utc,
    NAKSHATRA_SIZE
)
from src.ephemeris.planets_drik import get_nakshatra_pada


# Vimshottari Dasha periods (in years) - JHORA standard
DASHA_YEARS = {
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

# Dasha sequence (order in which dashas occur)
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Nakshatra lords (in order of 27 nakshatras) - JHORA standard
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]


def get_nakshatra_lord(nakshatra_index: int) -> str:
    """Get the lord of a nakshatra (JHORA standard)."""
    return NAKSHATRA_LORDS[nakshatra_index % 27]


def calculate_vimshottari_dasha_drik(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str,
    calculation_date: datetime = None
) -> Dict:
    """
    Calculate Vimshottari Dasha using Drik Panchang & JHORA methodology.
    
    Args:
        birth_date: Birth date
        birth_time: Birth time (HH:MM or HH:MM:SS)
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
        calculation_date: Date to calculate dasha for (defaults to current date)
    
    Returns:
        Complete dasha structure matching JHORA
    """
    if calculation_date is None:
        calculation_date = datetime.now()
    
    # Calculate Julian Day
    jd = get_julian_day_utc(birth_date, birth_time, timezone)
    
    # Get Moon position (Drik Panchang method)
    planets_drik = calculate_all_planets_drik(jd)
    moon_data = planets_drik["Moon"]
    
    moon_longitude = moon_data["longitude"]
    moon_nakshatra_data = get_nakshatra_pada(moon_longitude)
    moon_nakshatra_index = moon_nakshatra_data["index"]
    moon_nakshatra_name = moon_nakshatra_data["name"]
    
    # Get starting dasha lord
    dasha_lord = get_nakshatra_lord(moon_nakshatra_index)
    
    # Calculate balance (remaining fraction of nakshatra at birth)
    # JHORA method: exact calculation
    nakshatra_start_degree = moon_nakshatra_index * NAKSHATRA_SIZE
    degrees_elapsed_in_nakshatra = moon_longitude - nakshatra_start_degree
    if degrees_elapsed_in_nakshatra < 0:
        degrees_elapsed_in_nakshatra += 360
    
    remaining_degrees = NAKSHATRA_SIZE - degrees_elapsed_in_nakshatra
    remaining_fraction = remaining_degrees / NAKSHATRA_SIZE
    
    # Calculate remaining mahadasha period
    dasha_period_years = DASHA_YEARS[dasha_lord]
    remaining_dasha_years = dasha_period_years * remaining_fraction
    
    # Parse birth datetime
    time_parts = birth_time.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    second = int(time_parts[2]) if len(time_parts) > 2 else 0
    birth_datetime = datetime.combine(
        birth_date,
        datetime.min.time().replace(hour=hour, minute=minute, second=second)
    )
    
    # Build mahadasha sequence
    mahadasha_list = []
    current_date = birth_datetime
    current_lord_index = DASHA_SEQUENCE.index(dasha_lord)
    
    # First dasha (partial, from birth)
    first_end = birth_datetime + timedelta(days=remaining_dasha_years * 365.25)
    mahadasha_list.append({
        "lord": dasha_lord,
        "start": birth_datetime.isoformat(),
        "end": first_end.isoformat(),
        "years": round(remaining_dasha_years, 6),
        "total_years": dasha_period_years,
        "is_partial": True
    })
    
    current_date = first_end
    
    # Next 8 dashas (complete cycle)
    for i in range(1, 9):
        lord = DASHA_SEQUENCE[(current_lord_index + i) % 9]
        period_years = DASHA_YEARS[lord]
        period_days = period_years * 365.25
        
        end_date = current_date + timedelta(days=period_days)
        
        mahadasha_list.append({
            "lord": lord,
            "start": current_date.isoformat(),
            "end": end_date.isoformat(),
            "years": period_years,
            "total_years": period_years,
            "is_partial": False
        })
        
        current_date = end_date
    
    # Find current mahadasha
    current_mahadasha = None
    for dasha in mahadasha_list:
        start = datetime.fromisoformat(dasha["start"].replace('Z', '+00:00'))
        end = datetime.fromisoformat(dasha["end"].replace('Z', '+00:00'))
        if start <= calculation_date <= end:
            current_mahadasha = dasha
            break
    
    if current_mahadasha is None:
        current_mahadasha = mahadasha_list[0]
    
    # Calculate antardasha for current mahadasha
    antardashas = calculate_antardasha_drik(
        current_mahadasha["lord"],
        current_mahadasha["start"],
        calculation_date
    )
    
    return {
        "birth_details": {
            "date": birth_datetime.isoformat(),
            "moon_longitude": round(moon_longitude, 6),
            "moon_nakshatra": moon_nakshatra_name,
            "moon_nakshatra_index": moon_nakshatra_index,
            "moon_pada": moon_nakshatra_data["pada"],
            "dasha_lord": dasha_lord,
            "balance_years": round(remaining_dasha_years, 6)
        },
        "current_mahadasha": current_mahadasha,
        "current_antardasha": antardashas.get("current", {}),
        "upcoming_antardashas": antardashas.get("upcoming", []),
        "mahadasha_sequence": mahadasha_list
    }


def calculate_antardasha_drik(
    maha_dasha_lord: str,
    maha_dasha_start: str,
    calculation_date: datetime
) -> Dict:
    """
    Calculate Antardasha (Bhukti) periods within a Mahadasha.
    
    Formula: (Mahadasha years * Antardasha lord years) / 120
    
    Args:
        maha_dasha_lord: Mahadasha lord
        maha_dasha_start: Mahadasha start date (ISO format)
        calculation_date: Date to calculate for
    
    Returns:
        Current and upcoming antardashas
    """
    maha_start = datetime.fromisoformat(maha_dasha_start.replace('Z', '+00:00'))
    maha_years = DASHA_YEARS[maha_dasha_lord]
    maha_lord_index = DASHA_SEQUENCE.index(maha_dasha_lord)
    
    # Calculate all antardashas
    antardasha_list = []
    current_date = maha_start
    
    for i in range(9):
        antardasha_lord = DASHA_SEQUENCE[(maha_lord_index + i) % 9]
        antardasha_years = (maha_years * DASHA_YEARS[antardasha_lord]) / 120
        antardasha_days = antardasha_years * 365.25
        
        end_date = current_date + timedelta(days=antardasha_days)
        
        antardasha_list.append({
            "lord": antardasha_lord,
            "start": current_date.isoformat(),
            "end": end_date.isoformat(),
            "years": round(antardasha_years, 6)
        })
        
        current_date = end_date
    
    # Find current antardasha
    current_antardasha = None
    for antardasha in antardasha_list:
        start = datetime.fromisoformat(antardasha["start"].replace('Z', '+00:00'))
        end = datetime.fromisoformat(antardasha["end"].replace('Z', '+00:00'))
        if start <= calculation_date <= end:
            current_antardasha = antardasha
            break
    
    if current_antardasha is None:
        current_antardasha = antardasha_list[0]
    
    # Get upcoming antardashas
    current_index = antardasha_list.index(current_antardasha)
    upcoming = antardasha_list[current_index + 1:current_index + 4]  # Next 3
    
    return {
        "current": current_antardasha,
        "upcoming": upcoming,
        "all": antardasha_list
    }

