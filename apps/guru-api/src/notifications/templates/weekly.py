"""
Phase 12: Weekly Notification Templates

Templates for weekly summary messages.
"""

from typing import Dict, List


def weekly_summary(weekly_data: Dict, language: str = "english") -> str:
    """
    Phase 12: Generate weekly summary message template.
    
    Args:
        weekly_data: Weekly prediction data
        language: Language code
    
    Returns:
        Weekly summary message string
    """
    avg_score = weekly_data.get("average_score", 70)
    highlights = weekly_data.get("highlights", [])
    upcoming_events = weekly_data.get("upcoming_events", [])
    
    if language == "hindi":
        return f"""
📅 साप्ताहिक सारांश 📅

सप्ताह का औसत स्कोर: {int(avg_score)}/100

मुख्य बिंदु:
{chr(10).join('• ' + item for item in highlights[:5])}

आगामी घटनाएं:
{chr(10).join('• ' + item for item in upcoming_events[:3])}
"""
    elif language == "kannada":
        return f"""
📅 ವಾರದ ಸಾರಾಂಶ 📅

ವಾರದ ಸರಾಸರಿ ಸ್ಕೋರ್: {int(avg_score)}/100

ಮುಖ್ಯ ಅಂಶಗಳು:
{chr(10).join('• ' + item for item in highlights[:5])}

ಮುಂಬರುವ ಘಟನೆಗಳು:
{chr(10).join('• ' + item for item in upcoming_events[:3])}
"""
    else:  # english
        return f"""
📅 Weekly Summary 📅

Week's Average Score: {int(avg_score)}/100

Highlights:
{chr(10).join('• ' + item for item in highlights[:5])}

Upcoming Events:
{chr(10).join('• ' + item for item in upcoming_events[:3])}
"""

