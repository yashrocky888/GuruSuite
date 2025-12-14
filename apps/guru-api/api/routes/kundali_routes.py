"""
Phase 21: Kundali API Routes

Endpoints for birth chart and full interpretation.
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
    birth_latitude: float = None
    birth_longitude: float = None
    birth_place: str = None  # Place name (will be geocoded if coordinates not provided)
    timezone: str = "UTC"


@router.post("/full", response_model=Dict)
async def get_full_kundali(
    request: Request,
    birth_details: BirthDetailsRequest,
    api_key: str = Depends(api_key_dependency)
):
    """
    Phase 21: Get full kundali with interpretation.
    
    POST /api/kundali/full
    """
    # Check rate limit
    check_rate_limit_middleware(request, api_key)
    
    # Validate input
    try:
        datetime.strptime(birth_details.birth_date, "%Y-%m-%d")
        hour, minute = map(int, birth_details.birth_time.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValidationError("Invalid birth time format. Use HH:MM (24-hour format).")
    except ValueError:
        raise ValidationError("Invalid birth date format. Use YYYY-MM-DD.")
    
    # Get precise coordinates (location-based like Drik Panchanga)
    latitude = birth_details.birth_latitude
    longitude = birth_details.birth_longitude
    
    # If place name provided but coordinates not, geocode the place
    if (latitude is None or longitude is None) and birth_details.birth_place:
        from src.utils.location import geocode_place
        coords = geocode_place(birth_details.birth_place)
        if coords:
            latitude, longitude = coords
        else:
            raise ValidationError(f"Could not geocode place: {birth_details.birth_place}. Please provide latitude and longitude.")
    elif latitude is None or longitude is None:
        raise ValidationError("Either birth_place or both birth_latitude and birth_longitude must be provided.")
    
    # Validate coordinates
    from src.utils.location import validate_coordinates
    if not validate_coordinates(latitude, longitude):
        raise ValidationError("Invalid coordinates. Latitude must be -90 to 90, Longitude must be -180 to 180.")
    
    # Convert to dictionary with precise coordinates
    birth_details_dict = {
        "birth_date": birth_details.birth_date,
        "birth_time": birth_details.birth_time,
        "birth_latitude": latitude,
        "birth_longitude": longitude,
        "birth_place": birth_details.birth_place or "",
        "timezone": birth_details.timezone
    }
    
    # Generate report
    with PerformanceTimer("full_kundali"):
        result = guru_api.get_full_report(birth_details_dict)
    
    # Log request
    log_request(request, api_key, 0.0)  # Duration logged by timer
    
    return {
        "success": True,
        "data": result,
        "generated_at": datetime.now().isoformat()
    }

