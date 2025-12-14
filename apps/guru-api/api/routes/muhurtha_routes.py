"""
Phase 21: Muhurtha API Routes

Endpoints for Muhurtha calculations.
"""

from fastapi import APIRouter, Depends, Request, Query
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


@router.post("/get", response_model=Dict)
async def get_muhurtha(
    request: Request,
    birth_details: BirthDetailsRequest,
    task: str = Query(..., description="Task type: travel, job_application, marriage_talk, investment, property_purchase, business_start, medical_treatment, spiritual_initiation, naming_ceremony"),
    date: str = Query(..., description="Date for Muhurtha (YYYY-MM-DD)"),
    api_key: str = Depends(api_key_dependency)
):
    """
    Phase 21: Get best Muhurtha time windows.
    
    POST /api/muhurtha/get
    """
    # Check rate limit
    check_rate_limit_middleware(request, api_key)
    
    # Validate input
    try:
        datetime.strptime(birth_details.birth_date, "%Y-%m-%d")
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
    
    # Valid task types
    valid_tasks = [
        "travel", "job_application", "marriage_talk", "investment",
        "property_purchase", "business_start", "medical_treatment",
        "spiritual_initiation", "naming_ceremony", "buy_vehicle", "general"
    ]
    
    if task not in valid_tasks:
        raise ValidationError(f"Invalid task type. Must be one of: {', '.join(valid_tasks)}")
    
    # Parse date
    calc_date = datetime.strptime(date, "%Y-%m-%d")
    
    # Build location
    location = {
        "latitude": birth_details.birth_latitude,
        "longitude": birth_details.birth_longitude,
        "timezone": birth_details.timezone
    }
    
    # Convert to dictionary
    birth_details_dict = {
        "birth_date": birth_details.birth_date,
        "birth_time": birth_details.birth_time,
        "birth_latitude": birth_details.birth_latitude,
        "birth_longitude": birth_details.birth_longitude,
        "timezone": birth_details.timezone
    }
    
    # Generate Muhurtha
    with PerformanceTimer("muhurtha"):
        result = guru_api.get_muhurtha(task, calc_date, location, birth_details_dict)
    
    log_request(request, api_key, 0.0)
    
    return {
        "success": True,
        "data": result,
        "generated_at": datetime.now().isoformat()
    }

