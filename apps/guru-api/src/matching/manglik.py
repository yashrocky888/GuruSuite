"""
Phase 13: Manglik (Kuja Dosha) Analysis

Checks for Mangal Dosha and cancellation rules.
"""

from typing import Dict


def check_manglik(kundli: Dict) -> Dict:
    """
    Phase 13: Check if a person has Manglik (Kuja Dosha).
    
    Manglik occurs when Mars is in:
    - 1st house (Lagna)
    - 4th house (Sukha)
    - 7th house (Kalatra)
    - 8th house (Ayur)
    - 12th house (Vyaya)
    
    Args:
        kundli: Kundli dictionary with planets and houses
    
    Returns:
        Dictionary with manglik status and details
    """
    # Get Mars position
    mars_degree = kundli["Planets"]["Mars"]["degree"]
    
    # Calculate which house Mars is in
    ascendant_deg = kundli["Ascendant"]["degree"]
    
    # Calculate relative position from ascendant
    relative_pos = (mars_degree - ascendant_deg) % 360
    mars_house = int(relative_pos / 30) + 1
    if mars_house > 12:
        mars_house = 1
    
    # Check if Mars is in Manglik houses
    manglik_houses = [1, 4, 7, 8, 12]
    is_manglik = mars_house in manglik_houses
    
    # Get Mars sign
    from src.utils.converters import degrees_to_sign
    mars_sign, _ = degrees_to_sign(mars_degree)
    
    return {
        "is_manglik": is_manglik,
        "mars_house": mars_house,
        "mars_sign": mars_sign,
        "mars_degree": round(mars_degree, 4),
        "manglik_houses": manglik_houses,
        "severity": "High" if mars_house in [1, 4, 7] else "Moderate" if mars_house in [8, 12] else "None"
    }


def check_manglik_cancellation(boy_manglik: Dict, girl_manglik: Dict) -> Dict:
    """
    Phase 13: Check Manglik cancellation rules.
    
    Cancellation occurs when:
    1. Both are Manglik - cancels each other
    2. Mars in own sign (Aries, Scorpio) - cancels
    3. Mars in exaltation (Capricorn) - cancels
    4. Mars in friendly sign - reduces severity
    
    Args:
        boy_manglik: Boy's manglik status
        girl_manglik: Girl's manglik status
    
    Returns:
        Dictionary with cancellation status
    """
    boy_cancelled = False
    girl_cancelled = False
    
    # Check if both are Manglik (mutual cancellation)
    if boy_manglik["is_manglik"] and girl_manglik["is_manglik"]:
        boy_cancelled = True
        girl_cancelled = True
        cancellation_reason = "Both are Manglik - mutual cancellation"
    
    # Check Mars in own sign (Aries=0, Scorpio=7)
    elif boy_manglik["is_manglik"] and boy_manglik["mars_sign"] in [0, 7]:
        boy_cancelled = True
        cancellation_reason = "Mars in own sign (Aries/Scorpio)"
    elif girl_manglik["is_manglik"] and girl_manglik["mars_sign"] in [0, 7]:
        girl_cancelled = True
        cancellation_reason = "Mars in own sign (Aries/Scorpio)"
    
    # Check Mars in exaltation (Capricorn=9)
    elif boy_manglik["is_manglik"] and boy_manglik["mars_sign"] == 9:
        boy_cancelled = True
        cancellation_reason = "Mars in exaltation (Capricorn)"
    elif girl_manglik["is_manglik"] and girl_manglik["mars_sign"] == 9:
        girl_cancelled = True
        cancellation_reason = "Mars in exaltation (Capricorn)"
    
    else:
        cancellation_reason = "No cancellation"
    
    # Overall compatibility
    if boy_cancelled and girl_cancelled:
        overall_status = "Cancelled - Safe for marriage"
    elif not boy_manglik["is_manglik"] and not girl_manglik["is_manglik"]:
        overall_status = "No Manglik - Safe for marriage"
    elif (boy_manglik["is_manglik"] and not girl_manglik["is_manglik"]) or (girl_manglik["is_manglik"] and not boy_manglik["is_manglik"]):
        overall_status = "One Manglik - Remedies recommended"
    else:
        overall_status = "Both Manglik - Mutual cancellation"
    
    return {
        "boy_manglik": boy_manglik["is_manglik"],
        "girl_manglik": girl_manglik["is_manglik"],
        "boy_cancelled": boy_cancelled,
        "girl_cancelled": girl_cancelled,
        "cancellation_reason": cancellation_reason,
        "overall_status": overall_status,
        "safe_for_marriage": boy_cancelled and girl_cancelled or (not boy_manglik["is_manglik"] and not girl_manglik["is_manglik"]),
        "remedies_needed": not (boy_cancelled and girl_cancelled) and (boy_manglik["is_manglik"] or girl_manglik["is_manglik"])
    }

