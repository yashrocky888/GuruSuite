"""
Guru prompt templates for AI-generated astrological explanations.

This module provides pre-formatted prompts for different types of
astrological queries to ensure consistent, high-quality AI responses.
"""

from typing import Dict, List


def create_kundli_prompt(kundli_data: Dict) -> str:
    """
    Create a prompt for explaining a birth chart (kundli).
    
    Args:
        kundli_data: Complete kundli data dictionary
    
    Returns:
        Formatted prompt string
    """
    name = kundli_data.get("name", "the person")
    ascendant = kundli_data.get("ascendant", {})
    planets = kundli_data.get("planets", {})
    
    prompt = f"""Explain the birth chart (Kundli) for {name}.

Ascendant: {ascendant.get('sign_name', 'Unknown')} at {ascendant.get('degrees', 0):.2f} degrees

Planetary Positions:
"""
    
    for planet_name, planet_data in planets.items():
        prompt += f"- {planet_name}: {planet_data.get('sign_name', 'Unknown')} sign, "
        prompt += f"House {planet_data.get('house', 0)}, "
        prompt += f"Nakshatra {planet_data.get('nakshatra_name', 'Unknown')}\n"
    
    prompt += """
Provide a comprehensive analysis covering:
1. Overall personality based on ascendant and planetary positions
2. Strengths and challenges indicated by the chart
3. Career and financial prospects
4. Relationship and family life
5. Health considerations
6. Spiritual and karmic lessons

Write in a clear, insightful, and encouraging manner suitable for someone seeking astrological guidance.
"""
    
    return prompt


def create_dasha_prompt(dasha_data: Dict) -> str:
    """
    Create a prompt for explaining dasha periods.
    
    Args:
        dasha_data: Dasha calculation data
    
    Returns:
        Formatted prompt string
    """
    current_dasha = dasha_data.get("current_dasha", {})
    current_antardasha = dasha_data.get("current_antardasha", {})
    
    prompt = f"""Explain the current planetary period (Dasha) for this person.

Current Mahadasha: {current_dasha.get('lord', 'Unknown')} ({current_dasha.get('period_years', 0)} years)
Current Antardasha: {current_antardasha.get('lord', 'Unknown')}

Provide insights on:
1. What to expect during this dasha period
2. Areas of life that will be highlighted
3. Opportunities and challenges
4. Best practices and remedies if needed
5. Timing for important activities

Write in a practical, actionable manner.
"""
    
    return prompt


def create_daily_prompt(daily_data: Dict) -> str:
    """
    Create a prompt for explaining daily predictions.
    
    Args:
        daily_data: Daily prediction data
    
    Returns:
        Formatted prompt string
    """
    rating = daily_data.get("daily_rating", {})
    color = daily_data.get("lucky_color", {})
    
    prompt = f"""Provide a daily astrological guidance for today.

Daily Rating: {rating.get('rating', 'Unknown')}
Lucky Color: {color.get('primary_color', 'Unknown')}
Current Dasha: {rating.get('dasha', {}).get('maha_dasha', 'Unknown')} - {rating.get('dasha', {}).get('antardasha', 'Unknown')}

Provide:
1. Overall energy and mood for the day
2. Best times for important activities
3. Things to be cautious about
4. Recommendations for making the most of the day
5. Spiritual or karmic insights

Write in an encouraging, practical tone.
"""
    
    return prompt


def create_transit_prompt(transit_data: Dict) -> str:
    """
    Create a prompt for explaining planetary transits.
    
    Args:
        transit_data: Transit calculation data
    
    Returns:
        Formatted prompt string
    """
    transits = transit_data.get("transits", {})
    summary = transit_data.get("summary", {})
    
    prompt = f"""Explain the current planetary transits and their effects.

Transit Summary:
- Favorable transits: {summary.get('favorable_transits', 0)}
- Challenging transits: {summary.get('challenging_transits', 0)}
- Neutral transits: {summary.get('neutral_transits', 0)}

Key Transits:
"""
    
    for planet_name, transit_info in list(transits.items())[:5]:  # Top 5
        prompt += f"- {planet_name}: {transit_info.get('description', 'No description')}\n"
    
    prompt += """
Provide insights on:
1. Overall transit influences
2. Major life areas being affected
3. Opportunities to watch for
4. Challenges to navigate
5. Timing for important decisions

Write in a clear, actionable manner.
"""
    
    return prompt


def create_yoga_prompt(yogas_data: Dict) -> str:
    """
    Create a prompt for explaining yogas in the birth chart.
    
    Args:
        yogas_data: Yogas calculation data
    
    Returns:
        Formatted prompt string
    """
    total_yogas = yogas_data.get("total_yogas", 0)
    summary = yogas_data.get("summary", {})
    yogas = yogas_data.get("yogas", [])
    
    prompt = f"""Explain the yogas (planetary combinations) found in this birth chart.

Total Yogas Found: {total_yogas}
- Raj Yogas: {summary.get('raj_yogas', 0)}
- Dhana Yogas: {summary.get('dhana_yogas', 0)}
- Doshas: {summary.get('doshas', 0)}
- Spiritual Yogas: {summary.get('spiritual_yogas', 0)}

Key Yogas:
"""
    
    for yoga in yogas[:10]:  # Top 10 yogas
        prompt += f"- {yoga.get('name', 'Unknown')}: {yoga.get('description', 'No description')}\n"
    
    prompt += """
Provide insights on:
1. Overall chart strength based on yogas
2. Special talents and abilities indicated
3. Life challenges and how to overcome them
4. Remedies for any doshas
5. How to maximize the benefits of favorable yogas

Write in an insightful, encouraging manner.
"""
    
    return prompt

