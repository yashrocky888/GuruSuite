"""
Dasha (Planetary Periods) API routes.

This module provides FastAPI endpoints for calculating
Vimshottari Dasha periods and antardashas.

Phase 3: Added GET /dasha endpoint for core Vimshottari Dasha calculation.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import swisseph as swe

from src.db.schemas import DashaRequest
from src.jyotish.dasha import calculate_vimshottari_dasha
from src.jyotish.dasha_engine import calculate_vimshottari_dasha as calculate_dasha_engine
from src.jyotish.kundli_engine import get_planet_positions
from src.ephemeris.ephemeris_utils import get_ayanamsa
from src.utils.converters import normalize_degrees
from src.ai.explanation import add_explanation_to_response

router = APIRouter()


@router.get("/")
def get_dasha(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    timezone: str = Query("Asia/Kolkata", description="Timezone (default: Asia/Kolkata)")
):
    """
    Phase 3: Calculate Vimshottari Dasha - Core GET endpoint.
    
    This endpoint calculates the complete 120-year Vimshottari Dasha cycle
    based on Moon's nakshatra at birth using Drik Panchang/JHORA methodology.
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
        timezone: Timezone (default: Asia/Kolkata)
    
    Returns:
        Complete dasha data with:
        - julian_day: Julian Day Number
        - moon_degree: Moon's sidereal longitude
        - dasha: Complete dasha structure
    """
    try:
        # Parse date and time with proper timezone conversion
        from datetime import date
        birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
        
        # Parse time
        time_parts = time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        # Create local datetime
        birth_dt_local = datetime.combine(
            birth_date,
            datetime.min.time().replace(hour=hour, minute=minute, second=second)
        )
        
        # Convert to UTC (Swiss Ephemeris requires UTC)
        from src.utils.timezone import local_to_utc
        birth_dt_utc = local_to_utc(birth_dt_local, timezone)
        
        # Calculate Julian Day with proper UTC conversion
        jd = swe.julday(
            birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
            birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0,
            swe.GREG_CAL
        )
        
        # Use Drik Panchang dasha calculation
        from src.jyotish.dasha_drik import calculate_vimshottari_dasha_drik
        dasha = calculate_vimshottari_dasha_drik(
            birth_date, time, lat, lon, timezone
        )
        
        # Get Moon degree from dasha result
        moon_degree = dasha.get("birth_details", {}).get("moon_longitude", 0)
        
        return {
            "julian_day": round(jd, 6),
            "moon_degree": moon_degree,
            "dasha": dasha
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating dasha: {str(e)}")


@router.post("/dasha")
async def calculate_dasha(
    request: DashaRequest,
    include_explanation: bool = Query(False)
):
    """
    Calculate Vimshottari Dasha periods.
    
    Vimshottari Dasha is a 120-year cycle divided among 9 planets.
    The starting dasha is determined by the Moon's nakshatra at birth.
    
    Args:
        request: Dasha calculation request with birth details
        include_explanation: Whether to include AI-generated explanation
    
    Returns:
        Complete dasha data including current and upcoming periods
    """
    try:
        dasha_data = calculate_vimshottari_dasha(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_latitude=request.birth_latitude,
            birth_longitude=request.birth_longitude,
            timezone=request.timezone,
            calculation_date=request.calculation_date
        )
        
        if include_explanation:
            dasha_data = add_explanation_to_response(dasha_data, "dasha")
        
        return dasha_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating dasha: {str(e)}")


@router.post("/dasha/current")
async def get_current_dasha(request: DashaRequest):
    """
    Get only current maha dasha and antardasha.
    
    Args:
        request: Dasha calculation request
    
    Returns:
        Current dasha information
    """
    try:
        dasha_data = calculate_vimshottari_dasha(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_latitude=request.birth_latitude,
            birth_longitude=request.birth_longitude,
            timezone=request.timezone,
            calculation_date=request.calculation_date
        )
        
        return {
            "current_dasha": dasha_data["current_dasha"],
            "current_antardasha": dasha_data["current_antardasha"],
            "upcoming_antardashas": dasha_data["upcoming_antardashas"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating current dasha: {str(e)}")

