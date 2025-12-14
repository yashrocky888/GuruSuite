"""
Phase 18: Dasha Interpreter

Interprets Dasha periods and their effects.
"""

from typing import Dict, List
from src.liveguru.explanations.karakatva import get_karakatva
from src.liveguru.explanations.dasha_logic import explain_dasha


def interpret_mahadasha(planet: str, chart: Dict, yogas: List[Dict], transits: Dict) -> Dict:
    """
    Phase 18: Interpret Mahadasha period.
    
    Args:
        planet: Dasha lord planet
        chart: Birth chart
        yogas: Detected yogas
        transits: Current transits
    
    Returns:
        Mahadasha interpretation
    """
    karakatva = get_karakatva(planet)
    primary = ", ".join(karakatva.get("primary", [])[:3])
    
    # Check if planet is strong in chart
    planet_data = chart.get("Planets", {}).get(planet, {})
    planet_house = planet_data.get("house", 0)
    planet_strength = planet_data.get("strength", 50)
    
    interpretation = f"""
{planet} Mahadasha Period:

Planetary Nature:
{planet} represents: {primary}

Planet's Position in Chart:
• House: {planet_house}th house
• Strength: {planet_strength}/100
"""
    
    # Dignity assessment
    dignity = planet_data.get("dignity", "neutral")
    if dignity == "exalted":
        interpretation += "• Dignity: Exalted - Very strong and favorable\n"
    elif dignity == "own":
        interpretation += "• Dignity: Own Sign - Strong and comfortable\n"
    elif dignity == "debilitated":
        interpretation += "• Dignity: Debilitated - Weak, challenges expected\n"
    else:
        interpretation += f"• Dignity: {dignity.title()} - Moderate influence\n"
    
    interpretation += "\nDasha Effects:\n"
    
    # Planet-specific interpretations
    if planet == "Jupiter":
        interpretation += """
• Brings wisdom, knowledge, and spiritual growth
• Favorable for education, teaching, and guidance
• Enhances relationships and children matters
• Provides fortune and prosperity
• Good time for religious and spiritual activities
"""
    elif planet == "Saturn":
        interpretation += """
• Brings discipline, hard work, and responsibility
• May create delays and obstacles (karmic lessons)
• Favorable for career development and service
• Tests patience and perseverance
• Good time for long-term planning
"""
    elif planet == "Mars":
        interpretation += """
• Brings energy, action, and courage
• Favorable for new initiatives and projects
• May create conflicts and aggression
• Good time for physical activities and sports
• Enhances leadership and determination
"""
    elif planet == "Venus":
        interpretation += """
• Brings love, beauty, and relationships
• Favorable for marriage and partnerships
• Enhances creativity and arts
• Provides material comforts and luxury
• Good time for relationships and creative pursuits
"""
    elif planet == "Mercury":
        interpretation += """
• Brings communication, intellect, and business
• Favorable for learning and education
• Enhances business and commerce
• Good time for writing, speaking, and communication
• Provides mental clarity and intelligence
"""
    elif planet == "Sun":
        interpretation += """
• Brings authority, leadership, and recognition
• Favorable for career advancement
• Enhances self-confidence and ego
• Good time for leadership roles
• May create challenges with authority figures
"""
    elif planet == "Moon":
        interpretation += """
• Brings emotions, intuition, and popularity
• Favorable for relationships and emotional matters
• Enhances creativity and imagination
• Good time for nurturing and care
• May create mood swings and emotional sensitivity
"""
    elif planet == "Rahu":
        interpretation += """
• Brings material desires and ambitions
• Favorable for foreign connections and technology
• May create illusions and confusion
• Good time for unconventional pursuits
• Enhances material success but may create attachment
"""
    elif planet == "Ketu":
        interpretation += """
• Brings spirituality and detachment
• Favorable for spiritual practices and moksha
• May create isolation and confusion
• Good time for inner work and letting go
• Enhances intuition and mysticism
"""
    
    # Check for relevant yogas
    planet_yogas = [y for y in yogas if planet in y.get("planets", [])]
    if planet_yogas:
        interpretation += f"\nRelevant Yogas:\n"
        for yoga in planet_yogas[:3]:  # Top 3
            interpretation += f"• {yoga.get('name', 'Unknown')} - {yoga.get('description', '')[:100]}...\n"
    
    # Transit influence
    if transits:
        interpretation += "\nCurrent Transit Influence:\n"
        interpretation += "Transits modify the Dasha effects. Check current planetary positions for specific timing.\n"
    
    return {
        "planet": planet,
        "planet_house": planet_house,
        "planet_strength": planet_strength,
        "dignity": dignity,
        "interpretation": interpretation.strip(),
        "relevant_yogas": len(planet_yogas)
    }


def interpret_antardasha(lord1: str, lord2: str, chart: Dict) -> Dict:
    """
    Phase 18: Interpret Antardasha (sub-period).
    
    Args:
        lord1: Mahadasha lord
        lord2: Antardasha lord
        chart: Birth chart
    
    Returns:
        Antardasha interpretation
    """
    interpretation = f"""
{lord1} Mahadasha - {lord2} Antardasha:

This is a sub-period within {lord1} Mahadasha, ruled by {lord2}.

Combined Effect:
{lord2} modifies the effects of {lord1} Dasha period.

Interpretation:
"""
    
    # Check relationship between planets
    benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
    malefics = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]
    
    if lord1 in benefics and lord2 in benefics:
        interpretation += f"Both {lord1} and {lord2} are benefic planets. This creates a highly favorable period with positive results.\n"
    elif lord1 in malefics and lord2 in malefics:
        interpretation += f"Both {lord1} and {lord2} are malefic planets. This period may bring challenges and requires patience.\n"
    elif lord1 in benefics and lord2 in malefics:
        interpretation += f"{lord1} (benefic) Dasha with {lord2} (malefic) Antardasha. Mixed results - some challenges within a generally positive period.\n"
    else:
        interpretation += f"{lord1} (malefic) Dasha with {lord2} (benefic) Antardasha. Some relief and positive opportunities within a challenging period.\n"
    
    # Specific combinations
    if lord1 == "Jupiter" and lord2 == "Venus":
        interpretation += "\nExcellent combination for relationships, wealth, and spiritual growth.\n"
    elif lord1 == "Saturn" and lord2 == "Jupiter":
        interpretation += "\nKarmic lessons with wisdom. Good for learning and growth through challenges.\n"
    elif lord1 == "Rahu" and lord2 == "Jupiter":
        interpretation += "\nMaterial success with spiritual growth. Balance is key.\n"
    
    return {
        "mahadasha_lord": lord1,
        "antardasha_lord": lord2,
        "interpretation": interpretation.strip()
    }


def generate_dasha_predictions(birth_chart: Dict, dasha_sequence: List[Dict]) -> Dict:
    """
    Phase 18: Generate predictions for upcoming Dasha periods.
    
    Args:
        birth_chart: Birth chart
        dasha_sequence: List of upcoming Dasha periods
    
    Returns:
        Predictions dictionary
    """
    predictions = []
    
    for dasha in dasha_sequence[:5]:  # Next 5 periods
        planet = dasha.get("dasha_lord", "Unknown")
        start_date = dasha.get("start_date", "N/A")
        duration = dasha.get("duration", "N/A")
        
        # Get planet interpretation
        mahadasha_info = interpret_mahadasha(planet, birth_chart, [], {})
        
        predictions.append({
            "period": f"{planet} Mahadasha",
            "start_date": start_date,
            "duration": duration,
            "planet": planet,
            "prediction": mahadasha_info.get("interpretation", "")[:300] + "...",
            "overall_effect": "favorable" if planet in ["Jupiter", "Venus", "Mercury"] else "challenging" if planet in ["Saturn", "Rahu", "Ketu"] else "moderate"
        })
    
    return {
        "upcoming_periods": predictions,
        "total_periods": len(predictions),
        "summary": f"Analysis of next {len(predictions)} Dasha periods"
    }

