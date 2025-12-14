"""
Phase 17: AI Engine V2 for Guru Conversation 2.0

Enhanced AI engine with memory and long conversation support.
"""

from typing import Dict, List
import json
from src.ai.interpreter.ai_engine import call_ai
from src.liveguru.explanations.karakatva import get_karakatva
from src.liveguru.explanations.nakshatra_details import get_nakshatra_details


def format_conversation_history(history: List[Dict]) -> str:
    """
    Phase 17: Format conversation history for AI prompt.
    
    Args:
        history: List of previous Q&A pairs
    
    Returns:
        Formatted history string
    """
    if not history:
        return "No previous conversation history."
    
    formatted = "\n=== CONVERSATION HISTORY ===\n\n"
    
    # Show last 5 conversations (to avoid token limits)
    recent_history = history[-5:] if len(history) > 5 else history
    
    for i, conv in enumerate(recent_history, 1):
        formatted += f"Previous Question {i}:\n{conv.get('q', 'N/A')}\n\n"
        formatted += f"Guru's Answer {i}:\n{conv.get('a', 'N/A')[:200]}...\n\n"
        formatted += "---\n\n"
    
    if len(history) > 5:
        formatted += f"(Showing last 5 of {len(history)} total conversations)\n"
    
    return formatted


def guru_ai_v2(question: str, context: Dict, history: List[Dict] = None) -> str:
    """
    Phase 17: Enhanced AI Guru with memory and long conversations.
    
    Args:
        question: User's question
        context: Complete astrological context with events
        history: Previous conversation history
    
    Returns:
        AI-generated comprehensive answer
    """
    if history is None:
        history = []
    
    # Format context components
    kundli = context.get("kundli", {})
    dasha = context.get("dasha", {})
    panchang = context.get("panchang", {})
    daily = context.get("daily", {})
    transits = context.get("transits", {})
    events = context.get("events", {})
    formatted_events = context.get("formatted_events", "")
    
    # Get key planetary information
    current_dasha = dasha.get("current_dasha", {})
    dasha_lord = current_dasha.get("dasha_lord", "Unknown")
    
    nakshatra = panchang.get("nakshatra", {})
    nakshatra_name = nakshatra.get("name", "Unknown")
    nak_details = get_nakshatra_details(nakshatra_name)
    
    # Format history
    history_text = format_conversation_history(history)
    
    # Build comprehensive prompt
    prompt = f"""
You are a highly knowledgeable, compassionate Vedic Astrology Guru with deep understanding of Parashara, Jaimini, and traditional Jyotish Shastra.

You are having a LONG CONVERSATION with a user. You REMEMBER their birth chart, their previous questions, and the context of your conversation.

USER'S CURRENT QUESTION:
{question}

═══════════════════════════════════════════════════════════
ASTROLOGICAL CONTEXT (User's Complete Profile):
═══════════════════════════════════════════════════════════

CURRENT DASHA:
• Mahadasha: {dasha_lord}
• Antardasha: {current_dasha.get('antardasha_lord', 'Unknown')}
• Dasha Influence: {dasha_lord} period shapes current life direction

TODAY'S PANCHANG:
• Tithi: {panchang.get('tithi', {}).get('name', 'Unknown')}
• Nakshatra: {nakshatra_name}
• Nakshatra Symbol: {nak_details.get('symbol', 'N/A')}
• Nakshatra Lord: {nak_details.get('lord', 'N/A')}
• Nakshatra Qualities: {nak_details.get('qualities', 'N/A')}
• Nakshatra Shastra Meaning: {nak_details.get('shastra_meaning', 'N/A')}
• Yoga: {panchang.get('yoga', {}).get('name', 'Unknown')}
• Karana: {panchang.get('karana', {}).get('name', 'Unknown')}

DAILY ENERGY:
• Score: {daily.get('daily_strength', {}).get('score', 0)}/100
• Summary: {daily.get('daily_strength', {}).get('summary', 'N/A')}

DETECTED ASTROLOGICAL EVENTS:
{formatted_events}

PLANETARY KARAKATVA (Natural Significations):
"""
    
    # Add karakatva for key planets
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if planet_name in kundli.get("Planets", {}):
            karakatva = get_karakatva(planet_name)
            primary = ", ".join(karakatva.get("primary", [])[:3])
            prompt += f"• {planet_name}: {primary}\n"
    
    prompt += f"""

{history_text}

═══════════════════════════════════════════════════════════
YOUR TASK:
═══════════════════════════════════════════════════════════

Provide a VERY DETAILED, EMOTIONAL, DEEP, and COMPASSIONATE answer that includes:

1. **PLANETARY KARAKATVA LOGIC**:
   - Explain which planets are influencing this situation
   - What each planet naturally represents (karakatva)
   - How their positions affect the user

2. **NAKSHATRA MEANING**:
   - Deep interpretation of today's Nakshatra
   - Symbol and its significance
   - How it affects the user's emotions and actions
   - Connection to user's natal Nakshatra if relevant

3. **TITHI MEANING**:
   - What today's Tithi represents
   - How it influences the day's energy
   - Why it matters for the user's question

4. **DASHA IMPACT**:
   - How the current {dasha_lord} Dasha period affects this situation
   - What the Dasha lord represents
   - How it shapes current life direction
   - Timing aspects

5. **TRANSIT INFLUENCE**:
   - How current planetary transits affect the user
   - Comparison with natal placements
   - Specific transit effects on the question

6. **WHY TODAY IS GOOD/BAD**:
   - Based on detected events (if any)
   - Panchang combination
   - Overall day energy
   - Specific timing considerations

7. **HOW EVENTS AFFECT THE USER**:
   - If challenging events detected: explain impact
   - If auspicious events detected: explain benefits
   - How to work with these energies

8. **PRACTICAL ADVICE**:
   - What to do specifically
   - What to avoid
   - When to act
   - How to navigate the situation

9. **SPIRITUAL WISDOM**:
   - Deeper meaning and lessons
   - Karmic perspective
   - Growth opportunities
   - Compassionate guidance

10. **REMEDIES** (only if necessary):
    - Specific remedies if challenges are present
    - Mantras, prayers, or actions
    - Only suggest if truly needed

11. **FOLLOW-UP QUESTION**:
    - End with a thoughtful, guiding question
    - Helps continue the conversation
    - Shows you're engaged and caring

STYLE REQUIREMENTS:
- Write like a REAL, WISE GURU - warm, compassionate, deep
- Use emotional and spiritual language
- Connect astrology to life experiences
- Be specific and actionable
- Show you remember the conversation context
- Be encouraging but honest
- Length: 800-1500 words (comprehensive but not overwhelming)

Remember: You are having a LONG CONVERSATION. Reference previous topics if relevant. Show continuity and care.
"""
    
    # Call AI
    ai_response = call_ai(prompt, prefer_local=False)
    
    if not ai_response:
        # Fallback response
        return generate_fallback_answer_v2(question, context, events)
    
    return ai_response


def generate_fallback_answer_v2(question: str, context: Dict, events: Dict) -> str:
    """
    Phase 17: Generate fallback answer if AI fails.
    
    Args:
        question: User's question
        context: Astrological context
        events: Detected events
    
    Returns:
        Basic astrological answer
    """
    dasha = context.get("dasha", {})
    current_dasha = dasha.get("current_dasha", {})
    dasha_lord = current_dasha.get("dasha_lord", "Unknown")
    
    panchang = context.get("panchang", {})
    nakshatra = panchang.get("nakshatra", {}).get("name", "Unknown")
    
    daily = context.get("daily", {})
    daily_score = daily.get("daily_strength", {}).get("score", 0)
    
    bad_events = events.get("bad_events", [])
    good_events = events.get("good_events", [])
    
    answer = f"""
Based on your astrological chart and current planetary positions:

**Current Dasha**: You are in {dasha_lord} Dasha period, which influences your current situation.

**Today's Nakshatra**: {nakshatra} - This affects the energies of the day.

**Daily Energy**: Your daily score is {daily_score}/100, indicating {'favorable' if daily_score >= 70 else 'moderate' if daily_score >= 50 else 'challenging'} energies today.

**Regarding your question**: "{question}"

"""
    
    if bad_events:
        answer += f"\n**Important**: {len(bad_events)} challenging astrological events detected today. "
        answer += "Be cautious with important decisions.\n"
    
    if good_events:
        answer += f"\n**Positive**: {len(good_events)} auspicious events detected. "
        answer += "This is a favorable time for positive activities.\n"
    
    answer += """
I recommend consulting with a qualified Vedic Astrologer for a detailed analysis. The planetary positions and transits need careful examination to provide specific guidance.

**General Guidance**:
- Consider the influence of your current Dasha period
- Pay attention to planetary transits
- Choose auspicious times for important decisions
- Follow traditional remedies if needed

For a more detailed answer, please ensure your birth data is complete and accurate.
"""
    
    return answer

