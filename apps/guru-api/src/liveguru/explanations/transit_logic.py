"""
Phase 16: Transit Logic Explanation

Deep explanation of how current transits affect the user based on natal chart.
"""

from typing import Dict
from src.utils.converters import degrees_to_sign
from src.jyotish.panchang import get_nakshatra
from src.liveguru.explanations.nakshatra_details import get_nakshatra_details


def explain_transit(transit_data: Dict, kundli: Dict) -> str:
    """
    Phase 16: Explain current transit influence in detail.
    
    Args:
        transit_data: Current transit information
        kundli: User's birth chart
    
    Returns:
        Detailed explanation of transit influence
    """
    if not transit_data or not kundli:
        return "Transit information not available."
    
    # Get current Moon position
    current_moon = transit_data.get("moon", {})
    if not current_moon:
        return "Current Moon transit information not available."
    
    # Get natal Moon
    natal_moon = kundli.get("Planets", {}).get("Moon", {})
    if not natal_moon:
        return "Natal Moon information not available."
    
    # Current Moon details
    current_moon_deg = current_moon.get("degree", 0)
    current_nakshatra_name, current_nakshatra_index = get_nakshatra(current_moon_deg)
    current_moon_sign, _ = degrees_to_sign(current_moon_deg)
    
    # Natal Moon details
    natal_moon_deg = natal_moon.get("degree", 0)
    natal_nakshatra_name, natal_nakshatra_index = get_nakshatra(natal_moon_deg)
    natal_moon_sign, _ = degrees_to_sign(natal_moon_deg)
    
    # Get nakshatra details
    current_nak_details = get_nakshatra_details(current_nakshatra_name)
    natal_nak_details = get_nakshatra_details(natal_nakshatra_name)
    
    explanation = f"""
🌙 Current Moon Transit Analysis 🌙

Today's Moon Position:
• Nakshatra: {current_nakshatra_name}
• Sign: {current_moon_sign}
• Qualities: {current_nak_details.get('qualities', 'N/A')}
• Meaning: {current_nak_details.get('shastra_meaning', 'N/A')[:150]}...

Your Natal Moon:
• Nakshatra: {natal_nakshatra_name}
• Sign: {natal_moon_sign}
• Qualities: {natal_nak_details.get('qualities', 'N/A')}

Transit Impact:
"""
    
    # Calculate nakshatra distance
    nakshatra_distance = (current_nakshatra_index - natal_nakshatra_index) % 27
    
    # Explain based on distance
    if nakshatra_distance == 0:
        explanation += """
• Moon is in your natal Nakshatra - Very powerful day!
• Your emotions and intuition are heightened
• This is an auspicious time for important decisions
• You feel more connected to your inner self
"""
    elif nakshatra_distance in [1, 2, 3]:
        explanation += """
• Moon is close to your natal Nakshatra - Strong influence
• You feel more aligned with your natural tendencies
• Good time for activities related to your Moon's nature
• Emotional clarity is enhanced
"""
    elif nakshatra_distance in [13, 14, 15]:
        explanation += """
• Moon is opposite your natal Nakshatra - Contrasting energy
• You may feel pulled in different directions
• Balance is important today
• Consider both sides before making decisions
"""
    else:
        explanation += """
• Moon is in a different Nakshatra - New energy
• This brings fresh perspectives and experiences
• Be open to new ways of thinking and feeling
• Adaptability is key today
"""
    
    # Sign comparison
    if current_moon_sign == natal_moon_sign:
        explanation += """
• Moon is in your natal Moon sign - Emotional comfort
• You feel at home emotionally
• This is a supportive time for emotional matters
"""
    else:
        sign_diff = abs(current_moon_sign - natal_moon_sign)
        if sign_diff > 6:
            sign_diff = 12 - sign_diff
        
        if sign_diff in [1, 5, 9]:
            explanation += """
• Moon is in a friendly sign - Harmonious energy
• Emotional support is available
• Good time for relationships and connections
"""
        elif sign_diff in [3, 7]:
            explanation += """
• Moon is in opposite sign - Complementary energy
• Different perspectives are valuable
• Balance your approach today
"""
        else:
            explanation += """
• Moon is in a different sign - New emotional landscape
• Be open to different emotional experiences
• Adaptability will serve you well
"""
    
    return explanation


def explain_planet_transits(transit_data: Dict, kundli: Dict) -> str:
    """
    Phase 16: Explain other planetary transits.
    
    Args:
        transit_data: Transit information
        kundli: Birth chart
    
    Returns:
        Explanation of planetary transits
    """
    if not transit_data or not kundli:
        return ""
    
    explanation = "\n🪐 Other Planetary Transits:\n"
    
    # Check key transits
    planets_to_check = ["Sun", "Mars", "Jupiter", "Saturn", "Venus", "Mercury"]
    
    for planet_name in planets_to_check:
        if planet_name in transit_data and planet_name in kundli.get("Planets", {}):
            transit_planet = transit_data[planet_name]
            natal_planet = kundli["Planets"][planet_name]
            
            if isinstance(transit_planet, dict) and "degree" in transit_planet:
                transit_sign, _ = degrees_to_sign(transit_planet["degree"])
                natal_sign, _ = degrees_to_sign(natal_planet.get("degree", 0))
                
                if transit_sign == natal_sign:
                    explanation += f"• {planet_name} is in your natal {planet_name} sign - Strong influence\n"
                else:
                    explanation += f"• {planet_name} is transiting Sign {transit_sign} (your natal: {natal_sign})\n"
    
    return explanation

