"""
Planetary Strength API routes.

Phase 5: Shadbala and Ashtakavarga calculation endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import swisseph as swe

from src.jyotish.strength.shadbala import calculate_shadbala
from src.jyotish.strength.ashtakavarga import calculate_ashtakavarga
from src.jyotish.kundli_engine import get_planet_positions
from src.ephemeris.ephemeris_utils import get_ascendant, get_houses

router = APIRouter()


@router.get("/shadbala")
def get_shadbala(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Phase 5: Calculate Shadbala (Six-fold Strength) for all planets.
    
    Shadbala consists of:
    - Naisargika Bala (Natural strength)
    - Cheshta Bala (Motional strength - retrograde)
    - Sthana Bala (Positional strength)
    - Dig Bala (Directional strength)
    - Kala Bala (Temporal strength)
    - Drik Bala (Aspectual strength)
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        Complete Shadbala data for all planets
    """
    try:
        # Parse date and time
        dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        
        # Calculate Julian Day
        jd = swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Calculate Shadbala
        shadbala_data = calculate_shadbala(jd, lat, lon)
        
        return {
            "julian_day": round(jd, 6),
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon
            },
            "shadbala": shadbala_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating shadbala: {str(e)}")


@router.get("/ashtakavarga")
def get_ashtakavarga(
    dob: str = Query(..., description="Date of birth in YYYY-MM-DD format"),
    time: str = Query(..., description="Time of birth in HH:MM format"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Phase 5: Calculate Ashtakavarga (Eight-fold Division).
    
    Ashtakavarga shows house strength based on planetary relationships:
    - Bhinnashtakavarga (BAV): Individual planet's ashtakavarga
    - Sarvashtakavarga (SAV): Combined ashtakavarga of all planets
    
    Args:
        dob: Date of birth (YYYY-MM-DD)
        time: Time of birth (HH:MM)
        lat: Birth latitude
        lon: Birth longitude
    
    Returns:
        Complete Ashtakavarga data (BAV + SAV)
    """
    try:
        # Parse date and time
        dt = datetime.strptime(f"{dob} {time}", "%Y-%m-%d %H:%M")
        
        # Calculate Julian Day
        jd = swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute / 60.0,
            swe.GREG_CAL
        )
        
        # Get planet positions (sidereal)
        planet_positions = get_planet_positions(jd)
        
        # Get ascendant and houses
        ascendant = get_ascendant(jd, lat, lon)
        houses_list = get_houses(jd, lat, lon)
        
        # Calculate Ashtakavarga
        ashtakavarga_data = calculate_ashtakavarga(
            planet_positions, houses_list, ascendant
        )
        
        return {
            "julian_day": round(jd, 6),
            "birth_details": {
                "date": dob,
                "time": time,
                "latitude": lat,
                "longitude": lon
            },
            "ashtakavarga": ashtakavarga_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating ashtakavarga: {str(e)}")

