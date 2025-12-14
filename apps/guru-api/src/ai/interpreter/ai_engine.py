"""
Phase 8: AI Engine - OpenAI and Local LLM Support

This module handles AI API calls with fallback support.
"""

import json
import os
from typing import Dict, Optional
import requests

from src.config import settings


def call_openai(prompt: str) -> Optional[str]:
    """
    Phase 8: Call OpenAI API for AI interpretation.
    
    Args:
        prompt: The prompt to send to OpenAI
    
    Returns:
        AI response text or None if error
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None)
        
        if not api_key:
            return None
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o-mini",  # Using cost-effective model
            "messages": [
                {"role": "system", "content": "You are a Vedic Astrology Guru. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None


def call_ollama(prompt: str, model: str = "llama3") -> Optional[str]:
    """
    Phase 8: Call local Ollama LLM for AI interpretation.
    
    Args:
        prompt: The prompt to send to Ollama
        model: Ollama model name (default: llama3)
    
    Returns:
        AI response text or None if error
    """
    try:
        url = "http://localhost:11434/api/generate"
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1500
            }
        }
        
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", None)
    
    except requests.exceptions.ConnectionError:
        print("Ollama not running on localhost:11434")
        return None
    except Exception as e:
        print(f"Ollama API error: {e}")
        return None


def call_ai(prompt: str, prefer_local: bool = False) -> Optional[str]:
    """
    Phase 8: Call AI with automatic fallback.
    
    Tries OpenAI first (if key available), then falls back to Ollama.
    Or vice versa if prefer_local is True.
    
    Args:
        prompt: The prompt to send
        prefer_local: If True, try Ollama first
    
    Returns:
        AI response text or None if both fail
    """
    if prefer_local:
        # Try Ollama first
        response = call_ollama(prompt)
        if response:
            return response
        
        # Fallback to OpenAI
        return call_openai(prompt)
    else:
        # Try OpenAI first
        response = call_openai(prompt)
        if response:
            return response
        
        # Fallback to Ollama
        return call_ollama(prompt)


def parse_ai_response(response: str) -> Dict:
    """
    Phase 8: Parse AI response and extract JSON.
    
    Args:
        response: Raw AI response text
    
    Returns:
        Parsed dictionary or default structure
    """
    # Default structure
    default = {
        "summary": "A day of balanced energies and opportunities.",
        "lucky_color": "White",
        "best_time": "10:00 - 14:00",
        "what_to_do": [
            "Focus on important tasks",
            "Connect with loved ones",
            "Practice gratitude"
        ],
        "what_to_avoid": [
            "Rash decisions",
            "Unnecessary conflicts"
        ],
        "planet_in_focus": "Moon",
        "energy_rating": 70,
        "detailed_prediction": "Today brings balanced cosmic energies. The planetary influences suggest a day of moderate activity and opportunities. Focus on important tasks during favorable hours. Maintain harmony in relationships. Take care of health and wellness.",
        "morning_message": "May this day bring you peace, prosperity, and spiritual growth."
    }
    
    if not response:
        return default
    
    try:
        # Try to extract JSON from response
        # Look for JSON block in markdown or plain text
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        elif "```" in response:
            json_start = response.find("```") + 3
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        else:
            # Try to find JSON object
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
            else:
                json_str = response
        
        parsed = json.loads(json_str)
        
        # Validate and merge with defaults
        result = {**default, **parsed}
        return result
    
    except json.JSONDecodeError:
        # If JSON parsing fails, return default with response as detailed_prediction
        return {
            **default,
            "detailed_prediction": response[:500] if len(response) > 500 else response
        }
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return default

