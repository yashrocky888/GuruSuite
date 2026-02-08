"""
LLM client for AI-powered astrological explanations.

This module provides a unified interface to interact with either
OpenAI API or local LLM services for generating astrological insights.
"""

from typing import Optional, Dict, List
import os
import requests
from openai import OpenAI

from src.config import settings


class LLMClient:
    """
    Unified LLM client that can work with OpenAI or local LLM.
    """
    
    def __init__(self):
        """Initialize LLM client based on configuration."""
        self.openai_client = None
        self.local_llm_url = settings.local_llm_url
        self.openai_api_key = settings.openai_api_key
        
        # Initialize OpenAI client if API key is available (resilient to library compat issues)
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.mode = "openai"
            except Exception:
                self.openai_client = None
                self.mode = "none"
        elif self.local_llm_url:
            self.mode = "local"
        else:
            self.mode = "none"
    
    def generate_explanation(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate astrological explanation using LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
        
        Returns:
            Generated explanation text
        """
        if self.mode == "openai":
            return self._generate_openai(prompt, max_tokens, temperature)
        elif self.mode == "local":
            return self._generate_local(prompt, max_tokens, temperature)
        else:
            return "AI explanations are not configured. Please set OPENAI_API_KEY or LOCAL_LLM_URL."
    
    def _generate_openai(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert Vedic astrologer providing clear, insightful explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
    def _generate_local(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using local LLM (e.g., Ollama)."""
        try:
            url = f"{self.local_llm_url}/api/generate"
            payload = {
                "model": settings.local_llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "No response generated")
        except Exception as e:
            return f"Error generating explanation: {str(e)}"


# Global LLM client instance
llm_client = LLMClient()

