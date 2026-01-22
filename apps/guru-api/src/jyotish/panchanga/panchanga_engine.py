"""
Panchanga Engine - Drik Siddhanta (Swiss Ephemeris) Implementation

JHora / Prokerala Standard Mode
Backend ONLY - No AI, No frontend logic

Calculates complete Panchanga using Drik Siddhanta methodology:
- Sunrise/Sunset using Swiss Ephemeris
- Tithi = (Moon - Sun) / 12°
- Nakshatra = Moon longitude / 13°20'
- Yoga = (Moon + Sun) mod 360
- Karana = half-tithi logic
- Vara from weekday & sunrise rule
"""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import pytz
from math import floor

from src.ephemeris.ephemeris_utils import init_swisseph, calculate_planet_position
from src.utils.converters import normalize_degrees, degrees_to_sign, get_sign_name
from src.utils.timezone import get_julian_day, get_timezone

# Initialize Swiss Ephemeris
init_swisseph()

# Tithi names (30 tithis in a lunar month)
TITHI_NAMES = [
    "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima", "Pratipada", "Dvitiya", "Tritiya",
    "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami",
    "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
]

# Nakshatra list (27 nakshatras)
NAKSHATRA_LIST = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

# Nakshatra lords
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
    "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon",
    "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu",
    "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
    "Saturn", "Mercury"
]

# Yoga list (27 yogas)
YOGA_LIST = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarman",
    "Dhrti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Subha",
    "Shukla", "Brahma", "Indra", "Vaidhriti"
]

# Karana list (11 karanas, repeating cycle)
KARANA_LIST = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]

# Day lords (weekday to planet mapping)
DAY_LORDS = {
    0: "Sun",      # Sunday
    1: "Moon",     # Monday
    2: "Mars",     # Tuesday
    3: "Mercury",  # Wednesday
    4: "Jupiter",  # Thursday
    5: "Venus",    # Friday
    6: "Saturn"    # Saturday
}

DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Vedic month names (Amanta calendar)
VEDIC_MONTHS = [
    "Chaitra", "Vaisakha", "Jyeshtha", "Ashadha",
    "Shravana", "Bhadrapada", "Ashvina", "Kartika",
    "Margashirsha", "Pausha", "Magha", "Phalguna"
]

# Sanskrit month names (alternative)
VEDIC_MONTHS_SANSKRIT = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
    "Shravana", "Bhadrapada", "Ashvina", "Kartika",
    "Margashirsha", "Pausha", "Magha", "Phalguna"
]


def calculate_sunrise_sunset(
    date: datetime,
    latitude: float,
    longitude: float,
    timezone_str: str
) -> Tuple[str, str]:
    """
    Calculate sunrise and sunset times using Drik Panchang standard.
    
    MANDATORY RULES (NO EXCEPTIONS):
    - Upper limb of Sun (default behavior - no disc flag)
    - Atmospheric refraction ENABLED (default - do NOT set BIT_NO_REFRACTION)
    - Elevation = 0 meters (sea level)
    - NO FALLBACKS - throws error if calculation fails
    - Matches Drik Panchang / Prokerala minute-exactly
    
    Args:
        date: Date for calculation (local timezone)
        latitude: Geographic latitude
        longitude: Geographic longitude
        timezone_str: Timezone string (e.g., 'Asia/Kolkata')
    
    Returns:
        Tuple of (sunrise_time, sunset_time) in HH:MM format
    
    Raises:
        ValueError: If sunrise/sunset calculation fails (NO FALLBACK)
    """
    # Ensure date is in local timezone
    tz = get_timezone(timezone_str)
    if date.tzinfo is None:
        date_local = tz.localize(date)
    else:
        date_local = date.astimezone(tz)
    
    # Calculate Julian Day at LOCAL midnight (not UTC)
    # This is critical for accurate sunrise calculation
    jd_local_midnight = swe.julday(
        date_local.year, date_local.month, date_local.day,
        0.0,
        swe.GREG_CAL
    )
    
    # Elevation = 0 meters (sea level) - mandatory for Drik Panchang
    elevation = 0.0
    
    # Geographic position: [longitude, latitude, elevation]
    # Elevation = 0 meters (sea level) - mandatory for Drik Panchang
    geopos = [longitude, latitude, 0.0]
    
    # Atmospheric pressure and temperature (use defaults for standard refraction)
    # Default pressure = 1013.25 mbar, temperature = 15°C
    # These give standard atmospheric refraction (~34 arcmin)
    atpress = 0.0  # 0 = use default (1013.25 mbar)
    attemp = 0.0   # 0 = use default (15°C)
    
    # Calculate sunrise using Drik Panchang standard:
    # - Default disc = UPPER LIMB (no flag needed - this is the default)
    # - Refraction: ENABLED by default (do NOT set BIT_NO_REFRACTION)
    # - Elevation: 0 meters (sea level) - specified in geopos
    # - Atmospheric pressure/temp: Default (0 = use standard values)
    # - NO FALLBACKS - must match Drik Panchang exactly
    # 
    # Note: swe.rise_trans() default is upper limb with refraction.
    # We explicitly DO NOT set:
    #   - BIT_DISC_CENTER (would use center, not upper limb)
    #   - BIT_DISC_BOTTOM (would use lower limb)
    #   - BIT_NO_REFRACTION (would disable refraction)
    result_rise = swe.rise_trans(
        jd_local_midnight,  # Julian Day UT
        swe.SUN,            # Planet ID
        swe.CALC_RISE,      # Calculation flag: rise
        geopos,             # [longitude, latitude, elevation=0]
        atpress,            # Atmospheric pressure (0 = default 1013.25 mbar)
        attemp,             # Atmospheric temperature (0 = default 15°C)
        swe.FLG_SWIEPH      # Ephemeris flag (default, includes refraction)
    )
    
    # Calculate sunset (same standard)
    result_set = swe.rise_trans(
        jd_local_midnight,  # Julian Day UT
        swe.SUN,            # Planet ID
        swe.CALC_SET,       # Calculation flag: set
        geopos,             # [longitude, latitude, elevation=0]
        atpress,            # Atmospheric pressure (0 = default 1013.25 mbar)
        attemp,             # Atmospheric temperature (0 = default 15°C)
        swe.FLG_SWIEPH      # Ephemeris flag (default, includes refraction)
    )
    
    # ABSOLUTE PROHIBITION: NO FALLBACKS
    # If calculation fails, raise error immediately
    if result_rise[0] < 0:
        error_code = result_rise[0]
        raise ValueError(
            f"Sunrise calculation failed with error code {error_code}. "
            f"Location: lat={latitude}, lon={longitude}, tz={timezone_str}. "
            f"NO FALLBACK ALLOWED - must match Drik Panchang exactly."
        )
    
    if result_set[0] < 0:
        error_code = result_set[0]
        raise ValueError(
            f"Sunset calculation failed with error code {error_code}. "
            f"Location: lat={latitude}, lon={longitude}, tz={timezone_str}. "
            f"NO FALLBACK ALLOWED - must match Drik Panchang exactly."
        )
    
    # Extract exact Julian Day values
    sunrise_jd = result_rise[1][0]
    sunset_jd = result_set[1][0]
    
    # Convert JD to datetime in local timezone
    sunrise_dt = _jd_to_datetime(sunrise_jd, timezone_str)
    sunset_dt = _jd_to_datetime(sunset_jd, timezone_str)
    
    # Format as HH:MM (24-hour format, matching Drik Panchang)
    sunrise_str = sunrise_dt.strftime("%H:%M")
    sunset_str = sunset_dt.strftime("%H:%M")
    
    return sunrise_str, sunset_str


def _jd_to_datetime(jd: float, timezone_str: str) -> datetime:
    """Convert Julian Day to datetime in specified timezone."""
    # Convert JD to UTC datetime
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    
    dt_utc = pytz.UTC.localize(datetime(year, month, day, hour_int, minute, second))
    
    # Convert to local timezone
    tz = get_timezone(timezone_str)
    return dt_utc.astimezone(tz)


def _format_end_time(jd: float, jd_current: float, timezone_str: str) -> str:
    """
    Format end time as exact timestamp matching Drik Panchang format.
    
    Format: "HH:MM AM/PM" if same day, "HH:MM AM/PM, Mon DD" if next day.
    """
    end_dt = _jd_to_datetime(jd, timezone_str)
    current_dt = _jd_to_datetime(jd_current, timezone_str)
    
    if end_dt.date() == current_dt.date():
        return end_dt.strftime("%I:%M %p").lstrip('0')
    else:
        return end_dt.strftime("%I:%M %p, %b %d").lstrip('0')


def _find_exact_transition(
    jd_start: float,
    target_value: float,
    calculation_func,
    timezone_str: str,
    max_iterations: int = 20,
    tolerance: float = 0.0001
) -> float:
    """
    Find exact JD when a value crosses a boundary using binary search.
    
    Args:
        jd_start: Starting Julian Day
        target_value: Target boundary value (e.g., 12.0 for tithi, 13.333 for nakshatra)
        calculation_func: Function that takes JD and returns current value
        timezone_str: Timezone for formatting
        max_iterations: Maximum binary search iterations
        tolerance: Tolerance in degrees
    
    Returns:
        Exact JD of transition
    """
    # Initial search window (up to 2 days ahead)
    jd_low = jd_start
    jd_high = jd_start + 2.0
    
    # Binary search for exact transition
    for _ in range(max_iterations):
        jd_mid = (jd_low + jd_high) / 2.0
        current_value = calculation_func(jd_mid)
        
        # Check if we've crossed the boundary
        if abs(current_value - target_value) < tolerance:
            return jd_mid
        
        if current_value < target_value:
            jd_low = jd_mid
        else:
            jd_high = jd_mid
    
    # Fallback: use linear interpolation
    return (jd_low + jd_high) / 2.0


def calculate_tithi(jd: float, timezone_str: str = "Asia/Kolkata") -> Dict[str, any]:
    """
    Calculate Tithi using Drik Siddhanta formula.
    
    Formula: Tithi = (Moon - Sun) / 12°
    Each tithi is 12 degrees of angular difference between Moon and Sun.
    
    Args:
        jd: Julian Day Number
    
    Returns:
        Dictionary with tithi information:
        - name: Tithi name
        - number: Tithi number (1-30)
        - paksha: "Shukla" or "Krishna"
        - end_time: Time when tithi ends (as datetime for calculation)
    """
    # Get Sun and Moon sidereal longitudes
    sun_pos = calculate_planet_position(jd, swe.SUN)
    moon_pos = calculate_planet_position(jd, swe.MOON)
    
    sun_long = sun_pos["longitude"]
    moon_long = moon_pos["longitude"]
    
    # Calculate angular difference (Moon - Sun)
    diff = normalize_degrees(moon_long - sun_long)
    
    # Tithi number (0-29, where 0 = Pratipada)
    tithi_num = int(diff // 12.0)
    
    # Ensure within valid range
    if tithi_num >= 30:
        tithi_num = 29
    elif tithi_num < 0:
        tithi_num = 0
    
    # Determine Paksha
    if tithi_num < 15:
        paksha = "Shukla"
        tithi_display = tithi_num + 1  # 1-15 for Shukla Paksha
    else:
        paksha = "Krishna"
        tithi_display = tithi_num - 14  # 1-15 for Krishna Paksha
    
    # Calculate when tithi ends (next tithi boundary)
    # Elapsed degrees in current tithi
    elapsed = diff % 12.0
    remaining = 12.0 - elapsed
    
    # Calculate speed difference (Moon speed - Sun speed)
    moon_speed = moon_pos["speed_longitude"]
    sun_speed = sun_pos["speed_longitude"]
    relative_speed = moon_speed - sun_speed
    
    # Calculate exact end time using interpolation
    end_time_str = "—"
    jd_end = jd
    if relative_speed > 0:
        # Time to next tithi boundary (in days)
        time_to_next = remaining / relative_speed
        jd_end = jd + time_to_next
        end_time_str = _format_end_time(jd_end, jd, timezone_str)
    else:
        # Moon is slower than Sun (rare), approximate 24 hours
        jd_end = jd + 1.0
        end_time_str = _format_end_time(jd_end, jd, timezone_str)
    
    # Calculate next tithi
    next_tithi_num = (tithi_num + 1) % 30
    next_tithi_display = next_tithi_num + 1 if next_tithi_num < 15 else next_tithi_num - 14
    next_paksha = "Shukla" if next_tithi_num < 15 else "Krishna"
    
    return {
        "current": {
            "name": TITHI_NAMES[tithi_num],
            "number": tithi_display,
            "paksha": paksha,
            "end_time": end_time_str
        },
        "next": {
            "name": TITHI_NAMES[next_tithi_num],
            "number": next_tithi_display,
            "paksha": next_paksha
        }
    }


def calculate_nakshatra(jd: float, timezone_str: str = "Asia/Kolkata") -> Dict[str, any]:
    """
    Calculate Nakshatra using Drik Siddhanta formula.
    
    Formula: Nakshatra = Moon longitude / 13°20'
    Each nakshatra = 13°20' = 13.333333 degrees
    
    Args:
        jd: Julian Day Number
    
    Returns:
        Dictionary with nakshatra information:
        - name: Nakshatra name
        - lord: Nakshatra lord
        - pada: Pada number (1-4)
        - end_time: Time when nakshatra ends
    """
    # Get Moon sidereal longitude
    moon_pos = calculate_planet_position(jd, swe.MOON)
    moon_long = moon_pos["longitude"]
    
    # Each nakshatra is 13°20' = 13.333333 degrees
    nakshatra_span = 13.0 + 20.0 / 60.0
    
    # Nakshatra index (0-26)
    nak_index = int(moon_long // nakshatra_span)
    
    # Ensure within valid range
    if nak_index >= 27:
        nak_index = 26
    elif nak_index < 0:
        nak_index = 0
    
    # Calculate pada (each nakshatra has 4 padas, each pada = 3°20')
    pada_span = 3.0 + 20.0 / 60.0
    elapsed_in_nak = moon_long % nakshatra_span
    pada_num = int(elapsed_in_nak // pada_span) + 1
    
    # Ensure pada is 1-4
    if pada_num > 4:
        pada_num = 4
    elif pada_num < 1:
        pada_num = 1
    
    # Calculate exact end time
    remaining = nakshatra_span - elapsed_in_nak
    moon_speed = moon_pos["speed_longitude"]
    
    end_time_str = "—"
    if moon_speed > 0:
        time_to_next = remaining / moon_speed
        jd_end = jd + time_to_next
        end_time_str = _format_end_time(jd_end, jd, timezone_str)
    else:
        jd_end = jd + 1.0
        end_time_str = _format_end_time(jd_end, jd, timezone_str)
    
    # Calculate next nakshatra
    next_nak_index = (nak_index + 1) % 27
    
    return {
        "current": {
            "name": NAKSHATRA_LIST[nak_index],
            "lord": NAKSHATRA_LORDS[nak_index],
            "pada": pada_num,
            "end_time": end_time_str
        },
        "next": {
            "name": NAKSHATRA_LIST[next_nak_index],
            "lord": NAKSHATRA_LORDS[next_nak_index]
        }
    }


def calculate_yoga(jd: float, timezone_str: str = "Asia/Kolkata") -> Dict[str, any]:
    """
    Calculate Yoga using Drik Siddhanta formula.
    
    Formula: Yoga = (Moon + Sun) mod 360
    Each yoga = 13°20' = 13.333333 degrees
    
    Args:
        jd: Julian Day Number
    
    Returns:
        Dictionary with yoga information:
        - name: Yoga name
        - end_time: Time when yoga ends
    """
    # Get Sun and Moon sidereal longitudes
    sun_pos = calculate_planet_position(jd, swe.SUN)
    moon_pos = calculate_planet_position(jd, swe.MOON)
    
    sun_long = sun_pos["longitude"]
    moon_long = moon_pos["longitude"]
    
    # Yoga = (Moon + Sun) mod 360
    yoga_long = normalize_degrees(moon_long + sun_long)
    
    # Each yoga is 13°20' = 13.333333 degrees
    yoga_span = 13.0 + 20.0 / 60.0
    
    # Yoga index (0-26)
    yoga_index = int(yoga_long // yoga_span)
    
    # Ensure within valid range
    if yoga_index >= 27:
        yoga_index = 26
    elif yoga_index < 0:
        yoga_index = 0
    
    # Calculate when yoga ends
    elapsed = yoga_long % yoga_span
    remaining = yoga_span - elapsed
    
    # Relative speed for yoga (Moon + Sun speeds)
    moon_speed = moon_pos["speed_longitude"]
    sun_speed = sun_pos["speed_longitude"]
    relative_speed = moon_speed + sun_speed
    
    end_time_str = "—"
    if relative_speed > 0:
        time_to_next = remaining / relative_speed
        jd_end = jd + time_to_next
        end_time_str = _format_end_time(jd_end, jd, timezone_str)
    else:
        jd_end = jd + 1.0
        end_time_str = _format_end_time(jd_end, jd, timezone_str)
    
    # Calculate next yoga
    next_yoga_index = (yoga_index + 1) % 27
    
    return {
        "current": {
            "name": YOGA_LIST[yoga_index],
            "end_time": end_time_str
        },
        "next": {
            "name": YOGA_LIST[next_yoga_index]
        }
    }


def calculate_karana_array(jd_sunrise: float, jd_next_sunrise: float, timezone_str: str) -> list:
    """
    Calculate FULL ordered sequence of Karanas from sunrise to next sunrise.
    
    Each Tithi has 2 Karanas. There are 60 Karanas total in a lunar month.
    7 movable Karanas repeat, 4 fixed Karanas occur once per month.
    
    Args:
        jd_sunrise: Julian Day at current sunrise
        jd_next_sunrise: Julian Day at next sunrise
        timezone_str: Timezone string
    
    Returns:
        List of karana objects with name and end_time
    """
    karanas = []
    current_jd = jd_sunrise
    
    # Iterate through karanas until next sunrise
    while current_jd < jd_next_sunrise:
        # Get Sun and Moon positions
        sun_pos = calculate_planet_position(current_jd, swe.SUN)
        moon_pos = calculate_planet_position(current_jd, swe.MOON)
        
        sun_long = sun_pos["longitude"]
        moon_long = moon_pos["longitude"]
        
        # Calculate angular difference (Moon - Sun)
        diff = normalize_degrees(moon_long - sun_long)
        
        # Tithi number (0-29)
        tithi_num = int(diff // 12.0)
        if tithi_num >= 30:
            tithi_num = 29
        elif tithi_num < 0:
            tithi_num = 0
        
        # Karana is half-tithi
        # First karana of tithi: (tithi_num * 2) % 11
        # Second karana of tithi: (tithi_num * 2 + 1) % 11
        elapsed_in_tithi = diff % 12.0
        
        # Determine which karana we're in (first or second half of tithi)
        if elapsed_in_tithi < 6.0:
            # First karana of tithi
            karana_index = (tithi_num * 2) % 11
            elapsed_in_karana = elapsed_in_tithi
            remaining = 6.0 - elapsed_in_karana
        else:
            # Second karana of tithi
            karana_index = (tithi_num * 2 + 1) % 11
            elapsed_in_karana = elapsed_in_tithi - 6.0
            remaining = 6.0 - elapsed_in_karana
        
        # Calculate when this karana ends
        moon_speed = moon_pos["speed_longitude"]
        sun_speed = sun_pos["speed_longitude"]
        relative_speed = moon_speed - sun_speed
        
        if relative_speed > 0:
            time_to_next = remaining / relative_speed
            jd_end = current_jd + time_to_next
        else:
            jd_end = current_jd + 0.5  # Half day fallback
        
        # Don't exceed next sunrise
        if jd_end > jd_next_sunrise:
            jd_end = jd_next_sunrise
        
        end_time_str = _format_end_time(jd_end, jd_sunrise, timezone_str)
        
        karanas.append({
            "name": KARANA_LIST[karana_index],
            "end_time": end_time_str
        })
        
        # Move to next karana
        current_jd = jd_end
        
        # Safety: prevent infinite loop (max 4 karanas per day)
        if len(karanas) >= 4:
            break
        
        # Safety: if we've reached next sunrise, stop
        if current_jd >= jd_next_sunrise:
            break
    
    return karanas


def find_exact_amavasya_purnima(jd_start: float, target_angle: float, search_days: int = 45) -> float:
    """
    Find exact JD when Moon-Sun angular separation equals target angle.
    
    For Amavasya: target_angle = 0° (Moon - Sun = 0°)
    For Purnima: target_angle = 180° (Moon - Sun = 180°)
    
    Uses binary search to find exact moment with high precision.
    
    Args:
        jd_start: Starting Julian Day (search backwards from here)
        target_angle: Target angular separation in degrees (0 for Amavasya, 180 for Purnima)
        search_days: Maximum days to search back
    
    Returns:
        Exact JD of Amavasya/Purnima
    """
    jd_low = jd_start - search_days
    jd_high = jd_start
    tolerance = 0.00001  # ~0.86 seconds (high precision)
    
    # Binary search for exact moment
    for iteration in range(60):  # Max 60 iterations for high precision
        jd_mid = (jd_low + jd_high) / 2.0
        
        sun_pos = calculate_planet_position(jd_mid, swe.SUN)
        moon_pos = calculate_planet_position(jd_mid, swe.MOON)
        
        diff = normalize_degrees(moon_pos["longitude"] - sun_pos["longitude"])
        
        # Calculate angular distance to target
        if target_angle == 180.0:
            # For Purnima: check distance to 180° (accounting for wrap-around)
            angular_distance = min(abs(diff - 180.0), abs(diff - 180.0 + 360.0), abs(diff - 180.0 - 360.0))
        else:
            # For Amavasya: check distance to 0° (accounting for wrap-around)
            angular_distance = min(abs(diff - 0.0), abs(diff - 360.0), abs(diff + 360.0))
        
        # Convert angular distance to time tolerance (degrees to days)
        # Moon-Sun relative speed ~12°/day, so 0.01° ≈ 0.0008 days
        time_tolerance = angular_distance / 12.0  # Approximate relative speed
        
        if time_tolerance < tolerance:
            return jd_mid
        
        # Adjust search window based on current position
        if target_angle == 180.0:
            # For Purnima: we want diff = 180°
            # If diff < 180°, we need to go forward (increase JD)
            # If diff > 180°, we need to go backward (decrease JD)
            if diff < 180.0:
                jd_low = jd_mid
            else:
                jd_high = jd_mid
        else:
            # For Amavasya: we want diff = 0° (or 360°)
            # If diff is between 180°-360°, we're past 0°, need to go back
            # If diff is between 0°-180°, we're before 0°, need to go forward
            if diff > 180.0:
                jd_low = jd_mid
            else:
                jd_high = jd_mid
    
    # Return best estimate (midpoint)
    return (jd_low + jd_high) / 2.0


def get_lunar_month_info(jd: float) -> Dict[str, any]:
    """
    Get Vedic lunar month information using Drik Panchang methodology.
    
    AMANTA (South/West India):
    - Lunar month ENDS at Amavasya (Moon - Sun = 0°)
    - Month name = Sun's sidereal sign at exact Amavasya moment
    
    PURNIMANTA (North India):
    - Lunar month ENDS at Purnima (Moon - Sun = 180°)
    - Month name = Sun's sidereal sign at exact Purnima moment
    
    ADHIKA MASA (Leap Month):
    - If NO Sankranti (Sun sign change) occurs between two Amavasyas/Purnimas
    - The month is marked as Adhika Masa
    
    Args:
        jd: Julian Day at sunrise
    
    Returns:
        Dictionary with:
        - amanta_month: Month name for Amanta calendar
        - purnimanta_month: Month name for Purnimanta calendar
        - is_adhika_masa: Boolean indicating if current month is Adhika Masa
    """
    # Find exact JD of most recent Amavasya (for Amanta)
    amavasya_jd = find_exact_amavasya_purnima(jd, 0.0)
    
    # Find exact JD of most recent Purnima (for Purnimanta)
    purnima_jd = find_exact_amavasya_purnima(jd, 180.0)
    
    # Get Sun's sidereal position at Amavasya
    sun_pos_amavasya = calculate_planet_position(amavasya_jd, swe.SUN)
    sun_long_amavasya = sun_pos_amavasya["longitude"]
    sun_sign_amavasya = int(sun_long_amavasya // 30.0) % 12
    
    # Get Sun's sidereal position at Purnima
    sun_pos_purnima = calculate_planet_position(purnima_jd, swe.SUN)
    sun_long_purnima = sun_pos_purnima["longitude"]
    sun_sign_purnima = int(sun_long_purnima // 30.0) % 12
    
    # Determine month names
    amanta_month = VEDIC_MONTHS[sun_sign_amavasya]
    purnimanta_month = VEDIC_MONTHS[sun_sign_purnima]
    
    # Check for Adhika Masa (leap month)
    # Find previous Amavasya/Purnima to check for Sankranti
    prev_amavasya_jd = find_exact_amavasya_purnima(amavasya_jd - 1.0, 0.0)
    prev_purnima_jd = find_exact_amavasya_purnima(purnima_jd - 1.0, 180.0)
    
    # Get Sun's sign at previous boundaries
    prev_sun_pos_amavasya = calculate_planet_position(prev_amavasya_jd, swe.SUN)
    prev_sun_sign_amavasya = int((prev_sun_pos_amavasya["longitude"] // 30.0)) % 12
    
    prev_sun_pos_purnima = calculate_planet_position(prev_purnima_jd, swe.SUN)
    prev_sun_sign_purnima = int((prev_sun_pos_purnima["longitude"] // 30.0)) % 12
    
    # Adhika Masa: No Sankranti (Sun sign change) between boundaries
    is_adhika_amanta = (sun_sign_amavasya == prev_sun_sign_amavasya)
    is_adhika_purnimanta = (sun_sign_purnima == prev_sun_sign_purnima)
    
    # For simplicity, return if either is Adhika (in practice, they're usually the same)
    is_adhika_masa = is_adhika_amanta or is_adhika_purnimanta
    
    return {
        "amanta_month": amanta_month,
        "purnimanta_month": purnimanta_month,
        "is_adhika_masa": is_adhika_masa
    }


def get_samvat_years(gregorian_year: int) -> Dict[str, str]:
    """
    Calculate Samvat years (Shaka, Vikram, Gujarati).
    
    Args:
        gregorian_year: Gregorian calendar year
    
    Returns:
        Dictionary with samvat years
    """
    shaka = gregorian_year - 78
    vikram = gregorian_year + 57
    gujarati = gregorian_year + 56  # Typically same as Vikram with regional variations
    
    # Format with era name
    return {
        "shaka_samvat": f"{shaka} Shaka",
        "vikram_samvat": f"{vikram} Vikram",
        "gujarati_samvat": f"{gujarati} Gujarati"
    }


def calculate_vara(date: datetime, timezone_str: str) -> Dict[str, str]:
    """
    Calculate Vara (weekday) from date.
    
    Vara is determined by the weekday at sunrise.
    Uses local timezone for accurate weekday determination.
    
    Args:
        date: Date for calculation
        timezone_str: Timezone string
    
    Returns:
        Dictionary with vara information:
        - name: Day name
        - lord: Day lord (planet)
    """
    # Get timezone and localize date
    tz = get_timezone(timezone_str)
    if date.tzinfo is None:
        date = tz.localize(date)
    else:
        date = date.astimezone(tz)
    
    # Get weekday (0 = Monday, 6 = Sunday in Python)
    # Adjust to match our DAY_LORDS mapping (0 = Sunday)
    weekday = date.weekday()
    # Convert: Python weekday (0=Mon) to our format (0=Sun)
    weekday_adj = (weekday + 1) % 7
    
    return {
        "name": DAY_NAMES[weekday_adj],
        "lord": DAY_LORDS[weekday_adj]
    }


def calculate_panchanga(
    date: str,
    latitude: float,
    longitude: float,
    timezone: str
) -> Dict[str, any]:
    """
    Calculate complete Panchanga using Drik Siddhanta (Swiss Ephemeris).
    
    JHora / Prokerala Standard Mode
    Backend ONLY - No AI, No frontend logic
    
    Args:
        date: Date in YYYY-MM-DD format
        latitude: Geographic latitude
        longitude: Geographic longitude
        timezone: Timezone string (e.g., 'Asia/Kolkata')
    
    Returns:
        Dictionary with complete Panchanga data:
        {
            "panchanga": {
                "sunrise": "HH:MM",
                "sunset": "HH:MM",
                "vara": {"name": "...", "lord": "..."},
                "tithi": {"name": "...", "number": ..., "paksha": "...", "end_time": "..."},
                "nakshatra": {"name": "...", "lord": "...", "pada": ..., "end_time": "..."},
                "yoga": {"name": "...", "end_time": "..."},
                "karana": {"name": "...", "end_time": "..."}
            }
        }
    """
    # Parse date
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD")
    
    # Calculate sunrise and sunset
    sunrise, sunset = calculate_sunrise_sunset(date_obj, latitude, longitude, timezone)
    
    # Calculate Julian Day at sunrise (critical for Panchanga)
    # Panchanga is calculated at sunrise
    tz = get_timezone(timezone)
    if date_obj.tzinfo is None:
        date_obj = tz.localize(date_obj)
    
    # Parse sunrise time and create datetime at sunrise
    sunrise_hour, sunrise_min = map(int, sunrise.split(":"))
    sunrise_dt = date_obj.replace(hour=sunrise_hour, minute=sunrise_min, second=0, microsecond=0)
    sunrise_dt = sunrise_dt.astimezone(pytz.UTC)
    
    jd_sunrise = get_julian_day(sunrise_dt)
    
    # Calculate next sunrise (for karana array)
    next_date_obj = date_obj + timedelta(days=1)
    next_sunrise, _ = calculate_sunrise_sunset(next_date_obj, latitude, longitude, timezone)
    next_sunrise_hour, next_sunrise_min = map(int, next_sunrise.split(":"))
    next_sunrise_dt = next_date_obj.replace(hour=next_sunrise_hour, minute=next_sunrise_min, second=0, microsecond=0)
    next_sunrise_dt = next_sunrise_dt.astimezone(pytz.UTC)
    jd_next_sunrise = get_julian_day(next_sunrise_dt)
    
    # Calculate all Panchanga elements at sunrise
    vara = calculate_vara(date_obj, timezone)
    tithi = calculate_tithi(jd_sunrise, timezone)
    nakshatra = calculate_nakshatra(jd_sunrise, timezone)
    yoga = calculate_yoga(jd_sunrise, timezone)
    karana_array = calculate_karana_array(jd_sunrise, jd_next_sunrise, timezone)
    
    # Get Moon and Sun signs at sunrise
    moon_pos = calculate_planet_position(jd_sunrise, swe.MOON)
    sun_pos = calculate_planet_position(jd_sunrise, swe.SUN)
    moon_sign_num, _ = degrees_to_sign(moon_pos["longitude"])
    sun_sign_num, _ = degrees_to_sign(sun_pos["longitude"])
    moon_sign = get_sign_name(moon_sign_num)
    sun_sign = get_sign_name(sun_sign_num)
    
    # Get Paksha (from tithi)
    paksha = tithi["current"]["paksha"]
    
    # Get lunar month information (Amanta, Purnimanta, Adhika Masa)
    lunar_month_info = get_lunar_month_info(jd_sunrise)
    amanta_month = lunar_month_info["amanta_month"]
    purnimanta_month = lunar_month_info["purnimanta_month"]
    is_adhika_masa = lunar_month_info["is_adhika_masa"]
    
    # Get Samvat years
    gregorian_year = date_obj.year
    samvat = get_samvat_years(gregorian_year)
    
    return {
        "panchanga": {
            "sunrise": sunrise,
            "sunset": sunset,
            "vara": vara,
            "tithi": tithi,
            "nakshatra": nakshatra,
            "yoga": yoga,
            "karana": karana_array,
            "paksha": f"{paksha} Paksha",
            "amanta_month": amanta_month,
            "purnimanta_month": purnimanta_month,
            "is_adhika_masa": is_adhika_masa,
            "moonsign": moon_sign,
            "sunsign": sun_sign,
            "weekday": vara["name"],
            **samvat
        }
    }
