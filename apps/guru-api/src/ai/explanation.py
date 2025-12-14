"""
AI explanation generator for astrological data.

This module uses the LLM client to generate human-readable
explanations of astrological calculations.
"""

from typing import Dict, Optional

from src.ai.llm_client import llm_client
from src.ai.guru_prompt import (
    create_kundli_prompt,
    create_dasha_prompt,
    create_daily_prompt,
    create_transit_prompt,
    create_yoga_prompt
)


def explain_kundli(kundli_data: Dict) -> str:
    """
    Generate AI explanation for a birth chart.
    
    Args:
        kundli_data: Complete kundli data dictionary
    
    Returns:
        AI-generated explanation text
    """
    prompt = create_kundli_prompt(kundli_data)
    return llm_client.generate_explanation(prompt, max_tokens=800)


def explain_dasha(dasha_data: Dict) -> str:
    """
    Generate AI explanation for dasha periods.
    
    Args:
        dasha_data: Dasha calculation data
    
    Returns:
        AI-generated explanation text
    """
    prompt = create_dasha_prompt(dasha_data)
    return llm_client.generate_explanation(prompt, max_tokens=600)


def explain_daily(daily_data: Dict) -> str:
    """
    Generate AI explanation for daily predictions.
    
    Args:
        daily_data: Daily prediction data
    
    Returns:
        AI-generated explanation text
    """
    prompt = create_daily_prompt(daily_data)
    return llm_client.generate_explanation(prompt, max_tokens=500)


def explain_transits(transit_data: Dict) -> str:
    """
    Generate AI explanation for planetary transits.
    
    Args:
        transit_data: Transit calculation data
    
    Returns:
        AI-generated explanation text
    """
    prompt = create_transit_prompt(transit_data)
    return llm_client.generate_explanation(prompt, max_tokens=600)


def explain_yogas(yogas_data: Dict) -> str:
    """
    Generate AI explanation for yogas.
    
    Args:
        yogas_data: Yogas calculation data
    
    Returns:
        AI-generated explanation text
    """
    prompt = create_yoga_prompt(yogas_data)
    return llm_client.generate_explanation(prompt, max_tokens=700)


def add_explanation_to_response(response_data: Dict, explanation_type: str) -> Dict:
    """
    Add AI explanation to a response dictionary.
    
    Args:
        response_data: Response data dictionary
        explanation_type: Type of explanation (kundli, dasha, daily, transit, yogas)
    
    Returns:
        Response data with added explanation
    """
    try:
        if explanation_type == "kundli":
            explanation = explain_kundli(response_data)
        elif explanation_type == "dasha":
            explanation = explain_dasha(response_data)
        elif explanation_type == "daily":
            explanation = explain_daily(response_data)
        elif explanation_type == "transit":
            explanation = explain_transits(response_data)
        elif explanation_type == "yogas":
            explanation = explain_yogas(response_data)
        else:
            explanation = "Explanation type not supported."
        
        response_data["ai_explanation"] = explanation
    except Exception as e:
        response_data["ai_explanation"] = f"Could not generate explanation: {str(e)}"
    
    return response_data

