"""
Phase 14: AI Guru

AI-powered question answering based on astrological context.
"""

from typing import Dict
import json

from src.ai.interpreter.ai_engine import call_ai, parse_ai_response


def ask_guru_ai(question: str, context: Dict) -> str:
    """
    Phase 14: Ask AI Guru a question with full astrological context.
    
    Args:
        question: User's question in natural language
        context: Complete astrological context dictionary
    
    Returns:
        AI-generated answer
    """
    formatted_context = context.get("formatted_context", "")
    
    prompt = f"""
You are an ancient Vedic Astrology Guru with deep knowledge of Parashara, Jaimini, and traditional Jyotish Shastra.

You have access to the user's complete astrological profile including:
- Birth chart (Kundli) with all planetary positions
- Current Vimshottari Dasha period
- Today's Panchang (Tithi, Nakshatra, Yoga, Karana)
- Current planetary transits (Gochar)
- Planet strengths and positions
- Detected Yogas
- Daily energy levels

USER QUESTION:
{question}

ASTROLOGICAL CONTEXT:
{formatted_context}

TASK:
Provide a comprehensive, compassionate, and practical answer based on Vedic Astrology principles.

Your answer MUST include:

1. **Clear Explanation**: Direct answer to the question based on astrological factors

2. **Planetary Reasoning**: Explain which planets are influencing this situation:
   - Current Dasha lord impact
   - Transit influences
   - Planetary positions in birth chart
   - Planet strengths

3. **Dasha Impact**: How the current Vimshottari Dasha period affects this question

4. **Transit Influence**: How current planetary transits (Gochar) are affecting the situation

5. **Timing Guidance**: 
   - Is this a good time or bad time?
   - When would be the best time?
   - What periods to avoid?

6. **Auspicious Elements**:
   - Lucky color for the day
   - Favorable direction
   - Best time of day

7. **Guru's Advice**: Practical guidance and wisdom based on the astrological analysis

8. **Remedies** (if needed): Specific remedies, mantras, or actions to improve the situation

FORMAT:
Write in a warm, compassionate, and traditional Guru style. Be specific and actionable.
Use clear sections but keep it conversational.

Keep the answer comprehensive but not overly long (500-800 words ideal).
Focus on practical guidance that the user can act upon.

Remember: You are a wise, experienced Vedic Astrologer helping someone with their life questions.
"""
    
    # Call AI engine
    ai_response = call_ai(prompt, prefer_local=False)
    
    if not ai_response:
        # Fallback response
        return generate_fallback_answer(question, context)
    
    return ai_response


def generate_fallback_answer(question: str, context: Dict) -> str:
    """
    Phase 14: Generate fallback answer if AI fails.
    
    Args:
        question: User's question
        context: Astrological context
    
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
    
    answer = f"""
Based on your astrological chart:

**Current Dasha**: You are currently in {dasha_lord} Dasha period, which influences your current situation.

**Today's Nakshatra**: {nakshatra} - This affects the energies of the day.

**Daily Energy**: Your daily score is {daily_score}/100, indicating {'favorable' if daily_score >= 70 else 'moderate' if daily_score >= 50 else 'challenging'} energies today.

**Regarding your question**: "{question}"

I recommend consulting with a qualified Vedic Astrologer for a detailed analysis. The planetary positions and transits need careful examination to provide specific guidance.

**General Guidance**:
- Consider the influence of your current Dasha period
- Pay attention to planetary transits
- Choose auspicious times for important decisions
- Follow traditional remedies if needed

For a more detailed answer, please ensure your birth data is complete and accurate.
"""
    
    return answer

