"""
Phase 13: AI Match Interpretation

AI-powered compatibility report generation.
"""

from typing import Dict
import json
from src.ai.interpreter.ai_engine import call_ai, parse_ai_response


def build_match_prompt(match_data: Dict) -> str:
    """
    Phase 13: Build AI prompt for match interpretation.
    
    Args:
        match_data: Complete match report data
    
    Returns:
        Formatted prompt string
    """
    prompt = f"""
You are a highly knowledgeable Vedic Astrology Guru specializing in marriage compatibility analysis.

Analyze the following match report and provide a comprehensive, compassionate, and practical interpretation.

MATCH DATA:

Guna Milan (36 Points System):
- Total Score: {match_data.get('guna_milan', {}).get('total', 0)}/36
- Percentage: {match_data.get('guna_milan', {}).get('percentage', 0)}%
- Verdict: {match_data.get('guna_milan', {}).get('verdict', 'N/A')}
- Key Points:
  * Varna: {match_data.get('guna_milan', {}).get('varna', {}).get('score', 0)}/1
  * Nadi: {match_data.get('guna_milan', {}).get('nadi', {}).get('score', 0)}/8 (Most Important)
  * Bhakoot: {match_data.get('guna_milan', {}).get('bhakoot', {}).get('score', 0)}/7
  * Gana: {match_data.get('guna_milan', {}).get('gana', {}).get('score', 0)}/6

Porutham (10 Checks System):
- Score: {match_data.get('porutham', {}).get('score', 0)}/10
- Percentage: {match_data.get('porutham', {}).get('percentage', 0)}%
- Verdict: {match_data.get('porutham', {}).get('verdict', 'N/A')}
- Rajju (Most Important): {match_data.get('porutham', {}).get('rajju', {}).get('compatible', False)}

Manglik Status:
- Boy Manglik: {match_data.get('manglik', {}).get('boy', {}).get('is_manglik', False)}
- Girl Manglik: {match_data.get('manglik', {}).get('girl', {}).get('is_manglik', False)}
- Cancellation: {match_data.get('manglik', {}).get('cancellation', {}).get('overall_status', 'N/A')}
- Safe for Marriage: {match_data.get('manglik', {}).get('cancellation', {}).get('safe_for_marriage', False)}

Advanced Compatibility:
- Overall Index: {match_data.get('advanced', {}).get('overall_index', 0)}/100
- Emotional Match: {match_data.get('advanced', {}).get('emotional_match', 0)}/100
- Communication Match: {match_data.get('advanced', {}).get('communication_match', 0)}/100
- Moon Distance: {match_data.get('advanced', {}).get('moon_distance', {}).get('compatibility', 'N/A')}
- Dasha Conflict: {match_data.get('advanced', {}).get('dasha_conflict', {}).get('has_conflict', False)}

Overall Match:
- Score: {match_data.get('overall', {}).get('score', 0)}/100
- Verdict: {match_data.get('overall', {}).get('verdict', 'N/A')}
- Recommendation: {match_data.get('overall', {}).get('recommendation', 'N/A')}

YOUR TASK:

Provide a comprehensive marriage compatibility report in JSON format:

{{
  "summary": "One powerful line summarizing the match (max 150 characters)",
  "marriage_outcome": "Prediction about marriage outcome (2-3 sentences)",
  "strengths": [
    "Strength 1",
    "Strength 2",
    "Strength 3"
  ],
  "weaknesses": [
    "Weakness 1",
    "Weakness 2"
  ],
  "manglik_analysis": "Detailed analysis of Manglik status and implications (2-3 sentences)",
  "final_verdict": "Final recommendation with reasoning (3-4 sentences)",
  "remedies": [
    "Remedy 1 (if score is low or issues present)",
    "Remedy 2",
    "Remedy 3"
  ],
  "detailed_analysis": "4-6 paragraphs of detailed analysis covering: compatibility factors, planetary influences, relationship dynamics, and practical guidance"
}}

IMPORTANT:
- Be compassionate and practical
- Focus on solutions, not just problems
- Provide actionable remedies
- Use traditional Vedic wisdom
- Be encouraging but honest
- Keep tone friendly and supportive
"""
    
    return prompt


def ai_match_interpretation(match_data: Dict) -> Dict:
    """
    Phase 13: Generate AI-powered match interpretation.
    
    Args:
        match_data: Complete match report dictionary
    
    Returns:
        AI-generated interpretation dictionary
    """
    prompt = build_match_prompt(match_data)
    
    # Call AI
    ai_response = call_ai(prompt, prefer_local=False)
    
    # Parse response
    if ai_response:
        try:
            # Try to extract JSON
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                json_str = ai_response[json_start:json_end].strip()
            elif "```" in ai_response:
                json_start = ai_response.find("```") + 3
                json_end = ai_response.find("```", json_start)
                json_str = ai_response[json_start:json_end].strip()
            elif "{" in ai_response:
                json_start = ai_response.find("{")
                json_end = ai_response.rfind("}") + 1
                json_str = ai_response[json_start:json_end]
            else:
                json_str = ai_response
            
            parsed = json.loads(json_str)
            return {
                **parsed,
                "ai_used": "openai" if ai_response else "none"
            }
        except:
            pass
    
    # Default response if AI fails
    overall_score = match_data.get("overall", {}).get("score", 0)
    
    return {
        "summary": f"Match score: {overall_score}/100 - {match_data.get('overall', {}).get('verdict', 'Moderate Match')}",
        "marriage_outcome": "The match shows moderate compatibility. With understanding and effort, a successful marriage is possible.",
        "strengths": [
            "Good foundation for relationship",
            "Mutual understanding possible"
        ],
        "weaknesses": [
            "Some areas need attention"
        ],
        "manglik_analysis": "Manglik status should be carefully considered.",
        "final_verdict": f"Overall compatibility is {overall_score}/100. {match_data.get('overall', {}).get('recommendation', 'Consider all factors carefully.')}",
        "remedies": [
            "Perform Mangal Dosha remedies if applicable",
            "Consult with experienced astrologer",
            "Choose auspicious wedding date"
        ],
        "detailed_analysis": "Based on the astrological analysis, this match shows various compatibility factors. Consider all aspects carefully before making a decision.",
        "ai_used": "none"
    }

