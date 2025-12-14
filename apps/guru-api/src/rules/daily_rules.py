"""
Daily rating rules engine.

This module calculates daily ratings (Excellent, Good, Mixed, Caution)
based on planetary positions, transits, and dasha periods.
"""

from typing import Dict
from datetime import datetime

from src.jyotish.dasha import calculate_vimshottari_dasha
from src.jyotish.transits import calculate_transits
from src.jyotish.panchang import calculate_panchang
from src.utils.timezone import local_to_utc


def calculate_daily_rating(
    birth_date: datetime,
    birth_time: str,
    birth_latitude: float,
    birth_longitude: float,
    timezone: str,
    query_date: datetime = None
) -> Dict:
    """
    Calculate daily rating for a given date.
    
    Rating is based on:
    - Current dasha and antardasha lords
    - Planetary transits
    - Panchang elements (tithi, nakshatra, yoga)
    - Overall planetary influences
    
    Args:
        birth_date: Birth date
        birth_time: Birth time in HH:MM format
        birth_latitude: Birth latitude
        birth_longitude: Birth longitude
        timezone: Timezone string
        query_date: Date to calculate rating for (defaults to current date)
    
    Returns:
        Dictionary with daily rating and details
    """
    if query_date is None:
        query_date = datetime.now()
    
    # Calculate dasha
    dasha_data = calculate_vimshottari_dasha(
        birth_date, birth_time, birth_latitude, birth_longitude, timezone, query_date
    )
    
    # Calculate transits
    transit_data = calculate_transits(
        birth_date, birth_time, birth_latitude, birth_longitude, timezone, query_date
    )
    
    # Calculate panchang
    panchang_data = calculate_panchang(
        query_date, birth_latitude, birth_longitude, timezone
    )
    
    # Score the day
    score = 0
    factors = []
    
    # Factor 1: Dasha lords (benefic vs malefic)
    maha_dasha_lord = dasha_data["current_dasha"]["lord"]
    antardasha_lord = dasha_data["current_antardasha"]["lord"]
    
    benefics = ["Venus", "Jupiter", "Mercury", "Moon"]
    malefics = ["Mars", "Saturn", "Rahu", "Ketu", "Sun"]
    
    if maha_dasha_lord in benefics:
        score += 2
        factors.append(f"Favorable Mahadasha: {maha_dasha_lord}")
    elif maha_dasha_lord in malefics:
        score -= 1
        factors.append(f"Challenging Mahadasha: {maha_dasha_lord}")
    
    if antardasha_lord in benefics:
        score += 2
        factors.append(f"Favorable Antardasha: {antardasha_lord}")
    elif antardasha_lord in malefics:
        score -= 1
        factors.append(f"Challenging Antardasha: {antardasha_lord}")
    
    # Factor 2: Transits
    favorable_transits = transit_data["summary"]["favorable_transits"]
    challenging_transits = transit_data["summary"]["challenging_transits"]
    
    score += favorable_transits
    score -= challenging_transits
    
    if favorable_transits > challenging_transits:
        factors.append(f"More favorable transits ({favorable_transits} favorable, {challenging_transits} challenging)")
    elif challenging_transits > favorable_transits:
        factors.append(f"More challenging transits ({favorable_transits} favorable, {challenging_transits} challenging)")
    
    # Factor 3: Tithi
    tithi = panchang_data["tithi"]
    favorable_tithis = [2, 3, 5, 7, 10, 11, 13, 15]  # Good tithis
    challenging_tithis = [4, 6, 8, 9, 14]  # Challenging tithis
    
    if tithi["number"] in favorable_tithis:
        score += 1
        factors.append(f"Favorable Tithi: {tithi['name']}")
    elif tithi["number"] in challenging_tithis:
        score -= 1
        factors.append(f"Challenging Tithi: {tithi['name']}")
    
    # Factor 4: Nakshatra
    nakshatra = panchang_data["nakshatra"]
    favorable_nakshatras = [2, 3, 5, 6, 7, 9, 10, 12, 13, 15, 17, 18, 20, 21, 23, 24, 26]
    
    if nakshatra["number"] in favorable_nakshatras:
        score += 1
        factors.append(f"Favorable Nakshatra: {nakshatra['name']}")
    
    # Determine rating
    if score >= 5:
        rating = "Excellent"
        color = "green"
    elif score >= 2:
        rating = "Good"
        color = "blue"
    elif score >= -1:
        rating = "Mixed"
        color = "yellow"
    else:
        rating = "Caution"
        color = "red"
    
    return {
        "date": query_date.isoformat(),
        "rating": rating,
        "score": score,
        "color": color,
        "factors": factors,
        "dasha": {
            "maha_dasha": maha_dasha_lord,
            "antardasha": antardasha_lord
        },
        "transits_summary": transit_data["summary"],
        "panchang": {
            "tithi": tithi["name"],
            "nakshatra": nakshatra["name"],
            "yoga": panchang_data["yoga"]["name"]
        }
    }

