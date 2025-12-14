"""
Phase 18: Remedies Generator

Generates astrological remedies based on chart weaknesses and doshas.
"""

from typing import Dict, List


# Phase 18: Gemstone recommendations
GEMSTONES = {
    "Sun": {"gemstone": "Ruby", "metal": "Gold", "finger": "Ring finger"},
    "Moon": {"gemstone": "Pearl", "metal": "Silver", "finger": "Little finger"},
    "Mars": {"gemstone": "Coral", "metal": "Copper", "finger": "Ring finger"},
    "Mercury": {"gemstone": "Emerald", "metal": "Gold/Silver", "finger": "Little finger"},
    "Jupiter": {"gemstone": "Yellow Sapphire", "metal": "Gold", "finger": "Index finger"},
    "Venus": {"gemstone": "Diamond", "metal": "Silver/Platinum", "finger": "Middle finger"},
    "Saturn": {"gemstone": "Blue Sapphire", "metal": "Iron", "finger": "Middle finger"},
    "Rahu": {"gemstone": "Hessonite (Gomedh)", "metal": "Silver", "finger": "Middle finger"},
    "Ketu": {"gemstone": "Cat's Eye", "metal": "Silver", "finger": "Ring finger"}
}

# Phase 18: Mantras
MANTRAS = {
    "Sun": "Om Suryaya Namah",
    "Moon": "Om Chandraya Namah",
    "Mars": "Om Kram Kreem Krom Sah Bhaumaya Namah",
    "Mercury": "Om Budhaya Namah",
    "Jupiter": "Om Gurave Namah",
    "Venus": "Om Shukraya Namah",
    "Saturn": "Om Shani Devaya Namah",
    "Rahu": "Om Raam Rahave Namah",
    "Ketu": "Om Kem Ketave Namah"
}

# Phase 18: Pujas and rituals
PUJAS = {
    "Sun": "Surya Puja on Sundays",
    "Moon": "Chandra Puja on Mondays",
    "Mars": "Mangal Puja on Tuesdays",
    "Mercury": "Budh Puja on Wednesdays",
    "Jupiter": "Guru Puja on Thursdays",
    "Venus": "Shukra Puja on Fridays",
    "Saturn": "Shani Puja on Saturdays",
    "Rahu": "Rahu Puja on Saturdays",
    "Ketu": "Ketu Puja on Tuesdays"
}


def generate_remedies(chart: Dict, weaknesses: List[str], doshas: List[str], planets: List[str]) -> Dict:
    """
    Phase 18: Generate remedies based on chart analysis.
    
    Args:
        chart: Birth chart
        weaknesses: List of identified weaknesses
        doshas: List of doshas (Manglik, etc.)
        planets: List of weak planets needing remedies
    
    Returns:
        Remedies dictionary
    """
    remedies = {
        "gemstones": [],
        "mantras": [],
        "pujas": [],
        "habits": [],
        "donations": [],
        "general": []
    }
    
    # Generate planet-specific remedies
    for planet in planets:
        if planet in GEMSTONES:
            gem_info = GEMSTONES[planet]
            remedies["gemstones"].append({
                "planet": planet,
                "gemstone": gem_info["gemstone"],
                "metal": gem_info["metal"],
                "finger": gem_info["finger"],
                "note": f"Wear {gem_info['gemstone']} in {gem_info['metal']} on {gem_info['finger']} after consulting astrologer"
            })
        
        if planet in MANTRAS:
            remedies["mantras"].append({
                "planet": planet,
                "mantra": MANTRAS[planet],
                "count": "108 times daily",
                "time": "Morning or evening",
                "note": f"Chant {MANTRAS[planet]} 108 times daily"
            })
        
        if planet in PUJAS:
            remedies["pujas"].append({
                "planet": planet,
                "puja": PUJAS[planet],
                "note": f"Perform {PUJAS[planet]}"
            })
    
    # Dosha-specific remedies
    if "Manglik" in doshas or "Mangal Dosha" in doshas:
        remedies["general"].append({
            "type": "Mangal Dosha",
            "remedy": "Marry a Manglik person or perform Kumbh Vivah (marriage to a tree/object) before actual marriage",
            "note": "Consult qualified astrologer for proper remedy"
        })
    
    # General remedies
    remedies["habits"].extend([
        {
            "habit": "Meditation",
            "frequency": "Daily",
            "benefit": "Reduces stress and improves mental clarity"
        },
        {
            "habit": "Prayer",
            "frequency": "Daily morning and evening",
            "benefit": "Connects with divine and brings peace"
        },
        {
            "habit": "Charity",
            "frequency": "Regular",
            "benefit": "Reduces negative karma and brings blessings"
        }
    ])
    
    # Donations based on planets
    donation_items = {
        "Sun": "Wheat, copper, gold",
        "Moon": "Rice, silver, white clothes",
        "Mars": "Red lentils, copper, red clothes",
        "Mercury": "Green gram, green clothes",
        "Jupiter": "Yellow gram, yellow clothes, gold",
        "Venus": "White gram, white clothes, silver",
        "Saturn": "Black sesame, black clothes, iron",
        "Rahu": "Blue clothes, coconut",
        "Ketu": "Brown clothes, mustard oil"
    }
    
    for planet in planets:
        if planet in donation_items:
            remedies["donations"].append({
                "planet": planet,
                "items": donation_items[planet],
                "day": "Planet's day",
                "note": f"Donate {donation_items[planet]} on {planet}'s day"
            })
    
    return remedies


def recommend_gemstones(weak_planets: List[str]) -> List[Dict]:
    """
    Phase 18: Recommend gemstones for weak planets.
    
    Args:
        weak_planets: List of weak planets
    
    Returns:
        List of gemstone recommendations
    """
    recommendations = []
    
    for planet in weak_planets:
        if planet in GEMSTONES:
            gem_info = GEMSTONES[planet]
            recommendations.append({
                "planet": planet,
                "gemstone": gem_info["gemstone"],
                "metal": gem_info["metal"],
                "finger": gem_info["finger"],
                "wearing_method": f"Wear {gem_info['gemstone']} in {gem_info['metal']} ring on {gem_info['finger']}",
                "activation": "Get gemstone activated by qualified astrologer",
                "caution": "Consult astrologer before wearing. Some gemstones may not suit everyone."
            })
    
    return recommendations


def recommend_mantras(planets: List[str]) -> List[Dict]:
    """
    Phase 18: Recommend mantras for planets.
    
    Args:
        planets: List of planets
    
    Returns:
        List of mantra recommendations
    """
    recommendations = []
    
    for planet in planets:
        if planet in MANTRAS:
            recommendations.append({
                "planet": planet,
                "mantra": MANTRAS[planet],
                "count": "108 times",
                "frequency": "Daily",
                "best_time": "Morning (Brahma Muhurta) or evening",
                "method": "Sit in meditation pose, close eyes, chant with devotion",
                "duration": "Continue for at least 40 days for best results"
            })
    
    return recommendations


def recommend_pujas(planets: List[str]) -> List[Dict]:
    """
    Phase 18: Recommend pujas for planets.
    
    Args:
        planets: List of planets
    
    Returns:
        List of puja recommendations
    """
    recommendations = []
    
    for planet in planets:
        if planet in PUJAS:
            recommendations.append({
                "planet": planet,
                "puja": PUJAS[planet],
                "frequency": "Weekly on planet's day",
                "benefit": f"Strengthens {planet} and reduces negative effects",
                "note": "Can be performed at home or temple"
            })
    
    return recommendations


def recommend_habits(chart: Dict, weaknesses: List[str]) -> List[Dict]:
    """
    Phase 18: Recommend daily habits based on chart.
    
    Args:
        chart: Birth chart
        weaknesses: List of weaknesses
    
    Returns:
        List of habit recommendations
    """
    habits = []
    
    # General habits
    habits.append({
        "habit": "Morning Meditation",
        "duration": "15-30 minutes",
        "benefit": "Improves mental clarity and reduces stress",
        "time": "Brahma Muhurta (4-6 AM)"
    })
    
    habits.append({
        "habit": "Prayer",
        "frequency": "Twice daily",
        "benefit": "Connects with divine and brings peace",
        "time": "Morning and evening"
    })
    
    habits.append({
        "habit": "Charity",
        "frequency": "Regular",
        "benefit": "Reduces negative karma",
        "suggestions": "Donate to temples, charities, or those in need"
    })
    
    # Chart-specific habits
    planets = chart.get("Planets", {})
    
    if "Saturn" in weaknesses:
        habits.append({
            "habit": "Service to Others",
            "frequency": "Regular",
            "benefit": "Pleases Saturn and reduces delays",
            "suggestions": "Help elderly, serve in community"
        })
    
    if "Mars" in weaknesses:
        habits.append({
            "habit": "Physical Exercise",
            "frequency": "Daily",
            "benefit": "Strengthens Mars energy",
            "suggestions": "Yoga, sports, or regular exercise"
        })
    
    if "Moon" in weaknesses:
        habits.append({
            "habit": "Emotional Balance",
            "frequency": "Daily",
            "benefit": "Strengthens Moon energy",
            "suggestions": "Practice mindfulness, avoid emotional conflicts"
        })
    
    return habits

