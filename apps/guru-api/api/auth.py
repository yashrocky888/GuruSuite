"""
Phase 21: API Key Authentication

Handles API key verification and management.
"""

import os
from typing import Optional, List
from fastapi import Request, HTTPException, status
from starlette.status import HTTP_401_UNAUTHORIZED


def load_api_keys_from_env() -> List[str]:
    """
    Phase 21: Load API keys from environment variable.
    
    Returns:
        List of valid API keys
    """
    api_keys_str = os.getenv("API_KEYS", "")
    
    if not api_keys_str:
        # Default key for development (should be changed in production)
        return ["dev-api-key-change-in-production"]
    
    # Split comma-separated keys
    keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
    
    return keys if keys else ["dev-api-key-change-in-production"]


# Cache API keys
_VALID_API_KEYS = None


def get_valid_api_keys() -> List[str]:
    """
    Phase 21: Get cached valid API keys.
    
    Returns:
        List of valid API keys
    """
    global _VALID_API_KEYS
    
    if _VALID_API_KEYS is None:
        _VALID_API_KEYS = load_api_keys_from_env()
    
    return _VALID_API_KEYS


def verify_api_key(request: Request) -> str:
    """
    Phase 21: Verify API key from request header.
    
    Args:
        request: FastAPI request object
    
    Returns:
        API key if valid
    
    Raises:
        HTTPException: If API key is missing or invalid
    """
    api_key = request.headers.get("x-api-key")
    
    if not api_key:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="API key is required. Please provide 'x-api-key' header."
        )
    
    valid_keys = get_valid_api_keys()
    
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API key. Please check your API key and try again."
        )
    
    return api_key


def api_key_dependency(request: Request) -> str:
    """
    Phase 21: FastAPI dependency for API key verification.
    
    Args:
        request: FastAPI request object
    
    Returns:
        API key if valid
    """
    return verify_api_key(request)

