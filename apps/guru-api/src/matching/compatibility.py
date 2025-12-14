"""
Phase 13: Advanced Compatibility Analysis

Advanced matching factors beyond Gun Milan and Porutham.
"""

from typing import Dict
from src.jyotish.panchang import get_nakshatra
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from src.utils.converters import degrees_to_sign, normalize_degrees, calculate_aspect
from datetime import datetime


def calculate_moon_distance(boy_moon_deg: float, girl_moon_deg: float) -> Dict:
    """
    Phase 13: Calculate Moon-Moon distance and compatibility.
    
    Optimal distance: 1, 3, 5, 7, 9 signs apart (120-180 degrees ideal).
    
    Args:
        boy_moon_deg: Boy's Moon degree
        girl_moon_deg: Girl's Moon degree
    
    Returns:
        Dictionary with distance and compatibility
    """
    distance = abs(boy_moon_deg - girl_moon_deg)
    if distance > 180:
        distance = 360 - distance
    
    # Convert to sign difference
    boy_sign, _ = degrees_to_sign(boy_moon_deg)
    girl_sign, _ = degrees_to_sign(girl_moon_deg)
    sign_diff = abs(boy_sign - girl_sign)
    if sign_diff > 6:
        sign_diff = 12 - sign_diff
    
    # Compatibility based on sign distance
    if sign_diff in [1, 3, 5, 7, 9]:
        compatibility = "Excellent"
        score = 100
    elif sign_diff in [2, 4, 6, 10]:
        compatibility = "Good"
        score = 75
    elif sign_diff == 0:
        compatibility = "Moderate"
        score = 50
    else:
        compatibility = "Challenging"
        score = 25
    
    return {
        "distance_degrees": round(distance, 2),
        "sign_difference": sign_diff,
        "compatibility": compatibility,
        "score": score
    }


def check_dasha_conflict(boy_dasha: Dict, girl_dasha: Dict) -> Dict:
    """
    Phase 13: Check for Dasha conflicts.
    
    Conflicts occur when:
    - Both in malefic dasha (Saturn, Rahu, Ketu)
    - Opposing dasha lords
    
    Args:
        boy_dasha: Boy's dasha information
        girl_dasha: Girl's dasha information
    
    Returns:
        Dictionary with conflict status
    """
    boy_lord = boy_dasha.get("nakshatra_lord", "")
    girl_lord = girl_dasha.get("nakshatra_lord", "")
    
    malefic_lords = ["Saturn", "Rahu", "Ketu", "Mars"]
    
    boy_malefic = boy_lord in malefic_lords
    girl_malefic = girl_lord in malefic_lords
    
    # Check for opposing lords
    opposing_pairs = [
        ("Sun", "Saturn"), ("Saturn", "Sun"),
        ("Moon", "Rahu"), ("Rahu", "Moon"),
        ("Mars", "Venus"), ("Venus", "Mars")
    ]
    
    is_opposing = (boy_lord, girl_lord) in opposing_pairs
    
    has_conflict = (boy_malefic and girl_malefic) or is_opposing
    
    return {
        "has_conflict": has_conflict,
        "boy_lord": boy_lord,
        "girl_lord": girl_lord,
        "conflict_type": "Both malefic" if (boy_malefic and girl_malefic) else "Opposing lords" if is_opposing else "None",
        "severity": "High" if has_conflict else "None"
    }


def calculate_rasi_compatibility(boy_kundli: Dict, girl_kundli: Dict) -> Dict:
    """
    Phase 13: Calculate Rasi (sign) compatibility.
    
    Args:
        boy_kundli: Boy's kundli
        girl_kundli: Girl's kundli
    
    Returns:
        Compatibility score and analysis
    """
    boy_moon_deg = boy_kundli["Planets"]["Moon"]["degree"]
    girl_moon_deg = girl_kundli["Planets"]["Moon"]["degree"]
    
    boy_sign, _ = degrees_to_sign(boy_moon_deg)
    girl_sign, _ = degrees_to_sign(girl_moon_deg)
    
    # Sign compatibility
    if boy_sign == girl_sign:
        compatibility = "Same sign - Good understanding"
        score = 85
    else:
        diff = abs(boy_sign - girl_sign)
        if diff > 6:
            diff = 12 - diff
        
        if diff in [1, 5, 9]:
            compatibility = "Excellent - Trine relationship"
            score = 95
        elif diff in [3, 7]:
            compatibility = "Good - Opposition (complementary)"
            score = 80
        elif diff in [2, 4, 6, 8, 10]:
            compatibility = "Moderate - Adjacent signs"
            score = 60
        else:
            compatibility = "Challenging"
            score = 40
    
    return {
        "boy_sign": boy_sign,
        "girl_sign": girl_sign,
        "compatibility": compatibility,
        "score": score
    }


def calculate_nakshatra_lord_compatibility(boy_kundli: Dict, girl_kundli: Dict) -> Dict:
    """
    Phase 13: Calculate Nakshatra lord compatibility.
    
    Args:
        boy_kundli: Boy's kundli
        girl_kundli: Girl's kundli
    
    Returns:
        Nakshatra lord compatibility
    """
    from src.jyotish.panchang import get_nakshatra_lord
    
    boy_moon_deg = boy_kundli["Planets"]["Moon"]["degree"]
    girl_moon_deg = girl_kundli["Planets"]["Moon"]["degree"]
    
    boy_nak_name, boy_nak_index = get_nakshatra(boy_moon_deg)
    girl_nak_name, girl_nak_index = get_nakshatra(girl_moon_deg)
    
    boy_lord = get_nakshatra_lord(boy_nak_index)
    girl_lord = get_nakshatra_lord(girl_nak_index)
    
    # Planetary friendship
    GRAHA_MAITRI = {
        "Sun": {"friend": ["Moon", "Mars", "Jupiter"], "enemy": ["Venus", "Saturn"]},
        "Moon": {"friend": ["Sun", "Mercury"], "enemy": []},
        "Mars": {"friend": ["Sun", "Moon", "Jupiter"], "enemy": ["Mercury"]},
        "Mercury": {"friend": ["Sun", "Venus"], "enemy": ["Moon"]},
        "Jupiter": {"friend": ["Sun", "Moon", "Mars"], "enemy": ["Venus", "Mercury"]},
        "Venus": {"friend": ["Mercury", "Saturn"], "enemy": ["Sun", "Moon"]},
        "Saturn": {"friend": ["Mercury", "Venus"], "enemy": ["Sun", "Moon", "Mars"]},
        "Ketu": {"friend": [], "enemy": []},
        "Rahu": {"friend": [], "enemy": []}
    }
    
    boy_friends = GRAHA_MAITRI.get(boy_lord, {}).get("friend", [])
    boy_enemies = GRAHA_MAITRI.get(boy_lord, {}).get("enemy", [])
    
    if boy_lord == girl_lord:
        compatibility = "Same lord - Good understanding"
        score = 90
    elif girl_lord in boy_friends:
        compatibility = "Friendly lords - Excellent"
        score = 95
    elif girl_lord in boy_enemies:
        compatibility = "Enemy lords - Challenging"
        score = 40
    else:
        compatibility = "Neutral lords - Moderate"
        score = 70
    
    return {
        "boy_lord": boy_lord,
        "girl_lord": girl_lord,
        "compatibility": compatibility,
        "score": score
    }


def calculate_papasamya_score(boy_kundli: Dict, girl_kundli: Dict) -> Dict:
    """
    Phase 13: Calculate Papasamya (Malefic balance) score.
    
    Checks balance of malefic planets in both charts.
    
    Args:
        boy_kundli: Boy's kundli
        girl_kundli: Girl's kundli
    
    Returns:
        Papasamya score and analysis
    """
    malefic_planets = ["Mars", "Saturn", "Sun", "Rahu", "Ketu"]
    
    # Count malefics in kendras (1, 4, 7, 10)
    boy_malefics = 0
    girl_malefics = 0
    
    asc_deg = boy_kundli["Ascendant"]["degree"]
    
    for planet in malefic_planets:
        if planet in boy_kundli["Planets"]:
            planet_deg = boy_kundli["Planets"][planet]["degree"]
            rel_pos = (planet_deg - asc_deg) % 360
            house = int(rel_pos / 30) + 1
            if house > 12:
                house = 1
            if house in [1, 4, 7, 10]:
                boy_malefics += 1
        
        if planet in girl_kundli["Planets"]:
            planet_deg = girl_kundli["Planets"][planet]["degree"]
            rel_pos = (planet_deg - asc_deg) % 360
            house = int(rel_pos / 30) + 1
            if house > 12:
                house = 1
            if house in [1, 4, 7, 10]:
                girl_malefics += 1
    
    # Calculate score (lower malefics = better)
    total_malefics = boy_malefics + girl_malefics
    if total_malefics == 0:
        score = 100
        verdict = "Excellent - No malefics in Kendra"
    elif total_malefics <= 2:
        score = 75
        verdict = "Good - Minimal malefics"
    elif total_malefics <= 4:
        score = 50
        verdict = "Moderate - Some malefics present"
    else:
        score = 25
        verdict = "Challenging - Many malefics in Kendra"
    
    return {
        "boy_malefics_in_kendra": boy_malefics,
        "girl_malefics_in_kendra": girl_malefics,
        "total_malefics": total_malefics,
        "score": score,
        "verdict": verdict
    }


def advanced_compatibility(boy_kundli: Dict, girl_kundli: Dict, boy_dasha: Dict, girl_dasha: Dict) -> Dict:
    """
    Phase 13: Calculate advanced compatibility factors.
    
    Args:
        boy_kundli: Boy's kundli
        girl_kundli: Girl's kundli
        boy_dasha: Boy's dasha information
        girl_dasha: Girl's dasha information
    
    Returns:
        Dictionary with all advanced compatibility factors
    """
    # Moon distance
    boy_moon_deg = boy_kundli["Planets"]["Moon"]["degree"]
    girl_moon_deg = girl_kundli["Planets"]["Moon"]["degree"]
    moon_distance = calculate_moon_distance(boy_moon_deg, girl_moon_deg)
    
    # Dasha conflict
    dasha_conflict = check_dasha_conflict(boy_dasha, girl_dasha)
    
    # Rasi compatibility
    rasi_comp = calculate_rasi_compatibility(boy_kundli, girl_kundli)
    
    # Nakshatra lord compatibility
    nak_lord_comp = calculate_nakshatra_lord_compatibility(boy_kundli, girl_kundli)
    
    # Papasamya score
    papasamya = calculate_papasamya_score(boy_kundli, girl_kundli)
    
    # Calculate overall compatibility index (JHora style)
    scores = [
        moon_distance["score"],
        rasi_comp["score"],
        nak_lord_comp["score"],
        papasamya["score"]
    ]
    
    # Reduce score if dasha conflict
    if dasha_conflict["has_conflict"]:
        conflict_penalty = 20
    else:
        conflict_penalty = 0
    
    overall_index = (sum(scores) / len(scores)) - conflict_penalty
    if overall_index < 0:
        overall_index = 0
    
    return {
        "moon_distance": moon_distance,
        "dasha_conflict": dasha_conflict,
        "rasi_compatibility": rasi_comp,
        "nakshatra_lord_compatibility": nak_lord_comp,
        "papasamya": papasamya,
        "emotional_match": round(moon_distance["score"] * 0.4 + rasi_comp["score"] * 0.3 + nak_lord_comp["score"] * 0.3, 1),
        "communication_match": round(rasi_comp["score"] * 0.5 + nak_lord_comp["score"] * 0.5, 1),
        "overall_index": round(overall_index, 1),
        "verdict": "Excellent" if overall_index >= 80 else "Very Good" if overall_index >= 70 else "Good" if overall_index >= 60 else "Moderate" if overall_index >= 50 else "Challenging"
    }

