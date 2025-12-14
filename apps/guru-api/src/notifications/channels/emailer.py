"""
Phase 12: Email Channel

Email delivery via SMTP (Gmail) or SendGrid.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional

from src.config import settings

# Phase 12: SMTP credentials from environment
SMTP_USER = os.getenv("SMTP_USER", getattr(settings, "smtp_user", None))
SMTP_PASS = os.getenv("SMTP_PASS", getattr(settings, "smtp_pass", None))
SMTP_HOST = os.getenv("SMTP_HOST", getattr(settings, "smtp_host", "smtp.gmail.com"))
SMTP_PORT = int(os.getenv("SMTP_PORT", str(getattr(settings, "smtp_port", 587) or 587)))

# SendGrid support (optional)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", getattr(settings, "sendgrid_api_key", None))


def send_email_smtp(to: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict:
    """
    Phase 12: Send email via SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body
    
    Returns:
        Dictionary with success status
    """
    if not SMTP_USER or not SMTP_PASS:
        return {
            "success": False,
            "error": "SMTP credentials not configured. Set SMTP_USER and SMTP_PASS."
        }
    
    try:
        # Create message
        if html_body:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
        else:
            msg = MIMEText(body)
        
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to
        
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        return {
            "success": True,
            "method": "smtp"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def send_email_sendgrid(to: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict:
    """
    Phase 12: Send email via SendGrid API.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body
    
    Returns:
        Dictionary with success status
    """
    if not SENDGRID_API_KEY:
        return {
            "success": False,
            "error": "SendGrid API key not configured"
        }
    
    try:
        import requests
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "personalizations": [{
                "to": [{"email": to}]
            }],
            "from": {"email": SMTP_USER or "noreply@guruapi.com"},
            "subject": subject,
            "content": [
                {
                    "type": "text/plain",
                    "value": body
                }
            ]
        }
        
        if html_body:
            payload["content"].append({
                "type": "text/html",
                "value": html_body
            })
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 202:
            return {
                "success": True,
                "method": "sendgrid"
            }
        else:
            return {
                "success": False,
                "error": f"SendGrid API error: {response.status_code} - {response.text}"
            }
    
    except ImportError:
        return {
            "success": False,
            "error": "requests package required for SendGrid"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def send_email(to: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict:
    """
    Phase 12: Send email (tries SendGrid first, falls back to SMTP).
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body
    
    Returns:
        Dictionary with success status
    """
    # Try SendGrid first if available
    if SENDGRID_API_KEY:
        result = send_email_sendgrid(to, subject, body, html_body)
        if result["success"]:
            return result
    
    # Fall back to SMTP
    return send_email_smtp(to, subject, body, html_body)

