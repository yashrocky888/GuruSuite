"""
Phase 3: Vimshottari Dasha Engine - Core Implementation

This module implements the complete Vimshottari Dasha system (120-year cycle)
following ancient Vedic astrology rules exactly.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from src.jyotish.panchang import get_nakshatra, get_nakshatra_lord


# Phase 3: Vimshottari Dasha durations in years (exact as per specification)
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

# Phase 3: Dasha sequence (order in which dashas occur)
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]


def calculate_vimshottari_dasha(birth_datetime: datetime, moon_degree: float) -> Dict:
    """
    Phase 3: Calculate complete Vimshottari Dasha system.
    
    This function:
    1. Determines Moon's nakshatra and its lord
    2. Calculates remaining fraction of nakshatra at birth
    3. Calculates full 120-year Mahadasha cycle
    4. Calculates Antardasha (Bhukti) periods for each Mahadasha
    
    Args:
        birth_datetime: Birth date and time
        moon_degree: Moon's sidereal longitude in degrees
    
    Returns:
        Complete dasha structure with:
        - nakshatra: Nakshatra name
        - nakshatra_lord: Starting dasha lord
        - mahadasha: List of all 9 mahadashas with start/end dates
        - antardasha_years: Antardasha durations for each mahadasha
    """
    # Step 1: Get nakshatra and its lord
    nakshatra_name, nak_index = get_nakshatra(moon_degree)
    nak_lord = get_nakshatra_lord(nak_index)
    
    # Step 2: Calculate fraction completed in nakshatra
    part = 13 + 20/60  # 13.333333 degrees per nakshatra
    completed_fraction = (moon_degree % part) / part
    remaining_fraction = 1 - completed_fraction
    
    # Step 3: Calculate remaining mahadasha for first lord
    first_dasha_years = DASHA_YEARS[nak_lord] * remaining_fraction
    
    # Step 4: Build mahadasha list
    dasha_list = []
    start_date = birth_datetime
    end_date = birth_datetime + timedelta(days=first_dasha_years * 365.25)
    
    # First dasha (partial, from birth)
    dasha_list.append({
        "lord": nak_lord,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "years": round(first_dasha_years, 4),
        "total_years": DASHA_YEARS[nak_lord]
    })
    
    # Calculate next 8 dashas (complete cycle)
    current_index = DASHA_SEQUENCE.index(nak_lord)
    cur_start = end_date
    
    for i in range(1, 9):
        lord = DASHA_SEQUENCE[(current_index + i) % 9]
        duration = DASHA_YEARS[lord]
        
        next_end = cur_start + timedelta(days=duration * 365.25)
        
        dasha_list.append({
            "lord": lord,
            "start": cur_start.isoformat(),
            "end": next_end.isoformat(),
            "years": duration,
            "total_years": duration
        })
        
        cur_start = next_end
    
    # Step 5: Calculate Antardasha (Bhukti) for each Mahadasha
    antardasha_list = {}
    
    for d in dasha_list:
        main_lord = d["lord"]
        main_dur = DASHA_YEARS[main_lord]
        
        antardasha_list[main_lord] = {}
        
        # Calculate antardasha for each sub-lord in sequence
        main_lord_index = DASHA_SEQUENCE.index(main_lord)
        
        for i in range(9):
            sub_lord = DASHA_SEQUENCE[(main_lord_index + i) % 9]
            # Formula: (Main Dasha duration * Sub-lord duration) / 120
            sub_duration_years = (main_dur * DASHA_YEARS[sub_lord]) / 120
            antardasha_list[main_lord][sub_lord] = round(sub_duration_years, 4)
    
    return {
        "nakshatra": nakshatra_name,
        "nakshatra_index": nak_index,
        "nakshatra_lord": nak_lord,
        "moon_degree": round(moon_degree, 4),
        "mahadasha": dasha_list,
        "antardasha_years": antardasha_list,
        "total_cycle_years": 120
    }

