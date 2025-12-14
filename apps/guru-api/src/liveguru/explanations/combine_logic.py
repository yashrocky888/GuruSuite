"""
Phase 16: Combined Logic Explanation

Combines all factors (Panchang, Daily, Dasha, Transits) for comprehensive interpretation.
"""

from typing import Dict
from src.jyotish.panchang import get_nakshatra


# Phase 16: Tithi meanings
TITHI_MEANINGS = {
    1: "Pratipada - New beginnings, starting fresh",
    2: "Dwitiya - Partnership, duality, balance",
    3: "Tritiya - Creativity, expression",
    4: "Chaturthi - Obstacles, challenges, Ganesha",
    5: "Panchami - Learning, knowledge, Saraswati",
    6: "Shashthi - Health, healing, Kartikeya",
    7: "Saptami - Completion, fulfillment",
    8: "Ashtami - Transformation, Durga",
    9: "Navami - Victory, success",
    10: "Dashami - Achievement, completion",
    11: "Ekadashi - Spiritual, fasting, Vishnu",
    12: "Dwadashi - Devotion, worship",
    13: "Trayodashi - Shiva, transformation",
    14: "Chaturdashi - Preparation, anticipation",
    15: "Purnima/Amavasya - Full/New Moon - Powerful day"
}


def combine_explanations(context: Dict) -> str:
    """
    Phase 16: Combine all astrological factors for comprehensive explanation.
    
    Args:
        context: Complete astrological context dictionary
    
    Returns:
        Combined explanation
    """
    panchang = context.get("panchang", {})
    daily = context.get("daily", {})
    dasha = context.get("dasha", {})
    kundli = context.get("kundli", {})
    
    explanation = """
═══════════════════════════════════════════════════════════
🌟 GURU'S COMPREHENSIVE DAILY ANALYSIS 🌟
═══════════════════════════════════════════════════════════

"""
    
    # Panchang Analysis
    if panchang:
        tithi = panchang.get("tithi", {})
        nakshatra = panchang.get("nakshatra", {})
        yoga = panchang.get("yoga", {})
        karana = panchang.get("karana", {})
        vaar = panchang.get("vaar", "Unknown")
        
        tithi_num = tithi.get("number", 0)
        tithi_name = tithi.get("name", "Unknown")
        tithi_meaning = TITHI_MEANINGS.get(tithi_num, "Tithi influence active")
        
        nakshatra_name = nakshatra.get("name", "Unknown")
        
        explanation += f"""
📅 TODAY'S PANCHANG (Five Elements):

Tithi (Lunar Day): {tithi_name}
• Meaning: {tithi_meaning}
• Influence: This lunar day shapes the overall energy of today

Nakshatra (Lunar Mansion): {nakshatra_name}
• Current Moon is in {nakshatra_name}
• This nakshatra's energy influences your emotions and actions today

Yoga: {yoga.get('name', 'Unknown')}
• The combination of Sun and Moon creates this Yoga
• This affects the overall harmony of the day

Karana: {karana.get('name', 'Unknown')}
• Half of the Tithi - affects specific activities

Vaar (Day): {vaar}
• Each day has a ruling planet with specific energy

"""
    
    # Daily Energy Analysis
    if daily:
        daily_strength = daily.get("daily_strength", {})
        score = daily_strength.get("score", 0)
        summary = daily_strength.get("summary", "Daily energy analysis available")
        
        explanation += f"""
⚡ DAILY ENERGY ANALYSIS:

Overall Score: {score}/100

Summary:
{summary}

Energy Interpretation:
"""
        
        if score >= 80:
            explanation += """
• Excellent day - High positive energy
• Favorable for important activities
• Success is more likely
• Good time for new beginnings
"""
        elif score >= 60:
            explanation += """
• Good day - Positive energy
• Favorable for most activities
• Some challenges may arise but manageable
• Balanced approach recommended
"""
        elif score >= 40:
            explanation += """
• Moderate day - Mixed energy
• Some positive and some challenging aspects
• Be cautious with important decisions
• Patience and care are advised
"""
        else:
            explanation += """
• Challenging day - Lower energy
• Be extra careful with decisions
• Focus on inner work and reflection
• Remedies and prayers may be helpful
"""
        
        # Lucky elements
        moon_data = daily_strength.get("moon", {})
        lucky_color = moon_data.get("lucky_color", "N/A")
        
        explanation += f"""
Lucky Elements:
• Lucky Color: {lucky_color}
• Wear or use this color to enhance positive energy
"""
    
    # Combined Interpretation
    explanation += """
═══════════════════════════════════════════════════════════
🎯 WHY THIS DAY AFFECTS YOU SPECIALLY:
═══════════════════════════════════════════════════════════

The combination of:
"""
    
    if panchang and dasha:
        explanation += """
• Today's Panchang (Tithi, Nakshatra, Yoga)
• Your current Dasha period
• Planetary transits
• Your natal chart placements

Creates a unique energy pattern that is specific to YOU today.

"""
    
    # Specific Guidance
    explanation += """
═══════════════════════════════════════════════════════════
💡 GURU'S GUIDANCE FOR TODAY:
═══════════════════════════════════════════════════════════

FOCUS ON:
"""
    
    if daily:
        score = daily.get("daily_strength", {}).get("score", 50)
        if score >= 70:
            explanation += """
• Taking action on important matters
• Starting new projects or initiatives
• Making decisions with confidence
• Engaging in positive activities
• Building relationships and connections
"""
        else:
            explanation += """
• Inner reflection and contemplation
• Completing pending tasks
• Being patient and observant
• Avoiding hasty decisions
• Taking care of health and well-being
"""
    
    explanation += """

AVOID:
"""
    
    if daily:
        score = daily.get("daily_strength", {}).get("score", 50)
        if score < 60:
            explanation += """
• Making major decisions without careful thought
• Starting new ventures impulsively
• Engaging in conflicts or arguments
• Taking unnecessary risks
• Ignoring your intuition
"""
        else:
            explanation += """
• Overconfidence or arrogance
• Neglecting important details
• Being too hasty in actions
• Ignoring others' perspectives
"""
    
    explanation += """

WHAT WILL GROW:
"""
    
    # Based on Dasha and transits
    if dasha:
        dasha_lord = dasha.get("current_dasha", {}).get("dasha_lord", "")
        if dasha_lord == "Jupiter":
            explanation += """
• Wisdom and knowledge
• Relationships and partnerships
• Spiritual growth
• Educational pursuits
"""
        elif dasha_lord == "Venus":
            explanation += """
• Love and relationships
• Creative pursuits
• Beauty and aesthetics
• Material comforts
"""
        elif dasha_lord == "Mars":
            explanation += """
• Energy and action
• Courage and determination
• New initiatives
• Physical activities
"""
        else:
            explanation += """
• Areas related to your current Dasha lord
• Activities aligned with planetary energies
• Opportunities that come naturally
"""
    
    explanation += """

WHAT WILL BE CHALLENGING:
"""
    
    if daily:
        score = daily.get("daily_strength", {}).get("score", 50)
        if score < 50:
            explanation += """
• Delays and obstacles may arise
• Patience will be tested
• Some plans may need adjustment
• Emotional balance may be needed
"""
        else:
            explanation += """
• Minor challenges may appear
• Stay focused and adaptable
• Don't let small issues distract you
"""
    
    explanation += """

═══════════════════════════════════════════════════════════
🙏 REMEDIES IF NEEDED:
═══════════════════════════════════════════════════════════

If today feels challenging:
• Chant your Ishta Devata's name
• Light a lamp (diya) in the morning
• Donate to those in need
• Practice gratitude
• Be kind to yourself and others
• Meditate or pray for clarity

Remember: Every day brings lessons and opportunities for growth.

═══════════════════════════════════════════════════════════
"""
    
    return explanation

