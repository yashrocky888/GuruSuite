"""
Phase 7: Daily Impact Engine

This module calculates daily impact using:
- Transit Moon + Vimshottari Dasha
- Shadbala
- Ashtakavarga
- Transit aspects
"""

from typing import Dict
from datetime import datetime
import swisseph as swe

from src.jyotish.transits.gochar import get_transits
from src.jyotish.transits.moon_daily import moon_daily_effects
from src.jyotish.strength.shadbala import calculate_shadbala
from src.jyotish.strength.ashtakavarga import calculate_ashtakavarga
from src.jyotish.kundli_engine import get_planet_positions
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses, get_ayanamsa
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.utils.converters import normalize_degrees, degrees_to_sign


def get_current_dasha_lord(birth_datetime: datetime, current_datetime: datetime, moon_degree: float) -> str:
    """
    Phase 7: Get current dasha lord for daily calculations.
    
    Args:
        birth_datetime: Birth datetime
        current_datetime: Current datetime
        moon_degree: Birth Moon degree
    
    Returns:
        Current dasha lord name
    """
    try:
        dasha_data = calculate_vimshottari_dasha(birth_datetime, moon_degree)
        mahadashas = dasha_data.get("mahadasha", [])
        
        # Find current dasha
        for dasha in mahadashas:
            start_str = dasha.get("start", "")
            end_str = dasha.get("end", "")
            
            if start_str and end_str:
                try:
                    start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00").split(".")[0])
                    end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00").split(".")[0])
                    
                    if start_dt <= current_datetime <= end_dt:
                        return dasha.get("lord", "Moon")
                except:
                    pass
        
        # Default to first dasha lord
        if mahadashas:
            return mahadashas[0].get("lord", "Moon")
    except:
        pass
    
    return "Moon"  # Default


def calculate_day_lord_strength(weekday: int) -> float:
    """
    Phase 7: Calculate day lord strength.
    
    Args:
        weekday: Weekday (0=Monday, 6=Sunday)
    
    Returns:
        Day lord strength (0-10)
    """
    # Day lords: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
    day_lord_strength = {
        0: 7.0,  # Monday (Moon)
        1: 5.0,  # Tuesday (Mars)
        2: 6.0,  # Wednesday (Mercury)
        3: 8.0,  # Thursday (Jupiter)
        4: 6.0,  # Friday (Venus)
        5: 5.0,  # Saturday (Saturn)
        6: 7.0   # Sunday (Sun)
    }
    
    return day_lord_strength.get(weekday, 5.0)


def compute_daily(
    birth_jd: float,
    current_jd: float,
    lat: float,
    lon: float,
    birth_datetime: datetime = None
) -> Dict:
    """
    Phase 7: Compute complete daily impact.
    
    Uses weighted formula:
    score = 
      + Moon strength (30%)
      + Transit benefic aspects (20%)
      + Ashtakavarga bindus (20%)
      + Current dasha lord strength (20%)
      + Day lord strength (10%)
    
    Args:
        birth_jd: Birth Julian Day
        current_jd: Current Julian Day
        lat: Geographic latitude
        lon: Geographic longitude
        birth_datetime: Birth datetime (for dasha calculation)
    
    Returns:
        Complete daily impact dictionary
    """
    # Get current planet positions
    current_planets = get_planet_positions(current_jd)
    moon_degree = current_planets["Moon"]
    
    # Get birth planet positions (for dasha)
    birth_planets = get_planet_positions(birth_jd)
    birth_moon_degree = birth_planets["Moon"]
    
    # Get transits
    transits_data = get_transits(current_jd, lat, lon)
    transits = transits_data["transits"]
    house_impacts = transits_data["house_impacts"]
    
    # Get Moon transit house
    moon_house = transits["Moon"]["house"]
    
    # Calculate Shadbala for current positions
    shadbala = calculate_shadbala(current_jd, lat, lon)
    moon_shadbala = shadbala.get("Moon", {}).get("total_shadbala", 50.0)
    
    # Calculate Ashtakavarga
    asc = get_ascendant(current_jd, lat, lon)
    ayanamsa = get_ayanamsa(current_jd)
    asc_sidereal = normalize_degrees(asc - ayanamsa)
    houses_list = get_houses(current_jd, lat, lon)
    houses_sidereal = [normalize_degrees(h - ayanamsa) for h in houses_list]
    
    ashtakavarga = calculate_ashtakavarga(current_planets, houses_sidereal, asc_sidereal)
    sav = ashtakavarga.get("SAV", {})
    moon_house_bindus = sav.get(f"house_{moon_house}", 0)
    
    # Get current dasha lord
    current_datetime = datetime.now() if birth_datetime is None else birth_datetime
    current_dasha_lord = get_current_dasha_lord(
        birth_datetime or current_datetime,
        current_datetime,
        birth_moon_degree
    )
    
    # Get dasha lord strength
    dasha_lord_strength = shadbala.get(current_dasha_lord, {}).get("total_shadbala", 50.0)
    
    # Calculate transit benefic aspects
    moon_aspect_strength = transits["Moon"]["aspect_strength"]
    transit_benefic_score = max(0, min(100, moon_aspect_strength["net_strength"] * 10))
    
    # Calculate day lord strength
    weekday = current_datetime.weekday()
    day_lord_score = calculate_day_lord_strength(weekday) * 10
    
    # Calculate daily score (weighted formula)
    score = (
        (moon_shadbala / 100.0) * 30 +          # Moon strength (30%)
        (transit_benefic_score / 100.0) * 20 +   # Transit benefic aspects (20%)
        (moon_house_bindus / 8.0) * 20 +         # Ashtakavarga bindus (20%)
        (dasha_lord_strength / 100.0) * 20 +     # Dasha lord strength (20%)
        (day_lord_score / 100.0) * 10            # Day lord strength (10%)
    )
    
    # Normalize score to 0-100
    score = max(0, min(100, score))
    
    # Determine summary
    if score >= 70:
        summary = "Excellent Day"
        rating = "Excellent"
    elif score >= 50:
        summary = "Good Day"
        rating = "Good"
    elif score >= 30:
        summary = "Mixed Day"
        rating = "Mixed"
    else:
        summary = "Caution Day"
        rating = "Caution"
    
    # Get Moon daily effects
    moon_info = moon_daily_effects(moon_degree)
    
    # Determine good/bad time windows (simplified)
    current_hour = current_datetime.hour
    good_time_start = (current_hour + 2) % 24
    good_time_end = (current_hour + 6) % 24
    caution_time_start = (current_hour + 12) % 24
    caution_time_end = (current_hour + 16) % 24
    
    return {
        "date": current_datetime.strftime("%Y-%m-%d"),
        "score": round(score, 2),
        "rating": rating,
        "summary": summary,
        "moon": moon_info,
        "transits": {
            "moon_house": moon_house,
            "moon_aspects": transits["Moon"]["aspects"],
            "moon_aspect_strength": moon_aspect_strength
        },
        "strength": {
            "moon_shadbala": round(moon_shadbala, 2),
            "dasha_lord": current_dasha_lord,
            "dasha_lord_strength": round(dasha_lord_strength, 2),
            "ashtakavarga_bindus": moon_house_bindus,
            "day_lord_score": round(day_lord_score, 2)
        },
        "timing": {
            "good_time": f"{good_time_start:02d}:00 - {good_time_end:02d}:00",
            "caution_time": f"{caution_time_start:02d}:00 - {caution_time_end:02d}:00",
            "current_hour": current_hour
        },
        "lucky_color": moon_info["lucky_color"],
        "house_impacts": house_impacts
    }

