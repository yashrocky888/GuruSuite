"""
Phase 11: Payment Engine

Core payment processing logic, transaction management, and subscription upgrades.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import Transaction, User, Subscription
from src.payments.razorpay_client import verify_payment_signature, get_payment_details
from src.payments.stripe_client import verify_payment


# Phase 11: Payment plans
PAYMENT_PLANS = {
    "premium_monthly": {
        "name": "Premium Monthly",
        "amount_inr": 299.0,
        "amount_usd": 3.99,
        "duration_months": 1
    },
    "premium_yearly": {
        "name": "Premium Yearly",
        "amount_inr": 1999.0,
        "amount_usd": 24.99,
        "duration_months": 12
    },
    "lifetime": {
        "name": "Lifetime Premium",
        "amount_inr": 4999.0,
        "amount_usd": 59.99,
        "duration_months": None  # Lifetime
    }
}


def get_plan_details(plan_key: str) -> Optional[Dict]:
    """
    Phase 11: Get payment plan details.
    
    Args:
        plan_key: Plan key (premium_monthly, premium_yearly, lifetime)
    
    Returns:
        Plan details dictionary or None
    """
    return PAYMENT_PLANS.get(plan_key)


def save_transaction(
    user_id: int,
    plan: str,
    amount: float,
    currency: str,
    gateway: str,
    status: str = "pending",
    gateway_order_id: Optional[str] = None,
    gateway_payment_id: Optional[str] = None,
    payment_data: Optional[Dict] = None
) -> Transaction:
    """
    Phase 11: Save payment transaction to database.
    
    Args:
        user_id: User ID
        plan: Plan key
        amount: Payment amount
        currency: Currency code (INR, USD)
        gateway: Payment gateway (razorpay, stripe)
        status: Transaction status (pending, success, failed)
        gateway_order_id: Gateway order ID
        gateway_payment_id: Gateway payment ID
        payment_data: Additional payment data
    
    Returns:
        Transaction object
    """
    db = SessionLocal()
    try:
        transaction = Transaction(
            user_id=user_id,
            plan=plan,
            amount=amount,
            currency=currency,
            gateway=gateway,
            status=status,
            gateway_order_id=gateway_order_id,
            gateway_payment_id=gateway_payment_id,
            payment_data=payment_data
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def upgrade_subscription(user_id: int, plan: str) -> Dict:
    """
    Phase 11: Upgrade user subscription after successful payment.
    
    Args:
        user_id: User ID
        plan: Plan key (premium_monthly, premium_yearly, lifetime)
    
    Returns:
        Dictionary with upgrade result
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        plan_details = get_plan_details(plan)
        if not plan_details:
            raise ValueError(f"Invalid plan: {plan}")
        
        # Determine subscription level
        if plan == "lifetime":
            subscription_level = "lifetime"
            expires_on = None
        else:
            subscription_level = "premium"
            # Calculate expiry date
            duration_months = plan_details.get("duration_months", 1)
            expires_on = datetime.now() + timedelta(days=duration_months * 30)
        
        # Update user subscription level
        user.subscription_level = subscription_level
        
        # Create or update subscription record
        existing_sub = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == "active"
        ).first()
        
        if existing_sub:
            # Update existing subscription
            existing_sub.plan = subscription_level
            existing_sub.expires_on = expires_on
            existing_sub.is_active = "active"
        else:
            # Create new subscription
            new_sub = Subscription(
                user_id=user_id,
                plan=subscription_level,
                expires_on=expires_on,
                is_active="active"
            )
            db.add(new_sub)
        
        db.commit()
        
        return {
            "success": True,
            "user_id": user_id,
            "subscription_level": subscription_level,
            "expires_on": expires_on.isoformat() if expires_on else None
        }
    
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def verify_and_complete_payment(
    user_id: int,
    plan: str,
    gateway: str,
    gateway_order_id: Optional[str] = None,
    gateway_payment_id: Optional[str] = None,
    signature: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict:
    """
    Phase 11: Verify payment and complete subscription upgrade.
    
    Args:
        user_id: User ID
        plan: Plan key
        gateway: Payment gateway (razorpay, stripe)
        gateway_order_id: Gateway order ID (for Razorpay)
        gateway_payment_id: Gateway payment ID (for Razorpay)
        signature: Payment signature (for Razorpay verification)
        session_id: Stripe session ID (for Stripe)
    
    Returns:
        Dictionary with verification result
    """
    plan_details = get_plan_details(plan)
    if not plan_details:
        raise ValueError(f"Invalid plan: {plan}")
    
    # Verify payment based on gateway
    if gateway == "razorpay":
        if not gateway_order_id or not gateway_payment_id or not signature:
            raise ValueError("Missing Razorpay payment verification data")
        
        # Verify signature
        is_valid = verify_payment_signature(gateway_order_id, gateway_payment_id, signature)
        if not is_valid:
            raise ValueError("Invalid Razorpay payment signature")
        
        # Get payment details
        payment_details = get_payment_details(gateway_payment_id)
        amount = plan_details["amount_inr"]
        currency = "INR"
        
    elif gateway == "stripe":
        if not session_id:
            raise ValueError("Missing Stripe session ID")
        
        # Verify session
        session = verify_payment(session_id)
        if not session:
            raise ValueError("Invalid Stripe session")
        
        if session.payment_status != "paid":
            raise ValueError(f"Payment not completed. Status: {session.payment_status}")
        
        gateway_payment_id = session.payment_intent
        amount = plan_details["amount_usd"]
        currency = "USD"
        
    else:
        raise ValueError(f"Invalid gateway: {gateway}")
    
    # Update transaction status
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.plan == plan,
            Transaction.gateway == gateway,
            Transaction.status == "pending"
        ).order_by(Transaction.created_at.desc()).first()
        
        if transaction:
            transaction.status = "success"
            transaction.gateway_payment_id = gateway_payment_id
            transaction.updated_at = datetime.now()
            db.commit()
        else:
            # Create new transaction record if not found
            save_transaction(
                user_id=user_id,
                plan=plan,
                amount=amount,
                currency=currency,
                gateway=gateway,
                status="success",
                gateway_order_id=gateway_order_id,
                gateway_payment_id=gateway_payment_id
            )
    finally:
        db.close()
    
    # Upgrade subscription
    upgrade_result = upgrade_subscription(user_id, plan)
    
    return {
        "success": True,
        "message": "Payment verified and subscription upgraded",
        "transaction_id": transaction.id if transaction else None,
        "upgrade_result": upgrade_result
    }

