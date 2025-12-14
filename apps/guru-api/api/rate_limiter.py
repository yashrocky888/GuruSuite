"""
Phase 21: Rate Limiting

Implements rate limiting for API endpoints.
"""

import os
import time
from typing import Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


# In-memory rate limit storage
# In production, use Redis for distributed systems
_rate_limit_store: Dict[str, Dict] = defaultdict(dict)


class RateLimiter:
    """
    Phase 21: Rate limiter class.
    
    Supports:
    - Requests per minute
    - Requests per day
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_day: int = 1000
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_day: Maximum requests per day
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
    
    def check_rate_limit(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Phase 21: Check if request is within rate limits.
        
        Args:
            api_key: API key identifier
        
        Returns:
            Tuple of (is_allowed, error_message)
        """
        now = datetime.now()
        key_data = _rate_limit_store[api_key]
        
        # Initialize if first request
        if "minute_requests" not in key_data:
            key_data["minute_requests"] = []
            key_data["day_requests"] = []
            key_data["day_start"] = now.date()
        
        # Reset day counter if new day
        if key_data["day_start"] != now.date():
            key_data["day_requests"] = []
            key_data["day_start"] = now.date()
        
        # Clean old minute requests (older than 1 minute)
        minute_requests = key_data["minute_requests"]
        minute_requests[:] = [
            req_time for req_time in minute_requests
            if (now - req_time).total_seconds() < 60
        ]
        
        # Check minute limit
        if len(minute_requests) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
        
        # Check day limit
        day_requests = key_data["day_requests"]
        if len(day_requests) >= self.requests_per_day:
            return False, f"Rate limit exceeded: {self.requests_per_day} requests per day"
        
        # Record request
        minute_requests.append(now)
        day_requests.append(now)
        
        return True, None
    
    def get_rate_limit_headers(self, api_key: str) -> Dict[str, str]:
        """
        Phase 21: Get rate limit headers for response.
        
        Args:
            api_key: API key identifier
        
        Returns:
            Dictionary of rate limit headers
        """
        key_data = _rate_limit_store.get(api_key, {})
        minute_requests = len(key_data.get("minute_requests", []))
        day_requests = len(key_data.get("day_requests", []))
        
        return {
            "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
            "X-RateLimit-Remaining-Minute": str(max(0, self.requests_per_minute - minute_requests)),
            "X-RateLimit-Limit-Day": str(self.requests_per_day),
            "X-RateLimit-Remaining-Day": str(max(0, self.requests_per_day - day_requests))
        }


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
    requests_per_day=int(os.getenv("RATE_LIMIT_PER_DAY", "1000"))
)


def check_rate_limit_middleware(request: Request, api_key: str):
    """
    Phase 21: Middleware function to check rate limits.
    
    Args:
        request: FastAPI request
        api_key: API key
    
    Raises:
        HTTPException: If rate limit exceeded
    """
    is_allowed, error_message = rate_limiter.check_rate_limit(api_key)
    
    if not is_allowed:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail=error_message,
            headers=rate_limiter.get_rate_limit_headers(api_key)
        )

