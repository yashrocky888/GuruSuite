"""
Phase 19: Natural Language Generator for Daily Transit Predictions

Formats transit predictions into human-readable, conversational text.
"""

from typing import Dict


def format_daily_transit_text(json_report: Dict) -> str:
    """
    Phase 19: Format daily transit report into natural language.
    
    Args:
        json_report: Complete daily transit report JSON
    
    Returns:
        Human-readable text report
    """
    date = json_report.get("date", "Today")
    summary = json_report.get("summary", "")
    overall_mood = json_report.get("overall_mood", {})
    areas = json_report.get("areas", {})
    key_transits = json_report.get("key_transits", [])
    danger_flags = json_report.get("danger_flags", [])
    opportunity_windows = json_report.get("opportunity_windows", [])
    actions = json_report.get("actions_today", {})
    
    text = f"""
╔═══════════════════════════════════════════════════════════╗
║         DAILY TRANSIT PREDICTION - {date}                  ║
║              Gochara Shastra Analysis                      ║
╚═══════════════════════════════════════════════════════════╝

"""
    
    # Overall Summary
    text += f"""
OVERALL SUMMARY:

{summary}

Overall Mood: {overall_mood.get('text', 'Balanced day')} (Score: {overall_mood.get('score', 5)}/10)

"""
    
    # Key Transits
    if key_transits:
        text += """
KEY PLANETARY TRANSITS TODAY:

"""
        for transit in key_transits:
            planet = transit.get("planet", "Unknown")
            description = transit.get("description", "")
            effect = transit.get("effect", "moderate")
            
            text += f"• {planet}: {description}\n"
            text += f"  Effect: {effect.title()}\n"
            
            notes = transit.get("notes", [])
            if notes:
                text += f"  Note: {notes[0]}\n"
            text += "\n"
    
    # Area-wise Analysis
    text += """
AREA-WISE GUIDANCE:

"""
    
    area_display_names = {
        "career": "Career & Profession",
        "money": "Finances & Wealth",
        "love": "Relationships & Love",
        "family": "Family & Home",
        "health": "Health & Wellbeing",
        "travel": "Travel & Journeys",
        "spiritual": "Spirituality & Growth"
    }
    
    for area_key, area_data in areas.items():
        area_name = area_display_names.get(area_key, area_key.title())
        score = area_data.get("score", 0)
        trend = area_data.get("trend", "stable")
        details = area_data.get("details", "")
        advice = area_data.get("advice", "")
        
        # Convert score to readable format
        score_display = f"{score:+d}" if score != 0 else "0"
        
        text += f"{area_name}:\n"
        text += f"  Score: {score_display}/10 | Trend: {trend.title()}\n"
        if details:
            text += f"  {details}\n"
        if advice:
            text += f"  Guidance: {advice}\n"
        text += "\n"
    
    # Danger Flags
    if danger_flags:
        text += """
⚠️  CAUTIONS & ALERTS:

"""
        for flag in danger_flags:
            flag_type = flag.get("type", "general").replace("_", " ").title()
            description = flag.get("description", "")
            advice = flag.get("advice", "")
            
            text += f"• {flag_type}: {description}\n"
            if advice:
                text += f"  Advice: {advice}\n"
            text += "\n"
    
    # Opportunity Windows
    if opportunity_windows:
        text += """
⏰ OPPORTUNITY WINDOWS:

"""
        for window in opportunity_windows:
            time_window = window.get("time_window", "general").title()
            description = window.get("description", "")
            
            text += f"• {time_window}: {description}\n"
        text += "\n"
    
    # Actions
    do_list = actions.get("do", [])
    avoid_list = actions.get("avoid", [])
    
    if do_list or avoid_list:
        text += """
📋 ACTIONS FOR TODAY:

"""
        if do_list:
            text += "✅ DO:\n"
            for action in do_list:
                text += f"   • {action}\n"
            text += "\n"
        
        if avoid_list:
            text += "❌ AVOID:\n"
            for action in avoid_list:
                text += f"   • {action}\n"
            text += "\n"
    
    # Closing
    text += """
═══════════════════════════════════════════════════════════

Remember: Planetary transits show the path, but your actions
and karma shape the outcome. Stay positive, practice patience,
and trust in the divine timing.

May the planetary energies guide you to success and peace.

═══════════════════════════════════════════════════════════
"""
    
    return text.strip()


def format_transit_explanation(transit_context: Dict) -> str:
    """
    Phase 19: Format detailed transit explanation.
    
    Args:
        transit_context: Transit context
    
    Returns:
        Detailed explanation text
    """
    current_transits = transit_context.get("current_transits", {})
    moon_specials = transit_context.get("moon_specials", {})
    saturn_specials = transit_context.get("saturn_specials", {})
    jupiter_specials = transit_context.get("jupiter_specials", {})
    current_dasha = transit_context.get("current_dasha", {})
    
    text = """
DETAILED TRANSIT ANALYSIS:

"""
    
    # Moon analysis
    if moon_specials:
        moon_house = moon_specials.get("house_from_natal_moon", 0)
        nakshatra = moon_specials.get("nakshatra", "Unknown")
        tithi = moon_specials.get("tithi", "Unknown")
        
        text += f"""
Moon Transit:
Today, the Moon is moving through {nakshatra} Nakshatra, {moon_house}th house from your natal Moon.
Tithi: {tithi}

"""
        if moon_house == 8:
            text += "Moon in 8th from natal Moon creates emotional sensitivity. Take care of emotional health.\n\n"
        elif moon_house in [1, 5, 9]:
            text += "Moon in trine from natal Moon - favorable emotional state and intuition.\n\n"
    
    # Saturn analysis
    if saturn_specials:
        if saturn_specials.get("sade_sati"):
            text += """
Saturn Transit - Sade Sati:
Saturn is in Sade Sati (12th, 1st, or 2nd from Moon). This is a 7.5-year period of challenges and transformation.
Be patient, practice discipline, and avoid hasty decisions. This period teaches important life lessons.

"""
        if saturn_specials.get("ashtama_shani"):
            text += """
Saturn Transit - Ashtama Shani:
Saturn is in 8th from Moon (Ashtama Shani). This creates mental pressure and obstacles.
Stay calm, avoid conflicts, and focus on inner strength. Remedies and prayers are recommended.

"""
    
    # Jupiter analysis
    if jupiter_specials:
        if jupiter_specials.get("is_trikona"):
            text += """
Jupiter Transit - Guru's Blessings:
Jupiter is in trine house from Moon/Lagna. This brings Guru's blessings, wisdom, and fortune.
Excellent time for learning, teaching, spiritual growth, and seeking guidance.

"""
    
    # Dasha combination
    if current_dasha:
        maha = current_dasha.get("mahadasha", "Unknown")
        antara = current_dasha.get("antardasha", "Unknown")
        
        text += f"""
Dasha Period:
Currently in {maha} Mahadasha - {antara} Antardasha.
The Dasha period shapes the overall life direction, while transits modify daily experiences.

"""
    
    return text.strip()

