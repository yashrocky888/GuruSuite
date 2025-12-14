"""
Authentication API routes.

Phase 9: User signup, login, and authentication endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from src.db.database import get_db
from src.db.models import User, LoginLog
from src.auth.auth_utils import hash_password, verify_password
from src.auth.jwt_handler import create_token, get_user_from_token
from src.auth.middleware import get_current_user

router = APIRouter()
security = HTTPBearer()


# Phase 9: Request/Response schemas
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
    subscription: str
    user_id: int


@router.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Phase 9: User signup endpoint.
    
    Creates a new user account with hashed password.
    
    Args:
        request: Signup request with name, email, password
        db: Database session
    
    Returns:
        Success message with user ID
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Create new user
    new_user = User(
        name=request.name,
        email=request.email,
        password=hashed_password,
        phone=request.phone,
        subscription_level="free"  # Default to free tier
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "email": new_user.email
    }


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Phase 9: User login endpoint.
    
    Authenticates user and returns JWT token.
    
    Args:
        request: Login request with email and password
        db: Database session
    
    Returns:
        JWT token and user subscription level
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Log failed login attempt
        login_log = LoginLog(
            user_id=0,  # Unknown user
            success="failed",
            ip_address=None,
            user_agent=None
        )
        db.add(login_log)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(request.password, user.password):
        # Log failed login attempt
        login_log = LoginLog(
            user_id=user.id,
            success="failed",
            ip_address=None,
            user_agent=None
        )
        db.add(login_log)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    token = create_token(user.id, user.subscription_level)
    
    # Log successful login
    login_log = LoginLog(
        user_id=user.id,
        success="success",
        ip_address=None,
        user_agent=None
    )
    db.add(login_log)
    db.commit()
    
    return {
        "token": token,
        "subscription": user.subscription_level,
        "user_id": user.id,
        "name": user.name
    }


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Phase 9: Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user (from middleware)
    
    Returns:
        User information
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "subscription_level": current_user.subscription_level,
        "daily_notifications": current_user.daily_notifications
    }



