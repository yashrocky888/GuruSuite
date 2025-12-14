"""
Phase 20: Karma Report API Routes

API endpoints for karma and soul path reports.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from datetime import datetime

from src.auth.middleware import get_current_user
from src.db.database import SessionLocal
from src.db.models import User, BirthDetail
from src.karma.life_path_engine import generate_karma_report
from src.nlg.nlg_karma import format_karma

router = APIRouter()


@router.get("/report", response_model=Dict)
async def get_karma_report(
    current_user: User = Depends(get_current_user)
):
    """
    Phase 20: Get karma and soul path report.
    """
    db = SessionLocal()
    try:
        birth_details = db.query(BirthDetail).filter(BirthDetail.user_id == current_user.id).first()
        if not birth_details:
            raise HTTPException(status_code=404, detail="Birth details not found for the user.")
        
        # Convert BirthDetail to dictionary
        birth_details_dict = {
            "birth_date": birth_details.birth_date.isoformat(),
            "birth_time": birth_details.birth_time,
            "birth_latitude": birth_details.birth_latitude,
            "birth_longitude": birth_details.birth_longitude,
            "timezone": birth_details.timezone
        }
        
        # Generate karma report
        karma_json = generate_karma_report(birth_details_dict)
        
        # Format text
        karma_text = format_karma(karma_json)
        
        return {
            "karma_json": karma_json,
            "karma_text": karma_text,
            "generated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating karma report: {str(e)}")
    finally:
        db.close()

