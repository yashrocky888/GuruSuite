"""
Phase 20: NLG for Monthly Predictions

Formats monthly prediction JSON into Guru-style guidance.
"""

from typing import Dict


def format_monthly(monthly_data: Dict) -> str:
    """
    Phase 20: Format monthly prediction data into human-readable text.
    
    Args:
        monthly_data: Monthly prediction dictionary
    
    Returns:
        Formatted text
    """
    month_name = monthly_data.get("month_name", "")
    year = monthly_data.get("year", "")
    summary = monthly_data.get("summary", "")
    weekly_trends = monthly_data.get("weekly_trends", {})
    areas = monthly_data.get("areas", {})
    important_dates = monthly_data.get("important_dates", {})
    key_transits = monthly_data.get("key_transits", [])
    final_advice = monthly_data.get("final_advice", "")
    
    text = f"🌟 Guru's Monthly Guidance for {month_name} {year} 🌟\n\n"
    
    text += f"Summary:\n{summary}\n\n"
    
    # Weekly trends
    if weekly_trends:
        text += "📅 Week-wise Trends:\n\n"
        for week_key, week_data in weekly_trends.items():
            week_num = week_key.replace("week_", "")
            trend = week_data.get("trend", "")
            description = week_data.get("description", "")
            
            text += f"Week {week_num}: {trend.title()} - {description}\n"
        text += "\n"
    
    # Area-wise predictions
    if areas:
        text += "📊 Area-wise Predictions:\n\n"
        for area_name, area_data in areas.items():
            score = area_data.get("score", 5)
            trend = area_data.get("trend", "stable")
            details = area_data.get("details", "")
            
            emoji = "✅" if trend == "positive" else "⚠️" if trend == "caution" else "➡️"
            text += f"{emoji} {area_name.title()}: Score {score}/10\n"
            text += f"   {details}\n\n"
    
    # Important dates
    if important_dates:
        good_days = important_dates.get("good_days", [])
        bad_days = important_dates.get("bad_days", [])
        major_events = important_dates.get("major_events", [])
        
        if good_days:
            text += "✨ Favorable Days:\n"
            for day in good_days[:5]:
                date = day.get("date", "")
                reason = day.get("reason", "")
                text += f"• {date}: {reason}\n"
            text += "\n"
        
        if bad_days:
            text += "⚠️ Challenging Days:\n"
            for day in bad_days[:5]:
                date = day.get("date", "")
                reason = day.get("reason", "")
                text += f"• {date}: {reason}\n"
            text += "\n"
        
        if major_events:
            text += "🌙 Major Planetary Events:\n"
            for event in major_events[:3]:
                date = event.get("date", "")
                description = event.get("description", "")
                text += f"• {date}: {description}\n"
            text += "\n"
    
    # Key transits
    if key_transits:
        text += "🪐 Key Transits:\n"
        for transit in key_transits[:3]:
            date = transit.get("date", "")
            description = transit.get("description", "")
            text += f"• {date}: {description}\n"
        text += "\n"
    
    # Final advice
    if final_advice:
        text += f"Guru's Monthly Guidance:\n{final_advice}\n\n"
    
    text += "May this month bring you growth, wisdom, and peace. 🙏"
    
    return text

