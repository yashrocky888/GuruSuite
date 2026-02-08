"""
Phase 8: Daily Interpreter

This module orchestrates the AI interpretation of daily astrological data.
"""

from typing import Dict, Optional
from src.ai.interpreter.guru_prompt import build_guru_prompt, build_morning_prompt
from src.ai.interpreter.ai_engine import call_ai, parse_ai_response


def interpret_daily(final_data: Dict, use_local: bool = False) -> Dict:
    """
    DEPRECATED: Use POST /api/v1/predict with timescale=daily ONLY.
    """
    raise RuntimeError("DEPRECATED: Use /api/v1/predict ONLY")

    # Build prompt
    prompt = build_guru_prompt(final_data)
    
    # Call AI
    ai_response = call_ai(prompt, prefer_local=use_local)
    
    # Parse response
    prediction = parse_ai_response(ai_response) if ai_response else {}
    
    # Add raw data reference
    return {
        **prediction,
        "ai_used": "openai" if ai_response and not use_local else "ollama" if ai_response else "none",
        "raw_data_available": True
    }


def interpret_morning(final_data: Dict, use_local: bool = False) -> Dict:
    """
    DEPRECATED: Use POST /api/v1/predict with timescale=daily ONLY.
    """
    raise RuntimeError("DEPRECATED: Use /api/v1/predict ONLY")

    # Build morning prompt
    prompt = build_morning_prompt(final_data)
    
    # Call AI
    ai_response = call_ai(prompt, prefer_local=use_local)
    
    # Parse response
    if ai_response:
        try:
            import json
            # Try to parse JSON
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
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
                "ai_used": "openai" if not use_local else "ollama"
            }
        except:
            pass
    
    # Default morning message
    return {
        "blessing": "May this day bring you peace, prosperity, and spiritual growth.",
        "lucky_color": "White",
        "focus": "Focus on important tasks and maintain harmony.",
        "mindful": "Be mindful of your words and actions today.",
        "ai_used": "none"
    }

