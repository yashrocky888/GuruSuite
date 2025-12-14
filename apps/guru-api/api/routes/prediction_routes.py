"""
Phase 21: Prediction API Routes

Endpoints for daily, monthly, and yearly predictions.
"""

from fastapi import APIRouter, Depends, Request, Query
from typing import Dict, Optional
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


@router.post("/today", response_model=Dict)
async def get_today_prediction(
    request: Request,
    birth_details: BirthDetailsRequest,
    on_date: Optional[str] = Query(None, description="Date for prediction (YYYY-MM-DD, defaults to today)"),
    api_key: str = Depends(api_key_dependency)
):
    """
    Phase 21: Get today's transit prediction.
    
    POST /api/prediction/today
    """
    # Check rate limit
    check_rate_limit_middleware(request, api_key)
    
    # Validate input
    try:
        datetime.strptime(birth_details.birth_date, "%Y-%m-%d")
        if on_date:
            datetime.strptime(on_date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
    
    # Convert to dictionary
    birth_details_dict = {
        "birth_date": birth_details.birth_date,
        "birth_time": birth_details.birth_time,
        "birth_latitude": birth_details.birth_latitude,
        "birth_longitude": birth_details.birth_longitude,
        "timezone": birth_details.timezone
    }
    
    # Generate report
    with PerformanceTimer("today_prediction"):
        result = guru_api.get_today_transit_report(birth_details_dict, on_date)
    
    log_request(request, api_key, 0.0)
    
    return {
        "success": True,
        "data": result,
        "generated_at": datetime.now().isoformat()
    }


@router.post("/monthly", response_model=Dict)
async def get_monthly_prediction(
    request: Request,
    birth_details: BirthDetailsRequest,
    month: int = Query(..., ge=1, le=12, description="Month number (1-12)"),
    year: int = Query(..., description="Year"),
    api_key: str = Depends(api_key_dependency)
):
    """
    Phase 21: Get monthly prediction.
    
    POST /api/prediction/monthly
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
    with PerformanceTimer("monthly_prediction"):
        result = guru_api.get_monthly_prediction(birth_details_dict, month, year)
    
    log_request(request, api_key, 0.0)
    
    return {
        "success": True,
        "data": result,
        "generated_at": datetime.now().isoformat()
    }


@router.post("/yearly", response_model=Dict)
async def get_yearly_prediction(
    request: Request,
    birth_details: BirthDetailsRequest,
    year: int = Query(..., description="Year"),
    api_key: str = Depends(api_key_dependency)
):
    """
    Phase 21: Get yearly prediction.
    
    POST /api/prediction/yearly
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
    with PerformanceTimer("yearly_prediction"):
        result = guru_api.get_yearly_prediction(birth_details_dict, year)
    
    log_request(request, api_key, 0.0)
    
    return {
        "success": True,
        "data": result,
        "generated_at": datetime.now().isoformat()
    }

