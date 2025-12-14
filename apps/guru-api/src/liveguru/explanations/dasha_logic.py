"""
Phase 16: Dasha Logic Explanation

Deep explanation of how current Dasha period affects the user.
"""

from typing import Dict
from src.liveguru.explanations.karakatva import get_karakatva


def explain_dasha(dasha_data: Dict) -> str:
    """
    Phase 16: Explain current Dasha influence in detail.
    
    Args:
        dasha_data: Dasha dictionary with current period information
    
    Returns:
        Detailed explanation of Dasha influence
    """
    if not dasha_data:
        return "Dasha information not available."
    
    current_dasha = dasha_data.get("current_dasha", {})
    if not current_dasha:
        return "Current Dasha period information not available."
    
    dasha_lord = current_dasha.get("dasha_lord", "Unknown")
    antardasha_lord = current_dasha.get("antardasha_lord", "Unknown")
    
    # Get karakatva for both lords
    main_karakatva = get_karakatva(dasha_lord)
    sub_karakatva = get_karakatva(antardasha_lord)
    
    # Dasha influence explanation
    main_primary = ", ".join(main_karakatva.get("primary", [])[:3])
    sub_primary = ", ".join(sub_karakatva.get("primary", [])[:3])
    
    # Determine Dasha strength and influence
    dasha_strength = current_dasha.get("strength", "moderate")
    
    explanation = f"""
🌟 Current Dasha Period Analysis 🌟

You are currently in:
• Mahadasha: {dasha_lord} (Main Period)
• Antardasha: {antardasha_lord} (Sub Period)

Planetary Nature:
• {dasha_lord} represents: {main_primary}
• {antardasha_lord} represents: {sub_primary}

Dasha Influence Today:
"""
    
    # Add specific influence based on planets
    if dasha_lord == "Jupiter":
        explanation += """
• Jupiter Dasha brings wisdom, expansion, and fortune
• Focus on learning, teaching, and spiritual growth
• Good time for education, travel, and seeking guidance
• Children and relationships may be highlighted
"""
    elif dasha_lord == "Saturn":
        explanation += """
• Saturn Dasha brings discipline, hard work, and delays
• Focus on long-term goals and patience
• Challenges may arise but lead to growth
• Good time for career development and service
"""
    elif dasha_lord == "Mars":
        explanation += """
• Mars Dasha brings energy, action, and courage
• Focus on taking initiative and being decisive
• Good time for starting new projects
• Be mindful of aggression and conflicts
"""
    elif dasha_lord == "Venus":
        explanation += """
• Venus Dasha brings love, beauty, and relationships
• Focus on partnerships and creative pursuits
• Good time for marriage, arts, and luxury
• Enjoy comfort but avoid over-indulgence
"""
    elif dasha_lord == "Mercury":
        explanation += """
• Mercury Dasha brings communication and intellect
• Focus on learning, writing, and business
• Good time for studies and commerce
• Be clear in communication
"""
    elif dasha_lord == "Sun":
        explanation += """
• Sun Dasha brings authority and leadership
• Focus on self-confidence and recognition
• Good time for career advancement
• Be mindful of ego and pride
"""
    elif dasha_lord == "Moon":
        explanation += """
• Moon Dasha brings emotions and intuition
• Focus on emotional well-being and relationships
• Good time for nurturing and care
• Be mindful of mood swings
"""
    elif dasha_lord == "Rahu":
        explanation += """
• Rahu Dasha brings material desires and ambition
• Focus on goals and achievements
• Good time for technology and foreign connections
• Be mindful of illusions and attachments
"""
    elif dasha_lord == "Ketu":
        explanation += """
• Ketu Dasha brings spirituality and detachment
• Focus on inner work and letting go
• Good time for spiritual practices
• Be mindful of isolation and confusion
"""
    
    # Add Antardasha influence
    explanation += f"""

Antardasha ({antardasha_lord}) Influence:
• The sub-period of {antardasha_lord} modifies the main Dasha
• {antardasha_lord} energy: {sub_karakatva.get('shastra_meaning', 'N/A')[:100]}...
• This combination creates specific opportunities and challenges

Dasha Strength: {dasha_strength.title()}
"""
    
    if dasha_strength == "strong":
        explanation += "• Your Dasha is strong - favorable outcomes are more likely\n"
        explanation += "• Planetary energies are well-aligned for success\n"
    elif dasha_strength == "weak":
        explanation += "• Your Dasha needs support - remedies may be helpful\n"
        explanation += "• Be patient and work with the energies\n"
    else:
        explanation += "• Your Dasha is moderate - balanced approach is best\n"
    
    return explanation


def explain_dasha_timing(dasha_data: Dict) -> str:
    """
    Phase 16: Explain timing aspects of Dasha.
    
    Args:
        dasha_data: Dasha dictionary
    
    Returns:
        Timing explanation
    """
    current_dasha = dasha_data.get("current_dasha", {})
    
    if not current_dasha:
        return ""
    
    start_date = current_dasha.get("start_date", "N/A")
    end_date = current_dasha.get("end_date", "N/A")
    
    return f"""
Dasha Timing:
• Started: {start_date}
• Ends: {end_date}
• This period shapes your overall life direction
• Daily events are influenced by this Dasha energy
"""

