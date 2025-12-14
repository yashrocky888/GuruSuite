"""
Phase 20: Choghadiya Engine

Computes Choghadiya (auspicious time segments) for day and night.
"""

from typing import Dict, List
from datetime import datetime


def compute_choghadiya(date: datetime, location: Dict) -> Dict:
    """
    Phase 20: Compute Choghadiya for a given date.
    
    Args:
        date: Date and time
        location: Location dictionary
    
    Returns:
        Choghadiya dictionary with day and night segments
    """
    # Get sunrise and sunset (simplified)
    from src.muhurtha.panchanga_engine import calculate_sunrise_sunset
    import swisseph as swe
    
    jd = swe.julday(
        date.year, date.month, date.day,
        date.hour + date.minute / 60.0,
        swe.GREG_CAL
    )
    lat = location.get("latitude", 0.0)
    lon = location.get("longitude", 0.0)
    
    sunrise_str, sunset_str = calculate_sunrise_sunset(jd, lat, lon)
    
    # Parse sunrise/sunset
    sunrise_hour = float(sunrise_str.split(':')[0]) + float(sunrise_str.split(':')[1]) / 60.0
    sunset_hour = float(sunset_str.split(':')[0]) + float(sunset_str.split(':')[1]) / 60.0
    
    # Day duration
    day_duration = sunset_hour - sunrise_hour
    segment_duration = day_duration / 8  # 8 Choghadiya segments per day
    
    # Night duration (from sunset to next sunrise)
    night_duration = (24 - sunset_hour) + sunrise_hour
    night_segment_duration = night_duration / 8
    
    # Choghadiya sequence (repeats every 8 segments)
    choghadiya_types = [
        {"name": "Udveg", "type": "bad", "meaning": "Anxiety, stress"},
        {"name": "Char", "type": "neutral", "meaning": "Movement, travel"},
        {"name": "Labh", "type": "good", "meaning": "Gains, profit"},
        {"name": "Amrit", "type": "excellent", "meaning": "Nectar, highly auspicious"},
        {"name": "Kaal", "type": "bad", "meaning": "Death, inauspicious"},
        {"name": "Shubh", "type": "good", "meaning": "Auspicious, favorable"},
        {"name": "Rog", "type": "bad", "meaning": "Disease, health issues"},
        {"name": "Labh", "type": "good", "meaning": "Gains, profit"}
    ]
    
    # Determine starting Choghadiya based on weekday
    weekday = date.weekday()  # 0=Monday, 6=Sunday
    start_index = weekday % 8
    
    # Generate day Choghadiya
    day_choghadiya = []
    current_hour = sunrise_hour
    
    for i in range(8):
        chog_type = choghadiya_types[(start_index + i) % 8]
        start_time = current_hour
        end_time = current_hour + segment_duration
        
        start_str = f"{int(start_time):02d}:{int((start_time % 1) * 60):02d}"
        end_str = f"{int(end_time):02d}:{int((end_time % 1) * 60):02d}"
        
        day_choghadiya.append({
            "segment": i + 1,
            "name": chog_type["name"],
            "type": chog_type["type"],
            "meaning": chog_type["meaning"],
            "start": start_str,
            "end": end_str,
            "duration": f"{segment_duration:.2f} hours"
        })
        
        current_hour = end_time
    
    # Generate night Choghadiya
    night_choghadiya = []
    current_hour = sunset_hour
    
    for i in range(8):
        chog_type = choghadiya_types[(start_index + i + 4) % 8]  # Night starts 4 segments ahead
        start_time = current_hour
        end_time = current_hour + night_segment_duration
        
        if end_time >= 24:
            end_time = end_time - 24
        
        start_str = f"{int(start_time):02d}:{int((start_time % 1) * 60):02d}"
        end_str = f"{int(end_time):02d}:{int((end_time % 1) * 60):02d}"
        
        night_choghadiya.append({
            "segment": i + 1,
            "name": chog_type["name"],
            "type": chog_type["type"],
            "meaning": chog_type["meaning"],
            "start": start_str,
            "end": end_str,
            "duration": f"{night_segment_duration:.2f} hours"
        })
        
        current_hour = end_time
        if current_hour >= 24:
            current_hour = current_hour - 24
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "sunrise": sunrise_str,
        "sunset": sunset_str,
        "day_choghadiya": day_choghadiya,
        "night_choghadiya": night_choghadiya,
        "best_segments": [
            seg for seg in day_choghadiya + night_choghadiya 
            if seg["type"] in ["excellent", "good"]
        ],
        "avoid_segments": [
            seg for seg in day_choghadiya + night_choghadiya 
            if seg["type"] == "bad"
        ]
    }

