"""
Phase 18: Transit Interpreter

Interprets planetary transits and their effects.
"""

from typing import Dict, List
from src.utils.converters import degrees_to_sign


def interpret_transit(planet: str, house: int, aspects: List[Dict], natal_positions: Dict) -> Dict:
    """
    Phase 18: Interpret a planetary transit.
    
    Args:
        planet: Planet name
        house: House being transited
        aspects: Aspects cast by the planet
        natal_positions: Natal planetary positions
    
    Returns:
        Transit interpretation
    """
    natal_planet = natal_positions.get(planet, {})
    natal_house = natal_planet.get("house", 0)
    
    interpretation = f"""
{planet} Transit in {house}th House:

Current Position:
{planet} is transiting through {house}th house.

Natal Position:
{planet} is in {natal_house}th house in natal chart.

Transit Effect:
"""
    
    # House significance
    house_meanings = {
        1: "Self, personality, physical appearance",
        2: "Wealth, family, speech",
        3: "Siblings, courage, communication",
        4: "Mother, home, education",
        5: "Children, education, creativity",
        6: "Health, enemies, service",
        7: "Marriage, partnerships, spouse",
        8: "Longevity, transformation, secrets",
        9: "Father, dharma, fortune",
        10: "Career, profession, reputation",
        11: "Gains, income, friends",
        12: "Losses, expenses, spirituality"
    }
    
    house_meaning = house_meanings.get(house, "General life area")
    interpretation += f"{planet} transiting {house}th house ({house_meaning}) affects this area of life.\n\n"
    
    # Compare with natal position
    if house == natal_house:
        interpretation += f"Return to Natal House: {planet} returns to its natal position. This is significant and may bring natal house matters to focus.\n"
    elif abs(house - natal_house) == 6:
        interpretation += f"Opposite to Natal: {planet} is opposite its natal position. This creates tension and may bring challenges.\n"
    elif abs(house - natal_house) in [3, 9]:
        interpretation += f"Trine to Natal: {planet} is in trine to natal position. This is favorable and supportive.\n"
    
    # Aspects
    if aspects:
        interpretation += "\nAspects Cast:\n"
        for aspect in aspects:
            target_house = aspect.get("house", 0)
            aspect_type = aspect.get("type", "general")
            interpretation += f"• {planet} aspects {target_house}th house ({aspect_type} aspect)\n"
    
    # Benefic/Malefic effects
    benefics = ["Jupiter", "Venus", "Mercury"]
    malefics = ["Saturn", "Mars", "Rahu", "Ketu"]
    
    if planet in benefics:
        interpretation += f"\nPositive Effect: {planet} is a benefic planet. Transit brings favorable results.\n"
    elif planet in malefics:
        interpretation += f"\nChallenging Effect: {planet} is a malefic planet. Transit may bring obstacles.\n"
    
    return {
        "planet": planet,
        "transit_house": house,
        "natal_house": natal_house,
        "aspects": aspects,
        "interpretation": interpretation.strip(),
        "is_benefic": planet in benefics,
        "is_malefic": planet in malefics
    }


def identify_good_bad_transits(transits: Dict, natal_chart: Dict) -> Dict:
    """
    Phase 18: Identify good and bad transits.
    
    Args:
        transits: Current transits dictionary
        natal_chart: Birth chart
    
    Returns:
        Dictionary with good and bad transits
    """
    good_transits = []
    bad_transits = []
    
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    for planet in planets:
        if planet not in transits:
            continue
        
        transit_data = transits.get(planet, {})
        transit_house = transit_data.get("house", 0)
        natal_planet = natal_chart.get("Planets", {}).get(planet, {})
        natal_house = natal_planet.get("house", 0)
        
        # Good transits
        if transit_house in [1, 5, 9]:  # Trines
            good_transits.append({
                "planet": planet,
                "house": transit_house,
                "reason": f"{planet} in trine house - favorable"
            })
        elif transit_house in [4, 7, 10]:  # Kendras (if benefic)
            if planet in ["Jupiter", "Venus", "Mercury"]:
                good_transits.append({
                    "planet": planet,
                    "house": transit_house,
                    "reason": f"Benefic {planet} in kendra - favorable"
                })
        
        # Bad transits
        if transit_house in [6, 8, 12]:  # Dusthanas
            bad_transits.append({
                "planet": planet,
                "house": transit_house,
                "reason": f"{planet} in dusthana house - challenging"
            })
        elif abs(transit_house - natal_house) == 6:  # Opposite to natal
            bad_transits.append({
                "planet": planet,
                "house": transit_house,
                "reason": f"{planet} opposite natal position - challenging"
            })
    
    return {
        "good_transits": good_transits,
        "bad_transits": bad_transits,
        "total_good": len(good_transits),
        "total_bad": len(bad_transits)
    }


def blend_transit_with_dasha(transits: Dict, dasha: Dict) -> Dict:
    """
    Phase 18: Blend transit effects with Dasha period.
    
    Args:
        transits: Current transits
        dasha: Current Dasha information
    
    Returns:
        Blended interpretation
    """
    current_dasha = dasha.get("current_dasha", {})
    dasha_lord = current_dasha.get("dasha_lord", "Unknown")
    
    interpretation = f"""
Combined Dasha + Transit Analysis:

Current Dasha: {dasha_lord} Mahadasha

Transit Influence:
"""
    
    # Check if Dasha lord is transiting favorable houses
    dasha_lord_transit = transits.get(dasha_lord, {})
    if dasha_lord_transit:
        transit_house = dasha_lord_transit.get("house", 0)
        
        if transit_house in [1, 5, 9]:
            interpretation += f"{dasha_lord} (Dasha lord) transiting trine house - Very favorable period.\n"
        elif transit_house in [6, 8, 12]:
            interpretation += f"{dasha_lord} (Dasha lord) transiting dusthana - Challenges expected.\n"
        else:
            interpretation += f"{dasha_lord} (Dasha lord) transiting {transit_house}th house - Moderate influence.\n"
    
    # Overall assessment
    good_bad = identify_good_bad_transits(transits, {})
    
    interpretation += f"\nOverall Transit Status:\n"
    interpretation += f"• Favorable transits: {good_bad['total_good']}\n"
    interpretation += f"• Challenging transits: {good_bad['total_bad']}\n"
    
    if good_bad['total_good'] > good_bad['total_bad']:
        interpretation += "\nOverall: Favorable transit period supporting Dasha effects.\n"
    elif good_bad['total_bad'] > good_bad['total_good']:
        interpretation += "\nOverall: Challenging transit period. Patience and remedies recommended.\n"
    else:
        interpretation += "\nOverall: Mixed transit period with both opportunities and challenges.\n"
    
    return {
        "dasha_lord": dasha_lord,
        "transit_analysis": interpretation.strip(),
        "good_transits": good_bad['total_good'],
        "bad_transits": good_bad['total_bad']
    }

