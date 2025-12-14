"""
Phase 15-16: AI Templates for Live Guru Messages

Enhanced templates with karakatva, nakshatra, dasha, and transit information.
"""

from typing import Dict
from src.liveguru.explanations.karakatva import get_karakatva
from src.liveguru.explanations.nakshatra_details import get_nakshatra_details
from src.liveguru.explanations.dasha_logic import explain_dasha
from src.liveguru.explanations.transit_logic import explain_transit


def build_ai_prompt(context: Dict, message_type: str) -> str:
    """
    Phase 16: Build enhanced AI prompt with all astrological details.
    
    Args:
        context: Complete astrological context
        message_type: Type of message
    
    Returns:
        Comprehensive AI prompt
    """
    kundli = context.get("kundli", {})
    dasha = context.get("dasha", {})
    panchang = context.get("panchang", {})
    daily = context.get("daily", {})
    transits = context.get("transits", {})
    
    prompt = f"""
You are a highly knowledgeable Vedic Astrology Guru with deep understanding of Parashara, Jaimini, and traditional Jyotish Shastra.

Generate a {message_type} message with ULTRA-DETAILED astrological explanations.

ASTROLOGICAL CONTEXT:

"""
    
    # Planetary Karakatva
    prompt += "\nPLANETARY KARAKATVA (Natural Significations):\n"
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if planet_name in kundli.get("Planets", {}):
            karakatva = get_karakatva(planet_name)
            primary = ", ".join(karakatva.get("primary", []))
            prompt += f"{planet_name}: {primary}\n"
    
    # Nakshatra Details
    if panchang:
        nakshatra = panchang.get("nakshatra", {})
        nakshatra_name = nakshatra.get("name", "Unknown")
        nak_details = get_nakshatra_details(nakshatra_name)
        
        prompt += f"""
NAKSHATRA INSIGHT:
Current Nakshatra: {nakshatra_name}
Symbol: {nak_details.get('symbol', 'N/A')}
Lord: {nak_details.get('lord', 'N/A')}
Qualities: {nak_details.get('qualities', 'N/A')}
Shastra Meaning: {nak_details.get('shastra_meaning', 'N/A')}
"""
    
    # Dasha Influence
    if dasha:
        dasha_explanation = explain_dasha(dasha)
        prompt += f"\nDASHA INFLUENCE:\n{dasha_explanation}\n"
    
    # Transit Impact
    if transits and kundli:
        transit_explanation = explain_transit(transits, kundli)
        prompt += f"\nTRANSIT IMPACT:\n{transit_explanation}\n"
    
    # Daily Energy
    if daily:
        daily_strength = daily.get("daily_strength", {})
        prompt += f"""
DAILY ENERGY:
Score: {daily_strength.get('score', 0)}/100
Summary: {daily_strength.get('summary', 'N/A')}
"""
    
    # Instructions
    prompt += f"""
YOUR TASK:

Create a {message_type} message that includes:

1. PLANETARY KARAKATVA EXPLANATION:
   - Explain what each key planet represents naturally
   - How their karakatva affects today

2. NAKSHATRA DEEP INTERPRETATION:
   - Symbol and its meaning
   - Lord's influence
   - Guna (Deva/Manushya/Rakshasa) impact
   - Positive qualities and shadow aspects
   - Shastra-level meaning

3. TRANSIT EXPLANATION:
   - Why Moon in this Nakshatra affects the user
   - How current transits compare to natal placements
   - Specific transit influences

4. DASHA/BHUKTI INFLUENCE:
   - Why this day is shaped by current Dasha
   - What events are supported or blocked
   - Dasha timing and effects

5. COMBINED INTERPRETATION:
   - Compare today's transits + Panchang energies
   - With user's birth chart
   - With their Dasha
   - Produce PRO ASTROLOGER LEVEL prediction

6. GURU TONE:
   - Clear and understandable
   - Friendly and compassionate
   - Deep and meaningful
   - Human and relatable
   - Wise and practical

7. SPECIFIC GUIDANCE:
   - What to focus on today
   - What to avoid
   - What will grow
   - What will be challenging
   - Remedies if needed

Keep the message comprehensive but not overwhelming (800-1200 words ideal).
Be specific, actionable, and deeply astrological.
"""
    
    return prompt

