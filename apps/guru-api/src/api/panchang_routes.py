"""
Panchang API routes.

This module provides FastAPI endpoints for calculating Panchang
(tithi, nakshatra, yoga, karana, vaar) for a given date.

Phase 4: Added GET /panchang endpoint with JHora-style calculations.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import swisseph as swe

from src.db.schemas import PanchangRequest
from src.jyotish.panchang import calculate_panchang
from src.jyotish.panchang_engine import generate_panchang
from src.jyotish.panchanga.panchanga_engine import calculate_panchanga

router = APIRouter()


@router.get("/")
def get_panchang(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    lat: float = Query(0.0, description="Latitude (optional, for sunrise/sunset)"),
    lon: float = Query(0.0, description="Longitude (optional, for sunrise/sunset)")
):
    """
    Phase 4: Calculate Panchang for a given date - JHora-style.
    
    This endpoint calculates the complete Panchang using JHora formulas:
    - Tithi (lunar day): (Moon - Sun) / 12 degrees
    - Nakshatra (lunar mansion): Moon / 13°20'
    - Yoga (Sun-Moon combination): (Sun + Moon) / 13°20'
    - Karana (half tithi): (Tithi * 2) % 11
    - Day Lord: Based on weekday
    
    Args:
        date: Date in YYYY-MM-DD format
        lat: Latitude (optional, for sunrise/sunset calculation)
        lon: Longitude (optional, for sunrise/sunset calculation)
    
    Returns:
        Complete Panchang data with all five elements
    """
    try:
        # Parse date
        dt = datetime.strptime(date, "%Y-%m-%d")
        
        # Calculate Julian Day at noon for the date
        jd = swe.julday(
            dt.year, dt.month, dt.day,
            12.0,  # Noon
            swe.GREG_CAL
        )
        
        # Generate Panchang
        panchang = generate_panchang(jd, dt, lat, lon)
        
        return {
            "julian_day": round(jd, 6),
            "panchang": panchang
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating panchang: {str(e)}")


@router.post("/panchang")
async def calculate_panchang_endpoint(request: PanchangRequest):
    """
    Calculate Panchang for a given date (POST endpoint with timezone support).
    
    Panchang includes:
    - Tithi (lunar day)
    - Nakshatra (lunar mansion)
    - Yoga (Sun-Moon combination)
    - Karana (half tithi)
    - Vaar (day of week)
    
    Args:
        request: Panchang calculation request
    
    Returns:
        Complete panchang data
    """
    try:
        panchang_data = calculate_panchang(
            date=request.date,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )
        
        return panchang_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating panchang: {str(e)}")


@router.get("/panchanga")
def get_panchanga(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    tz: str = Query(..., description="Timezone (e.g., 'Asia/Kolkata')")
):
    """
    Calculate Panchanga using Drik Siddhanta (Swiss Ephemeris).
    
    JHora / Prokerala Standard Mode
    Backend ONLY - No AI, No frontend logic
    
    This endpoint calculates complete Panchanga using Drik Siddhanta methodology:
    - Sunrise/Sunset using Swiss Ephemeris
    - Tithi = (Moon - Sun) / 12°
    - Nakshatra = Moon longitude / 13°20'
    - Yoga = (Moon + Sun) mod 360
    - Karana = half-tithi logic
    - Vara from weekday & sunrise rule
    
    Args:
        date: Date in YYYY-MM-DD format
        lat: Latitude
        lon: Longitude
        tz: Timezone string (e.g., 'Asia/Kolkata')
    
    Returns:
        Complete Panchanga data with all elements
    """
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        
        # Calculate Panchanga
        panchanga_data = calculate_panchanga(
            date=date,
            latitude=lat,
            longitude=lon,
            timezone=tz
        )
        
        return panchanga_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating panchanga: {str(e)}")

