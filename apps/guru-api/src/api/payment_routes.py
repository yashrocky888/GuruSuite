"""
Payment API routes.

Phase 11: Payment gateway integration endpoints (Razorpay + Stripe).
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.db.database import get_db
from src.db.models import Transaction
from src.auth.middleware import get_current_user
from src.payments.razorpay_client import create_order
from src.payments.stripe_client import create_checkout_session
import os
from src.payments.payment_engine import (
    get_plan_details,
    PAYMENT_PLANS,
    save_transaction,
    verify_and_complete_payment
)

router = APIRouter()


# Phase 11: Request/Response schemas
class CreatePaymentRequest(BaseModel):
    plan: str  # premium_monthly, premium_yearly, lifetime
    gateway: str  # razorpay, stripe
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class VerifyPaymentRequest(BaseModel):
    plan: str
    gateway: str
    gateway_order_id: Optional[str] = None
    gateway_payment_id: Optional[str] = None
    signature: Optional[str] = None  # For Razorpay
    session_id: Optional[str] = None  # For Stripe


@router.get("/plans")
async def get_payment_plans():
    """
    Phase 11: Get available payment plans.
    
    Returns:
        List of available payment plans with pricing
    """
    plans = []
    for plan_key, plan_details in PAYMENT_PLANS.items():
        plans.append({
            "key": plan_key,
            "name": plan_details["name"],
            "amount_inr": plan_details["amount_inr"],
            "amount_usd": plan_details["amount_usd"],
            "duration_months": plan_details["duration_months"],
            "currency_inr": "INR",
            "currency_usd": "USD"
        })
    
    return {
        "plans": plans,
        "currencies": {
            "INR": "Indian Rupee (Razorpay)",
            "USD": "US Dollar (Stripe)"
        }
    }


@router.post("/create")
async def create_payment(
    request: CreatePaymentRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 11: Create payment order/session.
    
    Args:
        request: Payment creation request
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Payment order/session details
    """
    # Validate plan
    plan_details = get_plan_details(request.plan)
    if not plan_details:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {request.plan}")
    
    # Validate gateway
    if request.gateway not in ["razorpay", "stripe"]:
        raise HTTPException(status_code=400, detail="Invalid gateway. Use 'razorpay' or 'stripe'")
    
    try:
        if request.gateway == "razorpay":
            # Create Razorpay order
            amount = plan_details["amount_inr"]
            currency = "INR"
            
            order = create_order(
                amount=amount,
                currency=currency,
                notes={
                    "user_id": current_user.id,
                    "plan": request.plan,
                    "user_email": current_user.email
                }
            )
            
            # Save transaction
            transaction = save_transaction(
                user_id=current_user.id,
                plan=request.plan,
                amount=amount,
                currency=currency,
                gateway="razorpay",
                status="pending",
                gateway_order_id=order.get("id"),
                payment_data={"order": order}
            )
            
            return {
                "gateway": "razorpay",
                "order_id": order.get("id"),
                "amount": amount,
                "currency": currency,
                "key": os.getenv("RAZORPAY_KEY"),  # Publishable key for client
                "transaction_id": transaction.id,
                "order": order
            }
        
        elif request.gateway == "stripe":
            # Create Stripe checkout session
            amount = plan_details["amount_usd"]
            currency = "USD"
            
            session = create_checkout_session(
                amount=amount,
                currency=currency,
                success_url=request.success_url,
                cancel_url=request.cancel_url,
                metadata={
                    "user_id": str(current_user.id),
                    "plan": request.plan,
                    "user_email": current_user.email
                }
            )
            
            # Save transaction
            transaction = save_transaction(
                user_id=current_user.id,
                plan=request.plan,
                amount=amount,
                currency=currency,
                gateway="stripe",
                status="pending",
                gateway_order_id=session.get("id"),
                payment_data={"session": session}
            )
            
            return {
                "gateway": "stripe",
                "session_id": session.get("id"),
                "amount": amount,
                "currency": currency,
                "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
                "transaction_id": transaction.id,
                "session": session
            }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating payment: {str(e)}")


@router.post("/verify")
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 11: Verify payment and upgrade subscription.
    
    Args:
        request: Payment verification request
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Verification result and subscription upgrade status
    """
    try:
        result = verify_and_complete_payment(
            user_id=current_user.id,
            plan=request.plan,
            gateway=request.gateway,
            gateway_order_id=request.gateway_order_id,
            gateway_payment_id=request.gateway_payment_id,
            signature=request.signature,
            session_id=request.session_id
        )
        
        return {
            "success": True,
            "message": "Payment verified and subscription upgraded successfully",
            "result": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying payment: {str(e)}")


@router.get("/history")
async def get_payment_history(
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 11: Get user's payment transaction history.
    
    Args:
        limit: Maximum number of transactions to return
        offset: Number of transactions to skip
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of transactions
    """
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
    
    total_count = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).count()
    
    return {
        "total": total_count,
        "count": len(transactions),
        "transactions": [
            {
                "id": t.id,
                "plan": t.plan,
                "amount": t.amount,
                "currency": t.currency,
                "gateway": t.gateway,
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "gateway_order_id": t.gateway_order_id,
                "gateway_payment_id": t.gateway_payment_id
            }
            for t in transactions
        ]
    }


@router.get("/transaction/{transaction_id}")
async def get_transaction_details(
    transaction_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Phase 11: Get specific transaction details.
    
    Args:
        transaction_id: Transaction ID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Transaction details
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "id": transaction.id,
        "plan": transaction.plan,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "gateway": transaction.gateway,
        "status": transaction.status,
        "gateway_order_id": transaction.gateway_order_id,
        "gateway_payment_id": transaction.gateway_payment_id,
        "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
        "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
        "payment_data": transaction.payment_data
    }

