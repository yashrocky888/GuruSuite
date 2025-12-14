"""
Phase 21: Health Check Route

Simple health check endpoint.
"""

from fastapi import APIRouter
from typing import Dict
from datetime import datetime

router = APIRouter()


@router.get("/health", response_model=Dict)
async def health_check():
    """
    Phase 21: Health check endpoint.
    
    GET /api/health
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Guru API"
    }

