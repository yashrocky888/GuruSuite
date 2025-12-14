"""
Phase 20: Strengths and Weaknesses Analyzer

Extracts top strengths and weaknesses from the birth chart.
"""

from typing import Dict, List


def extract_top_strengths(kundli: Dict) -> List[Dict]:
    """
    Phase 20: Extract top 5 strengths from the chart.
    
    Args:
        kundli: Birth chart
    
    Returns:
        List of top strengths
    """
    strengths = []
    
    planets = kundli.get("Planets", {})
    houses = kundli.get("Houses", [])
    
    # Strength 1: Benefic planets in favorable houses
    benefics = ["Jupiter", "Venus", "Mercury"]
    for planet_name in benefics:
        if planet_name in planets:
            planet_house = planets[planet_name].get("house", 0)
            if planet_house in [1, 4, 5, 7, 9, 10]:
                strengths.append({
                    "title": f"Strong {planet_name} placement",
                    "description": f"{planet_name} in {planet_house}th house brings natural blessings and positive qualities",
                    "score": 8
                })
    
    # Strength 2: Strong Lagna
    ascendant = kundli.get("Ascendant", {})
    lagna_sign = ascendant.get("sign", "Unknown")
    if lagna_sign:
        strengths.append({
            "title": f"Strong {lagna_sign} Lagna",
            "description": f"Your {lagna_sign} ascendant gives you natural leadership and personality strength",
            "score": 7
        })
    
    # Strength 3: Moon in favorable position
    moon = planets.get("Moon", {})
    moon_house = moon.get("house", 0)
    if moon_house in [1, 4, 5, 9]:
        strengths.append({
            "title": "Strong emotional intelligence",
            "description": f"Moon in {moon_house}th house indicates strong intuition and emotional awareness",
            "score": 7
        })
    
    # Strength 4: Jupiter aspects
    jupiter = planets.get("Jupiter", {})
    if jupiter:
        jup_house = jupiter.get("house", 0)
        if jup_house in [1, 5, 9]:
            strengths.append({
                "title": "Jupiter's blessings",
                "description": "Jupiter in trine brings wisdom, fortune, and spiritual growth",
                "score": 9
            })
    
    # Strength 5: Strong 10th house
    house_10 = next((h for h in houses if h.get("house") == 10), {})
    planets_in_10 = [p for p, data in planets.items() if data.get("house") == 10]
    if planets_in_10 and len(planets_in_10) > 0:
        strengths.append({
            "title": "Strong career potential",
            "description": f"Planets in 10th house ({', '.join(planets_in_10)}) indicate strong career focus and success",
            "score": 8
        })
    
    # Sort by score and return top 5
    strengths.sort(key=lambda x: x.get("score", 0), reverse=True)
    return strengths[:5]


def extract_top_weaknesses(kundli: Dict) -> List[Dict]:
    """
    Phase 20: Extract top 5 weaknesses from the chart.
    
    Args:
        kundli: Birth chart
    
    Returns:
        List of top weaknesses
    """
    weaknesses = []
    
    planets = kundli.get("Planets", {})
    houses = kundli.get("Houses", [])
    
    # Weakness 1: Malefics in challenging houses
    malefics = ["Saturn", "Mars"]
    for planet_name in malefics:
        if planet_name in planets:
            planet_house = planets[planet_name].get("house", 0)
            if planet_house in [6, 8, 12]:
                weaknesses.append({
                    "title": f"Challenging {planet_name} placement",
                    "description": f"{planet_name} in {planet_house}th house brings obstacles and challenges",
                    "score": 6,
                    "remedy": f"Practice patience and discipline. Chant {planet_name} mantras regularly."
                })
    
    # Weakness 2: Moon in challenging position
    moon = planets.get("Moon", {})
    moon_house = moon.get("house", 0)
    if moon_house in [6, 8, 12]:
        weaknesses.append({
            "title": "Emotional sensitivity",
            "description": f"Moon in {moon_house}th house indicates emotional challenges and sensitivity",
            "score": 5,
            "remedy": "Practice meditation and emotional regulation. Take care of mental health."
        })
    
    # Weakness 3: Weak Sun
    sun = planets.get("Sun", {})
    sun_house = sun.get("house", 0)
    if sun_house in [6, 8, 12]:
        weaknesses.append({
            "title": "Low self-confidence",
            "description": f"Sun in {sun_house}th house indicates challenges with self-expression and confidence",
            "score": 5,
            "remedy": "Practice self-affirmation. Worship Sun daily. Develop leadership skills."
        })
    
    # Weakness 4: Rahu in challenging position
    rahu = planets.get("Rahu", {})
    rahu_house = rahu.get("house", 0)
    if rahu_house in [6, 8, 12]:
        weaknesses.append({
            "title": "Material desires and confusion",
            "description": f"Rahu in {rahu_house}th house indicates confusion and excessive material desires",
            "score": 6,
            "remedy": "Practice detachment and meditation. Focus on spiritual growth over material gains."
        })
    
    # Weakness 5: Weak 7th house (relationships)
    house_7 = next((h for h in houses if h.get("house") == 7), {})
    malefics_in_7 = [p for p, data in planets.items() if p in ["Saturn", "Mars"] and data.get("house") == 7]
    if malefics_in_7:
        weaknesses.append({
            "title": "Relationship challenges",
            "description": f"Malefics in 7th house ({', '.join(malefics_in_7)}) indicate relationship challenges",
            "score": 6,
            "remedy": "Practice communication and understanding. Worship Venus. Be patient in relationships."
        })
    
    # Sort by score and return top 5
    weaknesses.sort(key=lambda x: x.get("score", 0), reverse=True)
    return weaknesses[:5]


def convert_to_human_language(strengths: List[Dict], weaknesses: List[Dict]) -> Dict:
    """
    Phase 20: Convert strengths and weaknesses to human-readable language.
    
    Args:
        strengths: List of strengths
        weaknesses: List of weaknesses
    
    Returns:
        Human-readable summary
    """
    strengths_text = "Your key strengths include:\n"
    for i, strength in enumerate(strengths, 1):
        strengths_text += f"{i}. {strength.get('title', 'Strength')}: {strength.get('description', '')}\n"
    
    weaknesses_text = "\nAreas for growth:\n"
    for i, weakness in enumerate(weaknesses, 1):
        weaknesses_text += f"{i}. {weakness.get('title', 'Area')}: {weakness.get('description', '')}\n"
        if weakness.get('remedy'):
            weaknesses_text += f"   Remedy: {weakness.get('remedy')}\n"
    
    return {
        "strengths_text": strengths_text.strip(),
        "weaknesses_text": weaknesses_text.strip(),
        "summary": f"You have {len(strengths)} key strengths and {len(weaknesses)} areas for growth. Focus on developing your strengths while working on the areas that need attention."
    }

