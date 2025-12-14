"""
Phase 20: Muhurtha API Routes

API endpoints for Muhurtha calculations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional
from datetime import datetime

from src.auth.middleware import get_current_user
from src.db.database import SessionLocal
from src.db.models import User, BirthDetail
from src.muhurtha.muhurtha_engine import get_best_muhurtha
from src.nlg.nlg_muhurtha import format_muhurtha
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.transit_ai.transit_context_builder import build_transit_context
import swisseph as swe

router = APIRouter()


@router.get("/best-time", response_model=Dict)
async def get_muhurtha(
    task: str = Query(..., description="Task type: travel, job_application, marriage_talk, investment, property_purchase, business_start, medical_treatment, spiritual_initiation, naming_ceremony"),
    date: Optional[str] = Query(None, description="Date for Muhurtha (YYYY-MM-DD, defaults to today)"),
    current_user: User = Depends(get_current_user)
):
    """
    Phase 20: Get best Muhurtha time windows for a task.
    """
    db = SessionLocal()
    try:
        birth_details = db.query(BirthDetail).filter(BirthDetail.user_id == current_user.id).first()
        if not birth_details:
            raise HTTPException(status_code=404, detail="Birth details not found for the user.")
        
        # Parse date
        if date:
            calc_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            calc_date = datetime.now()
        
        # Build location
        location = {
            "latitude": birth_details.birth_latitude,
            "longitude": birth_details.birth_longitude,
            "timezone": birth_details.timezone
        }
        
        # Build birth chart
        birth_date = birth_details.birth_date
        birth_time = birth_details.birth_time
        hour, minute = map(int, birth_time.split(':'))
        birth_dt = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        birth_jd = swe.julday(
            birth_dt.year, birth_dt.month, birth_dt.day,
            birth_dt.hour + birth_dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        natal_chart = generate_kundli(birth_jd, birth_details.birth_latitude, birth_details.birth_longitude)
        
        # Get Dasha
        moon_degree = natal_chart["Planets"]["Moon"]["degree"]
        dasha = calculate_vimshottari_dasha(birth_dt, moon_degree)
        
        # Build transit context
        transit_context = build_transit_context(birth_details, calc_date, location)
        
        # Get Muhurtha
        muhurtha_json = get_best_muhurtha(
            date=calc_date,
            location=location,
            task=task,
            birth_chart=natal_chart,
            dasha=dasha,
            transit=transit_context
        )
        
        # Format text
        muhurtha_text = format_muhurtha(muhurtha_json)
        
        return {
            "muhurtha_json": muhurtha_json,
            "muhurtha_text": muhurtha_text,
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Muhurtha: {str(e)}")
    finally:
        db.close()

