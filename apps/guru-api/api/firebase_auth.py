"""
Phase 21: Firebase Firestore API Key Authentication

Loads API keys from Firebase Firestore with caching.
"""

import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: firebase-admin not installed. Using fallback authentication.")


# Global cache for API keys
_api_keys_cache: Dict[str, Dict] = {}
_cache_timestamp: Optional[datetime] = None
_cache_ttl = timedelta(minutes=5)  # Cache for 5 minutes


def initialize_firebase():
    """
    Initialize Firebase Admin SDK.
    
    Returns:
        Firestore client or None
    """
    if not FIREBASE_AVAILABLE:
        return None
    
    # Check if already initialized
    if firebase_admin._apps:
        return firestore.client()
    
    # Get credentials - can be a file path or JSON content
    cred_value = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_value:
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. Using fallback authentication.")
        return None
    
    try:
        import json
        import tempfile
        
        # Check if it's a file path or JSON content
        if os.path.exists(cred_value):
            # It's a file path
            cred = credentials.Certificate(cred_value)
        else:
            # It might be JSON content - try to parse it
            try:
                # Try parsing as JSON
                cred_dict = json.loads(cred_value)
                # Write to temp file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(cred_dict, f)
                    temp_path = f.name
                cred = credentials.Certificate(temp_path)
            except (json.JSONDecodeError, ValueError):
                # Not JSON, treat as file path anyway
                cred = credentials.Certificate(cred_value)
        
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Warning: Could not initialize Firebase: {e}. Using fallback authentication.")
        return None


def load_api_keys_from_firestore() -> Dict[str, Dict]:
    """
    Load API keys from Firebase Firestore.
    
    Returns:
        Dictionary mapping API keys to their metadata
    """
    db = initialize_firebase()
    if not db:
        return {}
    
    try:
        # Get all active API keys from Firestore
        api_keys_ref = db.collection('api_keys')
        docs = api_keys_ref.where('active', '==', True).stream()
        
        keys_dict = {}
        for doc in docs:
            data = doc.to_dict()
            key_value = data.get('key')
            if key_value:
                keys_dict[key_value] = {
                    'name': data.get('name', ''),
                    'created_at': data.get('created_at'),
                    'last_used': data.get('last_used'),
                    'usage_count': data.get('usage_count', 0),
                    'active': data.get('active', True)
                }
        
        return keys_dict
    except Exception as e:
        print(f"Error loading API keys from Firestore: {e}")
        return {}


def get_cached_api_keys() -> Dict[str, Dict]:
    """
    Get API keys from cache or load from Firestore.
    
    Returns:
        Dictionary of API keys
    """
    global _api_keys_cache, _cache_timestamp
    
    now = datetime.now()
    
    # Check if cache is valid
    if _cache_timestamp and (now - _cache_timestamp) < _cache_ttl:
        return _api_keys_cache
    
    # Load from Firestore
    _api_keys_cache = load_api_keys_from_firestore()
    _cache_timestamp = now
    
    return _api_keys_cache


def load_api_keys_from_env() -> List[str]:
    """
    Fallback: Load API keys from environment variable.
    
    Returns:
        List of API keys
    """
    api_keys_str = os.getenv("API_KEYS", "")
    
    if not api_keys_str:
        return ["dev-api-key-change-in-production"]
    
    keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
    return keys if keys else ["dev-api-key-change-in-production"]


def verify_api_key(request: Request) -> str:
    """
    Verify API key from request header.
    Checks Firestore first, then falls back to environment.
    
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
    
    # Try Firestore first
    cached_keys = get_cached_api_keys()
    if cached_keys and api_key in cached_keys:
        # Update last used timestamp (async, don't block)
        try:
            db = initialize_firebase()
            if db:
                api_keys_ref = db.collection('api_keys')
                docs = api_keys_ref.where('key', '==', api_key).stream()
                for doc in docs:
                    doc.reference.update({
                        'last_used': firestore.SERVER_TIMESTAMP,
                        'usage_count': firestore.Increment(1)
                    })
        except Exception:
            pass  # Don't fail if update fails
        
        return api_key
    
    # Fallback to environment variable
    env_keys = load_api_keys_from_env()
    if api_key in env_keys:
        return api_key
    
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid API key. Please check your API key and try again."
    )


def api_key_dependency(request: Request) -> str:
    """
    FastAPI dependency for API key verification.
    
    Args:
        request: FastAPI request object
    
    Returns:
        API key if valid
    """
    return verify_api_key(request)


def clear_api_keys_cache():
    """Clear the API keys cache to force reload."""
    global _api_keys_cache, _cache_timestamp
    _api_keys_cache = {}
    _cache_timestamp = None

