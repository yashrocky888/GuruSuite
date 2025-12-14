"""
Phase 19: Daily Transit Prediction API Routes

API endpoints for daily transit predictions and guidance.
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from datetime import datetime

from src.auth.jwt_handler import decode_token
from src.transit_ai.daily_prediction_engine import generate_daily_transit_report
from src.transit_ai.transit_nlg import format_daily_transit_text, format_transit_explanation
from src.db.database import SessionLocal
from src.db.models import BirthDetail, User

router = APIRouter()


def get_user_from_token(token: str) -> User:
    """Get user from JWT token."""
    try:
        token_data = decode_token(token)
        user_id = token_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


@router.get("/today")
async def get_today_transit_report(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (defaults to today)"),
    lat: Optional[float] = Query(None, description="Current latitude (optional)"),
    lon: Optional[float] = Query(None, description="Current longitude (optional)"),
    timezone: Optional[str] = Query("UTC", description="Timezone (default: UTC)")
):
    """
    Phase 19: Get today's transit prediction report.
    
    Returns:
        Complete daily transit report with JSON and natural language text
    """
    # Extract token
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        token = authorization.replace("Bearer ", "").strip()
    elif token:
        token = token.strip()
    else:
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    # Get user
    user = get_user_from_token(token)
    
    # Get birth data
    db = SessionLocal()
    try:
        birth_data = db.query(BirthDetail).filter(BirthDetail.user_id == user.id).first()
        
        if not birth_data:
            raise HTTPException(
                status_code=400,
                detail="Birth data not found. Please save your birth details first."
            )
        
        # Parse date
        if date:
            on_datetime = datetime.strptime(date, "%Y-%m-%d")
        else:
            on_datetime = datetime.now()
        
        # Build birth details
        birth_details = {
            "birth_date": birth_data.birth_date,
            "birth_time": birth_data.birth_time,
            "birth_latitude": birth_data.birth_latitude,
            "birth_longitude": birth_data.birth_longitude
        }
        
        # Build location
        location = {
            "latitude": lat if lat else birth_data.birth_latitude,
            "longitude": lon if lon else birth_data.birth_longitude,
            "timezone": timezone
        }
        
        # Generate report
        report_json = generate_daily_transit_report(birth_details, on_datetime, location)
        
        # Generate natural language text
        report_text = format_daily_transit_text(report_json)
        
        return {
            "success": True,
            "user_id": user.id,
            "date": report_json.get("date"),
            "daily_transit_json": report_json,
            "daily_transit_text": report_text,
            "generated_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating transit report: {str(e)}")
    
    finally:
        db.close()


@router.get("/detailed")
async def get_detailed_transit_analysis(
    authorization: Optional[str] = Header(None),
    date: Optional[str] = Query(None)
):
    """
    Phase 19: Get detailed transit analysis with explanations.
    
    Returns:
        Detailed transit analysis with explanations
    """
    # Similar implementation to /today but with more detailed explanations
    # For now, return same as /today
    return await get_today_transit_report(authorization=authorization, date=date)

