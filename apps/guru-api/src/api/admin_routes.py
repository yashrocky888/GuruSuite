"""
Admin API routes.

Phase 10: Admin endpoints for system management and debugging.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.db.database import get_db
from src.db.models import User, Notification
from src.notifications.notification_engine import run_daily_notifications
from src.notifications.scheduler import get_scheduler_status
from src.auth.middleware import get_current_user

router = APIRouter()


def require_admin(current_user = None):
    """
    Phase 10: Require admin access (simplified - check subscription or add admin flag).
    
    For now, allow premium users or add admin check later.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # TODO: Add proper admin check (e.g., is_admin flag in User model)
    # For now, allow premium users
    if current_user.subscription_level not in ["premium", "lifetime"]:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.post("/trigger-daily")
async def manual_trigger_daily(
    current_user = Depends(get_current_user)
):
    """
    Phase 10: Manually trigger daily notification generation.
    
    Useful for testing and debugging.
    
    Args:
        current_user: Current authenticated user (must be admin/premium)
    
    Returns:
        Trigger result
    """
    # Allow premium users for now (add proper admin check later)
    if current_user.subscription_level not in ["premium", "lifetime"]:
        raise HTTPException(status_code=403, detail="Premium access required")
    
    try:
        result = run_daily_notifications()
        return {
            "message": "Daily notifications triggered manually",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering notifications: {str(e)}")


@router.get("/scheduler-status")
async def get_scheduler_status_endpoint(
    current_user = Depends(get_current_user)
):
    """
    Phase 10: Get scheduler status.
    
    Args:
        current_user: Current authenticated user (must be admin/premium)
    
    Returns:
        Scheduler status
    """
    if current_user.subscription_level not in ["premium", "lifetime"]:
        raise HTTPException(status_code=403, detail="Premium access required")
    
    status = get_scheduler_status()
    return status


@router.get("/notifications-stats")
async def get_notifications_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 10: Get notification statistics.
    
    Args:
        current_user: Current authenticated user (must be admin/premium)
        db: Database session
    
    Returns:
        Notification statistics
    """
    if current_user.subscription_level not in ["premium", "lifetime"]:
        raise HTTPException(status_code=403, detail="Premium access required")
    
    total_notifications = db.query(Notification).count()
    unread_count = db.query(Notification).filter(Notification.is_read == "unread").count()
    today_count = db.query(Notification).filter(
        Notification.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
    ).count()
    
    return {
        "total_notifications": total_notifications,
        "unread_count": unread_count,
        "today_count": today_count,
        "read_count": total_notifications - unread_count
    }


@router.get("/users-stats")
async def get_users_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 10: Get user statistics.
    
    Args:
        current_user: Current authenticated user (must be admin/premium)
        db: Database session
    
    Returns:
        User statistics
    """
    if current_user.subscription_level not in ["premium", "lifetime"]:
        raise HTTPException(status_code=403, detail="Premium access required")
    
    total_users = db.query(User).count()
    users_with_birth_data = db.query(User).join(User.birth_details).distinct().count()
    premium_users = db.query(User).filter(User.subscription_level.in_(["premium", "lifetime"])).count()
    notifications_enabled = db.query(User).filter(User.daily_notifications == "enabled").count()
    
    return {
        "total_users": total_users,
        "users_with_birth_data": users_with_birth_data,
        "premium_users": premium_users,
        "notifications_enabled": notifications_enabled
    }

