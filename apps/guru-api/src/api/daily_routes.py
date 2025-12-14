"""
Daily Impact API routes.

Phase 7: Daily predictions and impact calculation endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import swisseph as swe

from src.jyotish.daily.daily_engine import compute_daily

router = APIRouter()


@router.get("/summary")
async def get_daily_summary(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Birth latitude"),
    lon: float = Query(..., description="Birth longitude"),
    current_date: str = Query(None, description="Date for daily calculation (YYYY-MM-DD, defaults to today)")
):
    """
    Phase 7: Get complete daily impact summary.
    
    This endpoint calculates:
    - Daily score (0-100)
    - Lucky color
    - Good/caution time windows
    - Transit details
    - Ashtakavarga bindus
    - Shadbala integration
    - Summary message
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
        current_date: Date for calculation (defaults to today)
    
    Returns:
        Complete daily impact data
    """
    try:
        # Parse birth date/time
        birth_dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        birth_jd = swe.julday(
            birth_dt.year, birth_dt.month, birth_dt.day,
            birth_dt.hour + birth_dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Parse current date/time
        if current_date:
            current_dt = datetime.strptime(current_date, "%Y-%m-%d")
        else:
            current_dt = datetime.now()
        
        current_jd = swe.julday(
            current_dt.year, current_dt.month, current_dt.day,
            12.0,  # Noon
            swe.GREG_CAL
        )
        
        # Compute daily impact
        daily_data = compute_daily(birth_jd, current_jd, lat, lon, birth_dt)
        
        return {
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon
            },
            **daily_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating daily summary: {str(e)}")


@router.get("/rating")
async def get_daily_rating(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Birth latitude"),
    lon: float = Query(..., description="Birth longitude")
):
    """
    Get quick daily rating (score and summary only).
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        Daily rating summary
    """
    try:
        birth_dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        birth_jd = swe.julday(
            birth_dt.year, birth_dt.month, birth_dt.day,
            birth_dt.hour + birth_dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        current_dt = datetime.now()
        current_jd = swe.julday(
            current_dt.year, current_dt.month, current_dt.day,
            12.0,
            swe.GREG_CAL
        )
        
        daily_data = compute_daily(birth_jd, current_jd, lat, lon, birth_dt)
        
        return {
            "date": daily_data["date"],
            "score": daily_data["score"],
            "rating": daily_data["rating"],
            "summary": daily_data["summary"],
            "lucky_color": daily_data["lucky_color"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating daily rating: {str(e)}")
