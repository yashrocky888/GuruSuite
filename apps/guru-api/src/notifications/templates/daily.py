"""
Phase 12: Daily Notification Templates

Templates for daily horoscope messages (short and full versions).
"""

from typing import Dict


def daily_short(data: Dict, language: str = "english") -> str:
    """
    Phase 12: Generate short daily message template.
    
    Args:
        data: Daily prediction data
        language: Language code (english, hindi, kannada)
    
    Returns:
        Short daily message string
    """
    daily = data.get("daily", {})
    summary = daily.get("summary", "A day of balanced energies")
    score = daily.get("score", 70)
    rating = daily.get("rating", "Good")
    
    # Get lucky color from moon data if available
    moon_data = data.get("moon", {})
    lucky_color = moon_data.get("lucky_color", "White")
    
    if language == "hindi":
        return f"""
🌅 गुरु का सुबह का संदेश 🌅

सारांश: {summary}
शुभ रंग: {lucky_color}
स्कोर: {int(score)}/100
रेटिंग: {rating}
"""
    elif language == "kannada":
        return f"""
🌅 ಗುರುಗಳ ಬೆಳಿಗ್ಗೆ ಸಂದೇಶ 🌅

ಸಾರಾಂಶ: {summary}
ಅದೃಷ್ಟದ ಬಣ್ಣ: {lucky_color}
ಸ್ಕೋರ್: {int(score)}/100
ರೇಟಿಂಗ್: {rating}
"""
    else:  # english
        return f"""
🌅 Guru's Morning Message 🌅

Summary: {summary}
Lucky Color: {lucky_color}
Score: {int(score)}/100
Rating: {rating}
"""


def daily_full(ai_msg: Dict, language: str = "english") -> str:
    """
    Phase 12: Generate full daily message template.
    
    Args:
        ai_msg: AI-generated prediction dictionary
        language: Language code
    
    Returns:
        Full daily message string
    """
    summary = ai_msg.get("summary", "A day of balanced energies")
    lucky_color = ai_msg.get("lucky_color", "White")
    best_time = ai_msg.get("best_time", "10:00 - 14:00")
    planet_focus = ai_msg.get("planet_in_focus", "Moon")
    energy_rating = ai_msg.get("energy_rating", 70)
    detailed = ai_msg.get("detailed_prediction", "Today brings balanced cosmic energies.")
    morning_msg = ai_msg.get("morning_message", "May this day bring you peace and prosperity.")
    
    what_to_do = ai_msg.get("what_to_do", [])
    what_to_avoid = ai_msg.get("what_to_avoid", [])
    
    if language == "hindi":
        return f"""🌟 आपका विस्तृत दैनिक मार्गदर्शन 🌟

{summary}

शुभ रंग: {lucky_color}
सर्वोत्तम समय: {best_time}
आज का ग्रह: {planet_focus}
ऊर्जा रेटिंग: {energy_rating}/100

क्या करें:
{chr(10).join('• ' + item for item in what_to_do[:3])}

क्या न करें:
{chr(10).join('• ' + item for item in what_to_avoid[:2])}

विस्तृत भविष्यवाणी:
{detailed}

सुबह का संदेश:
{morning_msg}
"""
    elif language == "kannada":
        return f"""🌟 ನಿಮ್ಮ ವಿವರವಾದ ದೈನಂದಿನ ಮಾರ್ಗದರ್ಶನ 🌟

{summary}

ಅದೃಷ್ಟದ ಬಣ್ಣ: {lucky_color}
ಉತ್ತಮ ಸಮಯ: {best_time}
ಇಂದಿನ ಗ್ರಹ: {planet_focus}
ಶಕ್ತಿ ರೇಟಿಂಗ್: {energy_rating}/100

ಏನು ಮಾಡಬೇಕು:
{chr(10).join('• ' + item for item in what_to_do[:3])}

ಏನು ಮಾಡಬಾರದು:
{chr(10).join('• ' + item for item in what_to_avoid[:2])}

ವಿವರವಾದ ಭವಿಷ್ಯ:
{detailed}

ಬೆಳಿಗ್ಗೆ ಸಂದೇಶ:
{morning_msg}
"""
    else:  # english
        return f"""🌟 Your Detailed Daily Guidance 🌟

{summary}

Lucky Color: {lucky_color}
Best Time: {best_time}
Planet in Focus: {planet_focus}
Energy Rating: {energy_rating}/100

What to Do:
{chr(10).join('• ' + item for item in what_to_do[:3])}

What to Avoid:
{chr(10).join('• ' + item for item in what_to_avoid[:2])}

Detailed Prediction:
{detailed}

Morning Message:
{morning_msg}
"""

