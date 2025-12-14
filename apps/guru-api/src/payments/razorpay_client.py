"""
Phase 11: Razorpay Payment Gateway Client

Handles Razorpay payment operations for Indian users.
"""

import razorpay
import os
from typing import Dict, Optional

from src.config import settings

# Phase 11: Razorpay credentials from environment
RAZORPAY_KEY = os.getenv("RAZORPAY_KEY", getattr(settings, "razorpay_key", None))
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET", getattr(settings, "razorpay_secret", None))

# Initialize Razorpay client
client = None
if RAZORPAY_KEY and RAZORPAY_SECRET:
    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
    except Exception as e:
        print(f"Warning: Could not initialize Razorpay client: {e}")


def create_order(amount: float, currency: str = "INR", notes: Optional[Dict] = None) -> Dict:
    """
    Phase 11: Create Razorpay payment order.
    
    Args:
        amount: Amount in rupees (will be converted to paise)
        currency: Currency code (default: INR)
        notes: Optional notes/metadata
    
    Returns:
        Razorpay order object
    
    Raises:
        ValueError: If Razorpay client is not initialized
    """
    if not client:
        raise ValueError("Razorpay client not initialized. Set RAZORPAY_KEY and RAZORPAY_SECRET environment variables.")
    
    try:
        # Razorpay amounts are in paise (smallest currency unit)
        # For INR: 1 rupee = 100 paise
        amount_in_paise = int(amount * 100)
        
        order_data = {
            "amount": amount_in_paise,
            "currency": currency,
            "payment_capture": 1,  # Auto-capture payment
            "notes": notes or {}
        }
        
        order = client.order.create(data=order_data)
        return order
    
    except Exception as e:
        raise ValueError(f"Error creating Razorpay order: {str(e)}")


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """
    Phase 11: Verify Razorpay payment signature.
    
    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        signature: Payment signature from Razorpay
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not client:
        return False
    
    try:
        # Verify payment signature
        params = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        }
        
        client.utility.verify_payment_signature(params)
        return True
    
    except Exception as e:
        print(f"Razorpay signature verification failed: {e}")
        return False


def get_payment_details(payment_id: str) -> Optional[Dict]:
    """
    Phase 11: Get payment details from Razorpay.
    
    Args:
        payment_id: Razorpay payment ID
    
    Returns:
        Payment details dictionary or None
    """
    if not client:
        return None
    
    try:
        payment = client.payment.fetch(payment_id)
        return payment
    except Exception as e:
        print(f"Error fetching Razorpay payment: {e}")
        return None

