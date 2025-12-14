"""
Phase 9: JWT Token Handler

JWT token creation and validation for user authentication.
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

from src.config import settings


# Phase 9: JWT Secret Key (from config or environment)
JWT_SECRET = os.getenv("JWT_SECRET", getattr(settings, "jwt_secret", "guru-api-secret-key-change-in-production"))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7  # Token expires in 7 days


def create_token(user_id: int, subscription_level: str = "free") -> str:
    """
    Phase 9: Create JWT token for authenticated user.
    
    Token includes:
    - user_id: User's database ID
    - subscription_level: User's subscription tier
    - exp: Expiration time (7 days from now)
    
    Args:
        user_id: User's database ID
        subscription_level: User's subscription level (free, premium, lifetime)
    
    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "subscription": subscription_level,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> Dict:
    """
    Phase 9: Decode and validate JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload dictionary
    
    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def get_user_from_token(token: str):
    """
    Phase 9: Get user ID and subscription from token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary with user_id and subscription
    """
    payload = decode_token(token)
    return {
        "user_id": payload.get("user_id"),
        "subscription": payload.get("subscription", "free")
    }



