"""
Phase 20: Muhurtha Rules Engine

Implements classical rules for different tasks and activities.
"""

from typing import Dict, List
from datetime import datetime


def evaluate_travel_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for travel.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check Tithi
    tithi = panchanga.get("tithi", {})
    tithi_num = tithi.get("number", 0)
    
    if tithi_num in [4, 9, 14]:  # Rikta Tithi
        score -= 3
        warnings.append("Rikta Tithi - avoid travel if possible")
    elif tithi_num in [1, 6, 11]:  # Good Tithis
        score += 2
        reasons.append("Favorable Tithi for travel")
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    
    good_nakshatras = ["Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    bad_nakshatras = ["Ashlesha", "Magha", "Mula", "Jyeshtha"]
    
    if nakshatra_name in good_nakshatras:
        score += 2
        reasons.append(f"{nakshatra_name} Nakshatra is favorable for travel")
    elif nakshatra_name in bad_nakshatras:
        score -= 2
        warnings.append(f"{nakshatra_name} Nakshatra is not ideal for travel")
    
    # Check Choghadiya
    current_chog = get_current_choghadiya(choghadiya, datetime.now())
    if current_chog:
        if current_chog.get("type") == "excellent":
            score += 3
            reasons.append(f"Amrit Choghadiya - highly auspicious")
        elif current_chog.get("type") == "good":
            score += 2
            reasons.append(f"{current_chog.get('name')} Choghadiya - favorable")
        elif current_chog.get("type") == "bad":
            score -= 2
            warnings.append(f"{current_chog.get('name')} Choghadiya - avoid travel")
    
    # Check Rahu Kalam
    rahu_kalam = panchanga.get("rahu_kalam", {})
    if is_in_time_window(datetime.now(), rahu_kalam):
        score -= 2
        warnings.append("Rahu Kalam - avoid travel")
    
    recommendation = "Favorable for travel" if score >= 3 else "Moderate - proceed with caution" if score >= 0 else "Not recommended - postpone if possible"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def evaluate_job_application_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for job application.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check weekday
    weekday = datetime.now().weekday()
    good_days = [0, 2, 3]  # Monday, Wednesday, Thursday
    if weekday in good_days:
        score += 1
        reasons.append("Favorable weekday for career matters")
    
    # Check Tithi
    tithi = panchanga.get("tithi", {})
    tithi_num = tithi.get("number", 0)
    if tithi_num in [1, 6, 11]:  # Good Tithis
        score += 2
        reasons.append("Favorable Tithi for new beginnings")
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    career_nakshatras = ["Pushya", "Hasta", "Swati", "Anuradha", "Shravana"]
    if nakshatra_name in career_nakshatras:
        score += 3
        reasons.append(f"{nakshatra_name} Nakshatra is excellent for career activities")
    
    # Check Choghadiya
    current_chog = get_current_choghadiya(choghadiya, datetime.now())
    if current_chog:
        if current_chog.get("type") in ["excellent", "good"]:
            score += 2
            reasons.append(f"{current_chog.get('name')} Choghadiya - favorable")
    
    # Check transit - Jupiter or Venus in 10th
    current_transits = transit_context.get("current_transits", {})
    if "Jupiter" in current_transits:
        jup_house = current_transits["Jupiter"].get("house_from_lagna", 0)
        if jup_house == 10:
            score += 3
            reasons.append("Jupiter in 10th house - excellent for career")
    
    recommendation = "Highly favorable" if score >= 5 else "Favorable" if score >= 2 else "Moderate" if score >= 0 else "Not ideal"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def evaluate_marriage_talk_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for marriage talks/discussions.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check weekday
    weekday = datetime.now().weekday()
    if weekday == 4:  # Friday (Venus day)
        score += 2
        reasons.append("Friday (Venus day) - favorable for relationship matters")
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    marriage_nakshatras = ["Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana", "Dhanishtha"]
    if nakshatra_name in marriage_nakshatras:
        score += 3
        reasons.append(f"{nakshatra_name} Nakshatra is favorable for marriage talks")
    
    # Check Venus transit
    current_transits = transit_context.get("current_transits", {})
    if "Venus" in current_transits:
        venus_house = current_transits["Venus"].get("house_from_lagna", 0)
        if venus_house in [1, 4, 5, 7, 9]:
            score += 3
            reasons.append("Venus in favorable position - excellent for relationships")
    
    # Check Choghadiya
    current_chog = get_current_choghadiya(choghadiya, datetime.now())
    if current_chog:
        if current_chog.get("type") in ["excellent", "good"]:
            score += 2
    
    recommendation = "Highly favorable" if score >= 5 else "Favorable" if score >= 2 else "Moderate"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def evaluate_investment_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for investments.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check Tithi
    tithi = panchanga.get("tithi", {})
    tithi_num = tithi.get("number", 0)
    if tithi_num in [4, 9, 14]:  # Rikta
        score -= 3
        warnings.append("Rikta Tithi - avoid financial decisions")
    
    # Check Jupiter transit
    current_transits = transit_context.get("current_transits", {})
    if "Jupiter" in current_transits:
        jup_house = current_transits["Jupiter"].get("house_from_lagna", 0)
        if jup_house in [2, 11]:
            score += 4
            reasons.append("Jupiter in wealth/gains house - excellent for investments")
    
    # Check Choghadiya
    current_chog = get_current_choghadiya(choghadiya, datetime.now())
    if current_chog:
        if current_chog.get("name") == "Labh":
            score += 3
            reasons.append("Labh Choghadiya - gains and profit")
    
    recommendation = "Favorable" if score >= 3 else "Moderate" if score >= 0 else "Not recommended"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def evaluate_property_purchase_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for buying property.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check weekday
    weekday = datetime.now().weekday()
    if weekday == 1:  # Tuesday (Mars - property)
        score += 1
        reasons.append("Tuesday favorable for property matters")
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    property_nakshatras = ["Rohini", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana"]
    if nakshatra_name in property_nakshatras:
        score += 3
        reasons.append(f"{nakshatra_name} Nakshatra favorable for property")
    
    # Check 4th house transit (property house)
    current_transits = transit_context.get("current_transits", {})
    if "Jupiter" in current_transits:
        jup_house = current_transits["Jupiter"].get("house_from_lagna", 0)
        if jup_house == 4:
            score += 4
            reasons.append("Jupiter in 4th house - excellent for property")
    
    recommendation = "Favorable" if score >= 4 else "Moderate" if score >= 1 else "Not ideal"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def evaluate_business_start_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for starting business.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check weekday
    weekday = datetime.now().weekday()
    if weekday == 2:  # Wednesday (Mercury - business)
        score += 2
        reasons.append("Wednesday (Mercury day) - favorable for business")
    
    # Check Tithi
    tithi = panchanga.get("tithi", {})
    tithi_num = tithi.get("number", 0)
    if tithi_num in [1, 6, 11]:  # Good for new beginnings
        score += 2
        reasons.append("Favorable Tithi for new beginnings")
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    business_nakshatras = ["Pushya", "Hasta", "Swati", "Anuradha", "Shravana"]
    if nakshatra_name in business_nakshatras:
        score += 3
        reasons.append(f"{nakshatra_name} Nakshatra excellent for business")
    
    # Check 10th house transit
    current_transits = transit_context.get("current_transits", {})
    if "Jupiter" in current_transits:
        jup_house = current_transits["Jupiter"].get("house_from_lagna", 0)
        if jup_house == 10:
            score += 4
            reasons.append("Jupiter in 10th house - excellent for business start")
    
    recommendation = "Highly favorable" if score >= 6 else "Favorable" if score >= 3 else "Moderate"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def evaluate_medical_treatment_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for medical treatment.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    medical_nakshatras = ["Ashwini", "Pushya", "Hasta", "Shravana", "Shatabhisha"]
    if nakshatra_name in medical_nakshatras:
        score += 3
        reasons.append(f"{nakshatra_name} Nakshatra favorable for medical matters")
    
    # Avoid Rog Choghadiya
    current_chog = get_current_choghadiya(choghadiya, datetime.now())
    if current_chog:
        if current_chog.get("name") == "Rog":
            score -= 2
            warnings.append("Rog Choghadiya - avoid medical procedures")
    
    recommendation = "Favorable" if score >= 2 else "Moderate" if score >= 0 else "Not ideal"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def evaluate_spiritual_initiation_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for spiritual initiation.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check weekday
    weekday = datetime.now().weekday()
    if weekday == 3:  # Thursday (Jupiter - spirituality)
        score += 2
        reasons.append("Thursday (Jupiter day) - favorable for spiritual matters")
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    spiritual_nakshatras = ["Pushya", "Hasta", "Swati", "Anuradha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    if nakshatra_name in spiritual_nakshatras:
        score += 3
        reasons.append(f"{nakshatra_name} Nakshatra excellent for spiritual activities")
    
    # Check Jupiter transit
    current_transits = transit_context.get("current_transits", {})
    if "Jupiter" in current_transits:
        jup_house = current_transits["Jupiter"].get("house_from_lagna", 0)
        if jup_house in [1, 5, 9]:
            score += 4
            reasons.append("Jupiter in trine - highly auspicious for spirituality")
    
    recommendation = "Highly favorable" if score >= 5 else "Favorable" if score >= 2 else "Moderate"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def evaluate_naming_ceremony_muhurtha(panchanga: Dict, choghadiya: Dict, transit_context: Dict) -> Dict:
    """
    Phase 20: Evaluate Muhurtha for naming ceremony.
    
    Args:
        panchanga: Panchanga data
        choghadiya: Choghadiya data
        transit_context: Transit context
    
    Returns:
        Evaluation dictionary
    """
    score = 0
    reasons = []
    warnings = []
    
    # Check Nakshatra
    nakshatra = panchanga.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "")
    good_nakshatras = ["Rohini", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana"]
    if nakshatra_name in good_nakshatras:
        score += 3
        reasons.append(f"{nakshatra_name} Nakshatra favorable for naming")
    
    # Check Choghadiya
    current_chog = get_current_choghadiya(choghadiya, datetime.now())
    if current_chog:
        if current_chog.get("type") in ["excellent", "good"]:
            score += 2
    
    recommendation = "Favorable" if score >= 3 else "Moderate"
    
    return {
        "score": max(-10, min(10, score)),
        "reason": "; ".join(reasons) if reasons else "Standard conditions",
        "warnings": warnings,
        "recommendation": recommendation
    }


def get_current_choghadiya(choghadiya: Dict, current_time: datetime) -> Dict:
    """
    Phase 20: Get current Choghadiya segment.
    
    Args:
        choghadiya: Choghadiya data
        current_time: Current time
    
    Returns:
        Current Choghadiya segment or None
    """
    current_hour = current_time.hour + current_time.minute / 60.0
    
    # Check day Choghadiya
    for segment in choghadiya.get("day_choghadiya", []):
        start_str = segment.get("start", "")
        end_str = segment.get("end", "")
        
        if start_str and end_str:
            start_hour = float(start_str.split(':')[0]) + float(start_str.split(':')[1]) / 60.0
            end_hour = float(end_str.split(':')[0]) + float(end_str.split(':')[1]) / 60.0
            
            if start_hour <= current_hour < end_hour:
                return segment
    
    # Check night Choghadiya
    for segment in choghadiya.get("night_choghadiya", []):
        start_str = segment.get("start", "")
        end_str = segment.get("end", "")
        
        if start_str and end_str:
            start_hour = float(start_str.split(':')[0]) + float(start_str.split(':')[1]) / 60.0
            end_hour = float(end_str.split(':')[0]) + float(end_str.split(':')[1]) / 60.0
            
            # Handle night segments that cross midnight
            if end_hour < start_hour:
                if current_hour >= start_hour or current_hour < end_hour:
                    return segment
            elif start_hour <= current_hour < end_hour:
                return segment
    
    return None


def is_in_time_window(current_time: datetime, time_window: Dict) -> bool:
    """
    Phase 20: Check if current time is in a time window.
    
    Args:
        current_time: Current time
        time_window: Time window dictionary with start and end
    
    Returns:
        True if in window, False otherwise
    """
    if not time_window:
        return False
    
    start_str = time_window.get("start", "")
    end_str = time_window.get("end", "")
    
    if not start_str or not end_str:
        return False
    
    current_hour = current_time.hour + current_time.minute / 60.0
    start_hour = float(start_str.split(':')[0]) + float(start_str.split(':')[1]) / 60.0
    end_hour = float(end_str.split(':')[0]) + float(end_str.split(':')[1]) / 60.0
    
    if end_hour < start_hour:  # Crosses midnight
        return current_hour >= start_hour or current_hour < end_hour
    else:
        return start_hour <= current_hour < end_hour

