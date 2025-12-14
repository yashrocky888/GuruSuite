"""
Phase 20: NLG for Muhurtha

Formats Muhurtha JSON into Guru-style guidance.
"""

from typing import Dict


def format_muhurtha(muhurtha_data: Dict) -> str:
    """
    Phase 20: Format Muhurtha data into human-readable text.
    
    Args:
        muhurtha_data: Muhurtha analysis dictionary
    
    Returns:
        Formatted text
    """
    task = muhurtha_data.get("task", "activity")
    date = muhurtha_data.get("date", "")
    overall_score = muhurtha_data.get("overall_score", 0)
    overall_recommendation = muhurtha_data.get("overall_recommendation", "")
    best_windows = muhurtha_data.get("best_windows", [])
    avoid_windows = muhurtha_data.get("avoid_windows", [])
    panchanga = muhurtha_data.get("panchanga", {})
    final_advice = muhurtha_data.get("final_advice", "")
    warnings = muhurtha_data.get("warnings", [])
    
    text = f"🌟 Guru's Muhurtha Guidance for {task.replace('_', ' ').title()} 🌟\n\n"
    text += f"Date: {date}\n\n"
    
    text += f"Overall Assessment: {overall_recommendation}\n"
    text += f"Score: {overall_score}/10\n\n"
    
    # Panchanga summary
    if panchanga:
        text += "Today's Panchanga:\n"
        text += f"• Tithi: {panchanga.get('tithi', 'N/A')}\n"
        text += f"• Nakshatra: {panchanga.get('nakshatra', 'N/A')}\n"
        text += f"• Yoga: {panchanga.get('yoga', 'N/A')}\n"
        text += f"• Karana: {panchanga.get('karana', 'N/A')}\n\n"
    
    # Best windows
    if best_windows:
        text += "✨ Best Time Windows:\n\n"
        for i, window in enumerate(best_windows, 1):
            start = window.get("start", "")
            end = window.get("end", "")
            score = window.get("score", 0)
            reason = window.get("reason", "")
            chog = window.get("choghadiya", "")
            
            text += f"{i}. {start} to {end} (Score: {score}/10)\n"
            text += f"   Choghadiya: {chog}\n"
            text += f"   Reason: {reason}\n\n"
    else:
        text += "⚠️ No highly favorable windows identified for this date.\n\n"
    
    # Avoid windows
    if avoid_windows:
        text += "❌ Avoid These Periods:\n\n"
        for window in avoid_windows[:5]:  # Top 5
            start = window.get("start", "")
            end = window.get("end", "")
            reason = window.get("reason", "")
            
            text += f"• {start} to {end}: {reason}\n"
        text += "\n"
    
    # Warnings
    if warnings:
        text += "⚠️ Warnings:\n"
        for warning in warnings:
            text += f"• {warning}\n"
        text += "\n"
    
    # Final advice
    if final_advice:
        text += f"Guru's Final Guidance:\n{final_advice}\n\n"
    
    text += "May you choose the most auspicious moment for your activity. 🙏"
    
    return text

