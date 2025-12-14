"""
Notification API routes.

Phase 10: User notification history and management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.db.database import get_db
from src.db.models import Notification
from src.auth.middleware import get_current_user

router = APIRouter()


@router.get("/history")
async def get_notification_history(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 10: Get user's notification history.
    
    Args:
        limit: Maximum number of notifications to return
        offset: Number of notifications to skip
        unread_only: If True, return only unread notifications
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of notifications
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == "unread")
    
    # Order by most recent first
    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    total_count = query.count()
    
    return {
        "total": total_count,
        "count": len(notifications),
        "notifications": [
            {
                "id": n.id,
                "type": n.notification_type,
                "title": n.title,
                "summary": n.summary,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "prediction_data": n.prediction_data
            }
            for n in notifications
        ]
    }


@router.get("/unread-count")
async def get_unread_count(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 10: Get count of unread notifications.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Unread notification count
    """
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == "unread"
    ).count()
    
    return {
        "unread_count": count
    }


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 10: Mark a notification as read.
    
    Args:
        notification_id: Notification ID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Success message
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = "read"
    notification.read_at = datetime.now()
    
    db.commit()
    
    return {
        "message": "Notification marked as read",
        "notification_id": notification_id
    }


@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 10: Mark all notifications as read for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Success message with count
    """
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == "unread"
    ).update({
        "is_read": "read",
        "read_at": datetime.now()
    })
    
    db.commit()
    
    return {
        "message": f"{count} notifications marked as read",
        "count": count
    }


@router.get("/latest")
async def get_latest_notification(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 10: Get the latest notification for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Latest notification or null
    """
    notification = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).first()
    
    if not notification:
        return {
            "notification": None,
            "message": "No notifications found"
        }
    
    return {
        "notification": {
            "id": notification.id,
            "type": notification.notification_type,
            "title": notification.title,
            "summary": notification.summary,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "prediction_data": notification.prediction_data
        }
    }

