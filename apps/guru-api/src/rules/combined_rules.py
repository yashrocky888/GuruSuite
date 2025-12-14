"""
Combined rules engine that integrates all rule modules.

This module provides a unified interface to get daily predictions
combining rating, color, and timing recommendations.
"""

from typing import Dict
from datetime import datetime

from src.rules.daily_rules import calculate_daily_rating
from src.rules.colour_rules import get_lucky_color
from src.rules.timing_rules import get_best_times


def get_daily_prediction(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str,
    query_date: datetime = None,
    activity_type: str = "general"
) -> Dict:
    """
    Get complete daily prediction including rating, color, and timing.
    
    This is the main function that combines all rule modules
    to provide a comprehensive daily prediction.
    
    Args:
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
        query_date: Date to calculate for (defaults to current date)
        activity_type: Type of activity for timing recommendations
    
    Returns:
        Complete daily prediction dictionary
    """
    if query_date is None:
        query_date = datetime.now()
    
    # Get all predictions
    daily_rating = calculate_daily_rating(
        birth_date, birth_time, birth_latitude, birth_longitude, timezone, query_date
    )
    
    lucky_color = get_lucky_color(
        birth_date, birth_time, birth_latitude, birth_longitude, timezone, query_date
    )
    
    best_times = get_best_times(
        query_date, birth_latitude, birth_longitude, timezone, activity_type
    )
    
    return {
        "date": query_date.isoformat(),
        "daily_rating": daily_rating,
        "lucky_color": lucky_color,
        "best_times": best_times,
        "summary": {
            "overall_rating": daily_rating["rating"],
            "lucky_color": lucky_color["primary_color"],
            "current_period": best_times["current_period"],
            "recommendation": best_times["recommendation"]
        }
    }

