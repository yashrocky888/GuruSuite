"""
Location utility functions for geocoding and coordinate validation.

Provides functions to validate and convert geographic coordinates,
and optionally geocode place names to coordinates.
"""

from typing import Tuple, Optional
import requests


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate that coordinates are within valid ranges.
    
    Args:
        latitude: Latitude in degrees (-90 to 90)
        longitude: Longitude in degrees (-180 to 180)
    
    Returns:
        True if coordinates are valid, False otherwise
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def geocode_place(place_name: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float]]:
    """
    Geocode a place name to coordinates using OpenStreetMap Nominatim API.
    
    This is a free service, but for production use, consider using
    a paid geocoding service for better reliability.
    
    Args:
        place_name: Name of the place to geocode
        api_key: Optional API key (not used for Nominatim, but kept for future use)
    
    Returns:
        Tuple of (latitude, longitude) if found, None otherwise
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "Guru-API/1.0"  # Required by Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return (lat, lon)
        
        return None
    except Exception:
        # Return None on any error (network, parsing, etc.)
        return None


def get_ayanamsa_offset(julian_day: float) -> float:
    """
    Calculate Ayanamsa offset for Lahiri (Chitra Paksha) ayanamsa.
    
    Ayanamsa is the difference between tropical and sidereal zodiac.
    Lahiri ayanamsa is the most commonly used in Indian astrology.
    
    Args:
        julian_day: Julian Day Number
    
    Returns:
        Ayanamsa offset in degrees
    """
    # Formula for Lahiri Ayanamsa
    # This is a simplified calculation; Swiss Ephemeris provides more accurate values
    t = (julian_day - 2451545.0) / 36525.0
    ayanamsa = 23.85305556 + (0.01388889 * t) + (0.00000000000000000001 * t * t)
    return ayanamsa

