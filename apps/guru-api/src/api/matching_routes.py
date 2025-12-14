"""
Kundli Matching API routes.

Phase 13: Matchmaking endpoints (Gun Milan, Porutham, Advanced, Full Report).
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import swisseph as swe

from src.jyotish.kundli_engine import generate_kundli
from src.matching.gun_milan import gun_milan
from src.matching.porutham import porutham
from src.matching.match_engine import full_match_report
from src.matching.match_ai import ai_match_interpretation

router = APIRouter()


def build_kundli(dob: str, time: str, lat: float, lon: float) -> tuple:
    """
    Phase 13: Build kundli from birth details.
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Latitude
        lon: Longitude
    
    Returns:
        Tuple of (kundli_dict, birth_datetime)
    """
    try:
        dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        jd = swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute / 60.0,
            swe.GREG_CAL
        )
        kundli = generate_kundli(jd, lat, lon)
        return kundli, dt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")


@router.get("/gunas")
async def get_gun_milan(
    boy_dob: str = Query(..., description="Boy's date of birth (YYYY-MM-DD)"),
    boy_time: str = Query(..., description="Boy's time of birth (HH:MM)"),
    boy_lat: float = Query(..., description="Boy's birth latitude"),
    boy_lon: float = Query(..., description="Boy's birth longitude"),
    girl_dob: str = Query(..., description="Girl's date of birth (YYYY-MM-DD)"),
    girl_time: str = Query(..., description="Girl's time of birth (HH:MM)"),
    girl_lat: float = Query(..., description="Girl's birth latitude"),
    girl_lon: float = Query(..., description="Girl's birth longitude")
):
    """
    Phase 13: Calculate Gun Milan (36 points system).
    
    Returns:
        Gun Milan analysis with all 8 gunas
    """
    try:
        boy_kundli, _ = build_kundli(boy_dob, boy_time, boy_lat, boy_lon)
        girl_kundli, _ = build_kundli(girl_dob, girl_time, girl_lat, girl_lon)
        
        result = gun_milan(boy_kundli, girl_kundli)
        
        return {
            "match_type": "Guna Milan",
            "boy_details": {
                "dob": boy_dob,
                "time": boy_time
            },
            "girl_details": {
                "dob": girl_dob,
                "time": girl_time
            },
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Gun Milan: {str(e)}")


@router.get("/porutham")
async def get_porutham(
    boy_dob: str = Query(..., description="Boy's date of birth (YYYY-MM-DD)"),
    boy_time: str = Query(..., description="Boy's time of birth (HH:MM)"),
    boy_lat: float = Query(..., description="Boy's birth latitude"),
    boy_lon: float = Query(..., description="Boy's birth longitude"),
    girl_dob: str = Query(..., description="Girl's date of birth (YYYY-MM-DD)"),
    girl_time: str = Query(..., description="Girl's time of birth (HH:MM)"),
    girl_lat: float = Query(..., description="Girl's birth latitude"),
    girl_lon: float = Query(..., description="Girl's birth longitude")
):
    """
    Phase 13: Calculate Porutham (10 checks system - South Indian).
    
    Returns:
        Porutham analysis with all 10 checks
    """
    try:
        boy_kundli, _ = build_kundli(boy_dob, boy_time, boy_lat, boy_lon)
        girl_kundli, _ = build_kundli(girl_dob, girl_time, girl_lat, girl_lon)
        
        result = porutham(boy_kundli, girl_kundli)
        
        return {
            "match_type": "Porutham",
            "boy_details": {
                "dob": boy_dob,
                "time": boy_time
            },
            "girl_details": {
                "dob": girl_dob,
                "time": girl_time
            },
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Porutham: {str(e)}")


@router.get("/advanced")
async def get_advanced_compatibility(
    boy_dob: str = Query(..., description="Boy's date of birth (YYYY-MM-DD)"),
    boy_time: str = Query(..., description="Boy's time of birth (HH:MM)"),
    boy_lat: float = Query(..., description="Boy's birth latitude"),
    boy_lon: float = Query(..., description="Boy's birth longitude"),
    girl_dob: str = Query(..., description="Girl's date of birth (YYYY-MM-DD)"),
    girl_time: str = Query(..., description="Girl's time of birth (HH:MM)"),
    girl_lat: float = Query(..., description="Girl's birth latitude"),
    girl_lon: float = Query(..., description="Girl's birth longitude")
):
    """
    Phase 13: Calculate advanced compatibility factors.
    
    Returns:
        Advanced compatibility analysis
    """
    try:
        boy_kundli, boy_dt = build_kundli(boy_dob, boy_time, boy_lat, boy_lon)
        girl_kundli, girl_dt = build_kundli(girl_dob, girl_time, girl_lat, girl_lon)
        
        from src.matching.compatibility import advanced_compatibility
        from src.jyotish.kundli_engine import get_planet_positions
        from src.jyotish.dasha_engine import calculate_vimshottari_dasha
        
        boy_planets = get_planet_positions(
            swe.julday(boy_dt.year, boy_dt.month, boy_dt.day,
                      boy_dt.hour + boy_dt.minute / 60.0, swe.GREG_CAL)
        )
        girl_planets = get_planet_positions(
            swe.julday(girl_dt.year, girl_dt.month, girl_dt.day,
                      girl_dt.hour + girl_dt.minute / 60.0, swe.GREG_CAL)
        )
        
        boy_dasha = calculate_vimshottari_dasha(boy_dt, boy_planets["Moon"])
        girl_dasha = calculate_vimshottari_dasha(girl_dt, girl_planets["Moon"])
        
        result = advanced_compatibility(boy_kundli, girl_kundli, boy_dasha, girl_dasha)
        
        return {
            "match_type": "Advanced Compatibility",
            "boy_details": {
                "dob": boy_dob,
                "time": boy_time
            },
            "girl_details": {
                "dob": girl_dob,
                "time": girl_time
            },
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating advanced compatibility: {str(e)}")


@router.get("/full-report")
async def get_full_match_report(
    boy_dob: str = Query(..., description="Boy's date of birth (YYYY-MM-DD)"),
    boy_time: str = Query(..., description="Boy's time of birth (HH:MM)"),
    boy_lat: float = Query(..., description="Boy's birth latitude"),
    boy_lon: float = Query(..., description="Boy's birth longitude"),
    girl_dob: str = Query(..., description="Girl's date of birth (YYYY-MM-DD)"),
    girl_time: str = Query(..., description="Girl's time of birth (HH:MM)"),
    girl_lat: float = Query(..., description="Girl's birth latitude"),
    girl_lon: float = Query(..., description="Girl's birth longitude"),
    include_ai: bool = Query(True, description="Include AI Guru interpretation")
):
    """
    Phase 13: Generate complete match report with all systems.
    
    Includes:
    - Gun Milan (36 points)
    - Porutham (10 checks)
    - Manglik analysis
    - Advanced compatibility
    - AI Guru interpretation (optional)
    
    Returns:
        Complete match report
    """
    try:
        boy_kundli, boy_dt = build_kundli(boy_dob, boy_time, boy_lat, boy_lon)
        girl_kundli, girl_dt = build_kundli(girl_dob, girl_time, girl_lat, girl_lon)
        
        # Generate full match report
        match_data = full_match_report(boy_kundli, girl_kundli, boy_dt, girl_dt)
        
        # AI interpretation (if requested)
        ai_report = None
        if include_ai:
            try:
                ai_report = ai_match_interpretation(match_data)
            except Exception as e:
                print(f"AI interpretation failed: {e}")
                ai_report = {"error": "AI interpretation unavailable", "ai_used": "none"}
        
        return {
            "match_type": "Full Match Report",
            "boy_details": {
                "dob": boy_dob,
                "time": boy_time,
                "latitude": boy_lat,
                "longitude": boy_lon
            },
            "girl_details": {
                "dob": girl_dob,
                "time": girl_time,
                "latitude": girl_lat,
                "longitude": girl_lon
            },
            "match_data": match_data,
            "ai_report": ai_report,
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating match report: {str(e)}")

