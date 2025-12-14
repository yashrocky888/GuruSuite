"""
Phase 20: Karma Indicators

Analyzes karmic indicators in the birth chart.
"""

from typing import Dict, List


def analyze_atmakaraka(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze Atmakaraka (Soul indicator).
    
    Args:
        kundli: Birth chart
    
    Returns:
        Atmakaraka analysis
    """
    planets = kundli.get("Planets", {})
    
    # Find planet with highest degree (Atmakaraka)
    max_degree = -1
    atmakaraka_planet = None
    
    for planet_name, planet_data in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        
        degree = planet_data.get("degree", 0)
        if degree > max_degree:
            max_degree = degree
            atmakaraka_planet = planet_name
    
    if not atmakaraka_planet:
        return {"planet": "Unknown", "meaning": "Unable to determine"}
    
    # Interpret Atmakaraka
    meanings = {
        "Sun": "Soul purpose related to leadership, authority, and self-expression",
        "Moon": "Soul purpose related to emotions, nurturing, and intuition",
        "Mars": "Soul purpose related to courage, action, and protection",
        "Mercury": "Soul purpose related to communication, learning, and business",
        "Jupiter": "Soul purpose related to wisdom, teaching, and expansion",
        "Venus": "Soul purpose related to love, beauty, and relationships",
        "Saturn": "Soul purpose related to discipline, karma, and service"
    }
    
    return {
        "planet": atmakaraka_planet,
        "degree": max_degree,
        "meaning": meanings.get(atmakaraka_planet, "Soul indicator"),
        "interpretation": f"Your Atmakaraka is {atmakaraka_planet}, indicating your primary soul purpose in this lifetime."
    }


def analyze_amatyakaraka(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze Amatyakaraka (Career indicator).
    
    Args:
        kundli: Birth chart
    
    Returns:
        Amatyakaraka analysis
    """
    planets = kundli.get("Planets", {})
    
    # Find planet with second highest degree (Amatyakaraka)
    degrees = []
    for planet_name, planet_data in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue
        degrees.append((planet_name, planet_data.get("degree", 0)))
    
    degrees.sort(key=lambda x: x[1], reverse=True)
    
    if len(degrees) < 2:
        return {"planet": "Unknown", "meaning": "Unable to determine"}
    
    amatyakaraka_planet = degrees[1][0]  # Second highest
    
    meanings = {
        "Sun": "Career in leadership, government, or authority roles",
        "Moon": "Career in nurturing, psychology, or creative fields",
        "Mars": "Career in military, engineering, or competitive fields",
        "Mercury": "Career in communication, business, or education",
        "Jupiter": "Career in teaching, law, or spiritual guidance",
        "Venus": "Career in arts, beauty, or relationship counseling",
        "Saturn": "Career in service, administration, or long-term projects"
    }
    
    return {
        "planet": amatyakaraka_planet,
        "meaning": meanings.get(amatyakaraka_planet, "Career indicator"),
        "interpretation": f"Your Amatyakaraka is {amatyakaraka_planet}, indicating your career direction and professional karma."
    }


def analyze_karmesha(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze Karmesha (10th lord - work karma).
    
    Args:
        kundli: Birth chart
    
    Returns:
        Karmesha analysis
    """
    houses = kundli.get("Houses", [])
    house_10 = next((h for h in houses if h.get("house") == 10), {})
    karmesha_lord = house_10.get("lord", "Unknown")
    
    meanings = {
        "Sun": "Work karma related to leadership and authority",
        "Moon": "Work karma related to emotions and nurturing",
        "Mars": "Work karma related to action and courage",
        "Mercury": "Work karma related to communication and business",
        "Jupiter": "Work karma related to wisdom and teaching",
        "Venus": "Work karma related to beauty and relationships",
        "Saturn": "Work karma related to discipline and service"
    }
    
    return {
        "lord": karmesha_lord,
        "meaning": meanings.get(karmesha_lord, "Work karma indicator"),
        "interpretation": f"Your 10th house lord is {karmesha_lord}, indicating your work karma and professional path."
    }


def analyze_bhagya(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze Bhagya (9th lord - fortune).
    
    Args:
        kundli: Birth chart
    
    Returns:
        Bhagya analysis
    """
    houses = kundli.get("Houses", [])
    house_9 = next((h for h in houses if h.get("house") == 9), {})
    bhagya_lord = house_9.get("lord", "Unknown")
    
    meanings = {
        "Sun": "Fortune through leadership and self-expression",
        "Moon": "Fortune through emotions and intuition",
        "Mars": "Fortune through courage and action",
        "Mercury": "Fortune through communication and learning",
        "Jupiter": "Fortune through wisdom and spiritual growth",
        "Venus": "Fortune through love and beauty",
        "Saturn": "Fortune through discipline and karma"
    }
    
    return {
        "lord": bhagya_lord,
        "meaning": meanings.get(bhagya_lord, "Fortune indicator"),
        "interpretation": f"Your 9th house lord is {bhagya_lord}, indicating your fortune and dharma."
    }


def analyze_moon_psychology(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze Moon psychology.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Moon psychology analysis
    """
    planets = kundli.get("Planets", {})
    moon = planets.get("Moon", {})
    
    moon_sign = moon.get("sign", "Unknown")
    moon_house = moon.get("house", 0)
    moon_nakshatra = moon.get("nakshatra", "Unknown")
    
    sign_meanings = {
        "Aries": "Emotional nature: Direct, impulsive, passionate",
        "Taurus": "Emotional nature: Stable, sensual, determined",
        "Gemini": "Emotional nature: Curious, communicative, adaptable",
        "Cancer": "Emotional nature: Nurturing, sensitive, intuitive",
        "Leo": "Emotional nature: Proud, creative, generous",
        "Virgo": "Emotional nature: Analytical, practical, service-oriented",
        "Libra": "Emotional nature: Balanced, harmonious, relationship-focused",
        "Scorpio": "Emotional nature: Intense, transformative, secretive",
        "Sagittarius": "Emotional nature: Optimistic, philosophical, adventurous",
        "Capricorn": "Emotional nature: Disciplined, ambitious, reserved",
        "Aquarius": "Emotional nature: Independent, humanitarian, unconventional",
        "Pisces": "Emotional nature: Compassionate, intuitive, dreamy"
    }
    
    return {
        "sign": moon_sign,
        "house": moon_house,
        "nakshatra": moon_nakshatra,
        "meaning": sign_meanings.get(moon_sign, "Emotional nature indicator"),
        "interpretation": f"Your Moon in {moon_sign} ({moon_nakshatra} Nakshatra) shapes your emotional psychology and inner world."
    }


def analyze_lagna_lord(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze Lagna and Lagna lord.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Lagna analysis
    """
    ascendant = kundli.get("Ascendant", {})
    lagna_sign = ascendant.get("sign", "Unknown")
    lagna_degree = ascendant.get("degree", 0)
    
    houses = kundli.get("Houses", [])
    house_1 = next((h for h in houses if h.get("house") == 1), {})
    lagna_lord = house_1.get("lord", "Unknown")
    
    return {
        "sign": lagna_sign,
        "degree": lagna_degree,
        "lord": lagna_lord,
        "interpretation": f"Your Lagna is {lagna_sign} with {lagna_lord} as lord, indicating your personality and life approach."
    }


def analyze_nodes_karma(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze Rahu/Ketu axis for karmic lessons.
    
    Args:
        kundli: Birth chart
    
    Returns:
        Nodes karma analysis
    """
    planets = kundli.get("Planets", {})
    rahu = planets.get("Rahu", {})
    ketu = planets.get("Ketu", {})
    
    rahu_house = rahu.get("house", 0)
    rahu_sign = rahu.get("sign", "Unknown")
    ketu_house = ketu.get("house", 0)
    ketu_sign = ketu.get("sign", "Unknown")
    
    rahu_meanings = {
        1: "Karmic lesson: Self-identity and ego",
        2: "Karmic lesson: Material possessions and values",
        3: "Karmic lesson: Communication and siblings",
        4: "Karmic lesson: Home and mother",
        5: "Karmic lesson: Creativity and children",
        6: "Karmic lesson: Service and health",
        7: "Karmic lesson: Relationships and partnerships",
        8: "Karmic lesson: Transformation and secrets",
        9: "Karmic lesson: Dharma and philosophy",
        10: "Karmic lesson: Career and reputation",
        11: "Karmic lesson: Gains and friendships",
        12: "Karmic lesson: Spirituality and liberation"
    }
    
    ketu_meanings = {
        1: "Past-life karma: Detachment from self",
        2: "Past-life karma: Detachment from material",
        3: "Past-life karma: Detachment from communication",
        4: "Past-life karma: Detachment from home",
        5: "Past-life karma: Detachment from creativity",
        6: "Past-life karma: Detachment from service",
        7: "Past-life karma: Detachment from relationships",
        8: "Past-life karma: Spiritual transformation",
        9: "Past-life karma: Spiritual wisdom",
        10: "Past-life karma: Detachment from career",
        11: "Past-life karma: Detachment from gains",
        12: "Past-life karma: Spiritual liberation"
    }
    
    return {
        "rahu": {
            "house": rahu_house,
            "sign": rahu_sign,
            "meaning": rahu_meanings.get(rahu_house, "Karmic lesson indicator"),
            "interpretation": f"Rahu in {rahu_house}th house ({rahu_sign}) - your karmic desires and material pursuits"
        },
        "ketu": {
            "house": ketu_house,
            "sign": ketu_sign,
            "meaning": ketu_meanings.get(ketu_house, "Past-life karma indicator"),
            "interpretation": f"Ketu in {ketu_house}th house ({ketu_sign}) - your past-life karma and spiritual detachment"
        },
        "axis_interpretation": f"The Rahu-Ketu axis shows your karmic journey from material desires (Rahu) to spiritual liberation (Ketu)."
    }


def analyze_past_life_indicators(kundli: Dict) -> Dict:
    """
    Phase 20: Analyze past-life indicators (Ketu position).
    
    Args:
        kundli: Birth chart
    
    Returns:
        Past-life analysis
    """
    planets = kundli.get("Planets", {})
    ketu = planets.get("Ketu", {})
    
    ketu_house = ketu.get("house", 0)
    ketu_sign = ketu.get("sign", "Unknown")
    ketu_nakshatra = ketu.get("nakshatra", "Unknown")
    
    past_life_meanings = {
        1: "Past life: Strong spiritual practice, renunciation",
        2: "Past life: Material accumulation, family focus",
        3: "Past life: Communication, learning, teaching",
        4: "Past life: Home, mother, emotional security",
        5: "Past life: Creativity, children, education",
        6: "Past life: Service, healing, helping others",
        7: "Past life: Relationships, partnerships, marriage",
        8: "Past life: Transformation, occult, secrets",
        9: "Past life: Dharma, philosophy, spiritual teacher",
        10: "Past life: Career, authority, leadership",
        11: "Past life: Gains, friendships, social networks",
        12: "Past life: Moksha, liberation, spiritual completion"
    }
    
    return {
        "house": ketu_house,
        "sign": ketu_sign,
        "nakshatra": ketu_nakshatra,
        "meaning": past_life_meanings.get(ketu_house, "Past-life indicator"),
        "interpretation": f"Ketu in {ketu_house}th house indicates your past-life karma and spiritual lessons carried forward."
    }

