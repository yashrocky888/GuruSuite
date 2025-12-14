"""
Phase 15-16: Live Guru Message Engine

Generates real-time astrological messages with ultra-detailed explanations.
"""

from typing import Dict
from src.liveguru.context_builder import build_context
from src.liveguru.ultra_message_engine import (
    generate_ultra_morning_message,
    generate_ultra_midday_message,
    generate_ultra_evening_message,
    generate_ultra_transit_alert
)
from src.db.models import BirthDetail


def generate_message(msg_type: str, birth_data: BirthDetail) -> str:
    """
    Phase 15-16: Generate Live Guru message with ultra-detailed explanations.
    
    Args:
        msg_type: Type of message (morning, midday, evening, transit)
        birth_data: BirthDetail object
    
    Returns:
        Complete Guru message with deep explanations
    """
    # Build complete context
    context = build_context(birth_data)
    
    # Generate ultra-detailed message based on type
    if msg_type == "morning":
        return generate_ultra_morning_message(context)
    elif msg_type == "midday":
        return generate_ultra_midday_message(context)
    elif msg_type == "evening":
        return generate_ultra_evening_message(context)
    elif msg_type == "transit" or msg_type == "transit_alert":
        return generate_ultra_transit_alert(context, "warning")
    else:
        # Default to morning message
        return generate_ultra_morning_message(context)


def generate_transit_warning(context: Dict, warning_type: str = "general") -> str:
    """
    Phase 16: Generate detailed transit warning message.
    
    Args:
        context: Astrological context
        warning_type: Type of warning
    
    Returns:
        Detailed transit warning
    """
    return generate_ultra_transit_alert(context, warning_type)

