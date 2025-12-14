"""
Phase 20: Life Path Engine

Combines all karma analysis to produce complete life path report.
"""

from typing import Dict
from src.karma.karma_indicators import (
    analyze_atmakaraka, analyze_amatyakaraka, analyze_karmesha,
    analyze_bhagya, analyze_moon_psychology, analyze_lagna_lord,
    analyze_nodes_karma, analyze_past_life_indicators
)
from src.karma.soul_purpose_engine import identify_life_lessons
from src.karma.strengths_weaknesses import extract_top_strengths, extract_top_weaknesses, convert_to_human_language


def generate_karma_report(birth_details: Dict) -> Dict:
    """
    Phase 20: Generate complete karma and life path report.
    
    Args:
        birth_details: Birth details dictionary
    
    Returns:
        Complete karma report
    """
    # Build birth chart
    from datetime import datetime
    import swisseph as swe
    from src.jyotish.kundli_engine import generate_kundli
    
    birth_date = birth_details.get("birth_date")
    birth_time = birth_details.get("birth_time")
    birth_lat = birth_details.get("birth_latitude")
    birth_lon = birth_details.get("birth_longitude")
    
    if isinstance(birth_date, str):
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
    else:
        birth_date_obj = birth_date if hasattr(birth_date, 'year') else datetime.strptime(str(birth_date), "%Y-%m-%d").date()
    
    hour, minute = map(int, birth_time.split(':'))
    birth_dt = datetime.combine(birth_date_obj, datetime.min.time().replace(hour=hour, minute=minute, second=0, microsecond=0))
    
    birth_jd = swe.julday(
        birth_dt.year, birth_dt.month, birth_dt.day,
        birth_dt.hour + birth_dt.minute / 60.0,
        swe.GREG_CAL
    )
    
    kundli = generate_kundli(birth_jd, birth_lat, birth_lon)
    
    # Analyze all karma indicators
    atmakaraka = analyze_atmakaraka(kundli)
    amatyakaraka = analyze_amatyakaraka(kundli)
    karmesha = analyze_karmesha(kundli)
    bhagya = analyze_bhagya(kundli)
    moon_psychology = analyze_moon_psychology(kundli)
    lagna_lord = analyze_lagna_lord(kundli)
    nodes_karma = analyze_nodes_karma(kundli)
    past_life = analyze_past_life_indicators(kundli)
    
    # Identify life lessons
    life_lessons = identify_life_lessons(kundli)
    
    # Extract strengths and weaknesses
    strengths = extract_top_strengths(kundli)
    weaknesses = extract_top_weaknesses(kundli)
    human_summary = convert_to_human_language(strengths, weaknesses)
    
    # Generate core personality
    core_personality = generate_core_personality(lagna_lord, moon_psychology, atmakaraka)
    
    # Generate soul purpose
    soul_purpose = generate_soul_purpose(atmakaraka, nodes_karma, past_life)
    
    # Generate karma lessons summary
    karma_lessons = [lesson.get("description", "") for lesson in life_lessons]
    
    # Generate spiritual direction
    spiritual_direction = generate_spiritual_direction(nodes_karma, past_life, bhagya)
    
    # Generate hidden gifts
    hidden_gifts = [lesson.get("description", "") for lesson in life_lessons if lesson.get("type") == "hidden_gifts"]
    
    # Generate growth advice
    growth_advice = generate_growth_advice(strengths, weaknesses, life_lessons)
    
    return {
        "core_personality": core_personality,
        "soul_purpose": soul_purpose,
        "karma_lessons": karma_lessons,
        "spiritual_direction": spiritual_direction,
        "hidden_gifts": hidden_gifts,
        "growth_advice": growth_advice,
        "strengths": [s.get("title", "") for s in strengths],
        "weaknesses": [w.get("title", "") for w in weaknesses],
        "detailed_strengths": strengths,
        "detailed_weaknesses": weaknesses,
        "human_summary": human_summary,
        "karma_indicators": {
            "atmakaraka": atmakaraka,
            "amatyakaraka": amatyakaraka,
            "karmesha": karmesha,
            "bhagya": bhagya,
            "moon_psychology": moon_psychology,
            "lagna_lord": lagna_lord,
            "nodes_karma": nodes_karma,
            "past_life": past_life
        },
        "life_lessons": life_lessons
    }


def generate_core_personality(lagna_lord: Dict, moon_psychology: Dict, atmakaraka: Dict) -> str:
    """
    Phase 20: Generate core personality description.
    
    Args:
        lagna_lord: Lagna lord analysis
        moon_psychology: Moon psychology analysis
        atmakaraka: Atmakaraka analysis
    
    Returns:
        Core personality text
    """
    lagna_sign = lagna_lord.get("sign", "Unknown")
    moon_sign = moon_psychology.get("sign", "Unknown")
    atmakaraka_planet = atmakaraka.get("planet", "Unknown")
    
    personality = f"Your core personality is shaped by {lagna_sign} Lagna, {moon_sign} Moon, and {atmakaraka_planet} as your soul indicator. "
    personality += f"This combination creates a unique blend of {lagna_sign} traits (personality) and {moon_sign} emotional nature, "
    personality += f"guided by the soul purpose indicated by {atmakaraka_planet}."
    
    return personality


def generate_soul_purpose(atmakaraka: Dict, nodes_karma: Dict, past_life: Dict) -> str:
    """
    Phase 20: Generate soul purpose description.
    
    Args:
        atmakaraka: Atmakaraka analysis
        nodes_karma: Nodes karma analysis
        past_life: Past life indicators
    
    Returns:
        Soul purpose text
    """
    atmakaraka_planet = atmakaraka.get("planet", "Unknown")
    atmakaraka_meaning = atmakaraka.get("meaning", "")
    
    ketu_house = nodes_karma.get("ketu", {}).get("house", 0)
    past_life_meaning = past_life.get("meaning", "")
    
    soul_purpose = f"Your soul purpose in this lifetime is indicated by {atmakaraka_planet} (Atmakaraka): {atmakaraka_meaning}. "
    soul_purpose += f"Your past-life karma ({past_life_meaning}) shows that you carry forward spiritual lessons. "
    soul_purpose += f"Ketu in {ketu_house}th house indicates areas where you need to practice detachment and spiritual growth."
    
    return soul_purpose


def generate_spiritual_direction(nodes_karma: Dict, past_life: Dict, bhagya: Dict) -> str:
    """
    Phase 20: Generate spiritual direction.
    
    Args:
        nodes_karma: Nodes karma analysis
        past_life: Past life indicators
        bhagya: Bhagya analysis
    
    Returns:
        Spiritual direction text
    """
    rahu_house = nodes_karma.get("rahu", {}).get("house", 0)
    ketu_house = nodes_karma.get("ketu", {}).get("house", 0)
    bhagya_lord = bhagya.get("lord", "Unknown")
    
    direction = f"Your spiritual direction involves balancing Rahu's material desires (house {rahu_house}) "
    direction += f"with Ketu's spiritual detachment (house {ketu_house}). "
    direction += f"Your fortune (Bhagya) is guided by {bhagya_lord}, indicating that spiritual growth comes through "
    direction += f"fulfilling your dharma and serving others."
    
    return direction


def generate_growth_advice(strengths: list, weaknesses: list, life_lessons: list) -> str:
    """
    Phase 20: Generate growth advice.
    
    Args:
        strengths: List of strengths
        weaknesses: List of weaknesses
        life_lessons: List of life lessons
    
    Returns:
        Growth advice text
    """
    advice = "Growth Guidance:\n\n"
    
    advice += "1. Develop Your Strengths:\n"
    for strength in strengths[:3]:
        advice += f"   • {strength.get('title', 'Strength')}: Focus on developing this area further.\n"
    
    advice += "\n2. Work on Areas for Growth:\n"
    for weakness in weaknesses[:3]:
        advice += f"   • {weakness.get('title', 'Area')}: {weakness.get('remedy', 'Practice patience and discipline')}\n"
    
    advice += "\n3. Life Lessons to Learn:\n"
    for lesson in life_lessons[:3]:
        advice += f"   • {lesson.get('title', 'Lesson')}: {lesson.get('advice', '')}\n"
    
    advice += "\n4. Overall: Use your strengths to overcome challenges. Practice regular spiritual disciplines. "
    advice += "Be patient with yourself and others. Trust the journey and focus on growth."
    
    return advice

