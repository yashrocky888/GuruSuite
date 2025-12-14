"""
Phase 18: Yoga Interpreter

Interprets yogas and their effects on the chart.
"""

from typing import Dict, List


def summarize_yogas(yogas_list: List[Dict]) -> Dict:
    """
    Phase 18: Summarize all detected yogas.
    
    Args:
        yogas_list: List of yoga dictionaries
    
    Returns:
        Summary dictionary
    """
    if not yogas_list:
        return {
            "total_yogas": 0,
            "summary": "No significant yogas detected in the chart.",
            "categories": {}
        }
    
    # Categorize yogas
    categories = {
        "raja_yogas": [],
        "dhana_yogas": [],
        "chandra_yogas": [],
        "surya_yogas": [],
        "mahapurusha_yogas": [],
        "other_yogas": []
    }
    
    for yoga in yogas_list:
        yoga_name = yoga.get("name", "").lower()
        yoga_type = yoga.get("type", "other")
        
        if "raja" in yoga_name or yoga_type == "raja":
            categories["raja_yogas"].append(yoga)
        elif "dhana" in yoga_name or "wealth" in yoga_name:
            categories["dhana_yogas"].append(yoga)
        elif "chandra" in yoga_name or "moon" in yoga_name:
            categories["chandra_yogas"].append(yoga)
        elif "surya" in yoga_name or "sun" in yoga_name:
            categories["surya_yogas"].append(yoga)
        elif "mahapurusha" in yoga_name:
            categories["mahapurusha_yogas"].append(yoga)
        else:
            categories["other_yogas"].append(yoga)
    
    # Build summary
    summary_text = f"""
Total Yogas Detected: {len(yogas_list)}

Yoga Categories:
• Raja Yogas: {len(categories['raja_yogas'])} - Royal combinations bringing power and success
• Dhana Yogas: {len(categories['dhana_yogas'])} - Wealth combinations bringing prosperity
• Chandra Yogas: {len(categories['chandra_yogas'])} - Moon combinations bringing emotional stability
• Surya Yogas: {len(categories['surya_yogas'])} - Sun combinations bringing authority
• Mahapurusha Yogas: {len(categories['mahapurusha_yogas'])} - Great person combinations
• Other Yogas: {len(categories['other_yogas'])} - Additional combinations

Overall Assessment:
"""
    
    total_auspicious = len(categories['raja_yogas']) + len(categories['dhana_yogas']) + len(categories['mahapurusha_yogas'])
    
    if total_auspicious >= 5:
        summary_text += "Excellent chart with many auspicious yogas. Strong potential for success and prosperity."
    elif total_auspicious >= 3:
        summary_text += "Good chart with several auspicious yogas. Favorable for success."
    elif total_auspicious >= 1:
        summary_text += "Moderate chart with some auspicious yogas. Potential for growth."
    else:
        summary_text += "Chart requires careful analysis. Focus on strengthening planets and remedies."
    
    return {
        "total_yogas": len(yogas_list),
        "summary": summary_text.strip(),
        "categories": {
            k: len(v) for k, v in categories.items()
        },
        "yogas_by_category": categories,
        "auspicious_count": total_auspicious
    }


def explain_individual_yoga(yoga: Dict) -> Dict:
    """
    Phase 18: Explain an individual yoga in detail.
    
    Args:
        yoga: Yoga dictionary
    
    Returns:
        Detailed explanation
    """
    yoga_name = yoga.get("name", "Unknown Yoga")
    yoga_type = yoga.get("type", "general")
    planets = yoga.get("planets", [])
    houses = yoga.get("houses", [])
    description = yoga.get("description", "")
    
    explanation = f"""
{yoga_name}:

Type: {yoga_type.title()}

Planets Involved:
{', '.join(planets) if planets else 'N/A'}

Houses Involved:
{', '.join([str(h) for h in houses]) if houses else 'N/A'}

Description:
{description}

Effects:
"""
    
    # Yoga-specific effects
    if "raja" in yoga_name.lower():
        explanation += """
• Brings power, authority, and success
• Enhances leadership qualities
• Provides recognition and status
• Favorable for career and public life
"""
    elif "dhana" in yoga_name.lower() or "wealth" in yoga_name.lower():
        explanation += """
• Brings wealth and prosperity
• Enhances financial gains
• Provides material comforts
• Favorable for business and investments
"""
    elif "chandra" in yoga_name.lower():
        explanation += """
• Brings emotional stability
• Enhances intuition and creativity
• Provides popularity and support
• Favorable for relationships
"""
    elif "mahapurusha" in yoga_name.lower():
        explanation += """
• Creates exceptional qualities
• Brings fame and recognition
• Enhances natural talents
• Indicates great potential
"""
    else:
        explanation += """
• Creates specific astrological effects
• Influences related life areas
• Provides unique qualities
"""
    
    # Strength assessment
    strength = yoga.get("strength", "moderate")
    if strength == "strong":
        explanation += "\nStrength: Strong - Excellent results expected"
    elif strength == "moderate":
        explanation += "\nStrength: Moderate - Good results expected"
    else:
        explanation += "\nStrength: Weak - Results may be limited"
    
    return {
        "yoga_name": yoga_name,
        "yoga_type": yoga_type,
        "planets": planets,
        "houses": houses,
        "description": description,
        "explanation": explanation.strip(),
        "strength": strength
    }

