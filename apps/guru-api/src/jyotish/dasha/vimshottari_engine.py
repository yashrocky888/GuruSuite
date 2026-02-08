"""
Vimshottari Dasha Engine - Complete Implementation
Drik Panchang / Prokerala / JHORA Standard

This module implements the complete Vimshottari Dasha system (120-year cycle)
following ancient Vedic astrology rules exactly.

Rules:
- Lahiri (Chitra Paksha) Ayanamsa ONLY
- Nakshatra size = 800 arc minutes (13°20')
- Year length = 365.25 days (astronomical solar year)
- Month length = 30 days (display conversion only)
- All calculations use exact formulas, no approximations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import swisseph as swe

from src.jyotish.drik_panchang_engine import (
    get_julian_day_utc,
    calculate_all_planets_drik,
    NAKSHATRA_SIZE,
    NAKSHATRA_NAMES
)
from src.utils.converters import normalize_degrees


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

# Planetary sequence (DO NOT CHANGE)
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


def get_nakshatra_from_longitude(moon_longitude: float) -> Dict:
    """
    Get nakshatra information from Moon's sidereal longitude.
    
    Args:
        moon_longitude: Moon's sidereal longitude in degrees (0-360)
    
    Returns:
        Dictionary with nakshatra index, name, and lord
    """
    # Normalize longitude to 0-360
    moon_longitude = normalize_degrees(moon_longitude)
    
    # Calculate nakshatra index (0-26)
    nakshatra_index = int(moon_longitude / NAKSHATRA_SIZE)
    
    # Get nakshatra name
    nakshatra_name = NAKSHATRA_NAMES[nakshatra_index]
    
    # Get nakshatra lord
    nakshatra_lord = get_nakshatra_lord(nakshatra_index)
    
    return {
        "index": nakshatra_index,
        "name": nakshatra_name,
        "lord": nakshatra_lord
    }


def calculate_balance_of_dasha(moon_longitude: float, nakshatra_index: int) -> Dict:
    """
    Calculate balance of dasha at birth.
    
    Formula:
    - Find arc covered inside nakshatra (in arc minutes)
    - Remaining arc = 800 arc minutes - covered
    - Remaining % = remaining / 800
    - Balance years = Remaining % × Planet years
    
    Also calculates elapsed fraction for Mahadasha anchor correction.
    
    Args:
        moon_longitude: Moon's sidereal longitude in degrees
        nakshatra_index: Index of the nakshatra (0-26)
    
    Returns:
        Dictionary with balance information including elapsed fraction
    """
    # Normalize longitude
    moon_longitude = normalize_degrees(moon_longitude)
    
    # Calculate nakshatra start degree
    nakshatra_start_degree = nakshatra_index * NAKSHATRA_SIZE
    
    # Calculate degrees elapsed in nakshatra
    degrees_elapsed = moon_longitude - nakshatra_start_degree
    if degrees_elapsed < 0:
        degrees_elapsed += 360
    
    # Convert to arc minutes (1 degree = 60 arc minutes)
    arc_minutes_elapsed = degrees_elapsed * 60
    
    # Calculate remaining arc minutes (800 arc minutes per nakshatra)
    arc_minutes_remaining = 800 - arc_minutes_elapsed
    
    # Calculate remaining fraction
    remaining_fraction = arc_minutes_remaining / 800
    
    # Calculate elapsed fraction (for Mahadasha anchor)
    elapsed_fraction = arc_minutes_elapsed / 800
    
    return {
        "degrees_elapsed": round(degrees_elapsed, 6),
        "arc_minutes_elapsed": round(arc_minutes_elapsed, 6),
        "arc_minutes_remaining": round(arc_minutes_remaining, 6),
        "remaining_degrees": round(arc_minutes_remaining / 60, 6),
        "remaining_fraction": round(remaining_fraction, 6),
        "elapsed_fraction": round(elapsed_fraction, 6)
    }


def calculate_vimshottari_dasha(
    birth_date: str,
    birth_time: str,
    latitude: float,
    longitude: float,
    timezone: str,
    calculation_date: Optional[datetime] = None
) -> Dict:
    """
    Calculate complete Vimshottari Dasha system.
    
    This function:
    1. Calculates Moon's sidereal longitude using Lahiri Ayanamsa
    2. Identifies Nakshatra and its lord (starting Mahadasha)
    3. Calculates balance of dasha at birth
    4. Generates full 120-year Mahadasha cycle
    5. Calculates Antardasha periods for each Mahadasha
    6. Calculates Pratyantar Dasha periods (optional)
    
    Args:
        birth_date: Birth date in YYYY-MM-DD format
        birth_time: Birth time in HH:MM format
        latitude: Birth latitude
        longitude: Birth longitude
        timezone: Timezone string (e.g., 'Asia/Kolkata')
        calculation_date: Date to calculate current dasha for (defaults to current date)
    
    Returns:
        Complete dasha structure with:
        - current_dasha: Current Mahadasha, Antardasha, Pratyantar
        - mahadashas: List of all 9 mahadashas with start/end dates
        - antardashas: Antardasha periods for each Mahadasha
        - pratyantardashas: Pratyantar Dasha periods (optional)
    """
    # FORCE Lahiri Ayanamsa (CRITICAL for Drik Panchang accuracy)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    
    if calculation_date is None:
        calculation_date = datetime.now()
    
    # Parse birth date
    birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
    
    # Parse birth time
    time_parts = birth_time.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    second = int(time_parts[2]) if len(time_parts) > 2 else 0
    
    # Create birth datetime
    birth_datetime = datetime.combine(
        birth_date_obj,
        datetime.min.time().replace(hour=hour, minute=minute, second=second)
    )
    
    # Calculate Julian Day (get_julian_day_utc expects date and time string)
    jd = get_julian_day_utc(birth_date_obj, birth_time, timezone)
    
    # Re-assert Lahiri Ayanamsa (some functions may reset it)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    
    # Get Moon position using Drik Panchang method
    planets_drik = calculate_all_planets_drik(jd)
    moon_data = planets_drik["Moon"]
    moon_longitude = moon_data["longitude"]
    
    # Get nakshatra information
    nakshatra_info = get_nakshatra_from_longitude(moon_longitude)
    nakshatra_index = nakshatra_info["index"]
    nakshatra_name = nakshatra_info["name"]
    dasha_lord = nakshatra_info["lord"]
    
    # Calculate balance of dasha at birth
    balance_info = calculate_balance_of_dasha(moon_longitude, nakshatra_index)
    remaining_fraction = balance_info["remaining_fraction"]
    elapsed_fraction = balance_info["elapsed_fraction"]
    
    # Calculate remaining mahadasha period
    dasha_period_years = DASHA_YEARS[dasha_lord]
    remaining_dasha_years = dasha_period_years * remaining_fraction
    remaining_dasha_days = remaining_dasha_years * 365.25
    
    # ***ABSOLUTE MAHADASHA ANCHOR (PROKERALA CORRECT)***
    # Compute elapsed days in current Mahadasha
    elapsed_dasha_years = dasha_period_years * elapsed_fraction
    elapsed_dasha_days = elapsed_dasha_years * 365.25
    
    # Mahadasha start datetime = birth_datetime - elapsed_days
    # This anchors the Mahadasha at the ACTUAL START of the Nakshatra cycle
    mahadasha_start_datetime = birth_datetime - timedelta(days=elapsed_dasha_days)
    
    # Build mahadasha sequence (full 120-year cycle)
    mahadasha_list = []
    current_date = mahadasha_start_datetime
    current_lord_index = DASHA_SEQUENCE.index(dasha_lord)
    
    # First dasha (starts at anchor, ends at birth + remaining)
    first_end = birth_datetime + timedelta(days=remaining_dasha_days)
    mahadasha_list.append({
        "planet": dasha_lord,
        "start": mahadasha_start_datetime.isoformat(),
        "end": first_end.isoformat()
    })
    
    current_date = first_end
    
    # Next 8 dashas (complete cycle)
    for i in range(1, 9):
        lord = DASHA_SEQUENCE[(current_lord_index + i) % 9]
        period_years = DASHA_YEARS[lord]
        period_days = period_years * 365.25
        
        end_date = current_date + timedelta(days=period_days)
        
        mahadasha_list.append({
            "planet": lord,
            "start": current_date.isoformat(),
            "end": end_date.isoformat()
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
        # If calculation_date is before birth, use first dasha
        # If after 120 years, use last dasha
        if calculation_date < birth_datetime:
            current_mahadasha = mahadasha_list[0]
        else:
            current_mahadasha = mahadasha_list[-1]
    
    # Calculate antardashas for all mahadashas
    antardashas_dict = {}
    for maha in mahadasha_list:
        maha_lord = maha["planet"]
        maha_start = datetime.fromisoformat(maha["start"].replace('Z', '+00:00'))
        maha_end = datetime.fromisoformat(maha["end"].replace('Z', '+00:00'))
        
        antardashas = calculate_antardashas(maha_lord, maha_start, maha_end)
        antardashas_dict[maha_lord] = antardashas
    
    # Find current antardasha
    current_antardasha = None
    current_antardashas = antardashas_dict.get(current_mahadasha["planet"], [])
    for antardasha in current_antardashas:
        start = datetime.fromisoformat(antardasha["start"].replace('Z', '+00:00'))
        end = datetime.fromisoformat(antardasha["end"].replace('Z', '+00:00'))
        if start <= calculation_date <= end:
            current_antardasha = antardasha
            break
    
    if current_antardasha is None and current_antardashas:
        current_antardasha = current_antardashas[0]
    
    # Calculate pratyantardashas for current antardasha
    current_pratyantar = None
    pratyantardashas_dict = {}
    
    if current_antardasha:
        maha_lord = current_mahadasha["planet"]
        antara_lord = current_antardasha["planet"]
        antara_start = datetime.fromisoformat(current_antardasha["start"].replace('Z', '+00:00'))
        antara_end = datetime.fromisoformat(current_antardasha["end"].replace('Z', '+00:00'))
        
        pratyantardashas = calculate_pratyantardashas(
            maha_lord, antara_lord, antara_start, antara_end
        )
        
        key = f"{maha_lord}-{antara_lord}"
        pratyantardashas_dict[key] = pratyantardashas
        
        # Find current pratyantar
        for pratyantar in pratyantardashas:
            start = datetime.fromisoformat(pratyantar["start"].replace('Z', '+00:00'))
            end = datetime.fromisoformat(pratyantar["end"].replace('Z', '+00:00'))
            if start <= calculation_date <= end:
                current_pratyantar = pratyantar
                break
        
        if current_pratyantar is None and pratyantardashas:
            current_pratyantar = pratyantardashas[0]
    
    # Build current dasha object
    current_dasha = {
        "mahadasha": current_mahadasha["planet"] if current_mahadasha else None,
        "antardasha": current_antardasha["planet"] if current_antardasha else None,
        "pratyantar": current_pratyantar["planet"] if current_pratyantar else None,
        "start": current_pratyantar["start"] if current_pratyantar else (current_antardasha["start"] if current_antardasha else current_mahadasha["start"]),
        "end": current_pratyantar["end"] if current_pratyantar else (current_antardasha["end"] if current_antardasha else current_mahadasha["end"])
    }
    
    return {
        "current_dasha": current_dasha,
        "mahadashas": mahadasha_list,
        "antardashas": antardashas_dict,
        "pratyantardashas": pratyantardashas_dict
    }


def calculate_antardashas(
    maha_dasha_lord: str,
    maha_dasha_start: datetime,
    maha_dasha_end: datetime
) -> List[Dict]:
    """
    Calculate Antardasha (Bhukti) periods within a Mahadasha.
    
    Formula: AD years = (MD years × AD planet years) / 120
    
    Args:
        maha_dasha_lord: Mahadasha lord
        maha_dasha_start: Mahadasha start date
        maha_dasha_end: Mahadasha end date
    
    Returns:
        List of antardashas with start/end dates
    """
    maha_years = DASHA_YEARS[maha_dasha_lord]
    maha_lord_index = DASHA_SEQUENCE.index(maha_dasha_lord)
    
    # Calculate all antardashas
    antardasha_list = []
    current_date = maha_dasha_start
    
    for i in range(9):
        antardasha_lord = DASHA_SEQUENCE[(maha_lord_index + i) % 9]
        antardasha_years = (maha_years * DASHA_YEARS[antardasha_lord]) / 120
        antardasha_days = antardasha_years * 365.25
        
        end_date = current_date + timedelta(days=antardasha_days)
        
        # Don't exceed mahadasha end date
        if end_date > maha_dasha_end:
            end_date = maha_dasha_end
        
        antardasha_list.append({
            "planet": antardasha_lord,
            "start": current_date.isoformat(),
            "end": end_date.isoformat()
        })
        
        current_date = end_date
        
        # Stop if we've reached the end
        if current_date >= maha_dasha_end:
            break
    
    return antardasha_list


def calculate_pratyantardashas(
    maha_dasha_lord: str,
    antara_dasha_lord: str,
    antara_dasha_start: datetime,
    antara_dasha_end: datetime
) -> List[Dict]:
    """
    Calculate Pratyantar Dasha periods within an Antardasha.
    
    Formula: PD days = (MD × AD × PD) / (120 × 120) × 365.25
    
    Args:
        maha_dasha_lord: Mahadasha lord
        antara_dasha_lord: Antardasha lord
        antara_dasha_start: Antardasha start date
        antara_dasha_end: Antardasha end date
    
    Returns:
        List of pratyantardashas with start/end dates
    """
    maha_years = DASHA_YEARS[maha_dasha_lord]
    antara_years = DASHA_YEARS[antara_dasha_lord]
    antara_lord_index = DASHA_SEQUENCE.index(antara_dasha_lord)
    
    # Calculate all pratyantardashas
    pratyantar_list = []
    current_date = antara_dasha_start
    
    for i in range(9):
        pratyantar_lord = DASHA_SEQUENCE[(antara_lord_index + i) % 9]
        pratyantar_years = (maha_years * antara_years * DASHA_YEARS[pratyantar_lord]) / (120 * 120)
        pratyantar_days = pratyantar_years * 365.25
        
        end_date = current_date + timedelta(days=pratyantar_days)
        
        # Don't exceed antardasha end date
        if end_date > antara_dasha_end:
            end_date = antara_dasha_end
        
        pratyantar_list.append({
            "planet": pratyantar_lord,
            "start": current_date.isoformat(),
            "end": end_date.isoformat()
        })
        
        current_date = end_date
        
        # Stop if we've reached the end
        if current_date >= antara_dasha_end:
            break
    
    return pratyantar_list
