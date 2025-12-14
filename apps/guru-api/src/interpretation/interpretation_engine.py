"""
Phase 18: Interpretation Engine (Orchestrator)

Orchestrates all interpretation modules to generate complete Jyotish reading.
"""

from typing import Dict, List
from src.interpretation.planet_interpreter import (
    interpret_planet_in_house,
    interpret_planet_in_sign,
    interpret_planet_relations,
    interpret_combustion,
    interpret_retrograde
)
from src.interpretation.house_interpreter import interpret_house
from src.interpretation.yoga_interpreter import summarize_yogas, explain_individual_yoga
from src.interpretation.dasha_interpreter import interpret_mahadasha, interpret_antardasha, generate_dasha_predictions
from src.interpretation.transit_interpreter import interpret_transit, identify_good_bad_transits, blend_transit_with_dasha
from src.interpretation.life_themes import (
    analyze_career, analyze_relationships, analyze_finances,
    analyze_health, analyze_spirituality, analyze_family,
    analyze_children, analyze_property, analyze_education
)
from src.interpretation.remedies import generate_remedies, recommend_gemstones, recommend_mantras, recommend_pujas, recommend_habits
from src.jyotish.panchang import get_nakshatra


def generate_full_interpretation(kundli: Dict) -> Dict:
    """
    Phase 18: Generate complete Jyotish interpretation.
    
    This is the main orchestrator that combines all interpretation modules.
    
    Args:
        kundli: Complete birth chart dictionary
    
    Returns:
        Complete interpretation dictionary
    """
    interpretation = {
        "planets": {},
        "houses": {},
        "yogas": {},
        "dasha": {},
        "transits": {},
        "life_themes": {},
        "remedies": {},
        "summary": ""
    }
    
    planets = kundli.get("Planets", {})
    houses = kundli.get("Houses", [])
    yogas = kundli.get("yogas", {}).get("detected_yogas", [])
    dasha = kundli.get("dasha", {})
    transits = kundli.get("transits", {})
    
    # 1. Planet-by-planet interpretation
    print("Interpreting planets...")
    for planet_name, planet_data in planets.items():
        if planet_name in ["Rahu", "Ketu"]:
            continue  # Handle separately if needed
        
        house = planet_data.get("house", 0)
        sign = planet_data.get("sign", "Unknown")
        degree = planet_data.get("degree", 0)
        dignity = planet_data.get("dignity", "neutral")
        strength = planet_data.get("strength", 50)
        
        # Get nakshatra
        nakshatra_name, _ = get_nakshatra(degree)
        
        # Interpret planet in house
        planet_house_interp = interpret_planet_in_house(planet_name, house, dignity, strength, nakshatra_name)
        
        # Interpret planet in sign
        planet_sign_interp = interpret_planet_in_sign(planet_name, sign)
        
        # Check combustion (if applicable)
        sun_degree = planets.get("Sun", {}).get("degree", 0)
        if sun_degree:
            sun_distance = abs(degree - sun_degree)
            if sun_distance > 180:
                sun_distance = 360 - sun_distance
            combustion_interp = interpret_combustion(planet_name, sun_distance)
        else:
            combustion_interp = {"is_combust": False}
        
        # Check retrograde
        is_retrograde = planet_data.get("is_retrograde", False)
        retrograde_interp = interpret_retrograde(planet_name, is_retrograde)
        
        interpretation["planets"][planet_name] = {
            "house": house,
            "sign": sign,
            "nakshatra": nakshatra_name,
            "dignity": dignity,
            "strength": strength,
            "house_interpretation": planet_house_interp.get("interpretation", ""),
            "sign_interpretation": planet_sign_interp.get("interpretation", ""),
            "combustion": combustion_interp,
            "retrograde": retrograde_interp,
            "overall": f"{planet_name} in {house}th house ({sign}) - {dignity} - Strength: {strength}/100"
        }
    
    # 2. House-by-house interpretation
    print("Interpreting houses...")
    for house_data in houses:
        house_num = house_data.get("house", 0)
        if house_num == 0:
            continue
        
        lord = house_data.get("lord", "Unknown")
        occupants = [p for p, data in planets.items() if data.get("house") == house_num]
        
        # Get aspects (simplified - would need full aspect calculation)
        aspects_in = []
        aspects_out = []
        
        house_interp = interpret_house(house_num, lord, occupants, aspects_in, aspects_out)
        interpretation["houses"][house_num] = house_interp
    
    # 3. Yoga summary
    print("Interpreting yogas...")
    yoga_summary = summarize_yogas(yogas)
    yoga_details = [explain_individual_yoga(y) for y in yogas[:10]]  # Top 10 yogas
    
    interpretation["yogas"] = {
        "summary": yoga_summary,
        "detailed": yoga_details,
        "total": len(yogas)
    }
    
    # 4. Dasha interpretation
    print("Interpreting dasha...")
    if dasha:
        current_dasha = dasha.get("current_dasha", {})
        dasha_lord = current_dasha.get("dasha_lord", "Unknown")
        antardasha_lord = current_dasha.get("antardasha_lord", "Unknown")
        
        mahadasha_interp = interpret_mahadasha(dasha_lord, kundli, yogas, transits)
        antardasha_interp = interpret_antardasha(dasha_lord, antardasha_lord, kundli)
        
        # Dasha predictions
        dasha_sequence = dasha.get("mahadasha", [])[:5]
        dasha_predictions = generate_dasha_predictions(kundli, dasha_sequence)
        
        interpretation["dasha"] = {
            "current_mahadasha": mahadasha_interp,
            "current_antardasha": antardasha_interp,
            "predictions": dasha_predictions
        }
    
    # 5. Transit interpretation
    print("Interpreting transits...")
    if transits:
        transit_interpretations = {}
        for planet_name, transit_data in transits.items():
            if isinstance(transit_data, dict):
                transit_house = transit_data.get("house", 0)
                if transit_house:
                    transit_interp = interpret_transit(planet_name, transit_house, [], planets)
                    transit_interpretations[planet_name] = transit_interp
        
        good_bad = identify_good_bad_transits(transits, kundli)
        blended = blend_transit_with_dasha(transits, dasha) if dasha else {}
        
        interpretation["transits"] = {
            "individual": transit_interpretations,
            "good_bad": good_bad,
            "blended": blended
        }
    
    # 6. Life themes
    print("Analyzing life themes...")
    interpretation["life_themes"] = {
        "career": analyze_career(kundli),
        "relationships": analyze_relationships(kundli),
        "finances": analyze_finances(kundli),
        "health": analyze_health(kundli),
        "spirituality": analyze_spirituality(kundli),
        "family": analyze_family(kundli),
        "children": analyze_children(kundli),
        "property": analyze_property(kundli),
        "education": analyze_education(kundli)
    }
    
    # 7. Remedies
    print("Generating remedies...")
    # Identify weak planets
    weak_planets = [p for p, data in planets.items() if data.get("strength", 50) < 40]
    weaknesses = [f"{p} weak" for p in weak_planets]
    
    # Check for doshas (simplified)
    doshas = []
    mars_house = planets.get("Mars", {}).get("house", 0)
    if mars_house in [1, 4, 7, 8, 12]:
        doshas.append("Mangal Dosha")
    
    remedies = generate_remedies(kundli, weaknesses, doshas, weak_planets)
    interpretation["remedies"] = remedies
    
    # 8. Generate summary
    print("Generating summary...")
    summary = generate_interpretation_summary(interpretation, kundli)
    interpretation["summary"] = summary
    
    return interpretation


def generate_interpretation_summary(interpretation: Dict, kundli: Dict) -> str:
    """
    Phase 18: Generate overall summary of interpretation.
    
    Args:
        interpretation: Complete interpretation dictionary
        kundli: Birth chart
    
    Returns:
        Summary text
    """
    planets = interpretation.get("planets", {})
    yogas = interpretation.get("yogas", {})
    dasha = interpretation.get("dasha", {})
    life_themes = interpretation.get("life_themes", {})
    
    summary = f"""
COMPLETE JYOTISH INTERPRETATION SUMMARY

Chart Overview:
This is a comprehensive Vedic Astrology interpretation based on your birth chart.

Planetary Analysis:
{len(planets)} planets analyzed with their positions, strengths, and significations.

Yogas Detected:
{yogas.get('total', 0)} yogas found in the chart, including {yogas.get('summary', {}).get('auspicious_count', 0)} highly auspicious combinations.

Dasha Period:
"""
    
    if dasha:
        current = dasha.get("current_mahadasha", {})
        dasha_lord = current.get("planet", "Unknown")
        summary += f"Currently in {dasha_lord} Mahadasha period.\n"
    
    summary += f"""
Life Themes Analyzed:
• Career: {life_themes.get('career', {}).get('analysis', 'N/A')[:100]}...
• Relationships: {life_themes.get('relationships', {}).get('analysis', 'N/A')[:100]}...
• Finances: {life_themes.get('finances', {}).get('analysis', 'N/A')[:100]}...
• Health: {life_themes.get('health', {}).get('analysis', 'N/A')[:100]}...

Remedies:
{len(interpretation.get('remedies', {}).get('gemstones', []))} gemstone recommendations
{len(interpretation.get('remedies', {}).get('mantras', []))} mantra recommendations
{len(interpretation.get('remedies', {}).get('pujas', []))} puja recommendations

This interpretation provides a complete analysis of your birth chart based on classical Vedic Astrology principles.
"""
    
    return summary.strip()

