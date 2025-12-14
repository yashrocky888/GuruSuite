"""
Phase 9: Authentication Middleware

Middleware for protecting routes based on subscription level.
"""

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.auth.jwt_handler import decode_token
from src.db.database import SessionLocal
from src.db.models import User

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Phase 9: Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
    
    Returns:
        User object from database
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id = payload.get("user_id")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
        finally:
            db.close()
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")


def require_premium(user = None):
    """
    Phase 9: Require premium subscription for route access.
    
    Args:
        user: Current user object (from get_current_user)
    
    Raises:
        HTTPException: If user doesn't have premium subscription
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if user.subscription_level not in ["premium", "lifetime"]:
        raise HTTPException(
            status_code=403,
            detail="Premium subscription required for this feature"
        )


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = None):
    """
    Phase 9: Get user if token provided, otherwise return None.
    
    Useful for routes that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Bearer token credentials
    
    Returns:
        User object or None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id = payload.get("user_id")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user
        finally:
            db.close()
    except:
        return None

