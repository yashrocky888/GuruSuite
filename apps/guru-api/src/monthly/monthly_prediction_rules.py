"""
Phase 20: Monthly Prediction Rules

Implements classical rules for monthly predictions based on transits.
"""

from typing import Dict, List


def evaluate_sun_transit_impact(sun_transit: Dict, natal_chart: Dict, dasha: Dict) -> Dict:
    """
    Phase 20: Evaluate Sun transit impact on career and authority.
    
    Args:
        sun_transit: Sun transit data
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Impact dictionary
    """
    impact = {
        "area": "career",
        "effect": "moderate",
        "description": "",
        "score": 0
    }
    
    sun_house = sun_transit.get("house_from_lagna", 0)
    
    if sun_house == 10:  # Career house
        impact["effect"] = "positive"
        impact["score"] = 7
        impact["description"] = "Sun in 10th house - strong focus on career, authority, and recognition"
    elif sun_house == 1:  # Self house
        impact["effect"] = "positive"
        impact["score"] = 6
        impact["description"] = "Sun in 1st house - enhanced self-confidence and leadership"
    elif sun_house in [6, 8, 12]:  # Dusthanas
        impact["effect"] = "challenging"
        impact["score"] = 3
        impact["description"] = "Sun in dusthana - challenges in career or authority matters"
    
    return impact


def evaluate_mars_transit_impact(mars_transit: Dict, natal_chart: Dict, dasha: Dict) -> Dict:
    """
    Phase 20: Evaluate Mars transit impact on energy and conflicts.
    
    Args:
        mars_transit: Mars transit data
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Impact dictionary
    """
    impact = {
        "area": "energy_conflicts",
        "effect": "moderate",
        "description": "",
        "score": 0
    }
    
    mars_house = mars_transit.get("house_from_lagna", 0)
    
    if mars_house in [3, 6, 11]:  # Upachaya houses
        impact["effect"] = "positive"
        impact["score"] = 6
        impact["description"] = "Mars in 3/6/11 - increased energy, courage, and gains"
    elif mars_house in [1, 7, 8, 12]:  # Challenging
        impact["effect"] = "challenging"
        impact["score"] = 3
        impact["description"] = "Mars in challenging houses - conflicts and aggression possible"
    
    return impact


def evaluate_mercury_transit_impact(mercury_transit: Dict, natal_chart: Dict, dasha: Dict) -> Dict:
    """
    Phase 20: Evaluate Mercury transit impact on communication and money.
    
    Args:
        mercury_transit: Mercury transit data
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Impact dictionary
    """
    impact = {
        "area": "communication_money",
        "effect": "moderate",
        "description": "",
        "score": 0
    }
    
    mercury_house = mercury_transit.get("house_from_lagna", 0)
    
    if mercury_house in [1, 4, 5, 9]:  # Favorable
        impact["effect"] = "positive"
        impact["score"] = 6
        impact["description"] = "Mercury in favorable houses - good communication and business"
    elif mercury_house in [6, 8, 12]:  # Challenging
        impact["effect"] = "challenging"
        impact["score"] = 3
        impact["description"] = "Mercury in dusthana - communication challenges"
    
    return impact


def evaluate_jupiter_transit_impact(jupiter_transit: Dict, natal_chart: Dict, dasha: Dict) -> Dict:
    """
    Phase 20: Evaluate Jupiter transit impact on blessings and expansion.
    
    Args:
        jupiter_transit: Jupiter transit data
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Impact dictionary
    """
    impact = {
        "area": "blessings_expansion",
        "effect": "positive",
        "description": "",
        "score": 7
    }
    
    jupiter_house = jupiter_transit.get("house_from_lagna", 0)
    
    if jupiter_house in [1, 5, 9]:  # Trikonas
        impact["effect"] = "highly_positive"
        impact["score"] = 9
        impact["description"] = "Jupiter in trine - Guru's blessings, wisdom, and fortune"
    elif jupiter_house in [4, 7, 10]:  # Kendras
        impact["effect"] = "positive"
        impact["score"] = 7
        impact["description"] = "Jupiter in kendra - favorable and supportive"
    elif jupiter_house in [6, 8, 12]:  # Dusthanas
        impact["effect"] = "moderate"
        impact["score"] = 4
        impact["description"] = "Jupiter in dusthana - reduced benefits"
    
    return impact


def evaluate_venus_transit_impact(venus_transit: Dict, natal_chart: Dict, dasha: Dict) -> Dict:
    """
    Phase 20: Evaluate Venus transit impact on love and comfort.
    
    Args:
        venus_transit: Venus transit data
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Impact dictionary
    """
    impact = {
        "area": "love_relationships",
        "effect": "positive",
        "description": "",
        "score": 6
    }
    
    venus_house = venus_transit.get("house_from_lagna", 0)
    
    if venus_house in [1, 4, 5, 7, 9]:  # Favorable
        impact["effect"] = "highly_positive"
        impact["score"] = 8
        impact["description"] = "Venus in favorable houses - love, relationships, and comfort"
    elif venus_house in [6, 8, 12]:  # Challenging
        impact["effect"] = "moderate"
        impact["score"] = 4
        impact["description"] = "Venus in dusthana - relationship challenges"
    
    return impact


def evaluate_saturn_transit_impact(saturn_transit: Dict, natal_chart: Dict, dasha: Dict) -> Dict:
    """
    Phase 20: Evaluate Saturn transit impact on pressure and long-term lessons.
    
    Args:
        saturn_transit: Saturn transit data
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Impact dictionary
    """
    impact = {
        "area": "discipline_karma",
        "effect": "challenging",
        "description": "",
        "score": 4
    }
    
    saturn_house = saturn_transit.get("house_from_lagna", 0)
    
    if saturn_house in [1, 5, 9]:  # Trikonas
        impact["effect"] = "moderate"
        impact["score"] = 5
        impact["description"] = "Saturn in trine - some positive effects with discipline"
    elif saturn_house in [6, 8, 12]:  # Dusthanas
        impact["effect"] = "challenging"
        impact["score"] = 2
        impact["description"] = "Saturn in dusthana - pressure, delays, and obstacles"
    elif saturn_house == 10:  # Career
        impact["effect"] = "moderate"
        impact["score"] = 5
        impact["description"] = "Saturn in 10th - hard work required for career"
    
    return impact


def evaluate_rahu_ketu_transit_impact(rahu_transit: Dict, ketu_transit: Dict, natal_chart: Dict, dasha: Dict) -> Dict:
    """
    Phase 20: Evaluate Rahu/Ketu transit impact on confusion and breakthroughs.
    
    Args:
        rahu_transit: Rahu transit data
        ketu_transit: Ketu transit data
        natal_chart: Birth chart
        dasha: Dasha data
    
    Returns:
        Impact dictionary
    """
    impact = {
        "area": "material_spiritual",
        "effect": "mixed",
        "description": "",
        "score": 5
    }
    
    rahu_house = rahu_transit.get("house_from_lagna", 0) if rahu_transit else 0
    ketu_house = ketu_transit.get("house_from_lagna", 0) if ketu_transit else 0
    
    if rahu_house in [3, 6, 11]:  # Upachaya
        impact["effect"] = "positive"
        impact["score"] = 6
        impact["description"] = "Rahu in upachaya - material gains and ambitions"
    elif rahu_house in [6, 8, 12]:  # Dusthanas
        impact["effect"] = "challenging"
        impact["score"] = 3
        impact["description"] = "Rahu in dusthana - confusion and illusions"
    
    if ketu_house in [9, 12]:  # Spiritual houses
        impact["description"] += "; Ketu in spiritual houses - spiritual growth"
        impact["score"] += 1
    
    return impact

