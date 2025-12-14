"""
Phase 20: Soul Purpose Engine

Identifies life lessons and soul purpose.
"""

from typing import Dict, List
from src.karma.karma_indicators import (
    analyze_atmakaraka, analyze_amatyakaraka, analyze_karmesha,
    analyze_bhagya, analyze_moon_psychology, analyze_lagna_lord,
    analyze_nodes_karma, analyze_past_life_indicators
)


def identify_life_lessons(kundli: Dict) -> List[Dict]:
    """
    Phase 20: Identify life lessons from the chart.
    
    Args:
        kundli: Birth chart
    
    Returns:
        List of life lessons
    """
    lessons = []
    
    # Relationship karma
    relationship_karma = analyze_relationship_karma(kundli)
    if relationship_karma:
        lessons.append(relationship_karma)
    
    # Work karma
    work_karma = analyze_work_karma(kundli)
    if work_karma:
        lessons.append(work_karma)
    
    # Emotional karma
    emotional_karma = analyze_emotional_karma(kundli)
    if emotional_karma:
        lessons.append(emotional_karma)
    
    # Family karma
    family_karma = analyze_family_karma(kundli)
    if family_karma:
        lessons.append(family_karma)
    
    # Spiritual mission
    spiritual_mission = analyze_spiritual_mission(kundli)
    if spiritual_mission:
        lessons.append(spiritual_mission)
    
    # Hidden gifts
    hidden_gifts = identify_hidden_gifts(kundli)
    if hidden_gifts:
        lessons.append(hidden_gifts)
    
    return lessons


def analyze_relationship_karma(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze relationship karma.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Relationship karma analysis
    """
    houses = kundli.get("Houses", [])
    house_7 = next((h for h in houses if h.get("house") == 7), {})
    house_7_lord = house_7.get("lord", "Unknown")
    
    planets = kundli.get("Planets", {})
    venus = planets.get("Venus", {})
    venus_house = venus.get("house", 0)
    
    # Analyze nodes in relationship houses
    rahu = planets.get("Rahu", {})
    ketu = planets.get("Ketu", {})
    rahu_house = rahu.get("house", 0)
    ketu_house = ketu.get("house", 0)
    
    relationship_theme = "Relationship karma: "
    
    if venus_house == 7:
        theme = "Strong relationship focus - learn balance and partnership"
    elif venus_house in [6, 8, 12]:
        theme = "Relationship challenges - learn to overcome obstacles and grow"
    else:
        theme = "Moderate relationship karma - learn to give and receive love"
    
    if rahu_house == 7:
        theme += ". Rahu in 7th indicates karmic relationships and material desires in partnerships."
    if ketu_house == 7:
        theme += ". Ketu in 7th indicates past-life relationship karma and spiritual partnerships."
    
    return {
        "type": "relationship_karma",
        "title": "Relationship Karma",
        "description": theme,
        "advice": "Focus on understanding your partner's needs, practice compassion, and learn to balance independence with togetherness."
    }


def analyze_work_karma(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze work karma.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Work karma analysis
    """
    karmesha = analyze_karmesha(kundli)
    amatyakaraka = analyze_amatyakaraka(kundli)
    
    work_theme = f"Work karma: Your career path is influenced by {karmesha.get('lord', 'Unknown')} (10th lord) and {amatyakaraka.get('planet', 'Unknown')} (Amatyakaraka). "
    
    houses = kundli.get("Houses", [])
    house_10 = next((h for h in houses if h.get("house") == 10), {})
    planets_in_10 = [p for p, data in kundli.get("Planets", {}).items() if data.get("house") == 10]
    
    if planets_in_10:
        work_theme += f"Planets in 10th house ({', '.join(planets_in_10)}) indicate strong career focus."
    
    work_theme += " Learn to balance ambition with service, and use your skills for the greater good."
    
    return {
        "type": "work_karma",
        "title": "Work Karma",
        "description": work_theme,
        "advice": "Focus on developing your professional skills, serve others through your work, and maintain integrity in all professional matters."
    }


def analyze_emotional_karma(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze emotional karma.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Emotional karma analysis
    """
    moon_psychology = analyze_moon_psychology(kundli)
    
    moon_sign = moon_psychology.get("sign", "Unknown")
    moon_house = moon_psychology.get("house", 0)
    
    emotional_theme = f"Emotional karma: Your Moon in {moon_sign} (house {moon_house}) shapes your emotional nature. "
    
    if moon_house in [6, 8, 12]:
        emotional_theme += "Challenges in emotional expression - learn to process and release emotions healthily."
    elif moon_house in [1, 4, 5, 9]:
        emotional_theme += "Strong emotional intelligence - use your sensitivity to help others."
    else:
        emotional_theme += "Balanced emotional nature - learn to trust your intuition."
    
    return {
        "type": "emotional_karma",
        "title": "Emotional Karma",
        "description": emotional_theme,
        "advice": "Practice emotional awareness, meditation, and self-care. Learn to balance your emotional needs with practical responsibilities."
    }


def analyze_family_karma(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze family karma.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Family karma analysis
    """
    houses = kundli.get("Houses", [])
    house_4 = next((h for h in houses if h.get("house") == 4), {})
    house_4_lord = house_4.get("lord", "Unknown")
    
    planets = kundli.get("Planets", {})
    moon = planets.get("Moon", {})
    sun = planets.get("Sun", {})
    
    moon_house = moon.get("house", 0)
    sun_house = sun.get("house", 0)
    
    family_theme = f"Family karma: 4th house lord is {house_4_lord}. "
    
    if moon_house == 4:
        family_theme += "Strong connection with mother and home - learn to create emotional security."
    if sun_house == 4:
        family_theme += "Father's influence is significant - learn to balance authority with love."
    
    family_theme += " Family relationships teach you about emotional security, roots, and nurturing."
    
    return {
        "type": "family_karma",
        "title": "Family Karma",
        "description": family_theme,
        "advice": "Honor your family traditions while creating your own path. Learn to give and receive love within family relationships."
    }


def analyze_spiritual_mission(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze spiritual mission.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Spiritual mission analysis
    """
    atmakaraka = analyze_atmakaraka(kundli)
    nodes_karma = analyze_nodes_karma(kundli)
    past_life = analyze_past_life_indicators(kundli)
    
    atmakaraka_planet = atmakaraka.get("planet", "Unknown")
    ketu_house = nodes_karma.get("ketu", {}).get("house", 0)
    
    spiritual_theme = f"Spiritual mission: Your soul purpose is indicated by {atmakaraka_planet} (Atmakaraka). "
    
    if ketu_house in [9, 12]:
        spiritual_theme += "Strong spiritual inclination from past lives - your mission involves teaching, healing, or guiding others."
    elif ketu_house in [1, 4, 5]:
        spiritual_theme += "Spiritual growth through self-discovery and inner work."
    else:
        spiritual_theme += "Spiritual growth through service and practical application of wisdom."
    
    return {
        "type": "spiritual_mission",
        "title": "Spiritual Mission",
        "description": spiritual_theme,
        "advice": "Engage in regular spiritual practices, meditation, and self-reflection. Use your gifts to serve others and fulfill your dharma."
    }


def identify_hidden_gifts(kundli: Dict) -> Dict:
    """
    Phase 20: Identify hidden gifts in the chart.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Hidden gifts analysis
    """
    planets = kundli.get("Planets", {})
    houses = kundli.get("Houses", [])
    
    gifts = []
    
    # Check for planets in 5th house (creativity)
    planets_in_5 = [p for p, data in planets.items() if data.get("house") == 5]
    if planets_in_5:
        gifts.append(f"Creative gifts indicated by planets in 5th house ({', '.join(planets_in_5)})")
    
    # Check for planets in 9th house (wisdom)
    planets_in_9 = [p for p, data in planets.items() if data.get("house") == 9]
    if planets_in_9:
        gifts.append(f"Wisdom and teaching gifts indicated by planets in 9th house ({', '.join(planets_in_9)})")
    
    # Check for Jupiter aspects
    jupiter = planets.get("Jupiter", {})
    if jupiter:
        jup_house = jupiter.get("house", 0)
        if jup_house in [1, 5, 9]:
            gifts.append("Jupiter's blessings indicate natural wisdom and teaching abilities")
    
    # Check for Venus in favorable position
    venus = planets.get("Venus", {})
    if venus:
        venus_house = venus.get("house", 0)
        if venus_house in [1, 4, 5, 7, 9]:
            gifts.append("Venus in favorable position indicates artistic and relationship gifts")
    
    if not gifts:
        gifts.append("Your hidden gifts will be revealed through self-discovery and practice")
    
    return {
        "type": "hidden_gifts",
        "title": "Hidden Gifts",
        "description": "; ".join(gifts),
        "advice": "Explore your creative and intuitive abilities. Trust your inner wisdom and develop your unique talents."
    }

