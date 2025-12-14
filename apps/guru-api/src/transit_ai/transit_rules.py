"""
Phase 19: Transit Rules Engine

Encodes classical gochara (transit) rules and evaluates them.
"""

from typing import Dict, List, Tuple


def evaluate_planet_transit(planet: str, transit_position: Dict, natal_chart: Dict, dasha_context: Dict) -> Dict:
    """
    Phase 19: Evaluate a planet's transit.
    
    Args:
        planet: Planet name
        transit_position: Transit position data
        natal_chart: Natal chart
        dasha_context: Current Dasha context
    
    Returns:
        Dictionary with score, tags, and notes
    """
    score = 0
    tags = []
    notes = []
    
    house_from_lagna = transit_position.get("house_from_lagna", 0)
    house_from_moon = transit_position.get("house_from_moon", 0)
    
    # Benefic planets
    benefics = ["Jupiter", "Venus", "Mercury"]
    malefics = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]
    
    # House classifications
    trikonas = [1, 5, 9]  # Trines - highly auspicious
    kendras = [4, 7, 10]  # Angles - important
    dusthanas = [6, 8, 12]  # Inauspicious houses
    upachayas = [3, 6, 10, 11]  # Growth houses
    
    # Benefic planet rules
    if planet in benefics:
        if house_from_lagna in trikonas or house_from_moon in trikonas:
            score += 8
            tags.append("highly_auspicious")
            notes.append(f"{planet} in trine house - excellent results")
        
        if house_from_lagna in kendras or house_from_moon in kendras:
            score += 5
            tags.append("auspicious")
            notes.append(f"{planet} in kendra - favorable")
        
        if house_from_lagna in dusthanas or house_from_moon in dusthanas:
            score -= 3
            tags.append("challenging")
            notes.append(f"{planet} in dusthana - reduced benefits")
    
    # Malefic planet rules
    elif planet in malefics:
        if house_from_lagna in dusthanas or house_from_moon in dusthanas:
            score -= 6
            tags.append("challenging")
            notes.append(f"{planet} in dusthana - obstacles and challenges")
        
        if house_from_lagna in trikonas or house_from_moon in trikonas:
            score += 2
            tags.append("moderate")
            notes.append(f"{planet} in trine - some positive effects")
        
        if house_from_lagna in kendras or house_from_moon in kendras:
            score -= 2
            tags.append("mixed")
            notes.append(f"{planet} in kendra - mixed results")
    
    # Specific planet rules
    if planet == "Jupiter":
        if house_from_lagna in trikonas or house_from_moon in trikonas:
            score += 3
            tags.append("guru_blessings")
            notes.append("Jupiter in trine - Guru's blessings")
    
    elif planet == "Saturn":
        if house_from_lagna == 8 or house_from_moon == 8:
            score -= 5
            tags.append("ashtama_shani")
            notes.append("Saturn in 8th - Ashtama Shani, mental pressure")
        
        if house_from_lagna in [12, 1, 2] or house_from_moon in [12, 1, 2]:
            score -= 4
            tags.append("sade_sati")
            notes.append("Saturn in Sade Sati - 7.5 years of challenges")
    
    elif planet == "Mars":
        if house_from_lagna in [3, 6, 11] or house_from_moon in [3, 6, 11]:
            score += 4
            tags.append("mars_energy")
            notes.append("Mars in 3/6/11 - courage, energy, gains")
        
        if house_from_lagna in [1, 7, 8, 12] or house_from_moon in [1, 7, 8, 12]:
            score -= 3
            tags.append("mars_conflict")
            notes.append("Mars in challenging houses - conflicts possible")
    
    elif planet == "Venus":
        if house_from_lagna in [1, 4, 5, 7, 9] or house_from_moon in [1, 4, 5, 7, 9]:
            score += 5
            tags.append("venus_benefits")
            notes.append("Venus in favorable houses - love, comfort, prosperity")
    
    elif planet == "Mercury":
        if house_from_lagna in [1, 4, 5, 9] or house_from_moon in [1, 4, 5, 9]:
            score += 3
            tags.append("mercury_intellect")
            notes.append("Mercury in favorable houses - communication, intellect")
    
    # Check if planet is aspecting natal Moon or Lagna
    natal_moon_house = natal_chart.get("Planets", {}).get("Moon", {}).get("house", 0)
    if house_from_moon == 1:
        score += 2
        tags.append("moon_transit")
        notes.append(f"{planet} transiting natal Moon - high emotional impact")
    
    # Dasha influence
    dasha_lord = dasha_context.get("mahadasha", "Unknown")
    if planet == dasha_lord:
        score += 3
        tags.append("dasha_lord_transit")
        notes.append(f"{planet} is Dasha lord - enhanced effects")
    
    # Clamp score to -10 to +10
    score = max(-10, min(10, score))
    
    return {
        "score": score,
        "tags": tags,
        "notes": notes,
        "overall_effect": "highly_positive" if score >= 7 else "positive" if score >= 3 else "neutral" if score >= -2 else "challenging" if score >= -5 else "highly_challenging"
    }


def evaluate_house_transit(house_number: int, transiting_planets: List[str], natal_chart: Dict) -> Dict:
    """
    Phase 19: Evaluate transit effects on a specific house.
    
    Args:
        house_number: House number (1-12)
        transiting_planets: List of planets transiting this house
        natal_chart: Natal chart
    
    Returns:
        Dictionary with score and notes
    """
    score = 0
    notes = []
    
    if not transiting_planets:
        return {"score": 0, "notes": ["No planets transiting this house"]}
    
    benefics = ["Jupiter", "Venus", "Mercury"]
    malefics = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]
    
    benefic_count = sum(1 for p in transiting_planets if p in benefics)
    malefic_count = sum(1 for p in transiting_planets if p in malefics)
    
    # House-specific significations
    house_meanings = {
        1: "Self, personality",
        2: "Wealth, family",
        3: "Siblings, courage",
        4: "Mother, home",
        5: "Children, education",
        6: "Health, enemies",
        7: "Marriage, partnerships",
        8: "Longevity, transformation",
        9: "Father, fortune",
        10: "Career, profession",
        11: "Gains, income",
        12: "Losses, spirituality"
    }
    
    house_meaning = house_meanings.get(house_number, "General life area")
    
    if benefic_count > malefic_count:
        score += 3
        notes.append(f"Benefic planets ({benefic_count}) transiting {house_number}th house ({house_meaning}) - favorable")
    elif malefic_count > benefic_count:
        score -= 3
        notes.append(f"Malefic planets ({malefic_count}) transiting {house_number}th house ({house_meaning}) - challenging")
    else:
        score += 0
        notes.append(f"Mixed planets transiting {house_number}th house ({house_meaning}) - balanced")
    
    # Specific house rules
    if house_number == 10:  # Career
        if "Jupiter" in transiting_planets:
            score += 2
            notes.append("Jupiter in 10th - career growth and recognition")
        if "Saturn" in transiting_planets:
            score -= 1
            notes.append("Saturn in 10th - hard work required, delays possible")
    
    elif house_number == 7:  # Marriage
        if "Venus" in transiting_planets:
            score += 3
            notes.append("Venus in 7th - relationship harmony")
        if "Mars" in transiting_planets:
            score -= 2
            notes.append("Mars in 7th - relationship conflicts possible")
    
    elif house_number == 11:  # Gains
        if "Jupiter" in transiting_planets or "Venus" in transiting_planets:
            score += 4
            notes.append("Benefic in 11th - financial gains")
    
    elif house_number == 6:  # Health
        if "Mars" in transiting_planets:
            score += 2
            notes.append("Mars in 6th - strong immunity, but be careful of injuries")
        if "Saturn" in transiting_planets:
            score -= 2
            notes.append("Saturn in 6th - health concerns, regular checkups needed")
    
    return {
        "score": max(-10, min(10, score)),
        "notes": notes,
        "transiting_planets": transiting_planets,
        "house_meaning": house_meaning
    }


def detect_special_conditions(transit_context: Dict) -> List[Dict]:
    """
    Phase 19: Detect special transit conditions.
    
    Args:
        transit_context: Complete transit context
    
    Returns:
        List of special conditions/events
    """
    events = []
    
    # Saturn specials
    saturn_specials = transit_context.get("saturn_specials", {})
    if saturn_specials.get("sade_sati"):
        events.append({
            "type": "sade_sati",
            "severity": "high",
            "description": "Saturn in Sade Sati (12th, 1st, or 2nd from Moon) - 7.5 years of challenges",
            "advice": "Be patient, practice discipline, avoid hasty decisions"
        })
    
    if saturn_specials.get("ashtama_shani"):
        events.append({
            "type": "ashtama_shani",
            "severity": "high",
            "description": "Saturn in 8th from Moon - Ashtama Shani, mental pressure and obstacles",
            "advice": "Stay calm, avoid conflicts, focus on inner strength"
        })
    
    # Jupiter specials
    jupiter_specials = transit_context.get("jupiter_specials", {})
    if jupiter_specials.get("is_trikona"):
        events.append({
            "type": "guru_blessings",
            "severity": "low",  # Low = good
            "description": "Jupiter in trine house - Guru's blessings and wisdom",
            "advice": "Excellent time for learning, teaching, and spiritual growth"
        })
    
    # Moon specials
    moon_specials = transit_context.get("moon_specials", {})
    moon_house = moon_specials.get("house_from_natal_moon", 0)
    
    if moon_house == 8:
        events.append({
            "type": "moon_8th",
            "severity": "medium",
            "description": "Moon transiting 8th from natal Moon - emotional sensitivity",
            "advice": "Take care of emotional health, avoid stress"
        })
    
    # Check for planet conjunctions
    current_transits = transit_context.get("current_transits", {})
    moon_deg = current_transits.get("Moon", {}).get("degree", 0)
    
    for planet_name, planet_data in current_transits.items():
        if planet_name == "Moon":
            continue
        
        planet_deg = planet_data.get("degree", 0)
        distance = abs(moon_deg - planet_deg)
        if distance > 180:
            distance = 360 - distance
        
        if distance < 5:  # Conjunction within 5 degrees
            if planet_name in ["Rahu", "Ketu"]:
                events.append({
                    "type": "moon_conjunction",
                    "severity": "medium",
                    "description": f"Moon conjunct {planet_name} - emotional confusion",
                    "advice": "Stay clear-headed, avoid illusions"
                })
            elif planet_name == "Mars":
                events.append({
                    "type": "moon_conjunction",
                    "severity": "medium",
                    "description": "Moon conjunct Mars - emotional intensity, anger possible",
                    "advice": "Control emotions, avoid conflicts"
                })
    
    return events

