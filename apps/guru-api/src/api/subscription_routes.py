"""
Subscription API routes.

Phase 9: Subscription management and status endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from src.db.database import get_db
from src.db.models import User, Subscription
from src.auth.middleware import get_current_user

router = APIRouter()


@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 9: Get user's subscription status.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Subscription status and details
    """
    # Get active subscription
    active_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == "active"
    ).first()
    
    # Check if subscription is expired
    if active_subscription and active_subscription.expires_on:
        if active_subscription.expires_on < datetime.now(active_subscription.expires_on.tzinfo):
            active_subscription.is_active = "expired"
            current_user.subscription_level = "free"
            db.commit()
            active_subscription = None
    
    if active_subscription:
        return {
            "plan": active_subscription.plan,
            "starts_on": active_subscription.starts_on.isoformat() if active_subscription.starts_on else None,
            "expires_on": active_subscription.expires_on.isoformat() if active_subscription.expires_on else None,
            "is_active": active_subscription.is_active,
            "is_lifetime": active_subscription.expires_on is None
        }
    else:
        return {
            "plan": current_user.subscription_level or "free",
            "starts_on": None,
            "expires_on": None,
            "is_active": "active" if current_user.subscription_level in ["premium", "lifetime"] else "inactive",
            "is_lifetime": current_user.subscription_level == "lifetime"
        }


@router.post("/upgrade")
async def upgrade_subscription(
    plan: str = "premium",
    months: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 9: Upgrade user subscription (for testing/admin use).
    
    In production, this would integrate with payment gateway.
    
    Args:
        plan: Subscription plan (premium, lifetime)
        months: Number of months (ignored for lifetime)
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated subscription status
    """
    if plan not in ["premium", "lifetime"]:
        raise HTTPException(status_code=400, detail="Invalid plan. Use 'premium' or 'lifetime'")
    
    # Create or update subscription
    existing_sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == "active"
    ).first()
    
    if existing_sub:
        # Update existing subscription
        existing_sub.plan = plan
        if plan == "lifetime":
            existing_sub.expires_on = None
        else:
            if existing_sub.expires_on and existing_sub.expires_on > datetime.now(existing_sub.expires_on.tzinfo):
                # Extend from current expiry
                existing_sub.expires_on = existing_sub.expires_on + timedelta(days=months * 30)
            else:
                # Start from now
                existing_sub.expires_on = datetime.now() + timedelta(days=months * 30)
        existing_sub.is_active = "active"
    else:
        # Create new subscription
        expires_on = None if plan == "lifetime" else datetime.now() + timedelta(days=months * 30)
        new_sub = Subscription(
            user_id=current_user.id,
            plan=plan,
            expires_on=expires_on,
            is_active="active"
        )
        db.add(new_sub)
    
    # Update user subscription level
    current_user.subscription_level = plan
    db.commit()
    
    return {
        "message": f"Subscription upgraded to {plan}",
        "plan": plan,
        "expires_on": None if plan == "lifetime" else (datetime.now() + timedelta(days=months * 30)).isoformat()
    }



