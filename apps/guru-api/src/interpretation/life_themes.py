"""
Phase 18: Life Themes Analyzer

Analyzes specific life areas: career, relationships, finances, health, etc.
"""

from typing import Dict, List


def analyze_career(chart: Dict) -> Dict:
    """
    Phase 18: Analyze career and profession.
    
    Args:
        chart: Birth chart
    
    Returns:
        Career analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 10th house (career)
    house_10 = next((h for h in houses if h.get("house") == 10), {})
    house_10_lord = house_10.get("lord", "Unknown")
    
    # Planets in 10th house
    planets_in_10 = [p for p, data in planets.items() if data.get("house") == 10]
    
    analysis = f"""
Career & Profession Analysis:

10th House (Career):
• House Lord: {house_10_lord}
• Planets in 10th: {', '.join(planets_in_10) if planets_in_10 else 'None'}
"""
    
    # Career indicators
    if "Jupiter" in planets_in_10 or house_10_lord == "Jupiter":
        analysis += "\nJupiter influence: Favorable for teaching, law, finance, or spiritual professions.\n"
    
    if "Mercury" in planets_in_10 or house_10_lord == "Mercury":
        analysis += "\nMercury influence: Favorable for business, communication, writing, or technology.\n"
    
    if "Mars" in planets_in_10 or house_10_lord == "Mars":
        analysis += "\nMars influence: Favorable for engineering, military, sports, or competitive fields.\n"
    
    if "Venus" in planets_in_10 or house_10_lord == "Venus":
        analysis += "\nVenus influence: Favorable for arts, beauty, fashion, or luxury businesses.\n"
    
    if "Saturn" in planets_in_10 or house_10_lord == "Saturn":
        analysis += "\nSaturn influence: Favorable for government, administration, or service-oriented careers.\n"
    
    # 6th house (service)
    house_6 = next((h for h in houses if h.get("house") == 6), {})
    if house_6:
        analysis += f"\n6th House (Service): {house_6.get('lord', 'Unknown')} lord - indicates service-oriented work.\n"
    
    return {
        "house_10_lord": house_10_lord,
        "planets_in_10": planets_in_10,
        "analysis": analysis.strip(),
        "career_indicators": len(planets_in_10)
    }


def analyze_relationships(chart: Dict) -> Dict:
    """
    Phase 18: Analyze relationships and marriage.
    
    Args:
        chart: Birth chart
    
    Returns:
        Relationship analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 7th house (marriage)
    house_7 = next((h for h in houses if h.get("house") == 7), {})
    house_7_lord = house_7.get("lord", "Unknown")
    planets_in_7 = [p for p, data in planets.items() if data.get("house") == 7]
    
    # Venus (relationships)
    venus = planets.get("Venus", {})
    venus_house = venus.get("house", 0)
    
    analysis = f"""
Relationships & Marriage Analysis:

7th House (Marriage):
• House Lord: {house_7_lord}
• Planets in 7th: {', '.join(planets_in_7) if planets_in_7 else 'None'}

Venus (Relationships):
• Venus in {venus_house}th house
"""
    
    # Relationship indicators
    if "Venus" in planets_in_7 or house_7_lord == "Venus":
        analysis += "\nStrong Venus: Excellent for relationships and marriage. Harmonious partnerships.\n"
    
    if "Jupiter" in planets_in_7:
        analysis += "\nJupiter in 7th: Favorable for marriage. Spouse may be wise and supportive.\n"
    
    if "Saturn" in planets_in_7 or house_7_lord == "Saturn":
        analysis += "\nSaturn influence: May delay marriage or bring older/mature partner.\n"
    
    if "Mars" in planets_in_7:
        analysis += "\nMars in 7th: May create conflicts in relationships. Need for patience.\n"
    
    return {
        "house_7_lord": house_7_lord,
        "planets_in_7": planets_in_7,
        "venus_house": venus_house,
        "analysis": analysis.strip()
    }


def analyze_finances(chart: Dict) -> Dict:
    """
    Phase 18: Analyze finances and wealth.
    
    Args:
        chart: Birth chart
    
    Returns:
        Financial analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 2nd house (wealth)
    house_2 = next((h for h in houses if h.get("house") == 2), {})
    house_2_lord = house_2.get("lord", "Unknown")
    planets_in_2 = [p for p, data in planets.items() if data.get("house") == 2]
    
    # 11th house (gains)
    house_11 = next((h for h in houses if h.get("house") == 11), {})
    house_11_lord = house_11.get("lord", "Unknown")
    
    analysis = f"""
Finances & Wealth Analysis:

2nd House (Wealth):
• House Lord: {house_2_lord}
• Planets in 2nd: {', '.join(planets_in_2) if planets_in_2 else 'None'}

11th House (Gains):
• House Lord: {house_11_lord}
"""
    
    # Financial indicators
    if "Jupiter" in planets_in_2 or house_2_lord == "Jupiter":
        analysis += "\nJupiter influence: Favorable for wealth accumulation. Prosperity through wisdom.\n"
    
    if "Venus" in planets_in_2:
        analysis += "\nVenus in 2nd: Good for wealth through arts, beauty, or luxury businesses.\n"
    
    if "Saturn" in planets_in_2:
        analysis += "\nSaturn in 2nd: May create financial challenges. Hard work required for wealth.\n"
    
    return {
        "house_2_lord": house_2_lord,
        "planets_in_2": planets_in_2,
        "house_11_lord": house_11_lord,
        "analysis": analysis.strip()
    }


def analyze_health(chart: Dict) -> Dict:
    """
    Phase 18: Analyze health.
    
    Args:
        chart: Birth chart
    
    Returns:
        Health analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 6th house (health)
    house_6 = next((h for h in houses if h.get("house") == 6), {})
    house_6_lord = house_6.get("lord", "Unknown")
    planets_in_6 = [p for p, data in planets.items() if data.get("house") == 6]
    
    # 1st house (physical body)
    house_1 = next((h for h in houses if h.get("house") == 1), {})
    planets_in_1 = [p for p, data in planets.items() if data.get("house") == 1]
    
    analysis = f"""
Health Analysis:

6th House (Health):
• House Lord: {house_6_lord}
• Planets in 6th: {', '.join(planets_in_6) if planets_in_6 else 'None'}

1st House (Physical Body):
• Planets in 1st: {', '.join(planets_in_1) if planets_in_1 else 'None'}
"""
    
    # Health indicators
    if "Mars" in planets_in_6:
        analysis += "\nMars in 6th: Strong immunity but may have accidents or injuries.\n"
    
    if "Saturn" in planets_in_6:
        analysis += "\nSaturn in 6th: May have chronic health issues. Regular checkups recommended.\n"
    
    if "Jupiter" in planets_in_6:
        analysis += "\nJupiter in 6th: Generally good health. May overcome diseases.\n"
    
    return {
        "house_6_lord": house_6_lord,
        "planets_in_6": planets_in_6,
        "planets_in_1": planets_in_1,
        "analysis": analysis.strip()
    }


def analyze_spirituality(chart: Dict) -> Dict:
    """
    Phase 18: Analyze spirituality.
    
    Args:
        chart: Birth chart
    
    Returns:
        Spirituality analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 9th house (dharma, spirituality)
    house_9 = next((h for h in houses if h.get("house") == 9), {})
    house_9_lord = house_9.get("lord", "Unknown")
    planets_in_9 = [p for p, data in planets.items() if data.get("house") == 9]
    
    # 12th house (moksha)
    house_12 = next((h for h in houses if h.get("house") == 12), {})
    planets_in_12 = [p for p, data in planets.items() if data.get("house") == 12]
    
    # Ketu (spirituality)
    ketu = planets.get("Ketu", {})
    ketu_house = ketu.get("house", 0)
    
    analysis = f"""
Spirituality Analysis:

9th House (Dharma, Spirituality):
• House Lord: {house_9_lord}
• Planets in 9th: {', '.join(planets_in_9) if planets_in_9 else 'None'}

12th House (Moksha, Liberation):
• Planets in 12th: {', '.join(planets_in_12) if planets_in_12 else 'None'}

Ketu (Spirituality):
• Ketu in {ketu_house}th house
"""
    
    if "Jupiter" in planets_in_9:
        analysis += "\nJupiter in 9th: Strong spiritual inclination. Favorable for religious practices.\n"
    
    if ketu_house in [9, 12]:
        analysis += "\nKetu in spiritual houses: Strong spiritual path. Detachment and moksha indicated.\n"
    
    return {
        "house_9_lord": house_9_lord,
        "planets_in_9": planets_in_9,
        "planets_in_12": planets_in_12,
        "ketu_house": ketu_house,
        "analysis": analysis.strip()
    }


def analyze_family(chart: Dict) -> Dict:
    """
    Phase 18: Analyze family matters.
    
    Args:
        chart: Birth chart
    
    Returns:
        Family analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 4th house (mother, family)
    house_4 = next((h for h in houses if h.get("house") == 4), {})
    house_4_lord = house_4.get("lord", "Unknown")
    planets_in_4 = [p for p, data in planets.items() if data.get("house") == 4]
    
    # 9th house (father)
    house_9 = next((h for h in houses if h.get("house") == 9), {})
    house_9_lord = house_9.get("lord", "Unknown")
    
    analysis = f"""
Family Analysis:

4th House (Mother, Family):
• House Lord: {house_4_lord}
• Planets in 4th: {', '.join(planets_in_4) if planets_in_4 else 'None'}

9th House (Father):
• House Lord: {house_9_lord}
"""
    
    if "Moon" in planets_in_4:
        analysis += "\nMoon in 4th: Strong connection with mother. Emotional family bonds.\n"
    
    if "Jupiter" in planets_in_4:
        analysis += "\nJupiter in 4th: Favorable family life. Good education and property.\n"
    
    return {
        "house_4_lord": house_4_lord,
        "planets_in_4": planets_in_4,
        "house_9_lord": house_9_lord,
        "analysis": analysis.strip()
    }


def analyze_children(chart: Dict) -> Dict:
    """
    Phase 18: Analyze children.
    
    Args:
        chart: Birth chart
    
    Returns:
        Children analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 5th house (children)
    house_5 = next((h for h in houses if h.get("house") == 5), {})
    house_5_lord = house_5.get("lord", "Unknown")
    planets_in_5 = [p for p, data in planets.items() if data.get("house") == 5]
    
    # Jupiter (children karaka)
    jupiter = planets.get("Jupiter", {})
    jupiter_house = jupiter.get("house", 0)
    
    analysis = f"""
Children Analysis:

5th House (Children):
• House Lord: {house_5_lord}
• Planets in 5th: {', '.join(planets_in_5) if planets_in_5 else 'None'}

Jupiter (Children Karaka):
• Jupiter in {jupiter_house}th house
"""
    
    if "Jupiter" in planets_in_5:
        analysis += "\nJupiter in 5th: Excellent for children. Favorable for having children.\n"
    
    if "Saturn" in planets_in_5:
        analysis += "\nSaturn in 5th: May delay children or create challenges.\n"
    
    return {
        "house_5_lord": house_5_lord,
        "planets_in_5": planets_in_5,
        "jupiter_house": jupiter_house,
        "analysis": analysis.strip()
    }


def analyze_property(chart: Dict) -> Dict:
    """
    Phase 18: Analyze property and assets.
    
    Args:
        chart: Birth chart
    
    Returns:
        Property analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 4th house (property)
    house_4 = next((h for h in houses if h.get("house") == 4), {})
    house_4_lord = house_4.get("lord", "Unknown")
    planets_in_4 = [p for p, data in planets.items() if data.get("house") == 4]
    
    analysis = f"""
Property & Assets Analysis:

4th House (Property):
• House Lord: {house_4_lord}
• Planets in 4th: {', '.join(planets_in_4) if planets_in_4 else 'None'}
"""
    
    if "Jupiter" in planets_in_4:
        analysis += "\nJupiter in 4th: Favorable for property and real estate.\n"
    
    if "Venus" in planets_in_4:
        analysis += "\nVenus in 4th: Good for property and material comforts.\n"
    
    return {
        "house_4_lord": house_4_lord,
        "planets_in_4": planets_in_4,
        "analysis": analysis.strip()
    }


def analyze_education(chart: Dict) -> Dict:
    """
    Phase 18: Analyze education.
    
    Args:
        chart: Birth chart
    
    Returns:
        Education analysis
    """
    houses = chart.get("Houses", [])
    planets = chart.get("Planets", {})
    
    # 4th house (education)
    house_4 = next((h for h in houses if h.get("house") == 4), {})
    planets_in_4 = [p for p, data in planets.items() if data.get("house") == 4]
    
    # 5th house (intelligence)
    house_5 = next((h for h in houses if h.get("house") == 5), {})
    house_5_lord = house_5.get("lord", "Unknown")
    planets_in_5 = [p for p, data in planets.items() if data.get("house") == 5]
    
    # Mercury (education karaka)
    mercury = planets.get("Mercury", {})
    mercury_house = mercury.get("house", 0)
    
    analysis = f"""
Education Analysis:

4th House (Education):
• Planets in 4th: {', '.join(planets_in_4) if planets_in_4 else 'None'}

5th House (Intelligence):
• House Lord: {house_5_lord}
• Planets in 5th: {', '.join(planets_in_5) if planets_in_5 else 'None'}

Mercury (Education Karaka):
• Mercury in {mercury_house}th house
"""
    
    if "Jupiter" in planets_in_5:
        analysis += "\nJupiter in 5th: Excellent for education and learning.\n"
    
    if "Mercury" in planets_in_5:
        analysis += "\nMercury in 5th: Strong intelligence and learning ability.\n"
    
    return {
        "planets_in_4": planets_in_4,
        "house_5_lord": house_5_lord,
        "planets_in_5": planets_in_5,
        "mercury_house": mercury_house,
        "analysis": analysis.strip()
    }

