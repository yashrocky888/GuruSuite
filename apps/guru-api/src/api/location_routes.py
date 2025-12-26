"""
Location Search API routes.

This module provides a proxy endpoint for location search to avoid CORS issues
when calling external geocoding services from the frontend.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Nominatim API endpoint
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"


@router.get("/location/search")
async def search_location(q: str = Query(..., description="Location search query")):
    """
    Search locations using OpenStreetMap Nominatim API (proxy endpoint).
    
    This endpoint proxies requests to Nominatim to avoid CORS issues
    when calling from the frontend browser.
    
    Args:
        q: Search query string (e.g., "Bangalore", "New York")
    
    Returns:
        List of location suggestions:
        [
            {
                "name": str,
                "display_name": str,
                "lat": float,
                "lon": float,
                "country": str,
                "state": Optional[str]
            }
        ]
    """
    if not q or len(q) < 2:
        return JSONResponse(status_code=200, content=[])
    
    try:
        # Call Nominatim API with required headers
        # Increased timeout to 15 seconds (Nominatim can be slow)
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(
                NOMINATIM_BASE_URL,
                params={
                    "q": q,
                    "format": "json",
                    "addressdetails": "1",
                    "limit": 5,
                },
                headers={
                    "User-Agent": "GuruSuite/1.0 (https://guru-api-660206747784.asia-south1.run.app)",
                    "Accept": "application/json",
                    "Referer": "https://guru-api-660206747784.asia-south1.run.app",
                },
            )
            
            # Check if response is HTML (blocked page) instead of JSON
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" in content_type:
                logger.warning(f"Location search blocked by Nominatim for query: {q}")
                return JSONResponse(status_code=200, content=[])
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            results = response.json() or []
            
            # Transform Nominatim results to normalized format
            normalized_results: List[Dict] = []
            for item in results:
                address = item.get("address", {})
                city = (
                    address.get("city") or
                    address.get("town") or
                    address.get("village") or
                    address.get("municipality") or
                    ""
                )
                country = address.get("country", "")
                state = address.get("state") or address.get("region", "")
                
                # Build display name
                display_name_parts = []
                if city:
                    display_name_parts.append(city)
                if state:
                    display_name_parts.append(state)
                if country:
                    display_name_parts.append(country)
                
                display_name = ", ".join(display_name_parts) if display_name_parts else item.get("display_name", q)
                
                normalized_results.append({
                    "name": city or item.get("display_name", q).split(",")[0],
                    "display_name": display_name,
                    "lat": float(item.get("lat", 0)),
                    "lon": float(item.get("lon", 0)),
                    "country": country,
                    "state": state if state else None,
                })
            
            logger.info(f"Location search for '{q}': found {len(normalized_results)} results")
            return JSONResponse(status_code=200, content=normalized_results)
            
    except httpx.TimeoutException:
        logger.warning(f"Location search timeout for query: {q}")
        return JSONResponse(status_code=200, content=[])
    except httpx.HTTPStatusError as e:
        logger.error(f"Location search HTTP error for query '{q}': {e.response.status_code}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"External service error: {e.response.status_code}"}
        )
    except Exception as e:
        logger.error(f"Location search error for query '{q}': {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Location search failed: {str(e)}"}
        )

