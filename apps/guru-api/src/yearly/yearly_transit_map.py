"""
Phase 20: Yearly Transit Map

Builds yearly matrix tracking slow planet movements and major events.
"""

from typing import Dict, List
from datetime import datetime
import swisseph as swe
import calendar

from src.jyotish.kundli_engine import get_planet_positions
from src.jyotish.panchang import get_nakshatra
from src.utils.converters import degrees_to_sign


def build_yearly_matrix(year: int) -> Dict:
    """
    Phase 20: Build yearly transit matrix.
    
    Args:
        year: Year
    
    Returns:
        Yearly transit matrix
    """
    # Track monthly positions for slow planets
    slow_planets = ["Jupiter", "Saturn", "Rahu", "Ketu"]
    fast_planets = ["Sun", "Moon", "Mars", "Mercury", "Venus"]
    
    monthly_positions = {}
    
    for month in range(1, 13):
        # Use mid-month (15th) for calculations
        date = datetime(year, month, 15, 12, 0)
        jd = swe.julday(year, month, 15, 12.0, swe.GREG_CAL)
        
        planets = get_planet_positions(jd)
        
        monthly_positions[month] = {}
        for planet_name, planet_degree in planets.items():
            sign, sign_num = degrees_to_sign(planet_degree)
            nakshatra_name, nakshatra_num = get_nakshatra(planet_degree)
            
            monthly_positions[month][planet_name] = {
                "degree": planet_degree,
                "sign": sign,
                "sign_number": sign_num,
                "nakshatra": nakshatra_name
            }
    
    # Track major events
    major_events = identify_yearly_major_events(monthly_positions, year)
    
    # Track retrogrades (simplified - would need proper calculation)
    retrogrades = identify_retrogrades(monthly_positions, year)
    
    # Track eclipses (simplified)
    eclipses = identify_eclipses(year)
    
    # Track major conjunctions
    conjunctions = identify_major_conjunctions(monthly_positions, year)
    
    return {
        "year": year,
        "monthly_positions": monthly_positions,
        "major_events": major_events,
        "retrogrades": retrogrades,
        "eclipses": eclipses,
        "conjunctions": conjunctions
    }


def identify_yearly_major_events(monthly_positions: Dict, year: int) -> List[Dict]:
    """
    Phase 20: Identify major yearly events.
    
    Args:
        monthly_positions: Monthly planet positions
        year: Year
    
    Returns:
        List of major events
    """
    events = []
    
    # Track Jupiter sign changes (Jupiter changes sign approximately once a year)
    jupiter_positions = {}
    for month, planets in monthly_positions.items():
        if "Jupiter" in planets:
            jupiter_positions[month] = planets["Jupiter"].get("sign_number", 0)
    
    # Find sign changes
    prev_sign = None
    for month in sorted(jupiter_positions.keys()):
        current_sign = jupiter_positions[month]
        if prev_sign is not None and current_sign != prev_sign:
            events.append({
                "date": f"{year}-{month:02d}-15",
                "event": "jupiter_sign_change",
                "description": f"Jupiter enters new sign - significant shift in fortune and wisdom",
                "impact": "high"
            })
        prev_sign = current_sign
    
    # Track Saturn sign changes (Saturn changes sign approximately every 2.5 years)
    saturn_positions = {}
    for month, planets in monthly_positions.items():
        if "Saturn" in planets:
            saturn_positions[month] = planets["Saturn"].get("sign_number", 0)
    
    prev_sign = None
    for month in sorted(saturn_positions.keys()):
        current_sign = saturn_positions[month]
        if prev_sign is not None and current_sign != prev_sign:
            events.append({
                "date": f"{year}-{month:02d}-15",
                "event": "saturn_sign_change",
                "description": f"Saturn enters new sign - major karmic shift",
                "impact": "high"
            })
        prev_sign = current_sign
    
    return events


def identify_retrogrades(monthly_positions: Dict, year: int) -> List[Dict]:
    """
    Phase 20: Identify retrograde periods (simplified).
    
    Args:
        monthly_positions: Monthly positions
        year: Year
    
    Returns:
        List of retrograde periods
    """
    retrogrades = []
    
    # Simplified - in production, use proper retrograde calculations
    # For now, provide approximate periods
    
    retrograde_periods = {
        "Mercury": [
            {"start": f"{year}-03-01", "end": f"{year}-03-25", "description": "Mercury retrograde - communication challenges"},
            {"start": f"{year}-07-01", "end": f"{year}-07-25", "description": "Mercury retrograde - review and reflect"},
            {"start": f"{year}-11-01", "end": f"{year}-11-25", "description": "Mercury retrograde - avoid hasty decisions"}
        ],
        "Venus": [
            {"start": f"{year}-06-01", "end": f"{year}-07-15", "description": "Venus retrograde - relationship review"}
        ],
        "Mars": [
            {"start": f"{year}-09-01", "end": f"{year}-11-15", "description": "Mars retrograde - energy internalization"}
        ],
        "Jupiter": [
            {"start": f"{year}-04-01", "end": f"{year}-08-15", "description": "Jupiter retrograde - internal growth"}
        ],
        "Saturn": [
            {"start": f"{year}-05-01", "end": f"{year}-09-15", "description": "Saturn retrograde - karmic review"}
        ]
    }
    
    for planet, periods in retrograde_periods.items():
        retrogrades.extend(periods)
    
    return retrogrades


def identify_eclipses(year: int) -> List[Dict]:
    """
    Phase 20: Identify eclipses for the year (simplified).
    
    Args:
        year: Year
    
    Returns:
        List of eclipses
    """
    eclipses = []
    
    # Simplified - in production, use proper eclipse calculations
    # Approximate eclipse periods
    eclipse_periods = [
        {"date": f"{year}-04-15", "type": "solar", "description": "Solar Eclipse - new beginnings, avoid important activities"},
        {"date": f"{year}-10-15", "type": "lunar", "description": "Lunar Eclipse - emotional release, spiritual time"}
    ]
    
    return eclipse_periods


def identify_major_conjunctions(monthly_positions: Dict, year: int) -> List[Dict]:
    """
    Phase 20: Identify major planetary conjunctions.
    
    Args:
        monthly_positions: Monthly positions
        year: Year
    
    Returns:
        List of conjunctions
    """
    conjunctions = []
    
    # Check for Jupiter-Saturn conjunction (rare, happens every ~20 years)
    # Simplified check
    for month in range(1, 13):
        if month in monthly_positions:
            planets = monthly_positions[month]
            if "Jupiter" in planets and "Saturn" in planets:
                jup_sign = planets["Jupiter"].get("sign_number", 0)
                sat_sign = planets["Saturn"].get("sign_number", 0)
                
                if jup_sign == sat_sign:
                    conjunctions.append({
                        "date": f"{year}-{month:02d}-15",
                        "planets": ["Jupiter", "Saturn"],
                        "description": "Jupiter-Saturn conjunction - major shift in fortune and karma",
                        "impact": "very_high"
                    })
    
    return conjunctions

