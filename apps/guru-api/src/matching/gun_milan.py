"""
Phase 13: Gun Milan (36 Points System)

North Indian matchmaking system with 8 gunas.
"""

from typing import Dict
from src.jyotish.panchang import get_nakshatra, get_nakshatra_lord
from src.utils.converters import degrees_to_sign, normalize_degrees


# Phase 13: Varna classification (1 point)
VARNA = {
    "Ashwini": 1, "Bharani": 1, "Krittika": 1, "Rohini": 1, "Mrigashira": 1, "Ardra": 1,
    "Punarvasu": 2, "Pushya": 2, "Ashlesha": 2, "Magha": 2, "Purva Phalguni": 2, "Uttara Phalguni": 2,
    "Hasta": 3, "Chitra": 3, "Swati": 3, "Vishakha": 3, "Anuradha": 3, "Jyeshtha": 3,
    "Mula": 4, "Purva Ashadha": 4, "Uttara Ashadha": 4, "Shravana": 4, "Dhanishtha": 4, "Shatabhisha": 4,
    "Purva Bhadrapada": 4, "Uttara Bhadrapada": 4, "Revati": 4
}


# Phase 13: Vashya (2 points)
VASHYA = {
    "Ashwini": "Chatushpada", "Bharani": "Chatushpada", "Krittika": "Chatushpada",
    "Rohini": "Chatushpada", "Mrigashira": "Chatushpada", "Ardra": "Chatushpada",
    "Punarvasu": "Manushya", "Pushya": "Manushya", "Ashlesha": "Manushya",
    "Magha": "Manushya", "Purva Phalguni": "Manushya", "Uttara Phalguni": "Manushya",
    "Hasta": "Manushya", "Chitra": "Manushya", "Swati": "Manushya",
    "Vishakha": "Manushya", "Anuradha": "Manushya", "Jyeshtha": "Manushya",
    "Mula": "Vanara", "Purva Ashadha": "Vanara", "Uttara Ashadha": "Vanara",
    "Shravana": "Vanara", "Dhanishtha": "Vanara", "Shatabhisha": "Vanara",
    "Purva Bhadrapada": "Jalachara", "Uttara Bhadrapada": "Jalachara", "Revati": "Jalachara"
}

VASHYA_COMPATIBILITY = {
    ("Chatushpada", "Chatushpada"): 2,
    ("Manushya", "Manushya"): 2,
    ("Vanara", "Vanara"): 2,
    ("Jalachara", "Jalachara"): 2,
    ("Chatushpada", "Manushya"): 1,
    ("Manushya", "Chatushpada"): 1,
    ("Vanara", "Jalachara"): 1,
    ("Jalachara", "Vanara"): 1,
    ("Chatushpada", "Vanara"): 0,
    ("Vanara", "Chatushpada"): 0,
    ("Manushya", "Jalachara"): 0,
    ("Jalachara", "Manushya"): 0,
}


# Phase 13: Tara (3 points) - Based on nakshatra distance
def calculate_tara(boy_nak: int, girl_nak: int) -> int:
    """
    Calculate Tara (Star) compatibility.
    
    Distance from boy's nakshatra to girl's nakshatra:
    - 1, 3, 5, 7 = 3 points (best)
    - 2, 4, 6 = 1.5 points
    - 8, 9 = 0 points (worst)
    """
    distance = (girl_nak - boy_nak) % 27
    if distance in [1, 3, 5, 7]:
        return 3
    elif distance in [2, 4, 6]:
        return 1.5
    elif distance in [8, 9]:
        return 0
    else:
        return 1.5  # Default


# Phase 13: Yoni (4 points)
YONI = {
    "Ashwini": "Horse", "Bharani": "Elephant", "Krittika": "Goat", "Rohini": "Serpent",
    "Mrigashira": "Serpent", "Ardra": "Dog", "Punarvasu": "Cat", "Pushya": "Goat",
    "Ashlesha": "Cat", "Magha": "Rat", "Purva Phalguni": "Rat", "Uttara Phalguni": "Cow",
    "Hasta": "Buffalo", "Chitra": "Tiger", "Swati": "Buffalo", "Vishakha": "Tiger",
    "Anuradha": "Deer", "Jyeshtha": "Hare", "Mula": "Dog", "Purva Ashadha": "Monkey",
    "Uttara Ashadha": "Mongoose", "Shravana": "Monkey", "Dhanishtha": "Lion",
    "Shatabhisha": "Horse", "Purva Bhadrapada": "Lion", "Uttara Bhadrapada": "Cow", "Revati": "Elephant"
}

YONI_COMPATIBILITY = {
    ("Horse", "Horse"): 4, ("Elephant", "Elephant"): 4, ("Goat", "Goat"): 4,
    ("Serpent", "Serpent"): 4, ("Dog", "Dog"): 4, ("Cat", "Cat"): 4,
    ("Rat", "Rat"): 4, ("Cow", "Cow"): 4, ("Buffalo", "Buffalo"): 4,
    ("Tiger", "Tiger"): 4, ("Deer", "Deer"): 4, ("Hare", "Hare"): 4,
    ("Monkey", "Monkey"): 4, ("Mongoose", "Mongoose"): 4, ("Lion", "Lion"): 4,
    # Friends
    ("Horse", "Dog"): 3, ("Dog", "Horse"): 3,
    ("Elephant", "Lion"): 3, ("Lion", "Elephant"): 3,
    ("Goat", "Cow"): 3, ("Cow", "Goat"): 3,
    # Enemies (0 points)
    ("Serpent", "Mongoose"): 0, ("Mongoose", "Serpent"): 0,
    ("Cat", "Rat"): 0, ("Rat", "Cat"): 0,
    ("Tiger", "Deer"): 0, ("Deer", "Tiger"): 0,
}


# Phase 13: Graha Maitri (5 points) - Planetary friendship
GRAHA_MAITRI = {
    "Sun": {"friend": ["Moon", "Mars", "Jupiter"], "enemy": ["Venus", "Saturn"]},
    "Moon": {"friend": ["Sun", "Mercury"], "enemy": []},
    "Mars": {"friend": ["Sun", "Moon", "Jupiter"], "enemy": ["Mercury"]},
    "Mercury": {"friend": ["Sun", "Venus"], "enemy": ["Moon"]},
    "Jupiter": {"friend": ["Sun", "Moon", "Mars"], "enemy": ["Venus", "Mercury"]},
    "Venus": {"friend": ["Mercury", "Saturn"], "enemy": ["Sun", "Moon"]},
    "Saturn": {"friend": ["Mercury", "Venus"], "enemy": ["Sun", "Moon", "Mars"]}
}


# Phase 13: Gana (6 points)
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

GANA_COMPATIBILITY = {
    ("Deva", "Deva"): 6,
    ("Manushya", "Manushya"): 6,
    ("Rakshasa", "Rakshasa"): 6,
    ("Deva", "Manushya"): 3,
    ("Manushya", "Deva"): 3,
    ("Deva", "Rakshasa"): 0,
    ("Rakshasa", "Deva"): 0,
    ("Manushya", "Rakshasa"): 0,
    ("Rakshasa", "Manushya"): 0,
}


# Phase 13: Bhakoot (7 points) - Rasi compatibility
def calculate_bhakoot(boy_sign: int, girl_sign: int) -> int:
    """
    Calculate Bhakoot (Rasi compatibility).
    
    Compatible signs:
    - Same sign: 7 points
    - 1, 5, 9 from each other: 7 points
    - 2, 3, 4, 10, 11, 12: 0 points (incompatible)
    """
    if boy_sign == girl_sign:
        return 7
    
    diff = abs(boy_sign - girl_sign)
    if diff > 6:
        diff = 12 - diff
    
    if diff in [1, 5]:  # 1st, 5th, 9th house
        return 7
    elif diff == 0:  # Same sign
        return 7
    else:
        return 0


# Phase 13: Nadi (8 points) - Most important
NADI = {
    "Ashwini": "Adi", "Bharani": "Madhya", "Krittika": "Adi",
    "Rohini": "Madhya", "Mrigashira": "Adi", "Ardra": "Madhya",
    "Punarvasu": "Adi", "Pushya": "Madhya", "Ashlesha": "Adi",
    "Magha": "Madhya", "Purva Phalguni": "Adi", "Uttara Phalguni": "Madhya",
    "Hasta": "Adi", "Chitra": "Madhya", "Swati": "Adi",
    "Vishakha": "Madhya", "Anuradha": "Adi", "Jyeshtha": "Madhya",
    "Mula": "Adi", "Purva Ashadha": "Madhya", "Uttara Ashadha": "Adi",
    "Shravana": "Madhya", "Dhanishtha": "Adi", "Shatabhisha": "Madhya",
    "Purva Bhadrapada": "Adi", "Uttara Bhadrapada": "Madhya", "Revati": "Adi"
}

NADI_COMPATIBILITY = {
    ("Adi", "Madhya"): 8,
    ("Madhya", "Adi"): 8,
    ("Adi", "Adi"): 0,  # Same Nadi - not compatible
    ("Madhya", "Madhya"): 0,  # Same Nadi - not compatible
}


def gun_milan(boy_kundli: Dict, girl_kundli: Dict) -> Dict:
    """
    Phase 13: Calculate Gun Milan (36 points system).
    
    Args:
        boy_kundli: Boy's kundli dictionary
        girl_kundli: Girl's kundli dictionary
    
    Returns:
        Dictionary with all 8 gunas and total score
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
    
    # 1. Varna (1 point)
    boy_varna = VARNA.get(boy_nak_name, 1)
    girl_varna = VARNA.get(girl_nak_name, 1)
    varna_score = 1 if abs(boy_varna - girl_varna) <= 1 else 0
    
    # 2. Vashya (2 points)
    boy_vashya = VASHYA.get(boy_nak_name, "Manushya")
    girl_vashya = VASHYA.get(girl_nak_name, "Manushya")
    vashya_score = VASHYA_COMPATIBILITY.get((boy_vashya, girl_vashya), 0)
    
    # 3. Tara (3 points)
    tara_score = calculate_tara(boy_nak_index, girl_nak_index)
    
    # 4. Yoni (4 points)
    boy_yoni = YONI.get(boy_nak_name, "Horse")
    girl_yoni = YONI.get(girl_nak_name, "Horse")
    yoni_score = YONI_COMPATIBILITY.get((boy_yoni, girl_yoni), 2)  # Default 2 if not found
    
    # 5. Graha Maitri (5 points)
    boy_moon_lord = get_nakshatra_lord(boy_nak_index)
    girl_moon_lord = get_nakshatra_lord(girl_nak_index)
    
    boy_friends = GRAHA_MAITRI.get(boy_moon_lord, {}).get("friend", [])
    boy_enemies = GRAHA_MAITRI.get(boy_moon_lord, {}).get("enemy", [])
    
    if girl_moon_lord in boy_friends:
        graha_maitri_score = 5
    elif girl_moon_lord in boy_enemies:
        graha_maitri_score = 0
    else:
        graha_maitri_score = 2.5  # Neutral
    
    # 6. Gana (6 points)
    boy_gana = GANA.get(boy_nak_name, "Manushya")
    girl_gana = GANA.get(girl_nak_name, "Manushya")
    gana_score = GANA_COMPATIBILITY.get((boy_gana, girl_gana), 0)
    
    # 7. Bhakoot (7 points)
    bhakoot_score = calculate_bhakoot(boy_sign, girl_sign)
    
    # 8. Nadi (8 points) - Most important
    boy_nadi = NADI.get(boy_nak_name, "Adi")
    girl_nadi = NADI.get(girl_nak_name, "Adi")
    nadi_score = NADI_COMPATIBILITY.get((boy_nadi, girl_nadi), 0)
    
    # Calculate total
    total = varna_score + vashya_score + tara_score + yoni_score + graha_maitri_score + gana_score + bhakoot_score + nadi_score
    
    return {
        "varna": {
            "boy": boy_varna,
            "girl": girl_varna,
            "score": round(varna_score, 1),
            "max": 1
        },
        "vashya": {
            "boy": boy_vashya,
            "girl": girl_vashya,
            "score": round(vashya_score, 1),
            "max": 2
        },
        "tara": {
            "boy_nakshatra": boy_nak_name,
            "girl_nakshatra": girl_nak_name,
            "score": round(tara_score, 1),
            "max": 3
        },
        "yoni": {
            "boy": boy_yoni,
            "girl": girl_yoni,
            "score": round(yoni_score, 1),
            "max": 4
        },
        "graha_maitri": {
            "boy_lord": boy_moon_lord,
            "girl_lord": girl_moon_lord,
            "score": round(graha_maitri_score, 1),
            "max": 5
        },
        "gana": {
            "boy": boy_gana,
            "girl": girl_gana,
            "score": round(gana_score, 1),
            "max": 6
        },
        "bhakoot": {
            "boy_sign": boy_sign,
            "girl_sign": girl_sign,
            "score": round(bhakoot_score, 1),
            "max": 7
        },
        "nadi": {
            "boy": boy_nadi,
            "girl": girl_nadi,
            "score": round(nadi_score, 1),
            "max": 8
        },
        "total": round(total, 1),
        "max_total": 36,
        "percentage": round((total / 36) * 100, 1),
        "verdict": "Excellent" if total >= 32 else "Very Good" if total >= 28 else "Good" if total >= 24 else "Average" if total >= 18 else "Below Average"
    }
