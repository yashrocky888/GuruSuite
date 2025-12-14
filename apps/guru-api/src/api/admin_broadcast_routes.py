"""
Admin Broadcast API routes.

Phase 12: Admin endpoints for broadcasting messages to users.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.db.database import get_db
from src.db.models import User, DeliveryLog
from src.auth.middleware import get_current_user
from src.notifications.channels.whatsapp import send_whatsapp
from src.notifications.channels.emailer import send_email
from src.notifications.channels.push import send_push
from src.notifications.preferences.user_prefs import get_prefs

router = APIRouter()


# Phase 12: Request schemas
class BroadcastRequest(BaseModel):
    message: str
    subject: Optional[str] = "Guru Broadcast"
    channel: Optional[str] = "all"  # all, whatsapp, email, push
    user_filter: Optional[str] = "all"  # all, premium


@router.post("/all")
async def broadcast_to_all(
    request: BroadcastRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 12: Broadcast message to all users.
    
    Requires premium/admin access.
    
    Args:
        request: Broadcast request
        current_user: Current authenticated user (must be premium/admin)
        db: Database session
    
    Returns:
        Broadcast result
    """
    # Check access
    if current_user.subscription_level not in ["premium", "lifetime"]:
        raise HTTPException(status_code=403, detail="Premium access required for broadcasting")
    
    # Get users based on filter
    if request.user_filter == "premium":
        users = db.query(User).filter(
            User.subscription_level.in_(["premium", "lifetime"])
        ).all()
    else:
        users = db.query(User).all()
    
    results = {
        "total_users": len(users),
        "whatsapp": {"sent": 0, "failed": 0},
        "email": {"sent": 0, "failed": 0},
        "push": {"sent": 0, "failed": 0}
    }
    
    for user in users:
        prefs = get_prefs(user.id, db)
        
        # WhatsApp
        if request.channel in ["all", "whatsapp"] and prefs.channel_whatsapp == "enabled":
            whatsapp_number = prefs.whatsapp_number or user.phone
            if whatsapp_number:
                result = send_whatsapp(whatsapp_number, request.message)
                if result.get("success"):
                    results["whatsapp"]["sent"] += 1
                else:
                    results["whatsapp"]["failed"] += 1
                
                # Log delivery
                log = DeliveryLog(
                    user_id=user.id,
                    channel="whatsapp",
                    status="success" if result.get("success") else "failed",
                    message_preview=request.message[:200],
                    error_message=result.get("error"),
                    gateway_response=result
                )
                db.add(log)
        
        # Email
        if request.channel in ["all", "email"] and prefs.channel_email == "enabled" and user.email:
            result = send_email(user.email, request.subject, request.message)
            if result.get("success"):
                results["email"]["sent"] += 1
            else:
                results["email"]["failed"] += 1
            
            # Log delivery
            log = DeliveryLog(
                user_id=user.id,
                channel="email",
                status="success" if result.get("success") else "failed",
                message_preview=request.message[:200],
                error_message=result.get("error"),
                gateway_response=result
            )
            db.add(log)
        
        # Push
        if request.channel in ["all", "push"] and prefs.channel_push == "enabled" and prefs.push_token:
            result = send_push(prefs.push_token, request.subject, request.message)
            if result.get("success"):
                results["push"]["sent"] += 1
            else:
                results["push"]["failed"] += 1
            
            # Log delivery
            log = DeliveryLog(
                user_id=user.id,
                channel="push",
                status="success" if result.get("success") else "failed",
                message_preview=request.message[:200],
                error_message=result.get("error"),
                gateway_response=result
            )
            db.add(log)
    
    db.commit()
    
    return {
        "message": "Broadcast completed",
        "results": results
    }


@router.post("/premium")
async def broadcast_to_premium(
    request: BroadcastRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 12: Broadcast message to premium users only.
    
    Requires premium/admin access.
    
    Args:
        request: Broadcast request
        current_user: Current authenticated user (must be premium/admin)
        db: Database session
    
    Returns:
        Broadcast result
    """
    # Override filter to premium
    request.user_filter = "premium"
    return await broadcast_to_all(request, current_user, db)

