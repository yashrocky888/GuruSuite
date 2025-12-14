"""
Phase 12: WhatsApp Channel

WhatsApp message delivery via Twilio WhatsApp API.
"""

import os
from typing import Optional, Dict

from src.config import settings

# Phase 12: Twilio credentials from environment
TWILIO_SID = os.getenv("TWILIO_SID", getattr(settings, "twilio_sid", None))
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN", getattr(settings, "twilio_auth_token", None))
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", getattr(settings, "twilio_whatsapp_from", None))

# Initialize Twilio client
client = None
if TWILIO_SID and TWILIO_AUTH:
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_AUTH)
    except ImportError:
        print("Warning: twilio package not installed. WhatsApp delivery will not work.")
    except Exception as e:
        print(f"Warning: Could not initialize Twilio client: {e}")


def send_whatsapp(
    to: str, 
    message: str = None, 
    content_sid: str = None, 
    content_variables: Dict = None
) -> Dict:
    """
    Phase 12: Send WhatsApp message via Twilio.
    
    Supports two methods:
    1. Simple text message (body parameter)
    2. Content template (content_sid + content_variables)
    
    Args:
        to: Recipient WhatsApp number (with country code, e.g., +919876543210)
        message: Message text (for simple messages)
        content_sid: Content template SID (for template messages)
        content_variables: Variables for content template (JSON string or dict)
    
    Returns:
        Dictionary with success status and details
    """
    if not client:
        return {
            "success": False,
            "error": "Twilio client not initialized. Set TWILIO_SID and TWILIO_AUTH_TOKEN."
        }
    
    if not TWILIO_WHATSAPP_FROM:
        return {
            "success": False,
            "error": "TWILIO_WHATSAPP_FROM not configured"
        }
    
    try:
        # Format phone number (ensure it starts with +)
        if not to.startswith("+"):
            to = f"+{to}"
        
        # Format from number
        from_number = f"whatsapp:{TWILIO_WHATSAPP_FROM}"
        to_number = f"whatsapp:{to}"
        
        # Build message parameters
        message_params = {
            "from_": from_number,
            "to": to_number
        }
        
        # Use content template if provided
        if content_sid:
            message_params["content_sid"] = content_sid
            if content_variables:
                # Convert dict to JSON string if needed
                if isinstance(content_variables, dict):
                    import json
                    message_params["content_variables"] = json.dumps(content_variables)
                else:
                    message_params["content_variables"] = content_variables
        # Otherwise use simple text message
        elif message:
            message_params["body"] = message
        else:
            return {
                "success": False,
                "error": "Either 'message' or 'content_sid' must be provided"
            }
        
        # Send message
        message_obj = client.messages.create(**message_params)
        
        return {
            "success": True,
            "message_sid": message_obj.sid,
            "status": message_obj.status,
            "method": "content_template" if content_sid else "text_message"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

