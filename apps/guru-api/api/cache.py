"""
Phase 21: Caching Layer

Implements caching for expensive calculations.
"""

import hashlib
import json
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from functools import wraps


# In-memory cache (use Redis in production)
_cache_store: Dict[str, Dict[str, Any]] = {}


def generate_cache_key(*args, **kwargs) -> str:
    """
    Phase 21: Generate cache key from function arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Cache key string
    """
    # Create a hashable representation
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return key_hash


def cache_result(ttl_seconds: int = 3600):
    """
    Phase 21: Decorator to cache function results.
    
    Args:
        ttl_seconds: Time to live in seconds (default: 1 hour)
    
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{generate_cache_key(*args, **kwargs)}"
            
            # Check cache
            if cache_key in _cache_store:
                cached_data = _cache_store[cache_key]
                cached_time = cached_data.get("timestamp")
                
                # Check if cache is still valid
                if cached_time and (datetime.now() - cached_time).total_seconds() < ttl_seconds:
                    return cached_data.get("result")
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            _cache_store[cache_key] = {
                "result": result,
                "timestamp": datetime.now()
            }
            
            return result
        
        return wrapper
    return decorator


def clear_cache(pattern: Optional[str] = None):
    """
    Phase 21: Clear cache entries.
    
    Args:
        pattern: Optional pattern to match cache keys (if None, clears all)
    """
    global _cache_store
    
    if pattern:
        keys_to_remove = [k for k in _cache_store.keys() if pattern in k]
        for key in keys_to_remove:
            del _cache_store[key]
    else:
        _cache_store.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Phase 21: Get cache statistics.
    
    Returns:
        Cache statistics dictionary
    """
    return {
        "total_entries": len(_cache_store),
        "cache_keys": list(_cache_store.keys())[:10]  # First 10 keys
    }

