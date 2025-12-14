"""
Phase 20: Yearly Prediction API Routes

API endpoints for yearly predictions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional
from datetime import datetime

from src.auth.middleware import get_current_user
from src.db.database import SessionLocal
from src.db.models import User, BirthDetail
from src.yearly.yearly_prediction_engine import generate_yearly_report
from src.nlg.nlg_yearly import format_yearly

router = APIRouter()


@router.get("/prediction", response_model=Dict)
async def get_yearly_prediction(
    year: Optional[int] = Query(None, description="Year (defaults to current year)"),
    current_user: User = Depends(get_current_user)
):
    """
    Phase 20: Get yearly prediction report.
    """
    db = SessionLocal()
    try:
        birth_details = db.query(BirthDetail).filter(BirthDetail.user_id == current_user.id).first()
        if not birth_details:
            raise HTTPException(status_code=404, detail="Birth details not found for the user.")
        
        # Determine year
        now = datetime.now()
        calc_year = year if year else now.year
        
        # Convert BirthDetail to dictionary
        birth_details_dict = {
            "birth_date": birth_details.birth_date.isoformat(),
            "birth_time": birth_details.birth_time,
            "birth_latitude": birth_details.birth_latitude,
            "birth_longitude": birth_details.birth_longitude,
            "timezone": birth_details.timezone
        }
        
        # Generate yearly report
        yearly_json = generate_yearly_report(birth_details_dict, calc_year)
        
        # Format text
        yearly_text = format_yearly(yearly_json)
        
        return {
            "yearly_json": yearly_json,
            "yearly_text": yearly_text,
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating yearly prediction: {str(e)}")
    finally:
        db.close()

