"""
Lucky color rules based on dasha lord.

This module determines the lucky color for a day based on
the current dasha and antardasha lords.
"""

from typing import Dict
from datetime import datetime

from src.jyotish.dasha import calculate_vimshottari_dasha


# Planet to color mapping
PLANET_COLORS = {
    "Sun": ["Orange", "Red", "Gold"],
    "Moon": ["White", "Silver", "Pearl"],
    "Mars": ["Red", "Coral"],
    "Mercury": ["Green", "Emerald"],
    "Jupiter": ["Yellow", "Gold", "Saffron"],
    "Venus": ["White", "Diamond", "Pink"],
    "Saturn": ["Blue", "Black", "Navy"],
    "Rahu": ["Grey", "Smoke", "Mixed"],
    "Ketu": ["Brown", "Khaki", "Variegated"]
}

# Primary color for each planet
PRIMARY_COLORS = {
    "Sun": "Orange",
    "Moon": "White",
    "Mars": "Red",
    "Mercury": "Green",
    "Jupiter": "Yellow",
    "Venus": "White",
    "Saturn": "Blue",
    "Rahu": "Grey",
    "Ketu": "Brown"
}


def get_lucky_color(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str,
    query_date: datetime = None
) -> Dict:
    """
    Get lucky color based on current dasha lord.
    
    The lucky color is primarily determined by the antardasha lord,
    with the maha dasha lord as a secondary influence.
    
    Args:
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
        query_date: Date to calculate for (defaults to current date)
    
    Returns:
        Dictionary with lucky color information
    """
    if query_date is None:
        query_date = datetime.now()
    
    # Calculate current dasha
    dasha_data = calculate_vimshottari_dasha(
        birth_date, birth_time, birth_latitude, birth_longitude, timezone, query_date
    )
    
    maha_dasha_lord = dasha_data["current_dasha"]["lord"]
    antardasha_lord = dasha_data["current_antardasha"]["lord"]
    
    # Primary color from antardasha lord
    primary_color = PRIMARY_COLORS.get(antardasha_lord, "White")
    all_colors = PLANET_COLORS.get(antardasha_lord, ["White"])
    
    # Secondary color from maha dasha lord (if different)
    secondary_color = None
    if maha_dasha_lord != antardasha_lord:
        secondary_color = PRIMARY_COLORS.get(maha_dasha_lord, "White")
    
    return {
        "date": query_date.isoformat(),
        "primary_color": primary_color,
        "all_colors": all_colors,
        "secondary_color": secondary_color,
        "based_on": {
            "maha_dasha_lord": maha_dasha_lord,
            "antardasha_lord": antardasha_lord,
            "reason": f"Color based on {antardasha_lord} antardasha period"
        },
        "suggestions": {
            "clothing": f"Wear {primary_color.lower()} colored clothing",
            "accessories": f"Use {primary_color.lower()} colored accessories or gemstones",
            "general": f"Surround yourself with {primary_color.lower()} color for positive energy"
        }
    }

