"""
Phase 20: Monthly Transit Map

Tracks planetary transits over a month and identifies major shifts.
"""

from typing import Dict, List
from datetime import datetime, timedelta
import calendar
import swisseph as swe

from src.jyotish.kundli_engine import get_planet_positions
from src.jyotish.panchang import get_nakshatra
from src.utils.converters import degrees_to_sign


def generate_month_transit_positions(month: int, year: int) -> Dict:
    """
    Phase 20: Generate transit positions for all days in a month.
    
    Args:
        month: Month number (1-12)
        year: Year
    
    Returns:
        Dictionary with daily transit positions
    """
    # Get number of days in month
    num_days = calendar.monthrange(year, month)[1]
    
    monthly_transits = {}
    
    for day in range(1, num_days + 1):
        date = datetime(year, month, day, 12, 0)  # Noon for calculations
        jd = swe.julday(year, month, day, 12.0, swe.GREG_CAL)
        
        # Get planet positions
        planets = get_planet_positions(jd)
        
        daily_transits = {}
        for planet_name, planet_degree in planets.items():
            if planet_name in ["Rahu", "Ketu"]:
                continue
            
            sign, sign_num = degrees_to_sign(planet_degree)
            nakshatra_name, nakshatra_num = get_nakshatra(planet_degree)
            
            daily_transits[planet_name] = {
                "degree": planet_degree,
                "sign": sign,
                "sign_number": sign_num,
                "nakshatra": nakshatra_name,
                "nakshatra_number": nakshatra_num
            }
        
        monthly_transits[day] = {
            "date": date.strftime("%Y-%m-%d"),
            "planets": daily_transits
        }
    
    # Identify major shifts
    major_shifts = identify_major_shifts(monthly_transits)
    
    return {
        "month": month,
        "year": year,
        "daily_transits": monthly_transits,
        "major_shifts": major_shifts
    }


def identify_major_shifts(monthly_transits: Dict) -> List[Dict]:
    """
    Phase 20: Identify major transit shifts in the month.
    
    Args:
        monthly_transits: Daily transit positions
    
    Returns:
        List of major shift events
    """
    shifts = []
    days = sorted(monthly_transits.keys())
    
    if len(days) < 2:
        return shifts
    
    # Track sign changes
    for i in range(len(days) - 1):
        day1 = days[i]
        day2 = days[i + 1]
        
        transits1 = monthly_transits[day1].get("planets", {})
        transits2 = monthly_transits[day2].get("planets", {})
        
        for planet_name in transits1:
            if planet_name not in transits2:
                continue
            
            sign1 = transits1[planet_name].get("sign_number", 0)
            sign2 = transits2[planet_name].get("sign_number", 0)
            
            # Check for sign change
            if sign1 != sign2:
                shifts.append({
                    "date": monthly_transits[day2].get("date", ""),
                    "planet": planet_name,
                    "event": "sign_change",
                    "from_sign": transits1[planet_name].get("sign", ""),
                    "to_sign": transits2[planet_name].get("sign", ""),
                    "description": f"{planet_name} enters {transits2[planet_name].get('sign', '')} sign"
                })
            
            # Check for Nakshatra change
            nak1 = transits1[planet_name].get("nakshatra_number", 0)
            nak2 = transits2[planet_name].get("nakshatra_number", 0)
            
            if nak1 != nak2:
                shifts.append({
                    "date": monthly_transits[day2].get("date", ""),
                    "planet": planet_name,
                    "event": "nakshatra_change",
                    "from_nakshatra": transits1[planet_name].get("nakshatra", ""),
                    "to_nakshatra": transits2[planet_name].get("nakshatra", ""),
                    "description": f"{planet_name} enters {transits2[planet_name].get('nakshatra', '')} Nakshatra"
                })
    
    return shifts

