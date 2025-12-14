"""
Phase 20: Panchanga Engine

Computes complete Panchanga for Muhurtha calculations.
"""

from typing import Dict
from datetime import datetime
import swisseph as swe

from src.jyotish.panchang import calculate_panchang, get_nakshatra
from src.ephemeris.ephemeris_utils import get_ayanamsa


def compute_panchanga(date: datetime, location: Dict) -> Dict:
    """
    Phase 20: Compute complete Panchanga for Muhurtha.
    
    Args:
        date: Date and time for calculation
        location: Dictionary with latitude, longitude, timezone
    
    Returns:
        Complete Panchanga dictionary
    """
    lat = location.get("latitude", 0.0)
    lon = location.get("longitude", 0.0)
    timezone = location.get("timezone", "UTC")
    
    # Calculate Panchanga
    panchang = calculate_panchang(date, lat, lon, timezone)
    
    # Calculate sunrise and sunset
    jd = swe.julday(
        date.year, date.month, date.day,
        date.hour + date.minute / 60.0,
        swe.GREG_CAL
    )
    
    # Get sunrise/sunset (simplified - would need proper calculation)
    sunrise, sunset = calculate_sunrise_sunset(jd, lat, lon)
    
    # Calculate Rahu Kalam, Yama Gandam, Gulika
    rahu_kalam = calculate_rahu_kalam(date.weekday(), sunrise, sunset)
    yama_gandam = calculate_yama_gandam(date.weekday(), sunrise, sunset)
    gulika = calculate_gulika(date.weekday(), sunrise, sunset)
    
    return {
        "tithi": panchang.get("tithi", {}),
        "vara": panchang.get("vaar", "Unknown"),
        "nakshatra": panchang.get("nakshatra", {}),
        "yoga": panchang.get("yoga", {}),
        "karana": panchang.get("karana", {}),
        "sunrise": sunrise,
        "sunset": sunset,
        "rahu_kalam": rahu_kalam,
        "yama_gandam": yama_gandam,
        "gulika": gulika,
        "date": date.isoformat()
    }


def calculate_sunrise_sunset(jd: float, lat: float, lon: float) -> tuple:
    """
    Phase 20: Calculate sunrise and sunset times.
    
    Args:
        jd: Julian Day
        lat: Latitude
        lon: Longitude
    
    Returns:
        Tuple of (sunrise_time, sunset_time) as strings
    """
    # Simplified calculation - in production, use proper astronomical calculations
    # For now, approximate based on location and date
    import math
    
    # Approximate calculation
    # This is simplified - real calculation needs proper ephemeris
    hour_offset = lon / 15.0  # Timezone offset
    
    # Approximate sunrise at 6 AM local, sunset at 6 PM local
    sunrise_hour = 6.0 - hour_offset
    sunset_hour = 18.0 - hour_offset
    
    sunrise_str = f"{int(sunrise_hour):02d}:{int((sunrise_hour % 1) * 60):02d}"
    sunset_str = f"{int(sunset_hour):02d}:{int((sunset_hour % 1) * 60):02d}"
    
    return sunrise_str, sunset_str


def calculate_rahu_kalam(weekday: int, sunrise: str, sunset: str) -> Dict:
    """
    Phase 20: Calculate Rahu Kalam (inauspicious time).
    
    Args:
        weekday: Day of week (0=Monday, 6=Sunday)
        sunrise: Sunrise time string
        sunset: Sunset time string
    
    Returns:
        Rahu Kalam time window
    """
    # Rahu Kalam timings (varies by weekday)
    rahu_timings = {
        0: (7.5, 9.0),   # Monday: 7:30 AM - 9:00 AM
        1: (15.0, 16.5), # Tuesday: 3:00 PM - 4:30 PM
        2: (12.0, 13.5), # Wednesday: 12:00 PM - 1:30 PM
        3: (13.5, 15.0), # Thursday: 1:30 PM - 3:00 PM
        4: (10.5, 12.0), # Friday: 10:30 AM - 12:00 PM
        5: (9.0, 10.5),  # Saturday: 9:00 AM - 10:30 AM
        6: (16.5, 18.0)  # Sunday: 4:30 PM - 6:00 PM
    }
    
    start_hour, end_hour = rahu_timings.get(weekday, (9.0, 10.5))
    
    start_str = f"{int(start_hour):02d}:{int((start_hour % 1) * 60):02d}"
    end_str = f"{int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
    
    return {
        "start": start_str,
        "end": end_str,
        "duration": f"{end_hour - start_hour:.1f} hours",
        "is_auspicious": False,
        "note": "Rahu Kalam - avoid important activities"
    }


def calculate_yama_gandam(weekday: int, sunrise: str, sunset: str) -> Dict:
    """
    Phase 20: Calculate Yama Gandam (inauspicious time).
    
    Args:
        weekday: Day of week
        sunrise: Sunrise time
        sunset: Sunset time
    
    Returns:
        Yama Gandam time window
    """
    # Yama Gandam timings
    yama_timings = {
        0: (10.5, 12.0), # Monday
        1: (13.5, 15.0), # Tuesday
        2: (16.5, 18.0), # Wednesday
        3: (7.5, 9.0),   # Thursday
        4: (15.0, 16.5), # Friday
        5: (12.0, 13.5), # Saturday
        6: (9.0, 10.5)   # Sunday
    }
    
    start_hour, end_hour = yama_timings.get(weekday, (9.0, 10.5))
    
    start_str = f"{int(start_hour):02d}:{int((start_hour % 1) * 60):02d}"
    end_str = f"{int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
    
    return {
        "start": start_str,
        "end": end_str,
        "duration": f"{end_hour - start_hour:.1f} hours",
        "is_auspicious": False,
        "note": "Yama Gandam - avoid important activities"
    }


def calculate_gulika(weekday: int, sunrise: str, sunset: str) -> Dict:
    """
    Phase 20: Calculate Gulika (inauspicious time).
    
    Args:
        weekday: Day of week
        sunrise: Sunrise time
        sunset: Sunset time
    
    Returns:
        Gulika time window
    """
    # Gulika timings
    gulika_timings = {
        0: (15.0, 16.5), # Monday
        1: (12.0, 13.5), # Tuesday
        2: (9.0, 10.5),  # Wednesday
        3: (16.5, 18.0), # Thursday
        4: (7.5, 9.0),   # Friday
        5: (13.5, 15.0), # Saturday
        6: (10.5, 12.0)  # Sunday
    }
    
    start_hour, end_hour = gulika_timings.get(weekday, (9.0, 10.5))
    
    start_str = f"{int(start_hour):02d}:{int((start_hour % 1) * 60):02d}"
    end_str = f"{int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
    
    return {
        "start": start_str,
        "end": end_str,
        "duration": f"{end_hour - start_hour:.1f} hours",
        "is_auspicious": False,
        "note": "Gulika - avoid important activities"
    }

