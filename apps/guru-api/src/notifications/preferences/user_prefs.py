"""
Phase 12: User Notification Preferences

Manages user notification delivery preferences.
"""

from typing import Optional
from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import NotificationPreferences, User


def get_prefs(user_id: int, db: Optional[Session] = None) -> NotificationPreferences:
    """
    Phase 12: Get user notification preferences, create default if not exists.
    
    Args:
        user_id: User ID
        db: Optional database session (creates new if not provided)
    
    Returns:
        NotificationPreferences object
    """
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        prefs = db.query(NotificationPreferences).filter(
            NotificationPreferences.user_id == user_id
        ).first()
        
        if not prefs:
            # Create default preferences
            prefs = NotificationPreferences(
                user_id=user_id,
                delivery_time="06:00",
                channel_whatsapp="disabled",
                channel_email="enabled",
                channel_push="disabled",
                channel_inapp="enabled",
                language="english"
            )
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        
        return prefs
    finally:
        if should_close:
            db.close()


def update_prefs(
    user_id: int,
    delivery_time: Optional[str] = None,
    channel_whatsapp: Optional[str] = None,
    channel_email: Optional[str] = None,
    channel_push: Optional[str] = None,
    channel_inapp: Optional[str] = None,
    language: Optional[str] = None,
    whatsapp_number: Optional[str] = None,
    push_token: Optional[str] = None,
    db: Optional[Session] = None
) -> NotificationPreferences:
    """
    Phase 12: Update user notification preferences.
    
    Args:
        user_id: User ID
        delivery_time: Preferred delivery time (HH:MM)
        channel_whatsapp: WhatsApp channel status (enabled/disabled)
        channel_email: Email channel status (enabled/disabled)
        channel_push: Push channel status (enabled/disabled)
        channel_inapp: In-app channel status (enabled/disabled)
        language: Preferred language (english/hindi/kannada)
        whatsapp_number: WhatsApp number
        push_token: FCM push token
        db: Optional database session
    
    Returns:
        Updated NotificationPreferences object
    """
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        prefs = get_prefs(user_id, db)
        
        if delivery_time is not None:
            prefs.delivery_time = delivery_time
        if channel_whatsapp is not None:
            prefs.channel_whatsapp = channel_whatsapp
        if channel_email is not None:
            prefs.channel_email = channel_email
        if channel_push is not None:
            prefs.channel_push = channel_push
        if channel_inapp is not None:
            prefs.channel_inapp = channel_inapp
        if language is not None:
            prefs.language = language
        if whatsapp_number is not None:
            prefs.whatsapp_number = whatsapp_number
        if push_token is not None:
            prefs.push_token = push_token
        
        db.commit()
        db.refresh(prefs)
        
        return prefs
    finally:
        if should_close:
            db.close()

