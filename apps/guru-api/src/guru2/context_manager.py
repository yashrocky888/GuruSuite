"""
Phase 17: Context Manager for Guru 2.0

Builds complete context including detected events.
"""

from typing import Dict
from src.liveguru.context_builder import build_context
from src.eventdetector.detector import detect_events
from src.db.models import BirthDetail


def build_full_context(birth_data: BirthDetail) -> Dict:
    """
    Phase 17: Build complete context including detected events.
    
    Args:
        birth_data: BirthDetail object
    
    Returns:
        Complete context with events
    """
    # Build base context (from Phase 15-16)
    context = build_context(birth_data)
    
    # Detect astrological events
    detected_events = detect_events(context)
    
    # Add events to context
    context["events"] = detected_events
    
    # Format events for AI consumption
    context["formatted_events"] = format_events_for_ai(detected_events)
    
    return context


def format_events_for_ai(events: Dict) -> str:
    """
    Phase 17: Format detected events as text for AI prompt.
    
    Args:
        events: Events dictionary
    
    Returns:
        Formatted events string
    """
    if not events:
        return "No significant astrological events detected today."
    
    formatted = "\n=== DETECTED ASTROLOGICAL EVENTS ===\n\n"
    
    # Bad events
    bad_events = events.get("bad_events", [])
    if bad_events:
        formatted += "⚠️ CHALLENGING PERIODS:\n\n"
        for event in bad_events:
            formatted += f"• {event.get('event_name', 'Unknown')} ({event.get('severity', 'medium')} severity)\n"
            formatted += f"  Reason: {event.get('reason', 'N/A')}\n"
            formatted += f"  Effect: {event.get('how_it_affects', 'N/A')}\n"
            formatted += f"  Advice: {event.get('what_to_do', 'N/A')}\n\n"
    
    # Good events
    good_events = events.get("good_events", [])
    if good_events:
        formatted += "✅ AUSPICIOUS PERIODS:\n\n"
        for event in good_events:
            formatted += f"• {event.get('event_name', 'Unknown')}\n"
            formatted += f"  Reason: {event.get('reason', 'N/A')}\n"
            formatted += f"  Benefit: {event.get('how_it_affects', 'N/A')}\n"
            formatted += f"  Advice: {event.get('what_to_do', 'N/A')}\n\n"
    
    formatted += f"\nOverall Day Status: {events.get('day_status', 'normal').upper()}\n"
    
    return formatted

