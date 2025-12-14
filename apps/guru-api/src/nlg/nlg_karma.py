"""
Phase 20: NLG for Karma Report

Formats karma report JSON into Guru-style guidance.
"""

from typing import Dict


def format_karma(karma_data: Dict) -> str:
    """
    Phase 20: Format karma report data into human-readable text.
    
    Args:
        karma_data: Karma report dictionary
    
    Returns:
        Formatted text
    """
    core_personality = karma_data.get("core_personality", "")
    soul_purpose = karma_data.get("soul_purpose", "")
    karma_lessons = karma_data.get("karma_lessons", [])
    spiritual_direction = karma_data.get("spiritual_direction", "")
    hidden_gifts = karma_data.get("hidden_gifts", [])
    growth_advice = karma_data.get("growth_advice", "")
    human_summary = karma_data.get("human_summary", {})
    life_lessons = karma_data.get("life_lessons", [])
    
    text = "🌟 Guru's Karma & Soul Path Report 🌟\n\n"
    
    text += "This report reveals your soul blueprint, karmic lessons, and life purpose based on your birth chart.\n\n"
    
    # Core personality
    if core_personality:
        text += "👤 Core Personality:\n"
        text += f"{core_personality}\n\n"
    
    # Soul purpose
    if soul_purpose:
        text += "✨ Soul Purpose:\n"
        text += f"{soul_purpose}\n\n"
    
    # Karma lessons
    if karma_lessons:
        text += "📚 Karmic Lessons:\n\n"
        for i, lesson in enumerate(karma_lessons, 1):
            text += f"{i}. {lesson}\n"
        text += "\n"
    
    # Life lessons (detailed)
    if life_lessons:
        text += "🎓 Detailed Life Lessons:\n\n"
        for lesson in life_lessons:
            title = lesson.get("title", "")
            description = lesson.get("description", "")
            advice = lesson.get("advice", "")
            
            text += f"• {title}\n"
            text += f"  {description}\n"
            if advice:
                text += f"  Guidance: {advice}\n"
            text += "\n"
    
    # Spiritual direction
    if spiritual_direction:
        text += "🕉️ Spiritual Direction:\n"
        text += f"{spiritual_direction}\n\n"
    
    # Hidden gifts
    if hidden_gifts:
        text += "🎁 Hidden Gifts:\n\n"
        for i, gift in enumerate(hidden_gifts, 1):
            text += f"{i}. {gift}\n"
        text += "\n"
    
    # Strengths and weaknesses
    if human_summary:
        strengths_text = human_summary.get("strengths_text", "")
        weaknesses_text = human_summary.get("weaknesses_text", "")
        summary = human_summary.get("summary", "")
        
        if strengths_text:
            text += f"{strengths_text}\n\n"
        
        if weaknesses_text:
            text += f"{weaknesses_text}\n\n"
        
        if summary:
            text += f"Summary: {summary}\n\n"
    
    # Growth advice
    if growth_advice:
        text += f"{growth_advice}\n\n"
    
    text += "May this guidance illuminate your path and help you fulfill your dharma. 🙏"
    
    return text

