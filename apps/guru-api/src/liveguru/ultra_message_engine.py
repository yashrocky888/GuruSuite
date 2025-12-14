"""
Phase 16: Ultra-Detailed Message Engine

Generates comprehensive Guru messages with deep shastra-level explanations.
"""

from typing import Dict
from src.liveguru.explanations.karakatva import format_karakatva_for_message, get_karakatva
from src.liveguru.explanations.nakshatra_details import format_nakshatra_for_message, get_nakshatra_details
from src.liveguru.explanations.dasha_logic import explain_dasha, explain_dasha_timing
from src.liveguru.explanations.transit_logic import explain_transit, explain_planet_transits
from src.liveguru.explanations.combine_logic import combine_explanations


def ultra_explanation(context: Dict, message_type: str = "morning") -> str:
    """
    Phase 16: Generate ultra-detailed Guru explanation.
    
    Args:
        context: Complete astrological context dictionary
        message_type: Type of message (morning, midday, evening, transit)
    
    Returns:
        Comprehensive Guru message with deep explanations
    """
    kundli = context.get("kundli", {})
    dasha = context.get("dasha", {})
    panchang = context.get("panchang", {})
    daily = context.get("daily", {})
    transits = context.get("transits", {})
    
    # Start building the message
    message = f"""
╔═══════════════════════════════════════════════════════════╗
║        🌟 GURU'S ULTRA-DETAILED WISDOM 🌟                 ║
║              {message_type.upper()} MESSAGE                  ║
╚═══════════════════════════════════════════════════════════╝

"""
    
    # Planetary Karakatva Section
    message += """
═══════════════════════════════════════════════════════════
📿 PLANETARY KARAKATVA (Natural Significations)
═══════════════════════════════════════════════════════════

Understanding what each planet naturally represents:

"""
    
    # Key planets for today
    key_planets = ["Sun", "Moon", "Mars", "Jupiter", "Venus", "Saturn"]
    
    for planet_name in key_planets:
        if planet_name in kundli.get("Planets", {}):
            karakatva = get_karakatva(planet_name)
            primary = ", ".join(karakatva.get("primary", [])[:4])
            message += f"• {planet_name:10s} → {primary}\n"
    
    message += "\n"
    
    # Nakshatra Deep Insight
    if panchang:
        nakshatra = panchang.get("nakshatra", {})
        nakshatra_name = nakshatra.get("name", "Unknown")
        nakshatra_num = nakshatra.get("number", 0)
        
        # Calculate pada
        moon_deg = panchang.get("moon", {}).get("degree", 0) if isinstance(panchang.get("moon"), dict) else 0
        if not moon_deg and "Planets" in kundli and "Moon" in kundli["Planets"]:
            moon_deg = kundli["Planets"]["Moon"].get("degree", 0)
        
        # Each nakshatra = 13.333 degrees, each pada = 3.333 degrees
        pada = int((moon_deg % 13.333) / 3.333) + 1 if moon_deg else 1
        
        message += f"""
═══════════════════════════════════════════════════════════
🌙 NAKSHATRA DEEP INSIGHT
═══════════════════════════════════════════════════════════

{format_nakshatra_for_message(nakshatra_name, pada)}

"""
    
    # Dasha Influence
    if dasha:
        message += """
═══════════════════════════════════════════════════════════
⏳ DASHA INFLUENCE
═══════════════════════════════════════════════════════════

"""
        message += explain_dasha(dasha)
        message += explain_dasha_timing(dasha)
        message += "\n"
    
    # Transit Impact
    if transits and kundli:
        message += """
═══════════════════════════════════════════════════════════
🔄 TRANSIT IMPACT
═══════════════════════════════════════════════════════════

"""
        message += explain_transit(transits, kundli)
        message += explain_planet_transits(transits, kundli)
        message += "\n"
    
    # Combined Interpretation
    message += combine_explanations(context)
    
    # Final Guru Blessing
    message += """
╔═══════════════════════════════════════════════════════════╗
║              🙏 GURU'S BLESSING 🙏                        ║
╚═══════════════════════════════════════════════════════════╝

May the planetary energies guide you today.
May you find clarity, peace, and success.
May you grow in wisdom and compassion.

Remember: You are the creator of your destiny.
The planets show the path, but you choose how to walk it.

With love and blessings,
Your Vedic Astrology Guru

╚═══════════════════════════════════════════════════════════╝
"""
    
    return message


def generate_ultra_morning_message(context: Dict) -> str:
    """
    Phase 16: Generate ultra-detailed morning message.
    
    Args:
        context: Astrological context
    
    Returns:
        Morning message
    """
    message = ultra_explanation(context, "morning")
    
    # Add morning-specific guidance
    morning_addon = """
🌅 MORNING-SPECIFIC GUIDANCE:

• Start your day with gratitude
• Set positive intentions
• Use the lucky color if possible
• Begin important tasks during auspicious times
• Be mindful of your energy levels
"""
    
    # Insert before final blessing
    message = message.replace("╔═══════════════════════════════════════════════════════════╗", 
                             morning_addon + "\n╔═══════════════════════════════════════════════════════════╗", 1)
    
    return message


def generate_ultra_midday_message(context: Dict) -> str:
    """
    Phase 16: Generate ultra-detailed midday message.
    
    Args:
        context: Astrological context
    
    Returns:
        Midday message
    """
    message = ultra_explanation(context, "midday")
    
    midday_addon = """
☀️ MIDDAY-SPECIFIC GUIDANCE:

• Review your morning progress
• Adjust plans if needed
• Take breaks to maintain energy
• Focus on important tasks
• Stay balanced and centered
"""
    
    message = message.replace("╔═══════════════════════════════════════════════════════════╗", 
                             midday_addon + "\n╔═══════════════════════════════════════════════════════════╗", 1)
    
    return message


def generate_ultra_evening_message(context: Dict) -> str:
    """
    Phase 16: Generate ultra-detailed evening message.
    
    Args:
        context: Astrological context
    
    Returns:
        Evening message
    """
    message = ultra_explanation(context, "evening")
    
    evening_addon = """
🌙 EVENING-SPECIFIC GUIDANCE:

• Reflect on the day's experiences
• Express gratitude for lessons learned
• Prepare for rest and renewal
• Set intentions for tomorrow
• Practice self-care and relaxation
"""
    
    message = message.replace("╔═══════════════════════════════════════════════════════════╗", 
                             evening_addon + "\n╔═══════════════════════════════════════════════════════════╗", 1)
    
    return message


def generate_ultra_transit_alert(context: Dict, transit_type: str = "warning") -> str:
    """
    Phase 16: Generate ultra-detailed transit alert.
    
    Args:
        context: Astrological context
        transit_type: Type of alert (warning, opportunity, etc.)
    
    Returns:
        Transit alert message
    """
    message = ultra_explanation(context, "transit_alert")
    
    alert_addon = f"""
⚠️ TRANSIT ALERT - {transit_type.upper()}:

• Important planetary transit is active
• This affects your chart specifically
• Be mindful of the energies
• Take appropriate action
• Remedies may be helpful
"""
    
    message = message.replace("╔═══════════════════════════════════════════════════════════╗", 
                             alert_addon + "\n╔═══════════════════════════════════════════════════════════╗", 1)
    
    return message

