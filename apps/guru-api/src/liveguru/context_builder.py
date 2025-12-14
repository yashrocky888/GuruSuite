"""
Phase 15-16: Live Guru Context Builder

Builds complete astrological context for Live Guru messages.
"""

from typing import Dict
from datetime import datetime
import swisseph as swe

from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.jyotish.panchang import calculate_panchang
from src.jyotish.daily.daily_engine import compute_daily
from src.db.models import BirthDetail


def build_context(birth_data: BirthDetail) -> Dict:
    """
    Phase 15-16: Build complete astrological context for Live Guru messages.
    
    Args:
        birth_data: BirthDetail object from database
    
    Returns:
        Complete context dictionary
    """
    # Convert birth data to datetime
    birth_date = birth_data.birth_date
    hour, minute = map(int, birth_data.birth_time.split(':'))
    dt = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Calculate Julian Day for birth
    jd = swe.julday(
        dt.year, dt.month, dt.day,
        dt.hour + dt.minute / 60.0,
        swe.GREG_CAL
    )
    
    # Use birth coordinates
    lat = birth_data.birth_latitude
    lon = birth_data.birth_longitude
    
    # 1. Generate Kundli (Birth Chart)
    kundli = generate_kundli(jd, lat, lon)
    
    # 2. Calculate Vimshottari Dasha
    moon_degree = kundli["Planets"]["Moon"]["degree"]
    dasha = calculate_vimshottari_dasha(dt, moon_degree)
    
    # 3. Generate Panchang for today
    today = datetime.now()
    today_jd = swe.julday(
        today.year, today.month, today.day,
        today.hour + today.minute / 60.0,
        swe.GREG_CAL
    )
    
    # Get timezone from birth data or default
    timezone = getattr(birth_data, 'timezone', 'UTC')
    panchang = calculate_panchang(today, lat, lon, timezone)
    
    # 4. Calculate Daily Energies
    # compute_daily needs birth_jd, current_jd, lat, lon, birth_datetime
    daily = compute_daily(jd, today_jd, lat, lon, dt)
    
    # 5. Calculate Current Transits
    try:
        from src.jyotish.transits.gochar import get_transits
        current_planets = get_planet_positions(today_jd)
        birth_planets_dict = {p: kundli["Planets"][p]["degree"] for p in kundli["Planets"]}
        transits = get_transits(birth_planets_dict, current_planets, jd, today_jd)
    except Exception:
        # Fallback
        current_planets = get_planet_positions(today_jd)
        transits = {
            "moon": {"degree": current_planets.get("Moon", 0)},
            "current_planets": current_planets
        }
    
    return {
        "kundli": kundli,
        "dasha": dasha,
        "panchang": panchang,
        "daily": daily,
        "transits": transits,
        "birth_data": birth_data
    }

