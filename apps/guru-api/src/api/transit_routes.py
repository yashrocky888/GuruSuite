"""
Transit (Gochar) API routes.

Phase 7: Planetary transit calculation endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import swisseph as swe

from src.jyotish.transits.gochar import get_transits

router = APIRouter()


@router.get("/all")
async def get_all_transits(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Birth latitude"),
    lon: float = Query(..., description="Birth longitude"),
    current_date: str = Query(None, description="Current date for transit (YYYY-MM-DD, defaults to today)"),
    current_time: str = Query("12:00", description="Current time for transit (HH:MM, defaults to noon)")
):
    """
    Phase 7: Calculate all planetary transits (Gochar).
    
    This endpoint calculates:
    - Current positions of all planets
    - Which house each planet is transiting
    - Aspects (Graha Drishti) from each planet
    - Benefic/malefic strength per house
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
        current_date: Current date for transit (defaults to today)
        current_time: Current time for transit (defaults to noon)
    
    Returns:
        Complete transit data
    """
    try:
        # Parse current date/time
        if current_date:
            current_dt = datetime.strptime(f"{current_date} {current_time}", "%Y-%m-%d %H:%M")
        else:
            current_dt = datetime.now()
            if current_time != "12:00":
                time_parts = current_time.split(":")
                current_dt = current_dt.replace(hour=int(time_parts[0]), minute=int(time_parts[1]) if len(time_parts) > 1 else 0)
        
        # Calculate Julian Day for current time
        current_jd = swe.julday(
            current_dt.year, current_dt.month, current_dt.day,
            current_dt.hour + current_dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Get transits
        transit_data = get_transits(current_jd, lat, lon)
        
        return {
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon
            },
            "current_datetime": current_dt.strftime("%Y-%m-%d %H:%M"),
            **transit_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating transits: {str(e)}")


@router.get("/daily")
async def get_daily_transits(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Birth latitude"),
    lon: float = Query(..., description="Birth longitude")
):
    """
    Get today's transit summary.
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        Today's transit summary
    """
    try:
        # Use today's date
        current_dt = datetime.now()
        current_jd = swe.julday(
            current_dt.year, current_dt.month, current_dt.day,
            12.0,  # Noon
            swe.GREG_CAL
        )
        
        transit_data = get_transits(current_jd, lat, lon)
        
        return {
            "date": current_dt.strftime("%Y-%m-%d"),
            "transits": transit_data["transits"],
            "summary": {
                "moon_house": transit_data["transits"]["Moon"]["house"],
                "moon_aspects": len(transit_data["transits"]["Moon"]["aspects"]),
                "active_houses": [h for h, impact in transit_data["house_impacts"].items() if impact["transiting_planets"]]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating daily transits: {str(e)}")
