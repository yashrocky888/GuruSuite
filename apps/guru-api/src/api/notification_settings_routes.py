"""
Notification Settings API routes.

Phase 12: User notification preferences management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.db.database import get_db
from src.auth.middleware import get_current_user
from src.notifications.preferences.user_prefs import get_prefs, update_prefs

router = APIRouter()


# Phase 12: Request/Response schemas
class NotificationPreferencesRequest(BaseModel):
    delivery_time: Optional[str] = None  # HH:MM format
    channel_whatsapp: Optional[str] = None  # enabled, disabled
    channel_email: Optional[str] = None  # enabled, disabled
    channel_push: Optional[str] = None  # enabled, disabled
    channel_inapp: Optional[str] = None  # enabled, disabled
    language: Optional[str] = None  # english, hindi, kannada
    whatsapp_number: Optional[str] = None
    push_token: Optional[str] = None


@router.get("/preferences")
async def get_notification_preferences(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 12: Get user's notification preferences.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        User notification preferences
    """
    prefs = get_prefs(current_user.id, db)
    
    return {
        "user_id": current_user.id,
        "delivery_time": prefs.delivery_time,
        "channel_whatsapp": prefs.channel_whatsapp,
        "channel_email": prefs.channel_email,
        "channel_push": prefs.channel_push,
        "channel_inapp": prefs.channel_inapp,
        "language": prefs.language,
        "whatsapp_number": prefs.whatsapp_number,
        "push_token": prefs.push_token is not None  # Don't expose actual token
    }


@router.post("/update")
async def update_notification_preferences(
    request: NotificationPreferencesRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 12: Update user's notification preferences.
    
    Args:
        request: Notification preferences update request
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated preferences
    """
    # Validate delivery_time format
    if request.delivery_time:
        try:
            hour, minute = map(int, request.delivery_time.split(':'))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM (00:00-23:59)")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    
    # Validate channel values
    valid_channels = ["enabled", "disabled"]
    if request.channel_whatsapp and request.channel_whatsapp not in valid_channels:
        raise HTTPException(status_code=400, detail="channel_whatsapp must be 'enabled' or 'disabled'")
    if request.channel_email and request.channel_email not in valid_channels:
        raise HTTPException(status_code=400, detail="channel_email must be 'enabled' or 'disabled'")
    if request.channel_push and request.channel_push not in valid_channels:
        raise HTTPException(status_code=400, detail="channel_push must be 'enabled' or 'disabled'")
    if request.channel_inapp and request.channel_inapp not in valid_channels:
        raise HTTPException(status_code=400, detail="channel_inapp must be 'enabled' or 'disabled'")
    
    # Validate language
    valid_languages = ["english", "hindi", "kannada"]
    if request.language and request.language not in valid_languages:
        raise HTTPException(status_code=400, detail=f"language must be one of: {', '.join(valid_languages)}")
    
    # Update preferences
    prefs = update_prefs(
        user_id=current_user.id,
        delivery_time=request.delivery_time,
        channel_whatsapp=request.channel_whatsapp,
        channel_email=request.channel_email,
        channel_push=request.channel_push,
        channel_inapp=request.channel_inapp,
        language=request.language,
        whatsapp_number=request.whatsapp_number,
        push_token=request.push_token,
        db=db
    )
    
    return {
        "message": "Notification preferences updated successfully",
        "preferences": {
            "delivery_time": prefs.delivery_time,
            "channel_whatsapp": prefs.channel_whatsapp,
            "channel_email": prefs.channel_email,
            "channel_push": prefs.channel_push,
            "channel_inapp": prefs.channel_inapp,
            "language": prefs.language
        }
    }


@router.get("/delivery-logs")
async def get_delivery_logs(
    limit: int = 20,
    offset: int = 0,
    channel: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 12: Get user's delivery logs.
    
    Args:
        limit: Maximum number of logs to return
        offset: Number of logs to skip
        channel: Filter by channel (whatsapp, email, push, in_app)
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of delivery logs
    """
    from src.db.models import DeliveryLog
    
    query = db.query(DeliveryLog).filter(DeliveryLog.user_id == current_user.id)
    
    if channel:
        query = query.filter(DeliveryLog.channel == channel)
    
    logs = query.order_by(DeliveryLog.created_at.desc()).offset(offset).limit(limit).all()
    total_count = query.count()
    
    return {
        "total": total_count,
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "channel": log.channel,
                "status": log.status,
                "message_preview": log.message_preview,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "error_message": log.error_message
            }
            for log in logs
        ]
    }

