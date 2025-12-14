"""
Phase 13: Porutham (10 Checks System)

South Indian matchmaking system with 10 poruthams.
"""

from typing import Dict
from src.jyotish.panchang import get_nakshatra, get_nakshatra_lord
from src.utils.converters import degrees_to_sign, normalize_degrees


# Phase 13: Dina Porutham (Day compatibility)
def check_dina_porutham(boy_nak: int, girl_nak: int) -> bool:
    """
    Dina Porutham: Nakshatra distance should not be 6, 8, 18, 20.
    
    Args:
        boy_nak: Boy's nakshatra index (0-26)
        girl_nak: Girl's nakshatra index (0-26)
    
    Returns:
        True if compatible, False otherwise
    """
    distance = (girl_nak - boy_nak) % 27
    incompatible = [6, 8, 18, 20]
    return distance not in incompatible


# Phase 13: Gana Porutham (Temperament compatibility)
GANA = {
    "Ashwini": "Deva", "Bharani": "Manushya", "Krittika": "Rakshasa",
    "Rohini": "Manushya", "Mrigashira": "Deva", "Ardra": "Manushya",
    "Punarvasu": "Deva", "Pushya": "Deva", "Ashlesha": "Rakshasa",
    "Magha": "Rakshasa", "Purva Phalguni": "Manushya", "Uttara Phalguni": "Manushya",
    "Hasta": "Deva", "Chitra": "Rakshasa", "Swati": "Deva",
    "Vishakha": "Rakshasa", "Anuradha": "Deva", "Jyeshtha": "Rakshasa",
    "Mula": "Rakshasa", "Purva Ashadha": "Manushya", "Uttara Ashadha": "Manushya",
    "Shravana": "Deva", "Dhanishtha": "Rakshasa", "Shatabhisha": "Rakshasa",
    "Purva Bhadrapada": "Manushya", "Uttara Bhadrapada": "Manushya", "Revati": "Deva"
}

def check_gana_porutham(boy_nak_name: str, girl_nak_name: str) -> bool:
    """
    Gana Porutham: Same gana is compatible.
    """
    boy_gana = GANA.get(boy_nak_name, "Manushya")
    girl_gana = GANA.get(girl_nak_name, "Manushya")
    return boy_gana == girl_gana


# Phase 13: Mahendra Porutham (Longevity)
def check_mahendra_porutham(boy_nak: int, girl_nak: int) -> bool:
    """
    Mahendra Porutham: Nakshatra distance should not be 5, 7, 9, 10, 11, 13, 15, 16, 17, 19, 21, 22, 23.
    """
    distance = (girl_nak - boy_nak) % 27
    incompatible = [5, 7, 9, 10, 11, 13, 15, 16, 17, 19, 21, 22, 23]
    return distance not in incompatible


# Phase 13: Sthree Deerga Porutham (Female longevity)
def check_sthree_deerga_porutham(boy_nak: int, girl_nak: int) -> bool:
    """
    Sthree Deerga Porutham: Nakshatra distance should not be 2, 4, 6, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20, 22, 26.
    """
    distance = (girl_nak - boy_nak) % 27
    incompatible = [2, 4, 6, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20, 22, 26]
    return distance not in incompatible


# Phase 13: Yoni Porutham (Sexual compatibility)
YONI = {
    "Ashwini": "Horse", "Bharani": "Elephant", "Krittika": "Goat", "Rohini": "Serpent",
    "Mrigashira": "Serpent", "Ardra": "Dog", "Punarvasu": "Cat", "Pushya": "Goat",
    "Ashlesha": "Cat", "Magha": "Rat", "Purva Phalguni": "Rat", "Uttara Phalguni": "Cow",
    "Hasta": "Buffalo", "Chitra": "Tiger", "Swati": "Buffalo", "Vishakha": "Tiger",
    "Anuradha": "Deer", "Jyeshtha": "Hare", "Mula": "Dog", "Purva Ashadha": "Monkey",
    "Uttara Ashadha": "Mongoose", "Shravana": "Monkey", "Dhanishtha": "Lion",
    "Shatabhisha": "Horse", "Purva Bhadrapada": "Lion", "Uttara Bhadrapada": "Cow", "Revati": "Elephant"
}

def check_yoni_porutham(boy_nak_name: str, girl_nak_name: str) -> bool:
    """
    Yoni Porutham: Same yoni or friendly yonis are compatible.
    """
    boy_yoni = YONI.get(boy_nak_name, "Horse")
    girl_yoni = YONI.get(girl_nak_name, "Horse")
    
    if boy_yoni == girl_yoni:
        return True
    
    # Friendly pairs
    friendly_pairs = [
        ("Horse", "Dog"), ("Dog", "Horse"),
        ("Elephant", "Lion"), ("Lion", "Elephant"),
        ("Goat", "Cow"), ("Cow", "Goat")
    ]
    
    return (boy_yoni, girl_yoni) in friendly_pairs


# Phase 13: Rasi Porutham (Sign compatibility)
def check_rasi_porutham(boy_sign: int, girl_sign: int) -> bool:
    """
    Rasi Porutham: Signs should be compatible (1, 5, 9 from each other or same).
    """
    if boy_sign == girl_sign:
        return True
    
    diff = abs(boy_sign - girl_sign)
    if diff > 6:
        diff = 12 - diff
    
    return diff in [1, 5]  # 1st, 5th, 9th house


# Phase 13: Rasi Adhipathi Porutham (Sign lord compatibility)
SIGN_LORDS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
    5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn",
    10: "Saturn", 11: "Jupiter"
}

GRAHA_MAITRI = {
    "Sun": {"friend": ["Moon", "Mars", "Jupiter"], "enemy": ["Venus", "Saturn"]},
    "Moon": {"friend": ["Sun", "Mercury"], "enemy": []},
    "Mars": {"friend": ["Sun", "Moon", "Jupiter"], "enemy": ["Mercury"]},
    "Mercury": {"friend": ["Sun", "Venus"], "enemy": ["Moon"]},
    "Jupiter": {"friend": ["Sun", "Moon", "Mars"], "enemy": ["Venus", "Mercury"]},
    "Venus": {"friend": ["Mercury", "Saturn"], "enemy": ["Sun", "Moon"]},
    "Saturn": {"friend": ["Mercury", "Venus"], "enemy": ["Sun", "Moon", "Mars"]}
}

def check_rasi_adhipathi_porutham(boy_sign: int, girl_sign: int) -> bool:
    """
    Rasi Adhipathi Porutham: Sign lords should be friends or neutral.
    """
    boy_lord = SIGN_LORDS.get(boy_sign, "Sun")
    girl_lord = SIGN_LORDS.get(girl_sign, "Sun")
    
    if boy_lord == girl_lord:
        return True
    
    boy_friends = GRAHA_MAITRI.get(boy_lord, {}).get("friend", [])
    boy_enemies = GRAHA_MAITRI.get(boy_lord, {}).get("enemy", [])
    
    if girl_lord in boy_friends:
        return True
    elif girl_lord in boy_enemies:
        return False
    else:
        return True  # Neutral


# Phase 13: Vasiya Porutham (Mutual attraction)
def check_vasiya_porutham(boy_sign: int, girl_sign: int) -> bool:
    """
    Vasiya Porutham: Signs should have mutual attraction.
    Compatible: Same sign, or 2, 4, 10, 12 from each other.
    """
    if boy_sign == girl_sign:
        return True
    
    diff = abs(boy_sign - girl_sign)
    if diff > 6:
        diff = 12 - diff
    
    return diff in [2, 4, 10, 12]


# Phase 13: Rajju Porutham (Longevity - most important)
def check_rajju_porutham(boy_nak: int, girl_nak: int) -> bool:
    """
    Rajju Porutham: Nakshatra distance should not be 6, 8, 12, 14, 18, 20, 24, 26.
    This is critical - if failed, marriage is not recommended.
    """
    distance = (girl_nak - boy_nak) % 27
    incompatible = [6, 8, 12, 14, 18, 20, 24, 26]
    return distance not in incompatible


# Phase 13: Vedha Porutham (Obstruction)
def check_vedha_porutham(boy_nak: int, girl_nak: int) -> bool:
    """
    Vedha Porutham: Nakshatras should not be in vedha (obstruction) position.
    Distance should not be 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 25, 26.
    """
    distance = (girl_nak - boy_nak) % 27
    incompatible = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 25, 26]
    return distance not in incompatible


def porutham(boy_kundli: Dict, girl_kundli: Dict) -> Dict:
    """
    Phase 13: Calculate Porutham (10 checks system).
    
    Args:
        boy_kundli: Boy's kundli dictionary
        girl_kundli: Girl's kundli dictionary
    
    Returns:
        Dictionary with all 10 poruthams and score
    """
    # Get Moon positions
    boy_moon_deg = boy_kundli["Planets"]["Moon"]["degree"]
    girl_moon_deg = girl_kundli["Planets"]["Moon"]["degree"]
    
    # Get nakshatras
    boy_nak_name, boy_nak_index = get_nakshatra(boy_moon_deg)
    girl_nak_name, girl_nak_index = get_nakshatra(girl_moon_deg)
    
    # Get signs
    boy_sign, _ = degrees_to_sign(boy_moon_deg)
    girl_sign, _ = degrees_to_sign(girl_moon_deg)
    
    # Calculate all poruthams
    dina = check_dina_porutham(boy_nak_index, girl_nak_index)
    gana = check_gana_porutham(boy_nak_name, girl_nak_name)
    mahendra = check_mahendra_porutham(boy_nak_index, girl_nak_index)
    sthree_deerga = check_sthree_deerga_porutham(boy_nak_index, girl_nak_index)
    yoni = check_yoni_porutham(boy_nak_name, girl_nak_name)
    rasi = check_rasi_porutham(boy_sign, girl_sign)
    rasi_adhipathi = check_rasi_adhipathi_porutham(boy_sign, girl_sign)
    vasiya = check_vasiya_porutham(boy_sign, girl_sign)
    rajju = check_rajju_porutham(boy_nak_index, girl_nak_index)
    vedha = check_vedha_porutham(boy_nak_index, girl_nak_index)
    
    # Calculate score
    score = sum([
        dina, gana, mahendra, sthree_deerga, yoni,
        rasi, rasi_adhipathi, vasiya, rajju, vedha
    ])
    
    return {
        "dina": {
            "compatible": dina,
            "description": "Day compatibility - ensures harmony"
        },
        "gana": {
            "compatible": gana,
            "description": "Temperament compatibility"
        },
        "mahendra": {
            "compatible": mahendra,
            "description": "Male longevity"
        },
        "sthree_deerga": {
            "compatible": sthree_deerga,
            "description": "Female longevity"
        },
        "yoni": {
            "compatible": yoni,
            "description": "Sexual compatibility"
        },
        "rasi": {
            "compatible": rasi,
            "description": "Sign compatibility"
        },
        "rasi_adhipathi": {
            "compatible": rasi_adhipathi,
            "description": "Sign lord compatibility"
        },
        "vasiya": {
            "compatible": vasiya,
            "description": "Mutual attraction"
        },
        "rajju": {
            "compatible": rajju,
            "description": "Longevity (most important)"
        },
        "vedha": {
            "compatible": vedha,
            "description": "Obstruction check"
        },
        "score": score,
        "max_score": 10,
        "percentage": round((score / 10) * 100, 1),
        "verdict": "Excellent" if score >= 9 else "Very Good" if score >= 7 else "Good" if score >= 5 else "Average" if score >= 3 else "Not Recommended"
    }

