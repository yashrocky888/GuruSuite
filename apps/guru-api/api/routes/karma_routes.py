"""
Phase 21: Karma API Routes

Endpoints for karma and soul path reports.
"""

from fastapi import APIRouter, Depends, Request
from typing import Dict
from pydantic import BaseModel
from datetime import datetime

from api.firebase_auth import api_key_dependency
from api.rate_limiter import check_rate_limit_middleware
from api.logging import log_request, PerformanceTimer
from api.errors import ValidationError
from guru_api import guru_api

router = APIRouter()


class BirthDetailsRequest(BaseModel):
    """Phase 21: Birth details request model."""
    birth_date: str  # YYYY-MM-DD
    birth_time: str  # HH:MM
    birth_latitude: float
    birth_longitude: float
    timezone: str = "UTC"


@router.post("/report", response_model=Dict)
async def get_karma_report(
    request: Request,
    birth_details: BirthDetailsRequest,
    api_key: str = Depends(api_key_dependency)
):
    """
    Phase 21: Get karma and soul path report.
    
    POST /api/karma/report
    """
    # Check rate limit
    check_rate_limit_middleware(request, api_key)
    
    # Validate input
    try:
        datetime.strptime(birth_details.birth_date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Invalid birth date format. Use YYYY-MM-DD.")
    
    # Convert to dictionary
    birth_details_dict = {
        "birth_date": birth_details.birth_date,
        "birth_time": birth_details.birth_time,
        "birth_latitude": birth_details.birth_latitude,
        "birth_longitude": birth_details.birth_longitude,
        "timezone": birth_details.timezone
    }
    
    # Generate report
    with PerformanceTimer("karma_report"):
        result = guru_api.get_karma_report(birth_details_dict)
    
    log_request(request, api_key, 0.0)
    
    return {
        "success": True,
        "data": result,
        "generated_at": datetime.now().isoformat()
    }

