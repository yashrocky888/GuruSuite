"""
LLM Client for GURU API
Handles all AI/LLM API requests with secure API key authentication
"""

import os
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment
API_KEY = os.getenv("GURU_API_KEY")

if not API_KEY:
    raise ValueError(
        "GURU_API_KEY not found in environment variables. "
        "Please ensure .env file exists with GURU_API_KEY set."
    )


class LLMClient:
    """
    Client for making AI/LLM API requests
    Automatically includes Authorization header with API key
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            base_url: Base URL for the AI API (optional, can be set via env)
        """
        self.api_key = API_KEY
        self.base_url = base_url or os.getenv("LLM_API_BASE_URL", "https://api.example.com/v1")
        self.session = requests.Session()
        
        # Set default headers with Authorization
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
    
    def chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request to LLM API
        
        Args:
            messages: List of message objects (role, content)
            model: Model name (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            API response as dictionary
        """
        payload = {
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if model:
            payload["model"] = model
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt
        
        Args:
            prompt: Input prompt text
            model: Model name (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Generated text
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Extract text from response (adjust based on actual API response format)
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        return ""
    
    def stream_chat(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ):
        """
        Stream chat completion (for real-time responses)
        
        Args:
            messages: List of message objects
            model: Model name (optional)
            temperature: Sampling temperature
            **kwargs: Additional parameters
        
        Yields:
            Chunks of response text
        """
        payload = {
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        if model:
            payload["model"] = model
        
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                yield line


# Global client instance (singleton pattern)
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create global LLM client instance
    
    Returns:
        LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


# Convenience functions for common operations
def generate_guru_response(
    user_message: str,
    context: Optional[str] = None,
    conversation_history: Optional[list] = None,
    **kwargs
) -> str:
    """
    Generate Guru response using LLM
    
    Args:
        user_message: User's message
        context: Conversation context
        conversation_history: Previous messages
        **kwargs: Additional LLM parameters
    
    Returns:
        Generated Guru response
    """
    client = get_llm_client()
    
    # Build messages list
    messages = []
    
    # Add system prompt if context provided
    if context:
        messages.append({
            "role": "system",
            "content": context
        })
    
    # Add conversation history
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Generate response
    response = client.chat_completion(messages=messages, **kwargs)
    
    if "choices" in response and len(response["choices"]) > 0:
        return response["choices"][0]["message"]["content"]
    
    return "I apologize, but I couldn't generate a response. Please try again."


if __name__ == "__main__":
    # Test the client
    client = get_llm_client()
    print(f"LLM Client initialized with API key: {client.api_key[:10]}...")
    print("Client ready to make API requests.")

