"""
User Profile API routes.

Phase 9: User profile and birth data management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date, time

from src.db.database import get_db
from src.db.models import User, BirthDetail
from src.auth.middleware import get_current_user

router = APIRouter()


# Phase 9: Request/Response schemas
class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    daily_notifications: Optional[str] = None


class BirthDataRequest(BaseModel):
    name: str
    dob: str  # YYYY-MM-DD
    time: str  # HH:MM
    lat: float
    lon: float
    gender: Optional[str] = None
    notes: Optional[str] = None


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Phase 9: Get user profile.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User profile information
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "subscription_level": current_user.subscription_level,
        "daily_notifications": current_user.daily_notifications,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.put("/profile")
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 9: Update user profile.
    
    Args:
        request: Profile update request
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated profile
    """
    if request.name is not None:
        current_user.name = request.name
    if request.phone is not None:
        current_user.phone = request.phone
    if request.daily_notifications is not None:
        if request.daily_notifications in ["enabled", "disabled"]:
            current_user.daily_notifications = request.daily_notifications
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Profile updated successfully",
        "profile": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "daily_notifications": current_user.daily_notifications
        }
    }


@router.post("/birthdata")
async def save_birthdata(
    request: BirthDataRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 9: Save birth data for authenticated user.
    
    Args:
        request: Birth data request
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Success message with birth data ID
    """
    try:
        # Parse date and time
        birth_date = datetime.strptime(request.dob, "%Y-%m-%d").date()
        birth_time_str = request.time
        
        # Create birth detail
        new_birthdata = BirthDetail(
            user_id=current_user.id,
            name=request.name,
            birth_date=datetime.combine(birth_date, datetime.min.time()),
            birth_time=birth_time_str,
            birth_latitude=request.lat,
            birth_longitude=request.lon,
            birth_place="",  # Can be added later
            timezone="UTC",  # Default timezone
            kundli_data=None,
            navamsa_data=None,
            dasamsa_data=None
        )
        
        db.add(new_birthdata)
        db.commit()
        db.refresh(new_birthdata)
        
        return {
            "message": "Birth data saved successfully",
            "birth_data_id": new_birthdata.id,
            "name": new_birthdata.name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving birth data: {str(e)}")


@router.get("/birthdata")
async def get_birthdata(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 9: Get all birth data for authenticated user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of birth data records
    """
    birth_data_list = db.query(BirthDetail).filter(BirthDetail.user_id == current_user.id).all()
    
    return {
        "count": len(birth_data_list),
        "birth_data": [
            {
                "id": bd.id,
                "name": bd.name,
                "birth_date": bd.birth_date.strftime("%Y-%m-%d") if bd.birth_date else None,
                "birth_time": bd.birth_time,
                "latitude": bd.birth_latitude,
                "longitude": bd.birth_longitude,
                "created_at": bd.created_at.isoformat() if bd.created_at else None
            }
            for bd in birth_data_list
        ]
    }
