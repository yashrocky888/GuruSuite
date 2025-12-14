"""
Phase 20: NLG for Yearly Predictions

Formats yearly prediction JSON into Guru-style guidance.
"""

from typing import Dict


def format_yearly(yearly_data: Dict) -> str:
    """
    Phase 20: Format yearly prediction data into human-readable text.
    
    Args:
        yearly_data: Yearly prediction dictionary
    
    Returns:
        Formatted text
    """
    year = yearly_data.get("year", "")
    summary = yearly_data.get("summary", "")
    themes = yearly_data.get("themes", {})
    major_events = yearly_data.get("major_events", [])
    good_periods = yearly_data.get("good_periods", [])
    bad_periods = yearly_data.get("bad_periods", [])
    final_advice = yearly_data.get("final_advice", "")
    solar_return = yearly_data.get("solar_return", "")
    
    text = f"🌟 Guru's Yearly Guidance for {year} 🌟\n\n"
    
    text += f"Year Summary:\n{summary}\n\n"
    
    # Themes
    if themes:
        text += "📊 Life Area Themes:\n\n"
        for area_name, theme_text in themes.items():
            text += f"• {area_name.title()}: {theme_text}\n"
        text += "\n"
    
    # Major events
    if major_events:
        text += "🌙 Major Planetary Events:\n\n"
        for event in major_events[:5]:
            date = event.get("date", "")
            description = event.get("description", "")
            impact = event.get("impact", "")
            
            text += f"• {date}: {description}\n"
            text += f"  Impact: {impact}\n\n"
    
    # Good periods
    if good_periods:
        text += "✨ Favorable Periods:\n\n"
        for period in good_periods[:5]:
            start = period.get("start", "")
            end = period.get("end", "")
            description = period.get("description", "")
            areas = period.get("areas", [])
            
            text += f"• {start} to {end}\n"
            text += f"  {description}\n"
            if areas:
                text += f"  Focus areas: {', '.join(areas)}\n"
            text += "\n"
    
    # Bad periods
    if bad_periods:
        text += "⚠️ Challenging Periods:\n\n"
        for period in bad_periods[:5]:
            start = period.get("start", "")
            end = period.get("end", "")
            description = period.get("description", "")
            advice = period.get("advice", "")
            
            text += f"• {start} to {end}\n"
            text += f"  {description}\n"
            if advice:
                text += f"  Guidance: {advice}\n"
            text += "\n"
    
    # Solar return
    if solar_return:
        text += f"📅 Solar Return Analysis:\n{solar_return}\n\n"
    
    # Final advice
    if final_advice:
        text += f"Guru's Yearly Guidance:\n{final_advice}\n\n"
    
    text += "May this year bring you fulfillment, growth, and spiritual progress. 🙏"
    
    return text

