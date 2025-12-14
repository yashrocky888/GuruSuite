"""
Astro Event Detection API routes.

Phase 17: Endpoints for detecting astrological events.
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional

from src.auth.jwt_handler import decode_token
from src.guru2.context_manager import build_full_context
from src.db.database import SessionLocal
from src.db.models import BirthDetail, User

router = APIRouter()


def get_user_from_token(token: str) -> User:
    """
    Phase 17: Get user from JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        User object
    
    Raises:
        HTTPException if token is invalid
    """
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


@router.get("/events")
async def get_astro_events(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None, description="JWT token (alternative to Authorization header)")
):
    """
    Phase 17: Get detected astrological events for the user.
    
    Detects:
    - Bad/Danger periods (Rikta Tithi, Vishti Karana, Moon in 8th, etc.)
    - Good/Auspicious periods (Pushkara, Siddhi Yoga, etc.)
    
    Requires:
    - Valid JWT token
    - User must have birth data saved
    
    Args:
        authorization: Bearer token in header
        token: Alternative token in query parameter
    
    Returns:
        Dictionary with detected events
    """
    # Extract token
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
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
        
        # Build context and detect events
        context = build_full_context(birth_data)
        events = context.get("events", {})
        
        return {
            "user_id": user.id,
            "detected_at": context.get("panchang", {}).get("date", "N/A"),
            "events": events,
            "summary": {
                "total_bad_events": events.get("total_bad", 0),
                "total_good_events": events.get("total_good", 0),
                "day_status": events.get("day_status", "normal"),
                "alerts_needed": len(events.get("alerts_needed", []))
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting events: {str(e)}")
    
    finally:
        db.close()


@router.get("/events/bad")
async def get_bad_events(
    authorization: Optional[str] = Header(None)
):
    """
    Phase 17: Get only bad/challenging events.
    
    Args:
        authorization: Bearer token
    
    Returns:
        List of bad events
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    
    token = authorization.replace("Bearer ", "").strip()
    user = get_user_from_token(token)
    
    db = SessionLocal()
    try:
        birth_data = db.query(BirthDetail).filter(BirthDetail.user_id == user.id).first()
        if not birth_data:
            raise HTTPException(status_code=400, detail="Birth data not found")
        
        context = build_full_context(birth_data)
        events = context.get("events", {})
        
        return {
            "bad_events": events.get("bad_events", []),
            "count": len(events.get("bad_events", [])),
            "day_status": events.get("day_status", "normal")
        }
    
    finally:
        db.close()


@router.get("/events/good")
async def get_good_events(
    authorization: Optional[str] = Header(None)
):
    """
    Phase 17: Get only good/auspicious events.
    
    Args:
        authorization: Bearer token
    
    Returns:
        List of good events
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    
    token = authorization.replace("Bearer ", "").strip()
    user = get_user_from_token(token)
    
    db = SessionLocal()
    try:
        birth_data = db.query(BirthDetail).filter(BirthDetail.user_id == user.id).first()
        if not birth_data:
            raise HTTPException(status_code=400, detail="Birth data not found")
        
        context = build_full_context(birth_data)
        events = context.get("events", {})
        
        return {
            "good_events": events.get("good_events", []),
            "count": len(events.get("good_events", [])),
            "day_status": events.get("day_status", "normal")
        }
    
    finally:
        db.close()

