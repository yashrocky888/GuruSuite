"""
Ask the Guru API routes.

Phase 14: AI-powered astrology question-answer system.
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from pydantic import BaseModel

from src.auth.jwt_handler import decode_token
from src.guru.question_engine import process_question, get_user_questions
from src.db.database import SessionLocal
from src.db.models import User

router = APIRouter()


class QuestionRequest(BaseModel):
    """Request model for asking a question."""
    question: str


def get_user_from_token(token: str) -> User:
    """
    Phase 14: Get user from JWT token.
    
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
async def ask_guru(
    request: QuestionRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Phase 14: Ask the Guru a question.
    
    Requires:
    - Valid JWT token in Authorization header
    - User must have birth data saved
    
    Args:
        request: QuestionRequest with question text
        authorization: Bearer token in header
    
    Returns:
        Dictionary with question and AI Guru answer
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
    
    # Process question
    result = process_question(user, request.question.strip())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to process question"))
    
    return result


@router.get("/history")
async def get_question_history(
    authorization: Optional[str] = Header(None),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of questions to return")
):
    """
    Phase 14: Get user's question history.
    
    Args:
        authorization: Bearer token in header
        limit: Maximum number of questions (1-100)
    
    Returns:
        List of previous questions and answers
    """
    # Extract token from Authorization header
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization.replace("Bearer ", "").strip()
    
    # Get user
    user = get_user_from_token(token)
    
    # Get question history
    questions = get_user_questions(user.id, limit)
    
    return {
        "user_id": user.id,
        "total_questions": len(questions),
        "questions": questions
    }


@router.get("/ask")
async def ask_guru_get(
    question: str = Query(..., min_length=5, description="Question to ask the Guru"),
    authorization: Optional[str] = Header(None)
):
    """
    Phase 14: Ask the Guru (GET method for convenience).
    
    Args:
        question: Question text
        authorization: Bearer token in header
    
    Returns:
        Dictionary with question and AI Guru answer
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
    result = process_question(user, question.strip())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to process question"))
    
    return result

