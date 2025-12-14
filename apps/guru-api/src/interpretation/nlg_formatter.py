"""
Phase 18: Natural Language Formatter

Formats interpretation data into readable natural language reports.
"""

from typing import Dict, List


def format_planet_section(planet_name: str, details: Dict) -> str:
    """
    Phase 18: Format planet interpretation section.
    
    Args:
        planet_name: Planet name
        details: Planet interpretation details
    
    Returns:
        Formatted text
    """
    text = f"""
═══════════════════════════════════════════════════════════
{planet_name.upper()} ANALYSIS
═══════════════════════════════════════════════════════════

{details.get('overall', 'Planet analysis')}

{details.get('house_interpretation', '')}

{details.get('sign_interpretation', '')}
"""
    
    # Add combustion info
    combustion = details.get('combustion', {})
    if combustion.get('is_combust'):
        text += f"\n{combustion.get('interpretation', '')}\n"
    
    # Add retrograde info
    retrograde = details.get('retrograde', {})
    if retrograde.get('is_retrograde'):
        text += f"\n{retrograde.get('interpretation', '')}\n"
    
    return text.strip()


def format_house_section(house_number: int, details: Dict) -> str:
    """
    Phase 18: Format house interpretation section.
    
    Args:
        house_number: House number
        details: House interpretation details
    
    Returns:
        Formatted text
    """
    text = f"""
═══════════════════════════════════════════════════════════
{house_number}TH HOUSE ({details.get('house_name', 'House').upper()})
═══════════════════════════════════════════════════════════

{details.get('interpretation', 'House analysis')}
"""
    
    return text.strip()


def format_yoga_section(yogas: Dict) -> str:
    """
    Phase 18: Format yoga section.
    
    Args:
        yogas: Yoga interpretation dictionary
    
    Returns:
        Formatted text
    """
    summary = yogas.get('summary', {})
    detailed = yogas.get('detailed', [])
    
    text = f"""
═══════════════════════════════════════════════════════════
YOGA ANALYSIS
═══════════════════════════════════════════════════════════

{summary.get('summary', 'Yoga analysis')}

Detailed Yogas:
"""
    
    for yoga_detail in detailed[:5]:  # Top 5 yogas
        text += f"\n{yoga_detail.get('explanation', '')}\n"
        text += "---\n"
    
    return text.strip()


def format_dasha_section(dasha_info: Dict) -> str:
    """
    Phase 18: Format Dasha section.
    
    Args:
        dasha_info: Dasha interpretation dictionary
    
    Returns:
        Formatted text
    """
    text = """
═══════════════════════════════════════════════════════════
DASHA ANALYSIS
═══════════════════════════════════════════════════════════

"""
    
    current_maha = dasha_info.get('current_mahadasha', {})
    if current_maha:
        text += f"{current_maha.get('interpretation', '')}\n\n"
    
    current_antara = dasha_info.get('current_antardasha', {})
    if current_antara:
        text += f"{current_antara.get('interpretation', '')}\n\n"
    
    predictions = dasha_info.get('predictions', {})
    if predictions:
        text += "Upcoming Dasha Periods:\n"
        for pred in predictions.get('upcoming_periods', [])[:3]:
            text += f"\n• {pred.get('period', 'N/A')} - {pred.get('start_date', 'N/A')}\n"
            text += f"  {pred.get('prediction', '')[:200]}...\n"
    
    return text.strip()


def format_life_theme_section(theme_name: str, theme_info: Dict) -> str:
    """
    Phase 18: Format life theme section.
    
    Args:
        theme_name: Theme name (career, relationships, etc.)
        theme_info: Theme analysis dictionary
    
    Returns:
        Formatted text
    """
    text = f"""
═══════════════════════════════════════════════════════════
{theme_name.upper()} ANALYSIS
═══════════════════════════════════════════════════════════

{theme_info.get('analysis', 'Analysis not available')}
"""
    
    return text.strip()


def format_remedies(remedy_list: Dict) -> str:
    """
    Phase 18: Format remedies section.
    
    Args:
        remedy_list: Remedies dictionary
    
    Returns:
        Formatted text
    """
    text = """
═══════════════════════════════════════════════════════════
REMEDIES & RECOMMENDATIONS
═══════════════════════════════════════════════════════════

"""
    
    # Gemstones
    gemstones = remedy_list.get('gemstones', [])
    if gemstones:
        text += "GEMSTONES:\n"
        for gem in gemstones:
            text += f"• {gem.get('planet', 'N/A')}: {gem.get('gemstone', 'N/A')} - {gem.get('note', '')}\n"
        text += "\n"
    
    # Mantras
    mantras = remedy_list.get('mantras', [])
    if mantras:
        text += "MANTRAS:\n"
        for mantra in mantras:
            text += f"• {mantra.get('planet', 'N/A')}: {mantra.get('mantra', 'N/A')} - {mantra.get('note', '')}\n"
        text += "\n"
    
    # Pujas
    pujas = remedy_list.get('pujas', [])
    if pujas:
        text += "PUJAS:\n"
        for puja in pujas:
            text += f"• {puja.get('planet', 'N/A')}: {puja.get('puja', 'N/A')}\n"
        text += "\n"
    
    # Habits
    habits = remedy_list.get('habits', [])
    if habits:
        text += "DAILY HABITS:\n"
        for habit in habits:
            text += f"• {habit.get('habit', 'N/A')}: {habit.get('frequency', 'N/A')} - {habit.get('benefit', '')}\n"
        text += "\n"
    
    # General
    general = remedy_list.get('general', [])
    if general:
        text += "GENERAL REMEDIES:\n"
        for gen in general:
            text += f"• {gen.get('type', 'N/A')}: {gen.get('remedy', 'N/A')}\n"
    
    text += "\nNote: Consult a qualified Vedic Astrologer before implementing remedies.\n"
    
    return text.strip()


def generate_final_text_report(interpretation: Dict) -> str:
    """
    Phase 18: Generate complete natural language report.
    
    Args:
        interpretation: Complete interpretation dictionary
    
    Returns:
        Full text report
    """
    report = """
╔═══════════════════════════════════════════════════════════╗
║         COMPLETE VEDIC ASTROLOGY INTERPRETATION           ║
║                  JYOTISH READING REPORT                    ║
╚═══════════════════════════════════════════════════════════╝

"""
    
    # Summary
    report += f"{interpretation.get('summary', '')}\n\n"
    
    # Planets
    planets = interpretation.get('planets', {})
    if planets:
        report += "\n" + "="*60 + "\n"
        report += "PLANETARY ANALYSIS\n"
        report += "="*60 + "\n"
        for planet_name, planet_data in planets.items():
            report += format_planet_section(planet_name, planet_data) + "\n\n"
    
    # Houses
    houses = interpretation.get('houses', {})
    if houses:
        report += "\n" + "="*60 + "\n"
        report += "HOUSE ANALYSIS\n"
        report += "="*60 + "\n"
        for house_num in sorted(houses.keys()):
            report += format_house_section(house_num, houses[house_num]) + "\n\n"
    
    # Yogas
    yogas = interpretation.get('yogas', {})
    if yogas:
        report += format_yoga_section(yogas) + "\n\n"
    
    # Dasha
    dasha = interpretation.get('dasha', {})
    if dasha:
        report += format_dasha_section(dasha) + "\n\n"
    
    # Life Themes
    life_themes = interpretation.get('life_themes', {})
    if life_themes:
        report += "\n" + "="*60 + "\n"
        report += "LIFE THEMES ANALYSIS\n"
        report += "="*60 + "\n"
        
        theme_names = {
            'career': 'Career & Profession',
            'relationships': 'Relationships & Marriage',
            'finances': 'Finances & Wealth',
            'health': 'Health',
            'spirituality': 'Spirituality',
            'family': 'Family',
            'children': 'Children',
            'property': 'Property & Assets',
            'education': 'Education'
        }
        
        for theme_key, theme_display in theme_names.items():
            if theme_key in life_themes:
                report += format_life_theme_section(theme_display, life_themes[theme_key]) + "\n\n"
    
    # Remedies
    remedies = interpretation.get('remedies', {})
    if remedies:
        report += format_remedies(remedies) + "\n\n"
    
    # Closing
    report += """
╔═══════════════════════════════════════════════════════════╗
║                    END OF REPORT                          ║
║                                                           ║
║  This interpretation is based on classical Vedic         ║
║  Astrology principles. For personalized guidance,        ║
║  consult a qualified Vedic Astrologer.                    ║
╚═══════════════════════════════════════════════════════════╝
"""
    
    return report.strip()

