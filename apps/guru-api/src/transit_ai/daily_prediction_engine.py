"""
Phase 19: Daily Prediction Engine

Produces structured daily transit predictions with area-wise guidance.
"""

from typing import Dict, List
from datetime import datetime

from src.transit_ai.transit_context_builder import build_transit_context
from src.transit_ai.transit_rules import evaluate_planet_transit, evaluate_house_transit, detect_special_conditions
from src.interpretation.dasha_interpreter import interpret_mahadasha


def generate_daily_transit_report(birth_details: Dict, on_datetime: datetime, location: Dict) -> Dict:
    """
    Phase 19: Generate complete daily transit report.
    
    Args:
        birth_details: Birth details dictionary
        on_datetime: Date/time for prediction
        location: Location dictionary
    
    Returns:
        Complete daily transit report
    """
    # Build transit context
    transit_context = build_transit_context(birth_details, on_datetime, location)
    
    natal_chart = transit_context.get("natal_chart", {})
    current_transits = transit_context.get("current_transits", {})
    current_dasha = transit_context.get("current_dasha", {})
    special_conditions = detect_special_conditions(transit_context)
    
    # Evaluate area-wise scores
    areas = evaluate_life_areas(transit_context)
    
    # Get overall mood
    overall_mood = calculate_overall_mood(transit_context, areas)
    
    # Get key transits
    key_transits = identify_key_transits(transit_context)
    
    # Get danger flags
    danger_flags = identify_danger_flags(transit_context, special_conditions)
    
    # Get opportunity windows
    opportunity_windows = identify_opportunity_windows(transit_context)
    
    # Get actions for today
    actions = generate_actions(transit_context, areas, special_conditions)
    
    # Generate summary
    summary = generate_summary(transit_context, areas, overall_mood)
    
    return {
        "date": on_datetime.strftime("%Y-%m-%d"),
        "summary": summary,
        "overall_mood": overall_mood,
        "areas": areas,
        "key_transits": key_transits,
        "danger_flags": danger_flags,
        "opportunity_windows": opportunity_windows,
        "actions_today": actions,
        "special_conditions": special_conditions
    }


def evaluate_life_areas(transit_context: Dict) -> Dict:
    """
    Phase 19: Evaluate all life areas based on transits.
    
    Args:
        transit_context: Complete transit context
    
    Returns:
        Dictionary with area-wise scores and guidance
    """
    areas = {}
    current_transits = transit_context.get("current_transits", {})
    natal_chart = transit_context.get("natal_chart", {})
    current_dasha = transit_context.get("current_dasha", {})
    
    # Career (10th house)
    career_planets = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 10]
    career_eval = evaluate_house_transit(10, career_planets, natal_chart)
    areas["career"] = {
        "score": career_eval.get("score", 0),
        "trend": "positive" if career_eval.get("score", 0) > 2 else "stable" if career_eval.get("score", 0) > -2 else "caution",
        "details": " ".join(career_eval.get("notes", [])),
        "advice": generate_area_advice("career", career_eval.get("score", 0), career_planets)
    }
    
    # Money (2nd, 11th houses)
    money_planets_2 = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 2]
    money_planets_11 = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 11]
    money_planets = list(set(money_planets_2 + money_planets_11))
    
    money_score = 0
    if money_planets_11:
        eval_11 = evaluate_house_transit(11, money_planets_11, natal_chart)
        money_score += eval_11.get("score", 0)
    if money_planets_2:
        eval_2 = evaluate_house_transit(2, money_planets_2, natal_chart)
        money_score += eval_2.get("score", 0)
    
    areas["money"] = {
        "score": max(-10, min(10, money_score)),
        "trend": "positive" if money_score > 2 else "stable" if money_score > -2 else "caution",
        "details": f"Transits affecting wealth (2nd) and gains (11th) houses",
        "advice": generate_area_advice("money", money_score, money_planets)
    }
    
    # Love/Relationships (7th house)
    love_planets = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 7]
    love_eval = evaluate_house_transit(7, love_planets, natal_chart)
    areas["love"] = {
        "score": love_eval.get("score", 0),
        "trend": "positive" if love_eval.get("score", 0) > 2 else "stable" if love_eval.get("score", 0) > -2 else "mixed",
        "details": " ".join(love_eval.get("notes", [])),
        "advice": generate_area_advice("love", love_eval.get("score", 0), love_planets)
    }
    
    # Family (4th house)
    family_planets = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 4]
    family_eval = evaluate_house_transit(4, family_planets, natal_chart)
    areas["family"] = {
        "score": family_eval.get("score", 0),
        "trend": "positive" if family_eval.get("score", 0) > 2 else "stable" if family_eval.get("score", 0) > -2 else "caution",
        "details": " ".join(family_eval.get("notes", [])),
        "advice": generate_area_advice("family", family_eval.get("score", 0), family_planets)
    }
    
    # Health (6th house, 1st house)
    health_planets_6 = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 6]
    health_planets_1 = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 1]
    health_planets = list(set(health_planets_6 + health_planets_1))
    
    health_score = 0
    if health_planets_6:
        eval_6 = evaluate_house_transit(6, health_planets_6, natal_chart)
        health_score += eval_6.get("score", 0)
    if health_planets_1:
        eval_1 = evaluate_house_transit(1, health_planets_1, natal_chart)
        health_score += eval_1.get("score", 0)
    
    areas["health"] = {
        "score": max(-10, min(10, health_score)),
        "trend": "positive" if health_score > 2 else "stable" if health_score > -2 else "caution",
        "details": f"Transits affecting health (6th) and self (1st) houses",
        "advice": generate_area_advice("health", health_score, health_planets)
    }
    
    # Travel (3rd, 9th houses)
    travel_planets_3 = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 3]
    travel_planets_9 = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 9]
    travel_planets = list(set(travel_planets_3 + travel_planets_9))
    
    travel_score = 0
    if travel_planets_3:
        eval_3 = evaluate_house_transit(3, travel_planets_3, natal_chart)
        travel_score += eval_3.get("score", 0)
    if travel_planets_9:
        eval_9 = evaluate_house_transit(9, travel_planets_9, natal_chart)
        travel_score += eval_9.get("score", 0)
    
    areas["travel"] = {
        "score": max(-10, min(10, travel_score)),
        "trend": "good" if travel_score > 2 else "stable" if travel_score > -2 else "caution",
        "details": f"Transits affecting short journeys (3rd) and long journeys (9th)",
        "advice": generate_area_advice("travel", travel_score, travel_planets)
    }
    
    # Spiritual (9th, 12th houses)
    spiritual_planets_9 = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 9]
    spiritual_planets_12 = [p for p, data in current_transits.items() if data.get("house_from_lagna") == 12]
    spiritual_planets = list(set(spiritual_planets_9 + spiritual_planets_12))
    
    spiritual_score = 0
    if spiritual_planets_9:
        eval_9 = evaluate_house_transit(9, spiritual_planets_9, natal_chart)
        spiritual_score += eval_9.get("score", 0)
    if spiritual_planets_12:
        eval_12 = evaluate_house_transit(12, spiritual_planets_12, natal_chart)
        spiritual_score += eval_12.get("score", 0)
    
    # Jupiter in 9th or 12th is highly spiritual
    if "Jupiter" in spiritual_planets:
        spiritual_score += 3
    
    areas["spiritual"] = {
        "score": max(-10, min(10, spiritual_score)),
        "trend": "strong" if spiritual_score > 3 else "moderate" if spiritual_score > 0 else "low",
        "details": f"Transits affecting dharma (9th) and moksha (12th) houses",
        "advice": generate_area_advice("spiritual", spiritual_score, spiritual_planets)
    }
    
    return areas


def calculate_overall_mood(transit_context: Dict, areas: Dict) -> Dict:
    """
    Phase 19: Calculate overall mood/energy for the day.
    
    Args:
        transit_context: Transit context
        areas: Area-wise evaluations
    
    Returns:
        Overall mood dictionary
    """
    # Average area scores
    area_scores = [a.get("score", 0) for a in areas.values()]
    avg_score = sum(area_scores) / len(area_scores) if area_scores else 0
    
    # Normalize to 0-10
    mood_score = int((avg_score + 10) / 2)
    
    # Check Moon position
    moon_specials = transit_context.get("moon_specials", {})
    moon_house = moon_specials.get("house_from_natal_moon", 0)
    
    mood_texts = {
        (8, 10): "Very optimistic, emotionally open, excellent day",
        (6, 8): "Positive, balanced, good day ahead",
        (4, 6): "Moderate, stable, normal day",
        (2, 4): "Cautious, some challenges, stay alert",
        (0, 2): "Challenging, emotional sensitivity, patience needed"
    }
    
    mood_text = "Moderate day with mixed energies"
    for (low, high), text in mood_texts.items():
        if low <= mood_score <= high:
            mood_text = text
            break
    
    # Adjust based on Moon
    if moon_house == 8:
        mood_text += ". Moon in 8th - emotional sensitivity today."
    elif moon_house in [1, 5, 9]:
        mood_text += ". Moon in trine - favorable emotional state."
    
    return {
        "score": mood_score,
        "text": mood_text
    }


def identify_key_transits(transit_context: Dict) -> List[Dict]:
    """
    Phase 19: Identify key transits affecting the day.
    
    Args:
        transit_context: Transit context
    
    Returns:
        List of key transit descriptions
    """
    key_transits = []
    current_transits = transit_context.get("current_transits", {})
    natal_chart = transit_context.get("natal_chart", {})
    current_dasha = transit_context.get("current_dasha", {})
    
    # Check important planets
    important_planets = ["Jupiter", "Saturn", "Mars", "Venus", "Moon"]
    
    for planet_name in important_planets:
        if planet_name not in current_transits:
            continue
        
        transit_data = current_transits[planet_name]
        house_lagna = transit_data.get("house_from_lagna", 0)
        house_moon = transit_data.get("house_from_moon", 0)
        
        # Evaluate transit
        eval_result = evaluate_planet_transit(planet_name, transit_data, natal_chart, current_dasha)
        
        if abs(eval_result.get("score", 0)) >= 3:  # Significant transit
            description = f"{planet_name} transiting {house_lagna}th house from Lagna"
            if house_moon != house_lagna:
                description += f" and {house_moon}th house from Moon"
            
            effect = eval_result.get("overall_effect", "moderate")
            key_transits.append({
                "planet": planet_name,
                "description": description,
                "effect": effect,
                "score": eval_result.get("score", 0),
                "notes": eval_result.get("notes", [])
            })
    
    return key_transits[:5]  # Top 5


def identify_danger_flags(transit_context: Dict, special_conditions: List[Dict]) -> List[Dict]:
    """
    Phase 19: Identify danger flags and cautions.
    
    Args:
        transit_context: Transit context
        special_conditions: Special conditions detected
    
    Returns:
        List of danger flags
    """
    flags = []
    
    # Check special conditions
    for condition in special_conditions:
        if condition.get("severity") in ["high", "medium"]:
            flags.append({
                "type": condition.get("type", "general"),
                "description": condition.get("description", ""),
                "advice": condition.get("advice", "")
            })
    
    # Check for malefic transits in dusthanas
    current_transits = transit_context.get("current_transits", {})
    malefics = ["Saturn", "Mars", "Rahu", "Ketu"]
    dusthanas = [6, 8, 12]
    
    for planet_name in malefics:
        if planet_name not in current_transits:
            continue
        
        house = current_transits[planet_name].get("house_from_lagna", 0)
        if house in dusthanas:
            flags.append({
                "type": "transit_challenge",
                "description": f"{planet_name} in {house}th house (dusthana) - challenges in related area",
                "advice": "Be patient, avoid hasty decisions, practice remedies"
            })
    
    # Check for conflicts
    current_transits = transit_context.get("current_transits", {})
    if "Mars" in current_transits:
        mars_house = current_transits["Mars"].get("house_from_lagna", 0)
        if mars_house in [1, 7]:
            flags.append({
                "type": "conflict",
                "description": "Mars in 1st or 7th - conflicts with self or partners possible",
                "advice": "Avoid arguments, control anger, practice patience"
            })
    
    return flags[:5]  # Top 5


def identify_opportunity_windows(transit_context: Dict) -> List[Dict]:
    """
    Phase 19: Identify opportunity time windows.
    
    Args:
        transit_context: Transit context
    
    Returns:
        List of opportunity windows
    """
    windows = []
    current_transits = transit_context.get("current_transits", {})
    moon_specials = transit_context.get("moon_specials", {})
    
    # Morning opportunities
    if "Jupiter" in current_transits or "Venus" in current_transits:
        windows.append({
            "time_window": "morning",
            "description": "Benefic planets active - good for communication, meetings, and important decisions"
        })
    
    # Afternoon opportunities
    if current_transits.get("Sun", {}).get("house_from_lagna", 0) in [1, 10]:
        windows.append({
            "time_window": "afternoon",
            "description": "Sun in favorable position - good for career matters and authority interactions"
        })
    
    # Evening opportunities
    if moon_specials.get("nakshatra") in ["Rohini", "Pushya", "Shravana"]:
        windows.append({
            "time_window": "evening",
            "description": "Auspicious Nakshatra - good for spiritual practice, meditation, and reflection"
        })
    
    # Default if none
    if not windows:
        windows.append({
            "time_window": "morning",
            "description": "Start day with positive intentions and clear goals"
        })
    
    return windows


def generate_actions(transit_context: Dict, areas: Dict, special_conditions: List[Dict]) -> Dict:
    """
    Phase 19: Generate actionable do's and don'ts.
    
    Args:
        transit_context: Transit context
        areas: Area evaluations
        special_conditions: Special conditions
    
    Returns:
        Actions dictionary
    """
    do_list = []
    avoid_list = []
    
    # Based on area scores
    for area_name, area_data in areas.items():
        score = area_data.get("score", 0)
        trend = area_data.get("trend", "stable")
        
        if trend == "positive" and score > 3:
            do_list.append(f"Focus on {area_name} matters - favorable time for progress")
        elif trend == "caution" and score < -2:
            avoid_list.append(f"Avoid major decisions in {area_name} - challenges indicated")
    
    # Based on special conditions
    for condition in special_conditions:
        if condition.get("severity") == "high":
            avoid_list.append(condition.get("advice", ""))
    
    # Based on transits
    current_transits = transit_context.get("current_transits", {})
    if "Jupiter" in current_transits:
        jupiter_house = current_transits["Jupiter"].get("house_from_lagna", 0)
        if jupiter_house in [1, 5, 9]:
            do_list.append("Seek guidance from elders or teachers - Jupiter's blessings available")
    
    if "Saturn" in current_transits:
        saturn_specials = transit_context.get("saturn_specials", {})
        if saturn_specials.get("sade_sati") or saturn_specials.get("ashtama_shani"):
            do_list.append("Practice patience and discipline - Saturn's lessons active")
            avoid_list.append("Avoid hasty decisions or conflicts - patience required")
    
    # Default actions if lists are empty
    if not do_list:
        do_list.append("Maintain positive attitude and focus on daily duties")
    
    if not avoid_list:
        avoid_list.append("Avoid unnecessary stress and overthinking")
    
    return {
        "do": do_list[:5],  # Top 5
        "avoid": avoid_list[:5]  # Top 5
    }


def generate_summary(transit_context: Dict, areas: Dict, overall_mood: Dict) -> str:
    """
    Phase 19: Generate overall summary.
    
    Args:
        transit_context: Transit context
        areas: Area evaluations
        overall_mood: Overall mood
    
    Returns:
        Summary text
    """
    mood_score = overall_mood.get("score", 5)
    
    # Count positive and negative areas
    positive_areas = sum(1 for a in areas.values() if a.get("score", 0) > 2)
    negative_areas = sum(1 for a in areas.values() if a.get("score", 0) < -2)
    
    if mood_score >= 7 and positive_areas >= 3:
        return f"Overall excellent day with {positive_areas} areas showing positive trends. Good time for important activities and decisions."
    elif mood_score >= 5:
        return f"Overall good day with balanced energies. {positive_areas} areas favorable, proceed with confidence."
    elif mood_score >= 3:
        return f"Overall moderate day with mixed energies. Some areas favorable, some need caution. Stay balanced."
    else:
        return f"Overall challenging day with {negative_areas} areas showing difficulties. Patience and caution recommended. Focus on remedies and inner strength."


def generate_area_advice(area: str, score: int, planets: List[str]) -> str:
    """
    Phase 19: Generate advice for a specific area.
    
    Args:
        area: Area name
        score: Area score
        planets: Transiting planets
    
    Returns:
        Advice text
    """
    if score > 3:
        if area == "career":
            return "Excellent time for career matters. Plan important meetings, seek promotions, and make strategic decisions."
        elif area == "money":
            return "Favorable for financial matters. Good time for investments, business deals, and wealth-building activities."
        elif area == "love":
            return "Harmonious time for relationships. Express feelings, spend quality time, and strengthen bonds."
        elif area == "spiritual":
            return "Strong spiritual energy. Excellent for meditation, prayers, and spiritual practices."
        else:
            return f"Favorable time for {area} matters. Proceed with confidence."
    
    elif score < -2:
        if area == "health":
            return "Take extra care of health. Regular checkups, proper rest, and avoid stress."
        elif area == "career":
            return "Challenges in career matters. Avoid major decisions, be patient, and focus on completing pending tasks."
        else:
            return f"Challenges in {area} matters. Be patient, avoid hasty decisions, and practice remedies."
    
    else:
        return f"Stable time for {area} matters. Maintain current approach and stay balanced."

