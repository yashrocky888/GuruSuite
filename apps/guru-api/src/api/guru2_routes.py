"""
Guru Conversation Engine 2.0 API routes.

Phase 17: Enhanced chat system with memory and long conversations.
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from pydantic import BaseModel

from src.auth.jwt_handler import decode_token
from src.guru2.long_chat_engine import process_long_chat, get_conversation_history
from src.db.database import SessionLocal
from src.db.models import User

router = APIRouter()


class QuestionRequest(BaseModel):
    """Request model for asking a question."""
    question: str


def get_user_from_token(token: str) -> User:
    """
    Phase 17: Get user from JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        User object
    
    Raises:
        HTTPException if token is invalid
    """
    try:
        token_data = decode_token(token)
        user_id = token_data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        finally:
            db.close()
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


@router.post("/ask")
async def guru_chat_v2(
    request: QuestionRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Phase 17: Ask the Guru (Conversation Engine 2.0).
    
    Features:
    - Multi-turn conversations with memory
    - Long, detailed answers
    - Shastra-based reasoning
    - Emotional and spiritual tone
    - Detected events included
    - Follow-up questions
    
    Requires:
    - Valid JWT token in Authorization header
    - User must have birth data saved
    
    Args:
        request: QuestionRequest with question text
        authorization: Bearer token in header
    
    Returns:
        Dictionary with question and comprehensive AI answer
    """
    # Extract token from Authorization header
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization.replace("Bearer ", "").strip()
    
    # Get user
    user = get_user_from_token(token)
    
    # Validate question
    if not request.question or len(request.question.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="Question must be at least 5 characters long"
        )
    
    # Process question in long chat mode
    result = process_long_chat(user, request.question.strip())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to process question"))
    
    return result


@router.get("/history")
async def get_chat_history(
    authorization: Optional[str] = Header(None),
    limit: int = 10
):
    """
    Phase 17: Get conversation history for Guru 2.0.
    
    Args:
        authorization: Bearer token in header
        limit: Maximum number of conversations (default: 10)
    
    Returns:
        List of previous conversations
    """
    # Extract token
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "").strip()
    
    # Get user
    user = get_user_from_token(token)
    
    # Get conversation history
    history = get_conversation_history(user.id, limit=min(limit, 50))
    
    return {
        "user_id": user.id,
        "total_conversations": len(history),
        "conversations": history
    }


@router.get("/ask")
async def guru_chat_v2_get(
    question: str,
    authorization: Optional[str] = Header(None)
):
    """
    Phase 17: Ask the Guru (GET method for convenience).
    
    Args:
        question: Question text
        authorization: Bearer token
    
    Returns:
        Comprehensive AI answer
    """
    # Extract token
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "").strip()
    
    # Get user
    user = get_user_from_token(token)
    
    # Process question
    result = process_long_chat(user, question.strip())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to process question"))
    
    return result

