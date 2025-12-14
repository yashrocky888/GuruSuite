"""
Timezone utility functions for handling timezone conversions.

Provides functions to convert between UTC, local time, and Julian Day calculations
required for Swiss Ephemeris.
"""

import pytz
from datetime import datetime
from typing import Optional


def get_timezone(timezone_str: str) -> pytz.BaseTzInfo:
    """
    Get timezone object from timezone string.
    
    Args:
        timezone_str: Timezone string (e.g., 'Asia/Kolkata', 'America/New_York')
    
    Returns:
        pytz timezone object
    
    Raises:
        ValueError: If timezone string is invalid
    """
    try:
        return pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValueError(f"Unknown timezone: {timezone_str}")


def local_to_utc(dt: datetime, timezone_str: str) -> datetime:
    """
    Convert local datetime to UTC.
    
    Args:
        dt: Local datetime object
        timezone_str: Timezone string for the local time
    
    Returns:
        UTC datetime object
    """
    tz = get_timezone(timezone_str)
    if dt.tzinfo is None:
        # If datetime is naive, localize it
        dt = tz.localize(dt)
    else:
        # If datetime has timezone, convert it
        dt = dt.astimezone(tz)
    return dt.astimezone(pytz.UTC)


def utc_to_local(dt: datetime, timezone_str: str) -> datetime:
    """
    Convert UTC datetime to local time.
    
    Args:
        dt: UTC datetime object
        timezone_str: Target timezone string
    
    Returns:
        Local datetime object
    """
    tz = get_timezone(timezone_str)
    if dt.tzinfo is None:
        # Assume UTC if naive
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(tz)


def get_julian_day(dt: datetime) -> float:
    """
    Convert datetime to Julian Day Number (JDN) for Swiss Ephemeris.
    
    Swiss Ephemeris uses Julian Day Number (JDN) for calculations.
    This function converts a datetime object to JDN using Swiss Ephemeris function
    for maximum precision (matching Drik Panchanga methodology).
    
    Args:
        dt: Datetime object (preferably UTC)
    
    Returns:
        Julian Day Number as float
    """
    # Ensure datetime is UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    else:
        dt = dt.astimezone(pytz.UTC)
    
    # Use Swiss Ephemeris julday function for maximum precision
    # This matches Drik Panchanga's calculation method
    import swisseph as swe
    
    # Calculate with full precision including microseconds
    hour_decimal = dt.hour + dt.minute / 60.0 + dt.second / 3600.0 + dt.microsecond / 3600000000.0
    
    jd = swe.julday(
        dt.year, dt.month, dt.day,
        hour_decimal,
        swe.GREG_CAL
    )
    
    return jd

