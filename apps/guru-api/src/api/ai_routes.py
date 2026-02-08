"""
AI Guru Interpretation API routes.

Phase 8: AI-powered daily predictions and interpretations.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import swisseph as swe

from typing import Dict
from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.jyotish.panchang_engine import generate_panchang
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.jyotish.daily.daily_engine import compute_daily
from src.jyotish.strength.shadbala import calculate_shadbala
from src.jyotish.strength.ashtakavarga import calculate_ashtakavarga
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses, get_ayanamsa
from src.utils.converters import degrees_to_sign, normalize_degrees
from src.ai.interpreter.daily_interpreter import interpret_daily, interpret_morning

router = APIRouter()


def prepare_complete_data(
    birth_jd: float,
    current_jd: float,
    lat: float,
    lon: float,
    birth_datetime: datetime
) -> Dict:
    """
    Phase 8: Prepare complete astrological data for AI interpretation.
    
    Args:
        birth_jd: Birth Julian Day
        current_jd: Current Julian Day
        lat: Latitude
        lon: Longitude
        birth_datetime: Birth datetime
    
    Returns:
        Complete data dictionary
    """
    # Generate Kundli
    kundli = generate_kundli(birth_jd, lat, lon)
    
    # Get planet positions for dasha
    birth_planets = get_planet_positions(birth_jd)
    moon_degree = birth_planets["Moon"]
    
    # Calculate Dasha
    dasha = calculate_vimshottari_dasha(birth_datetime, moon_degree)
    
    # Generate Panchang for current date
    current_datetime = datetime.now()
    panchang = generate_panchang(current_jd, current_datetime, lat, lon)
    
    # Prepare planets and houses for yoga detection
    planets = {}
    for p, d in kundli['Planets'].items():
        if p in ["Rahu", "Ketu"]:
            continue
        sign_num, _ = degrees_to_sign(d['degree'])
        asc_deg = kundli['Ascendant']['degree']
        rel_pos = (d['degree'] - asc_deg) % 360
        house_num = int(rel_pos / 30) + 1
        if house_num > 12:
            house_num = 1
        planets[p] = {'degree': d['degree'], 'sign': sign_num, 'house': house_num}
    
    houses = []
    asc_sign, _ = degrees_to_sign(kundli['Ascendant']['degree'])
    houses.append({'house': 1, 'degree': kundli['Ascendant']['degree'], 'sign': asc_sign})
    for h in kundli['Houses']:
        sign_num, _ = degrees_to_sign(h['degree'])
        houses.append({'house': h['house'], 'degree': h['degree'], 'sign': sign_num})
    
    # Detect Yogas
    yogas = detect_all_yogas(planets, houses)
    
    # Calculate Daily Impact
    daily = compute_daily(birth_jd, current_jd, lat, lon, birth_datetime)
    
    # Calculate Shadbala
    shadbala = calculate_shadbala(current_jd, lat, lon)
    
    # Calculate Ashtakavarga
    asc = get_ascendant(current_jd, lat, lon)
    ayanamsa = get_ayanamsa(current_jd)
    asc_sidereal = normalize_degrees(asc - ayanamsa)
    houses_list = get_houses(current_jd, lat, lon)
    houses_sidereal = [normalize_degrees(h - ayanamsa) for h in houses_list]
    current_planets = get_planet_positions(current_jd)
    ashtakavarga = calculate_ashtakavarga(current_planets, houses_sidereal, asc_sidereal)
    
    # Combine all data
    combined = {
        "kundli": {
            "ascendant": kundli["Ascendant"],
            "planets": kundli["Planets"],
            "houses": kundli["Houses"]
        },
        "dasha": {
            "current_mahadasha": dasha.get("mahadasha", [{}])[0] if dasha.get("mahadasha") else {},
            "nakshatra": dasha.get("nakshatra", ""),
            "nakshatra_lord": dasha.get("nakshatra_lord", "")
        },
        "panchang": panchang,
        "yogas": {
            "total": yogas.get("total_yogas", 0),
            "major": yogas.get("major_yogas", []),
            "summary": yogas.get("summary", {})
        },
        "daily": daily,
        "strength": {
            "shadbala": {p: s.get("total_shadbala", 0) for p, s in shadbala.items()},
            "ashtakavarga": {
                "sav_total": ashtakavarga.get("SAV_total", 0),
                "sav_average": ashtakavarga.get("SAV_average", 0)
            }
        }
    }
    
    return combined


@router.get("/daily")
async def ai_daily(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Birth latitude"),
    lon: float = Query(..., description="Birth longitude"),
    use_local: bool = Query(False, description="Use local LLM (Ollama) instead of OpenAI")
):
    # HARD CUTOVER: All daily predictions MUST come from POST /api/v1/predict only.
    raise RuntimeError("DEPRECATED: Use /api/v1/predict ONLY")
    """
    Phase 8: Get AI Guru daily prediction.
    
    This endpoint:
    1. Calculates all astrological data (Kundli, Dasha, Transits, Panchang, Yogas, Strength)
    2. Sends to AI Guru for interpretation
    3. Returns complete daily prediction with Guru guidance
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
        use_local: Use local LLM (Ollama) instead of OpenAI
    
    Returns:
        Complete AI Guru daily prediction
    """
    try:
        # Parse birth date/time
        birth_dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        birth_jd = swe.julday(
            birth_dt.year, birth_dt.month, birth_dt.day,
            birth_dt.hour + birth_dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Current date/time
        current_dt = datetime.now()
        current_jd = swe.julday(
            current_dt.year, current_dt.month, current_dt.day,
            12.0,  # Noon
            swe.GREG_CAL
        )
        
        # Prepare complete data
        combined_data = prepare_complete_data(birth_jd, current_jd, lat, lon, birth_dt)
        
        # Get AI interpretation
        ai_prediction = interpret_daily(combined_data, use_local=use_local)
        
        return {
            "date": current_dt.strftime("%Y-%m-%d"),
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon
            },
            "prediction": ai_prediction,
            "data_summary": {
                "daily_score": combined_data["daily"].get("score", 0),
                "daily_rating": combined_data["daily"].get("rating", ""),
                "yogas_count": combined_data["yogas"].get("total", 0),
                "current_dasha": combined_data["dasha"].get("current_mahadasha", {}).get("lord", "")
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI prediction: {str(e)}")


@router.get("/morning")
async def ai_morning(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Birth latitude"),
    lon: float = Query(..., description="Birth longitude"),
    use_local: bool = Query(False, description="Use local LLM (Ollama) instead of OpenAI")
):
    # HARD CUTOVER: Morning/daily text MUST come from POST /api/v1/predict only.
    raise RuntimeError("DEPRECATED: Use /api/v1/predict ONLY")
    """
    Phase 8: Get AI Guru morning notification.
    
    This endpoint provides a short morning blessing and guidance.
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
        use_local: Use local LLM (Ollama) instead of OpenAI
    
    Returns:
        Morning notification message
    """
    try:
        # Parse birth date/time
        birth_dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        birth_jd = swe.julday(
            birth_dt.year, birth_dt.month, birth_dt.day,
            birth_dt.hour + birth_dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Current date/time
        current_dt = datetime.now()
        current_jd = swe.julday(
            current_dt.year, current_dt.month, current_dt.day,
            12.0,
            swe.GREG_CAL
        )
        
        # Prepare data (simplified for morning message)
        combined_data = prepare_complete_data(birth_jd, current_jd, lat, lon, birth_dt)
        
        # Get morning interpretation
        morning_message = interpret_morning(combined_data, use_local=use_local)
        
        return {
            "date": current_dt.strftime("%Y-%m-%d"),
            "morning_message": morning_message
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating morning message: {str(e)}")

