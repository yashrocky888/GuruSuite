"""
Phase 11: Stripe Payment Gateway Client

Handles Stripe payment operations for international users.
"""

import stripe
import os
from typing import Dict, Optional

from src.config import settings

# Phase 11: Stripe credentials from environment
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", getattr(settings, "stripe_secret_key", None))
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", getattr(settings, "stripe_publishable_key", None))

# Initialize Stripe
if STRIPE_SECRET_KEY:
    try:
        stripe.api_key = STRIPE_SECRET_KEY
    except Exception as e:
        print(f"Warning: Could not initialize Stripe: {e}")


def create_checkout_session(
    amount: float,
    currency: str = "usd",
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Phase 11: Create Stripe checkout session.
    
    Args:
        amount: Amount in dollars (will be converted to cents)
        currency: Currency code (default: usd)
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect after cancelled payment
        metadata: Optional metadata
    
    Returns:
        Stripe checkout session object
    
    Raises:
        ValueError: If Stripe is not initialized
    """
    if not STRIPE_SECRET_KEY:
        raise ValueError("Stripe not initialized. Set STRIPE_SECRET_KEY environment variable.")
    
    try:
        # Stripe amounts are in cents (smallest currency unit)
        # For USD: 1 dollar = 100 cents
        amount_in_cents = int(amount * 100)
        
        # Default URLs (should be configured in production)
        if not success_url:
            success_url = "https://yourapp.com/payment/success"
        if not cancel_url:
            cancel_url = "https://yourapp.com/payment/cancel"
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "unit_amount": amount_in_cents,
                    "product_data": {
                        "name": "Guru Premium Subscription",
                        "description": "Access to full AI-powered daily horoscope predictions"
                    }
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {}
        )
        
        return session
    
    except Exception as e:
        raise ValueError(f"Error creating Stripe checkout session: {str(e)}")


def verify_payment(session_id: str) -> Optional[Dict]:
    """
    Phase 11: Verify Stripe payment by retrieving session.
    
    Args:
        session_id: Stripe checkout session ID
    
    Returns:
        Session object with payment status or None
    """
    if not STRIPE_SECRET_KEY:
        return None
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except Exception as e:
        print(f"Error retrieving Stripe session: {e}")
        return None


def get_payment_intent(payment_intent_id: str) -> Optional[Dict]:
    """
    Phase 11: Get Stripe payment intent details.
    
    Args:
        payment_intent_id: Stripe payment intent ID
    
    Returns:
        Payment intent object or None
    """
    if not STRIPE_SECRET_KEY:
        return None
    
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent
    except Exception as e:
        print(f"Error retrieving Stripe payment intent: {e}")
        return None

