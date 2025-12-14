"""
Best time of day rules based on Moon transit.

This module determines the best times of day for activities
based on Moon's transit through nakshatras and signs.
"""

from typing import Dict, List
from datetime import datetime, timedelta

from src.jyotish.panchang import calculate_panchang
from src.ephemeris.planets import calculate_planets_sidereal
from src.utils.timezone import local_to_utc


# Nakshatra timings (each nakshatra spans approximately 53 minutes)
NAKSHATRA_DURATION_MINUTES = 53

# Favorable nakshatras for different activities
FAVORABLE_NAKSHATRAS = {
    "business": [2, 3, 5, 6, 7, 9, 10, 12, 13, 15, 17, 18, 20, 21, 23, 24, 26],
    "travel": [0, 1, 2, 5, 6, 7, 9, 10, 12, 13, 15, 17, 18, 20, 21, 23, 24],
    "marriage": [2, 3, 5, 6, 7, 9, 10, 12, 13, 15, 17, 18, 20, 21, 23, 24],
    "health": [2, 3, 5, 6, 7, 9, 10, 12, 13, 15, 17, 18, 20, 21, 23, 24, 26],
    "education": [2, 3, 5, 6, 7, 9, 10, 12, 13, 15, 17, 18, 20, 21, 23, 24, 26]
}


def get_best_times(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone: str,
    activity_type: str = "general"
) -> Dict:
    """
    Get best times of day based on Moon's transit.
    
    The Moon transits through nakshatras throughout the day.
    Each nakshatra has specific qualities that make it
    favorable or unfavorable for different activities.
    
    Args:
        date: Date to calculate for
        latitude: Geographic latitude
        longitude: Geographic longitude
        timezone: Timezone string
        activity_type: Type of activity (business, travel, marriage, health, education, general)
    
    Returns:
        Dictionary with best time periods
    """
    # Calculate panchang for the day
    panchang = calculate_panchang(date, latitude, longitude, timezone)
    
    # Get current nakshatra
    current_nakshatra = panchang["nakshatra"]["number"]
    current_nakshatra_name = panchang["nakshatra"]["name"]
    
    # Get favorable nakshatras for the activity
    if activity_type in FAVORABLE_NAKSHATRAS:
        favorable_nakshatras = FAVORABLE_NAKSHATRAS[activity_type]
    else:
        favorable_nakshatras = FAVORABLE_NAKSHATRAS["business"]  # Default
    
    # Calculate time periods for each nakshatra during the day
    # Start from sunrise (approximately 6 AM)
    sunrise = date.replace(hour=6, minute=0, second=0, microsecond=0)
    
    best_times = []
    current_time = sunrise
    
    # Calculate for next 24 hours
    for nakshatra_num in range(27):
        nakshatra_start = current_time
        nakshatra_end = current_time + timedelta(minutes=NAKSHATRA_DURATION_MINUTES)
        
        is_favorable = nakshatra_num in favorable_nakshatras
        
        if is_favorable:
            best_times.append({
                "start": nakshatra_start.isoformat(),
                "end": nakshatra_end.isoformat(),
                "nakshatra": nakshatra_num,
                "nakshatra_name": panchang["nakshatra"]["name"] if nakshatra_num == current_nakshatra else "Unknown",
                "quality": "Favorable"
            })
        
        current_time = nakshatra_end
        
        if current_time > date + timedelta(days=1):
            break
    
    # Get current time period
    current_period = None
    for period in best_times:
        start = datetime.fromisoformat(period["start"])
        end = datetime.fromisoformat(period["end"])
        if start <= date <= end:
            current_period = period
            break
    
    return {
        "date": date.isoformat(),
        "activity_type": activity_type,
        "current_nakshatra": {
            "number": current_nakshatra,
            "name": current_nakshatra_name,
            "is_favorable": current_nakshatra in favorable_nakshatras
        },
        "current_period": current_period,
        "best_times": best_times[:5],  # Top 5 best times
        "recommendation": get_timing_recommendation(current_nakshatra, favorable_nakshatras)
    }


def get_timing_recommendation(
    current_nakshatra: int,
    favorable_nakshatras: List[int]
) -> str:
    """
    Get a recommendation based on current nakshatra.
    
    Args:
        current_nakshatra: Current nakshatra number
        favorable_nakshatras: List of favorable nakshatras
    
    Returns:
        Recommendation string
    """
    if current_nakshatra in favorable_nakshatras:
        return "Current time is favorable for your activity. Proceed with confidence."
    else:
        return "Current time is not ideal. Wait for the next favorable nakshatra period."

