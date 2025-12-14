"""
Phase 7: Moon Daily Effects Calculation

This module calculates daily effects based on Moon's position and nakshatra.
"""

from typing import Dict
from src.jyotish.panchang import get_nakshatra, get_nakshatra_lord
from src.utils.converters import normalize_degrees


def moon_daily_effects(moon_degree: float) -> Dict:
    """
    Phase 7: Calculate Moon's daily effects.
    
    Determines:
    - Current nakshatra
    - Nakshatra lord
    - Lucky color based on nakshatra lord
    
    Args:
        moon_degree: Moon's sidereal degree
    
    Returns:
        Dictionary with Moon daily effects
    """
    moon_degree = normalize_degrees(moon_degree)
    
    # Get nakshatra
    nakshatra_name, nakshatra_index = get_nakshatra(moon_degree)
    
    # Get nakshatra lord
    nakshatra_lord = get_nakshatra_lord(nakshatra_index)
    
    # Lucky colors based on nakshatra lord
    lucky_colors = {
        "Sun": "Red",
        "Moon": "White",
        "Mars": "Maroon",
        "Mercury": "Green",
        "Jupiter": "Yellow",
        "Venus": "Pink",
        "Saturn": "Black",
        "Rahu": "Grey",
        "Ketu": "Brown"
    }
    
    return {
        "nakshatra": nakshatra_name,
        "nakshatra_index": nakshatra_index,
        "nakshatra_lord": nakshatra_lord,
        "lucky_color": lucky_colors.get(nakshatra_lord, "White"),
        "moon_degree": round(moon_degree, 4)
    }


def calculate_moon_hourly_effects(moon_degree: float, current_hour: int) -> Dict:
    """
    Phase 7: Calculate Moon's hourly effects for time windows.
    
    Args:
        moon_degree: Moon's sidereal degree
        current_hour: Current hour (0-23)
    
    Returns:
        Dictionary with hourly effects
    """
    moon_info = moon_daily_effects(moon_degree)
    
    # Simple hourly calculation based on Moon's movement
    # Moon moves approximately 0.5 degrees per hour
    moon_speed = 0.5  # degrees per hour
    
    # Determine if current hour is favorable
    # This is a simplified calculation
    hour_mod = current_hour % 12
    is_favorable = hour_mod in [2, 5, 8, 11]  # Sample favorable hours
    
    return {
        **moon_info,
        "current_hour": current_hour,
        "is_favorable_hour": is_favorable,
        "moon_speed": moon_speed
    }

