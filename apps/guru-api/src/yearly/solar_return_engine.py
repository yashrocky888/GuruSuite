"""
Phase 20: Solar Return Engine (Varshaphala)

Computes and interprets solar return chart.
"""

from typing import Dict
from datetime import datetime
import swisseph as swe

from src.jyotish.kundli_engine import generate_kundli


def compute_solar_return_chart(birth_details: Dict, year: int) -> Dict:
    """
    Phase 20: Compute solar return chart (Varshaphala).
    
    Args:
        birth_details: Birth details
        year: Year for solar return
    
    Returns:
        Solar return chart
    """
    birth_date = birth_details.get("birth_date")
    birth_time = birth_details.get("birth_time")
    birth_lat = birth_details.get("birth_latitude")
    birth_lon = birth_details.get("birth_longitude")
    
    if isinstance(birth_date, str):
        from datetime import datetime as dt
        birth_date = dt.strptime(birth_date, "%Y-%m-%d").date()
    
    # Find solar return date (when Sun returns to natal Sun position)
    natal_sun_degree = get_natal_sun_degree(birth_details)
    
    # Approximate solar return (around birthday)
    solar_return_date = datetime(year, birth_date.month, birth_date.day, birth_date.hour, birth_date.minute)
    
    # Calculate exact solar return (when Sun is at same degree as natal)
    # Simplified - in production, calculate exact moment
    solar_return_jd = swe.julday(
        year, birth_date.month, birth_date.day,
        int(birth_time.split(':')[0]) + int(birth_time.split(':')[1]) / 60.0,
        swe.GREG_CAL
    )
    
    # Generate solar return chart
    solar_return_chart = generate_kundli(solar_return_jd, birth_lat, birth_lon)
    
    return {
        "year": year,
        "solar_return_date": solar_return_date.isoformat(),
        "chart": solar_return_chart,
        "interpretation": interpret_solar_return(solar_return_chart)
    }


def get_natal_sun_degree(birth_details: Dict) -> float:
    """
    Phase 20: Get natal Sun degree.
    
    Args:
        birth_details: Birth details
    
    Returns:
        Natal Sun degree
    """
    birth_date = birth_details.get("birth_date")
    birth_time = birth_details.get("birth_time")
    birth_lat = birth_details.get("birth_latitude")
    birth_lon = birth_details.get("birth_longitude")
    
    if isinstance(birth_date, str):
        from datetime import datetime as dt
        birth_date = dt.strptime(birth_date, "%Y-%m-%d").date()
    
    hour, minute = map(int, birth_time.split(':'))
    from datetime import datetime as dt
    birth_dt = dt.combine(birth_date, dt.min.time().replace(hour=hour, minute=minute, second=0, microsecond=0))
    
    birth_jd = swe.julday(
        birth_dt.year, birth_dt.month, birth_dt.day,
        birth_dt.hour + birth_dt.minute / 60.0,
        swe.GREG_CAL
    )
    
    from src.jyotish.kundli_engine import generate_kundli
    natal_chart = generate_kundli(birth_jd, birth_lat, birth_lon)
    
    return natal_chart.get("Planets", {}).get("Sun", {}).get("degree", 0)


def interpret_solar_return(solar_return_chart: Dict) -> str:
    """
    Phase 20: Interpret solar return chart.
    
    Args:
        solar_return_chart: Solar return chart
    
    Returns:
        Interpretation text
    """
    interpretation = "Solar Return Chart Analysis:\n\n"
    
    # Analyze Ascendant
    ascendant = solar_return_chart.get("Ascendant", {})
    asc_degree = ascendant.get("degree", 0)
    from src.utils.converters import degrees_to_sign
    asc_sign, _ = degrees_to_sign(asc_degree)
    
    interpretation += f"Ascendant: {asc_sign} - This year's focus and personality expression.\n\n"
    
    # Analyze 10th house (career)
    houses = solar_return_chart.get("Houses", [])
    house_10 = next((h for h in houses if h.get("house") == 10), {})
    house_10_lord = house_10.get("lord", "Unknown")
    
    interpretation += f"10th House Lord: {house_10_lord} - Career and profession focus for the year.\n\n"
    
    # Analyze planets in houses
    planets = solar_return_chart.get("Planets", {})
    planets_in_10 = [p for p, data in planets.items() if data.get("house") == 10]
    
    if planets_in_10:
        interpretation += f"Planets in 10th: {', '.join(planets_in_10)} - Strong career influences.\n"
    
    return interpretation

