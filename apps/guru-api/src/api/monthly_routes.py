"""
Phase 20: Monthly Prediction API Routes

API endpoints for monthly predictions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional
from datetime import datetime

from src.auth.middleware import get_current_user
from src.db.database import SessionLocal
from src.db.models import User, BirthDetail
from src.monthly.monthly_engine import generate_monthly_report
from src.nlg.nlg_monthly import format_monthly

router = APIRouter()


@router.get("/prediction", response_model=Dict)
async def get_monthly_prediction(
    month: Optional[int] = Query(None, ge=1, le=12, description="Month number (1-12, defaults to current month)"),
    year: Optional[int] = Query(None, description="Year (defaults to current year)"),
    current_user: User = Depends(get_current_user)
):
    """
    Phase 20: Get monthly prediction report.
    """
    db = SessionLocal()
    try:
        birth_details = db.query(BirthDetail).filter(BirthDetail.user_id == current_user.id).first()
        if not birth_details:
            raise HTTPException(status_code=404, detail="Birth details not found for the user.")
        
        # Determine month and year
        now = datetime.now()
        calc_month = month if month else now.month
        calc_year = year if year else now.year
        
        # Convert BirthDetail to dictionary
        birth_details_dict = {
            "birth_date": birth_details.birth_date.isoformat(),
            "birth_time": birth_details.birth_time,
            "birth_latitude": birth_details.birth_latitude,
            "birth_longitude": birth_details.birth_longitude,
            "timezone": birth_details.timezone
        }
        
        # Generate monthly report
        monthly_json = generate_monthly_report(birth_details_dict, calc_month, calc_year)
        
        # Format text
        monthly_text = format_monthly(monthly_json)
        
        return {
            "monthly_json": monthly_json,
            "monthly_text": monthly_text,
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating monthly prediction: {str(e)}")
    finally:
        db.close()

