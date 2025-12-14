"""
Phase 19: Transit Context Builder

Builds complete transit snapshot for a given date and location.
"""

from typing import Dict
from datetime import datetime
import swisseph as swe

from src.jyotish.kundli_engine import generate_kundli, get_planet_positions
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.jyotish.panchang import calculate_panchang, get_nakshatra
from src.utils.converters import degrees_to_sign


def build_transit_context(birth_details: Dict, on_datetime: datetime, location: Dict) -> Dict:
    """
    Phase 19: Build complete transit context for a given date.
    
    Args:
        birth_details: Dictionary with birth_date, birth_time, birth_latitude, birth_longitude
        on_datetime: Date/time for transit calculation
        location: Dictionary with latitude, longitude, timezone
    
    Returns:
        Complete transit context dictionary
    """
    # Extract birth details
    birth_date = birth_details.get("birth_date")
    birth_time = birth_details.get("birth_time")
    birth_lat = birth_details.get("birth_latitude")
    birth_lon = birth_details.get("birth_longitude")
    timezone = birth_details.get("timezone", "UTC")
    
    # Parse birth datetime
    if isinstance(birth_date, str):
        from datetime import datetime as dt
        birth_date_obj = dt.strptime(birth_date, "%Y-%m-%d").date()
    else:
        birth_date_obj = birth_date if hasattr(birth_date, 'year') else dt.strptime(str(birth_date), "%Y-%m-%d").date()
    
    hour, minute = map(int, birth_time.split(':'))
    birth_dt_local = dt.combine(birth_date_obj, dt.min.time().replace(hour=hour, minute=minute, second=0, microsecond=0))
    
    # Convert local time to UTC (Swiss Ephemeris requires UTC)
    from src.utils.timezone import local_to_utc
    birth_dt_utc = local_to_utc(birth_dt_local, timezone)
    
    # Calculate birth Julian Day from UTC
    birth_jd = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0,
        swe.GREG_CAL
    )
    
    # Generate natal chart
    natal_chart = generate_kundli(birth_jd, birth_lat, birth_lon)
    
    # Calculate current transits
    transit_lat = location.get("latitude", birth_lat)
    transit_lon = location.get("longitude", birth_lon)
    timezone = location.get("timezone", "UTC")
    
    transit_jd = swe.julday(
        on_datetime.year, on_datetime.month, on_datetime.day,
        on_datetime.hour + on_datetime.minute / 60.0,
        swe.GREG_CAL
    )
    
    current_planets = get_planet_positions(transit_jd)
    
    # Build current transits dictionary
    current_transits = {}
    natal_asc = natal_chart.get("Ascendant", {}).get("degree", 0)
    natal_moon = natal_chart.get("Planets", {}).get("Moon", {}).get("degree", 0)
    
    # Calculate current Ascendant
    from src.ephemeris.houses import calculate_houses_sidereal
    current_asc = calculate_houses_sidereal(transit_jd, transit_lat, transit_lon)[0]
    
    for planet_name, planet_degree in current_planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        
        # Calculate sign and house from natal Ascendant
        sign, sign_num = degrees_to_sign(planet_degree)
        
        # Calculate house from natal Ascendant
        rel_degree = (planet_degree - natal_asc) % 360
        house_from_lagna = int(rel_degree / 30) + 1
        if house_from_lagna > 12:
            house_from_lagna = 1
        
        # Calculate house from natal Moon
        rel_degree_moon = (planet_degree - natal_moon) % 360
        house_from_moon = int(rel_degree_moon / 30) + 1
        if house_from_moon > 12:
            house_from_moon = 1
        
        # Get nakshatra
        nakshatra_name, nakshatra_num = get_nakshatra(planet_degree)
        
        # Calculate pada
        nakshatra_degree = (planet_degree % 360) % (360 / 27)
        pada = int(nakshatra_degree / (360 / 27 / 4)) + 1
        
        current_transits[planet_name] = {
            "sign": sign,
            "sign_number": sign_num,
            "degree": planet_degree,
            "house_from_lagna": house_from_lagna,
            "house_from_moon": house_from_moon,
            "nakshatra": nakshatra_name,
            "nakshatra_number": nakshatra_num,
            "nakshatra_pada": pada
        }
    
    # Calculate aspects
    current_aspects = calculate_transit_aspects(current_transits, natal_chart)
    
    # Get current Dasha
    moon_degree = natal_chart["Planets"]["Moon"]["degree"]
    dasha_data = calculate_vimshottari_dasha(birth_dt_utc, moon_degree)
    
    # Find current Dasha period
    current_dasha = get_current_dasha_period(dasha_data, on_datetime)
    
    # Moon specials
    moon_specials = get_moon_specials(on_datetime, transit_lat, transit_lon, timezone, natal_moon)
    
    # Saturn specials
    saturn_specials = get_saturn_specials(current_transits.get("Saturn", {}), natal_chart)
    
    # Jupiter specials
    jupiter_specials = get_jupiter_specials(current_transits.get("Jupiter", {}), natal_chart)
    
    return {
        "natal_chart": natal_chart,
        "current_transits": current_transits,
        "current_aspects": current_aspects,
        "current_dasha": current_dasha,
        "moon_specials": moon_specials,
        "saturn_specials": saturn_specials,
        "jupiter_specials": jupiter_specials,
        "transit_date": on_datetime.isoformat(),
        "transit_location": location
    }


def calculate_transit_aspects(current_transits: Dict, natal_chart: Dict) -> Dict:
    """
    Phase 19: Calculate aspects from transit planets to natal chart.
    
    Args:
        current_transits: Current transit positions
        natal_chart: Natal chart
    
    Returns:
        Aspects dictionary
    """
    aspects = {}
    natal_planets = natal_chart.get("Planets", {})
    natal_houses = natal_chart.get("Houses", [])
    
    for planet_name, transit_data in current_transits.items():
        transit_degree = transit_data.get("degree", 0)
        aspects[planet_name] = {
            "aspects_to_planets": [],
            "aspects_to_houses": []
        }
        
        # Check aspects to natal planets
        for natal_planet_name, natal_planet_data in natal_planets.items():
            natal_degree = natal_planet_data.get("degree", 0)
            distance = abs(transit_degree - natal_degree)
            if distance > 180:
                distance = 360 - distance
            
            # Vedic aspects: 7th (180°), 4th (120°), 8th (240°), 3rd (60°), 10th (300°)
            # Special aspects: Jupiter (5th, 9th), Saturn (3rd, 10th), Mars (4th, 8th)
            
            aspect_type = None
            if abs(distance - 180) < 5:  # 7th aspect
                aspect_type = "7th"
            elif abs(distance - 120) < 5 or abs(distance - 240) < 5:  # 4th/8th
                aspect_type = "4th/8th"
            elif planet_name == "Jupiter" and (abs(distance - 60) < 5 or abs(distance - 300) < 5):  # 5th/9th
                aspect_type = "5th/9th (Jupiter special)"
            elif planet_name == "Saturn" and (abs(distance - 60) < 5 or abs(distance - 300) < 5):  # 3rd/10th
                aspect_type = "3rd/10th (Saturn special)"
            elif planet_name == "Mars" and (abs(distance - 120) < 5 or abs(distance - 240) < 5):  # 4th/8th
                aspect_type = "4th/8th (Mars special)"
            
            if aspect_type:
                aspects[planet_name]["aspects_to_planets"].append({
                    "natal_planet": natal_planet_name,
                    "aspect_type": aspect_type,
                    "distance": distance
                })
        
        # Check aspects to houses (simplified - using house cusps)
        for house_data in natal_houses:
            house_num = house_data.get("house", 0)
            house_cusp = house_data.get("degree", 0)
            
            distance = abs(transit_degree - house_cusp)
            if distance > 180:
                distance = 360 - distance
            
            if abs(distance - 180) < 5:  # 7th aspect to house
                aspects[planet_name]["aspects_to_houses"].append({
                    "house": house_num,
                    "aspect_type": "7th",
                    "distance": distance
                })
    
    return aspects


def get_current_dasha_period(dasha_data: Dict, on_datetime: datetime) -> Dict:
    """
    Phase 19: Get current Dasha period for given date.
    
    Args:
        dasha_data: Complete Dasha data
        on_datetime: Date to check
    
    Returns:
        Current Dasha period info
    """
    mahadashas = dasha_data.get("mahadasha", [])
    
    for dasha in mahadashas:
        start_str = dasha.get("start", "")
        end_str = dasha.get("end", "")
        
        if start_str and end_str:
            try:
                start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00").split(".")[0])
                end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00").split(".")[0])
                
                if start_dt <= on_datetime <= end_dt:
                    # Find antardasha
                    antardashas = dasha.get("antardasha", [])
                    for antardasha in antardashas:
                        ant_start = datetime.fromisoformat(antardasha.get("start", "").replace("Z", "+00:00").split(".")[0])
                        ant_end = datetime.fromisoformat(antardasha.get("end", "").replace("Z", "+00:00").split(".")[0])
                        
                        if ant_start <= on_datetime <= ant_end:
                            return {
                                "mahadasha": dasha.get("dasha_lord", "Unknown"),
                                "antardasha": antardasha.get("antardasha_lord", "Unknown"),
                                "pratyantar": antardasha.get("pratyantar_lord", "Unknown"),
                                "start_date": start_str,
                                "end_date": end_str
                            }
            except:
                continue
    
    # Fallback
    return {
        "mahadasha": "Unknown",
        "antardasha": "Unknown",
        "pratyantar": "Unknown"
    }


def get_moon_specials(on_datetime: datetime, lat: float, lon: float, timezone: str, natal_moon_deg: float) -> Dict:
    """
    Phase 19: Get Moon special conditions.
    
    Args:
        on_datetime: Current date/time
        lat: Latitude
        lon: Longitude
        timezone: Timezone
        natal_moon_deg: Natal Moon degree
    
    Returns:
        Moon specials dictionary
    """
    # Get Panchang - ensure datetime has timezone info
    if on_datetime.tzinfo is None:
        from src.utils.timezone import get_timezone
        tz = get_timezone(timezone)
        on_datetime = tz.localize(on_datetime)
    panchang = calculate_panchang(on_datetime, lat, lon, timezone)
    
    # Get current Moon position
    import swisseph as swe
    transit_jd = swe.julday(
        on_datetime.year, on_datetime.month, on_datetime.day,
        on_datetime.hour + on_datetime.minute / 60.0,
        swe.GREG_CAL
    )
    current_planets = get_planet_positions(transit_jd)
    current_moon_deg = current_planets.get("Moon", 0)
    
    # Calculate relationship to natal Moon
    distance = abs(current_moon_deg - natal_moon_deg)
    if distance > 180:
        distance = 360 - distance
    
    # Convert to house difference
    sign_diff = abs(int(current_moon_deg / 30) - int(natal_moon_deg / 30))
    if sign_diff > 6:
        sign_diff = 12 - sign_diff
    
    moon_relationship = f"{sign_diff}th from natal Moon"
    
    return {
        "tithi": panchang.get("tithi", {}).get("name", "Unknown"),
        "nakshatra": panchang.get("nakshatra", {}).get("name", "Unknown"),
        "yoga": panchang.get("yoga", {}).get("name", "Unknown"),
        "karana": panchang.get("karana", {}).get("name", "Unknown"),
        "relationship_to_natal_moon": moon_relationship,
        "house_from_natal_moon": sign_diff
    }


def get_saturn_specials(saturn_transit: Dict, natal_chart: Dict) -> Dict:
    """
    Phase 19: Get Saturn special conditions (Sade Sati, Ashtama Shani, etc.).
    
    Args:
        saturn_transit: Saturn transit data
        natal_chart: Natal chart
    
    Returns:
        Saturn specials dictionary
    """
    if not saturn_transit:
        return {"sade_sati": False, "ashtama_shani": False}
    
    natal_moon = natal_chart.get("Planets", {}).get("Moon", {})
    natal_moon_house = natal_moon.get("house", 0)
    
    saturn_house_from_moon = saturn_transit.get("house_from_moon", 0)
    
    # Sade Sati: Saturn in 12th, 1st, or 2nd from Moon
    sade_sati = saturn_house_from_moon in [12, 1, 2]
    
    # Ashtama Shani: Saturn in 8th from Moon
    ashtama_shani = saturn_house_from_moon == 8
    
    # Dhaiyya (Kantaka): Saturn in 4th from Moon
    dhaiyya = saturn_house_from_moon == 4
    
    return {
        "sade_sati": sade_sati,
        "ashtama_shani": ashtama_shani,
        "dhaiyya": dhaiyya,
        "house_from_moon": saturn_house_from_moon,
        "status": "sade_sati" if sade_sati else "ashtama_shani" if ashtama_shani else "dhaiyya" if dhaiyya else "normal"
    }


def get_jupiter_specials(jupiter_transit: Dict, natal_chart: Dict) -> Dict:
    """
    Phase 19: Get Jupiter special conditions.
    
    Args:
        jupiter_transit: Jupiter transit data
        natal_chart: Natal chart
    
    Returns:
        Jupiter specials dictionary
    """
    if not jupiter_transit:
        return {}
    
    natal_moon = natal_chart.get("Planets", {}).get("Moon", {})
    natal_moon_house = natal_moon.get("house", 0)
    
    jupiter_house_from_moon = jupiter_transit.get("house_from_moon", 0)
    jupiter_house_from_lagna = jupiter_transit.get("house_from_lagna", 0)
    
    # Benefic houses: 1, 5, 9 (Trikonas), 4, 7, 10 (Kendras)
    trikonas = [1, 5, 9]
    kendras = [4, 7, 10]
    
    is_trikona = jupiter_house_from_moon in trikonas or jupiter_house_from_lagna in trikonas
    is_kendra = jupiter_house_from_moon in kendras or jupiter_house_from_lagna in kendras
    
    return {
        "house_from_moon": jupiter_house_from_moon,
        "house_from_lagna": jupiter_house_from_lagna,
        "is_trikona": is_trikona,
        "is_kendra": is_kendra,
        "is_benefic": is_trikona or is_kendra,
        "status": "highly_auspicious" if (is_trikona and is_kendra) else "auspicious" if (is_trikona or is_kendra) else "moderate"
    }

