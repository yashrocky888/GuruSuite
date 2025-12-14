"""
Phase 14: Context Builder

Builds complete astrological context for AI Guru questions.
Includes: Kundli, Dasha, Panchang, Yogas, Daily energies, Transits.
"""

from typing import Dict
from datetime import datetime
import swisseph as swe
import json

from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.jyotish.panchang import calculate_panchang
from src.jyotish.daily.daily_engine import compute_daily
from src.db.models import BirthDetail
from src.utils.converters import degrees_to_sign


def build_context(birth_data: BirthDetail) -> Dict:
    """
    Phase 14: Build complete astrological context.
    
    Includes:
    - Birth chart (Kundli)
    - Vimshottari Dasha
    - Current transits (Gochar)
    - Today's Panchang
    - Planet strengths
    - Yogas
    - Daily energies
    
    Args:
        birth_data: BirthData object from database
    
    Returns:
        Dictionary with all astrological context
    """
    # Convert birth data to datetime
    birth_date = birth_data.birth_date
    hour, minute = map(int, birth_data.birth_time.split(':'))
    dt = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Calculate Julian Day
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
    panchang = calculate_panchang(today_jd, today, lat, lon)
    
    # 4. Calculate Daily Energies
    daily = compute_daily(jd, lat, lon)
    
    # 5. Calculate Current Transits (Gochar)
    try:
        from src.jyotish.transits.gochar import get_transits
        current_planets = get_planet_positions(today_jd)
        birth_planets_dict = {p: kundli["Planets"][p]["degree"] for p in kundli["Planets"]}
        transits = get_transits(birth_planets_dict, current_planets, jd, today_jd)
    except ImportError:
        # Fallback if transits module not available
        current_planets = get_planet_positions(today_jd)
        transits = {
            "current_planets": {p: round(pos, 4) for p, pos in current_planets.items()},
            "note": "Basic transit positions available"
        }
    except Exception as e:
        # Fallback if transits calculation fails
        transits = {
            "note": "Transit calculation unavailable",
            "error": str(e)
        }
    
    # 6. Calculate Planet Strengths
    planet_strengths = calculate_planet_strengths(kundli)
    
    # 7. Detect Yogas
    yogas = detect_all_yogas(kundli["Planets"], kundli["Houses"])
    
    # Format context for AI
    context_text = format_context_for_ai(
        kundli=kundli,
        dasha=dasha,
        panchang=panchang,
        daily=daily,
        transits=transits,
        planet_strengths=planet_strengths,
        yogas=yogas,
        birth_data=birth_data
    )
    
    return {
        "kundli": kundli,
        "dasha": dasha,
        "panchang": panchang,
        "daily": daily,
        "transits": transits,
        "planet_strengths": planet_strengths,
        "yogas": yogas,
        "formatted_context": context_text
    }


def calculate_planet_strengths(kundli: Dict) -> Dict:
    """
    Phase 14: Calculate planet strengths.
    
    Args:
        kundli: Kundli dictionary
    
    Returns:
        Dictionary with planet strengths
    """
    strengths = {}
    planets = kundli.get("Planets", {})
    
    for planet_name, planet_data in planets.items():
        # Basic strength calculation
        # In own sign, exaltation, friendly sign, etc.
        degree = planet_data.get("degree", 0)
        sign, _ = degrees_to_sign(degree)
        
        # Check if in own sign
        own_signs = {
            "Sun": 4,  # Leo
            "Moon": 3,  # Cancer
            "Mars": 0,  # Aries
            "Mercury": 1,  # Gemini/Virgo (simplified)
            "Jupiter": 10,  # Sagittarius
            "Venus": 1,  # Taurus
            "Saturn": 9,  # Capricorn
            "Rahu": 7,  # Aquarius (simplified)
            "Ketu": 0  # Aries (simplified)
        }
        
        is_own_sign = own_signs.get(planet_name) == sign
        
        # Check if in exaltation
        exaltation_signs = {
            "Sun": 0,  # Aries
            "Moon": 2,  # Taurus
            "Mars": 9,  # Capricorn
            "Mercury": 5,  # Virgo
            "Jupiter": 3,  # Cancer
            "Venus": 5,  # Pisces
            "Saturn": 6  # Libra
        }
        
        is_exalted = exaltation_signs.get(planet_name) == sign
        
        # Calculate strength score
        if is_exalted:
            strength = "Very Strong (Exalted)"
            score = 100
        elif is_own_sign:
            strength = "Strong (Own Sign)"
            score = 90
        else:
            strength = "Moderate"
            score = 60
        
        strengths[planet_name] = {
            "strength": strength,
            "score": score,
            "sign": sign,
            "degree": round(degree, 4)
        }
    
    return strengths


def detect_all_yogas(planets: Dict, houses: Dict) -> Dict:
    """
    Phase 14: Detect all yogas from planets and houses.
    
    Args:
        planets: Planets dictionary
        houses: Houses dictionary
    
    Returns:
        Dictionary with detected yogas
    """
    try:
        from src.jyotish.yogas.yoga_engine import detect_all_yogas as detect_yogas
        return detect_yogas(planets, houses)
    except ImportError:
        # Fallback if yoga engine not available
        return {
            "major_yogas": [],
            "minor_yogas": [],
            "total_count": 0
        }


def format_context_for_ai(
    kundli: Dict,
    dasha: Dict,
    panchang: Dict,
    daily: Dict,
    transits: Dict,
    planet_strengths: Dict,
    yogas: Dict,
    birth_data: BirthDetail
) -> str:
    """
    Phase 14: Format context as text for AI prompt.
    
    Args:
        All context components
    
    Returns:
        Formatted context string
    """
    context = f"""
=== BIRTH DETAILS ===
Date: {birth_data.birth_date}
Time: {birth_data.birth_time}
Place: {birth_data.birth_latitude}°N, {birth_data.birth_longitude}°E
Place Name: {birth_data.birth_place}

=== CURRENT DASHA ===
Main Dasha: {dasha.get('current_dasha', {}).get('dasha_lord', 'N/A')}
Sub Dasha: {dasha.get('current_dasha', {}).get('antardasha_lord', 'N/A')}
Dasha Period: {dasha.get('current_dasha', {}).get('start_date', 'N/A')} to {dasha.get('current_dasha', {}).get('end_date', 'N/A')}

=== TODAY'S PANCHANG ===
Tithi: {panchang.get('tithi', {}).get('name', 'N/A')}
Nakshatra: {panchang.get('nakshatra', {}).get('name', 'N/A')}
Yoga: {panchang.get('yoga', {}).get('name', 'N/A')}
Karana: {panchang.get('karana', {}).get('name', 'N/A')}
Vaar: {panchang.get('vaar', 'N/A')}

=== PLANET POSITIONS (Birth Chart) ===
"""
    
    for planet_name, planet_data in kundli.get("Planets", {}).items():
        degree = planet_data.get("degree", 0)
        sign, _ = degrees_to_sign(degree)
        strength = planet_strengths.get(planet_name, {}).get("strength", "Moderate")
        context += f"{planet_name}: Sign {sign}, Degree {degree:.2f}°, Strength: {strength}\n"
    
    context += f"""
=== CURRENT TRANSITS ===
"""
    if transits:
        for planet_name, transit_data in transits.items():
            if isinstance(transit_data, dict):
                current_sign = transit_data.get("current_sign", "N/A")
                context += f"{planet_name}: Currently in Sign {current_sign}\n"
    
    context += f"""
=== DETECTED YOGAS ===
"""
    if yogas:
        major = yogas.get("major_yogas", [])
        minor = yogas.get("minor_yogas", [])
        context += f"Major Yogas: {len(major)}\n"
        for yoga in major[:5]:  # Top 5
            context += f"  - {yoga.get('name', 'N/A')}\n"
        context += f"Minor Yogas: {len(minor)}\n"
    
    context += f"""
=== DAILY ENERGIES ===
Daily Score: {daily.get('daily_strength', {}).get('score', 0)}/100
Summary: {daily.get('daily_strength', {}).get('summary', 'N/A')}
Lucky Color: {daily.get('daily_strength', {}).get('moon', {}).get('lucky_color', 'N/A')}
"""
    
    return context


def degrees_to_sign(degrees: float) -> tuple:
    """Helper to convert degrees to sign."""
    from src.utils.converters import degrees_to_sign as d2s
    return d2s(degrees)

