"""
Phase 18: Planet Interpreter

Interprets planetary positions, dignity, strength, and relationships.
"""

from typing import Dict, List
from src.liveguru.explanations.karakatva import get_karakatva
from src.liveguru.explanations.nakshatra_details import get_nakshatra_details
from src.jyotish.panchang import get_nakshatra


def interpret_planet_in_house(planet: str, house: int, dignity: str, strength: float, nakshatra: str) -> Dict:
    """
    Phase 18: Interpret planet in a specific house.
    
    Args:
        planet: Planet name
        house: House number (1-12)
        dignity: Planetary dignity (exalted, debilitated, own, friendly, enemy, neutral)
        strength: Planet strength (0-100)
        nakshatra: Nakshatra name
    
    Returns:
        Interpretation dictionary
    """
    karakatva = get_karakatva(planet)
    nak_details = get_nakshatra_details(nakshatra)
    
    # House meanings
    house_meanings = {
        1: "Self, personality, physical appearance, head",
        2: "Wealth, family, speech, food, face",
        3: "Siblings, courage, communication, short journeys, hands",
        4: "Mother, home, education, chest, motherland",
        5: "Children, education, creativity, intelligence, stomach",
        6: "Health, enemies, service, debts, diseases",
        7: "Marriage, partnerships, spouse, business",
        8: "Longevity, transformation, secrets, sudden events",
        9: "Father, dharma, fortune, higher learning, luck",
        10: "Career, profession, reputation, knees",
        11: "Gains, income, friends, elder siblings, ambitions",
        12: "Losses, expenses, foreign lands, spirituality, liberation"
    }
    
    house_meaning = house_meanings.get(house, "General life area")
    
    # Dignity interpretation
    dignity_effects = {
        "exalted": "Very strong and favorable. Planet gives excellent results.",
        "own": "Strong and comfortable. Planet gives good results.",
        "friendly": "Moderately strong. Planet gives positive results.",
        "neutral": "Moderate strength. Planet gives mixed results.",
        "enemy": "Weakened. Planet may give challenging results.",
        "debilitated": "Very weak. Planet struggles to give positive results."
    }
    
    dignity_effect = dignity_effects.get(dignity, "Moderate influence")
    
    # Strength interpretation
    if strength >= 80:
        strength_desc = "Very strong - excellent results expected"
    elif strength >= 60:
        strength_desc = "Strong - good results expected"
    elif strength >= 40:
        strength_desc = "Moderate - mixed results"
    else:
        strength_desc = "Weak - challenging results, remedies needed"
    
    # Nakshatra influence
    nak_qualities = nak_details.get("qualities", "")
    nak_lord = nak_details.get("lord", "")
    
    # Generate interpretation
    interpretation = f"""
{planet} in {house}th House ({house_meaning}):

Planetary Nature:
{planet} naturally represents: {', '.join(karakatva.get('primary', [])[:3])}

Position Analysis:
• House: {house}th house represents {house_meaning.lower()}
• Dignity: {dignity.title()} - {dignity_effect}
• Strength: {strength:.1f}/100 - {strength_desc}
• Nakshatra: {nakshatra} (Lord: {nak_lord})
• Nakshatra Qualities: {nak_qualities}

Interpretation:
"""
    
    # Specific house interpretations
    if house == 1:
        interpretation += f"{planet} in Ascendant shapes your personality and self-expression. "
        if dignity == "exalted":
            interpretation += f"Strong {planet} gives excellent self-confidence and leadership qualities."
        elif dignity == "debilitated":
            interpretation += f"Weak {planet} may create self-doubt and challenges in self-expression."
    
    elif house == 2:
        interpretation += f"{planet} in 2nd house affects wealth, family, and speech. "
        if planet in ["Jupiter", "Venus"]:
            interpretation += f"Benefic {planet} here brings wealth and family harmony."
        elif planet in ["Saturn", "Mars"]:
            interpretation += f"Malefic {planet} here may create financial challenges."
    
    elif house == 5:
        interpretation += f"{planet} in 5th house affects children, education, and creativity. "
        if planet == "Jupiter":
            interpretation += "Jupiter here is excellent for education and children."
        elif planet == "Saturn":
            interpretation += "Saturn here may delay children or create educational challenges."
    
    elif house == 7:
        interpretation += f"{planet} in 7th house affects marriage and partnerships. "
        if planet in ["Venus", "Jupiter"]:
            interpretation += f"Benefic {planet} brings harmonious relationships."
        elif planet in ["Saturn", "Mars"]:
            interpretation += f"Malefic {planet} may create relationship challenges."
    
    elif house == 10:
        interpretation += f"{planet} in 10th house affects career and reputation. "
        if dignity == "exalted" or strength >= 70:
            interpretation += f"Strong {planet} brings career success and recognition."
        else:
            interpretation += f"{planet} here shapes your professional life and public image."
    
    # Add strength-based predictions
    if strength >= 70:
        interpretation += f"\nPositive Effects: Strong {planet} brings favorable results in {house_meaning.lower()}."
    elif strength < 40:
        interpretation += f"\nChallenges: Weak {planet} may create obstacles in {house_meaning.lower()}. Remedies recommended."
    
    return {
        "planet": planet,
        "house": house,
        "house_meaning": house_meaning,
        "dignity": dignity,
        "strength": strength,
        "nakshatra": nakshatra,
        "nakshatra_lord": nak_lord,
        "interpretation": interpretation.strip(),
        "positive_effects": strength >= 60,
        "remedies_needed": strength < 40
    }


def interpret_planet_in_sign(planet: str, rashi: str) -> Dict:
    """
    Phase 18: Interpret planet in a specific sign.
    
    Args:
        planet: Planet name
        rashi: Sign name
    
    Returns:
        Interpretation dictionary
    """
    # Sign meanings
    sign_meanings = {
        "Aries": "Fire, leadership, initiative, courage",
        "Taurus": "Earth, stability, material comfort, patience",
        "Gemini": "Air, communication, intelligence, versatility",
        "Cancer": "Water, emotions, nurturing, home",
        "Leo": "Fire, creativity, authority, self-expression",
        "Virgo": "Earth, analysis, service, perfectionism",
        "Libra": "Air, balance, relationships, aesthetics",
        "Scorpio": "Water, transformation, intensity, secrets",
        "Sagittarius": "Fire, philosophy, expansion, wisdom",
        "Capricorn": "Earth, discipline, ambition, structure",
        "Aquarius": "Air, innovation, freedom, humanitarianism",
        "Pisces": "Water, spirituality, compassion, intuition"
    }
    
    sign_meaning = sign_meanings.get(rashi, "General sign qualities")
    
    interpretation = f"""
{planet} in {rashi} Sign:

Sign Qualities:
{rashi} represents {sign_meaning.lower()}

Planet-Sign Combination:
{planet} expresses its energy through {rashi} qualities.
"""
    
    # Specific combinations
    if planet == "Sun" and rashi == "Leo":
        interpretation += "Sun in own sign (Leo) - Very strong. Excellent leadership and self-confidence."
    elif planet == "Moon" and rashi == "Cancer":
        interpretation += "Moon in own sign (Cancer) - Very strong. Excellent emotional intelligence."
    elif planet == "Jupiter" and rashi in ["Sagittarius", "Pisces"]:
        interpretation += f"Jupiter in own sign ({rashi}) - Very strong. Excellent wisdom and fortune."
    
    return {
        "planet": planet,
        "sign": rashi,
        "sign_meaning": sign_meaning,
        "interpretation": interpretation.strip()
    }


def interpret_planet_relations(planet: str, aspects: List[Dict], conjunctions: List[Dict]) -> Dict:
    """
    Phase 18: Interpret planetary relationships (aspects and conjunctions).
    
    Args:
        planet: Planet name
        aspects: List of aspects received
        conjunctions: List of conjunctions
    
    Returns:
        Interpretation dictionary
    """
    interpretation = f"""
{planet} Planetary Relationships:

"""
    
    # Aspects
    if aspects:
        interpretation += "Aspects Received:\n"
        for aspect in aspects:
            aspecting_planet = aspect.get("planet", "Unknown")
            aspect_type = aspect.get("type", "general")
            interpretation += f"• {aspecting_planet} aspects {planet} ({aspect_type} aspect)\n"
    
    # Conjunctions
    if conjunctions:
        interpretation += "\nConjunctions:\n"
        for conj in conjunctions:
            other_planet = conj.get("planet", "Unknown")
            distance = conj.get("distance", 0)
            interpretation += f"• {planet} conjunct {other_planet} (within {distance:.1f}°)\n"
    
    # Benefic/Malefic effects
    benefics = ["Jupiter", "Venus", "Mercury"]
    malefics = ["Saturn", "Mars", "Rahu", "Ketu"]
    
    benefic_aspects = [a for a in aspects if a.get("planet") in benefics]
    malefic_aspects = [a for a in aspects if a.get("planet") in malefics]
    
    if benefic_aspects:
        interpretation += f"\nPositive: Benefic planets aspecting {planet} bring favorable influences."
    
    if malefic_aspects:
        interpretation += f"\nChallenges: Malefic planets aspecting {planet} may create obstacles."
    
    return {
        "planet": planet,
        "aspects": aspects,
        "conjunctions": conjunctions,
        "benefic_aspects": len(benefic_aspects),
        "malefic_aspects": len(malefic_aspects),
        "interpretation": interpretation.strip()
    }


def interpret_combustion(planet: str, sun_distance: float) -> Dict:
    """
    Phase 18: Interpret planetary combustion.
    
    Args:
        planet: Planet name
        sun_distance: Distance from Sun in degrees
    
    Returns:
        Interpretation dictionary
    """
    # Combustion limits (degrees from Sun)
    combustion_limits = {
        "Mercury": 14,
        "Venus": 10,
        "Mars": 17,
        "Jupiter": 11,
        "Saturn": 15
    }
    
    limit = combustion_limits.get(planet, 10)
    is_combust = abs(sun_distance) < limit
    
    if not is_combust:
        return {
            "planet": planet,
            "is_combust": False,
            "interpretation": f"{planet} is not combust. Planet functions normally."
        }
    
    interpretation = f"""
{planet} is Combust (within {limit}° of Sun):

Effect:
Combustion weakens {planet}'s natural significations. The planet's energy is overshadowed by the Sun's powerful influence.

Impact:
• {planet}'s karakatva (natural significations) are reduced
• Planet struggles to express its positive qualities
• Results related to {planet} may be delayed or weakened

Remedies:
• Chant {planet} mantras
• Perform {planet} remedies
• Wear gemstone for {planet} (if recommended by astrologer)
"""
    
    return {
        "planet": planet,
        "is_combust": True,
        "sun_distance": sun_distance,
        "interpretation": interpretation.strip(),
        "severity": "high" if abs(sun_distance) < limit * 0.5 else "medium"
    }


def interpret_retrograde(planet: str, is_retrograde: bool) -> Dict:
    """
    Phase 18: Interpret retrograde planets.
    
    Args:
        planet: Planet name
        is_retrograde: Whether planet is retrograde
    
    Returns:
        Interpretation dictionary
    """
    if not is_retrograde:
        return {
            "planet": planet,
            "is_retrograde": False,
            "interpretation": f"{planet} is direct. Planet functions normally."
        }
    
    retrograde_effects = {
        "Mercury": "Mercury retrograde affects communication, travel, and technology. Review and reflect rather than starting new projects.",
        "Venus": "Venus retrograde affects relationships, finances, and creativity. Re-evaluate relationships and financial matters.",
        "Mars": "Mars retrograde affects energy, action, and conflicts. Control anger and avoid hasty decisions.",
        "Jupiter": "Jupiter retrograde affects wisdom, growth, and fortune. Internal growth and reflection are emphasized.",
        "Saturn": "Saturn retrograde affects discipline, delays, and karma. Past karmas come to fruition. Patience required.",
        "Rahu": "Rahu retrograde affects desires and material pursuits. Re-evaluate goals and ambitions.",
        "Ketu": "Ketu retrograde affects spirituality and detachment. Deep spiritual introspection is indicated."
    }
    
    effect = retrograde_effects.get(planet, f"{planet} retrograde brings internal reflection and review.")
    
    interpretation = f"""
{planet} is Retrograde:

Effect:
Retrograde motion brings internalization and review. The planet's energy turns inward.

Impact:
{effect}

Positive Aspects:
• Opportunity for reflection and review
• Internal growth and understanding
• Re-evaluation of related life areas

Challenges:
• Delays in planet-related matters
• Need for patience and introspection
• Revisiting past issues

Remedies:
• Chant {planet} mantras
• Practice patience and reflection
• Avoid forcing outcomes
"""
    
    return {
        "planet": planet,
        "is_retrograde": True,
        "interpretation": interpretation.strip(),
        "effect": effect
    }

