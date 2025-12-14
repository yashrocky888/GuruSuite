"""
Varga (Divisional Charts) calculation module.

This module provides functions to calculate various divisional charts:
- D9 (Navamsa) - 9th division chart
- D10 (Dasamsa) - 10th division chart
- And other vargas
"""

from typing import Dict
from datetime import datetime

from src.ephemeris.planets import calculate_planets_sidereal
from src.ephemeris.houses import calculate_houses_sidereal
from src.utils.timezone import local_to_utc
from src.utils.converters import normalize_degrees, degrees_to_sign, get_sign_name


def varga_degree(main_degree: float, n: int) -> float:
    """
    Calculate varga (divisional chart) degree for a given division.
    
    Formula: (main_degree % 30) * n
    This gives the position within the sign multiplied by the division number.
    
    Args:
        main_degree: Main chart degree (0-360)
        n: Division number (e.g., 9 for Navamsa, 10 for Dasamsa)
    
    Returns:
        Varga degree
    """
    # Get degrees within the sign (0-30)
    degrees_in_sign = main_degree % 30
    # Multiply by division number
    varga_deg = degrees_in_sign * n
    return normalize_degrees(varga_deg)


def generate_navamsa(degree: float) -> float:
    """
    Generate Navamsa (D9) degree from main chart degree.
    
    Navamsa is the 9th division chart.
    
    Args:
        degree: Main chart degree
    
    Returns:
        Navamsa degree
    """
    return varga_degree(degree, 9)


def generate_dasamsa(degree: float) -> float:
    """
    Generate Dasamsa (D10) degree from main chart degree.
    
    Dasamsa is the 10th division chart.
    
    Args:
        degree: Main chart degree
    
    Returns:
        Dasamsa degree
    """
    return varga_degree(degree, 10)


def calculate_navamsa(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str
) -> Dict:
    """
    Calculate Navamsa (D9) chart - 9th divisional chart.
    
    Navamsa is one of the most important divisional charts in Vedic astrology.
    Each sign is divided into 9 equal parts of 3.33 degrees each.
    It's used for:
    - Marriage and spouse analysis
    - Spiritual matters
    - Final results of planets
    
    Args:
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
    
    Returns:
        Navamsa chart data
    """
    # Parse birth time
    hour, minute = map(int, birth_time.split(':'))
    birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    birth_datetime_utc = local_to_utc(birth_datetime, timezone)
    
    # Calculate main chart planets
    main_planets = calculate_planets_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    
    # Calculate Navamsa positions
    # Each sign (30 degrees) is divided into 9 parts = 3.33 degrees each
    navamsa_planets = {}
    
    for planet_name, planet_data in main_planets.items():
        longitude = planet_data["longitude"]
        
        # Find which navamsa division within the sign
        sign_num, degrees_in_sign = degrees_to_sign(longitude)
        navamsa_division = int(degrees_in_sign / (30.0 / 9))
        
        # Calculate navamsa sign
        # Each navamsa division corresponds to a sign starting from the sign itself
        navamsa_sign = (sign_num * 9 + navamsa_division) % 12
        
        # Calculate navamsa longitude
        navamsa_longitude = navamsa_sign * 30 + (degrees_in_sign % (30.0 / 9))
        
        navamsa_planets[planet_name] = {
            "longitude": normalize_degrees(navamsa_longitude),
            "sign": navamsa_sign,
            "sign_name": get_sign_name(navamsa_sign),
            "degrees_in_sign": degrees_in_sign % (30.0 / 9),
            "navamsa_division": navamsa_division + 1
        }
    
    return {
        "chart_type": "D9 (Navamsa)",
        "planets": navamsa_planets,
        "description": "Navamsa chart for marriage and spiritual matters"
    }


def calculate_dasamsa(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str
) -> Dict:
    """
    Calculate Dasamsa (D10) chart - 10th divisional chart.
    
    Dasamsa is used for:
    - Career and profession
    - Status and reputation
    - Karma and work
    
    Each sign is divided into 10 equal parts of 3 degrees each.
    
    Args:
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
    
    Returns:
        Dasamsa chart data
    """
    # Parse birth time
    hour, minute = map(int, birth_time.split(':'))
    birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    birth_datetime_utc = local_to_utc(birth_datetime, timezone)
    
    # Calculate main chart planets
    main_planets = calculate_planets_sidereal(birth_datetime_utc, birth_latitude, birth_longitude)
    
    # Calculate Dasamsa positions
    # Each sign (30 degrees) is divided into 10 parts = 3 degrees each
    dasamsa_planets = {}
    
    for planet_name, planet_data in main_planets.items():
        longitude = planet_data["longitude"]
        
        # Find which dasamsa division within the sign
        sign_num, degrees_in_sign = degrees_to_sign(longitude)
        dasamsa_division = int(degrees_in_sign / 3.0)
        
        # Calculate dasamsa sign
        # Dasamsa signs follow a specific pattern based on the original sign
        # Starting from the sign itself, counting forward
        dasamsa_sign = (sign_num + dasamsa_division) % 12
        
        # Calculate dasamsa longitude
        dasamsa_longitude = dasamsa_sign * 30 + (degrees_in_sign % 3.0)
        
        dasamsa_planets[planet_name] = {
            "longitude": normalize_degrees(dasamsa_longitude),
            "sign": dasamsa_sign,
            "sign_name": get_sign_name(dasamsa_sign),
            "degrees_in_sign": degrees_in_sign % 3.0,
            "dasamsa_division": dasamsa_division + 1
        }
    
    return {
        "chart_type": "D10 (Dasamsa)",
        "planets": dasamsa_planets,
        "description": "Dasamsa chart for career and profession"
    }

