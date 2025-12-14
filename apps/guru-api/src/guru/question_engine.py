"""
Phase 14: Question Engine

Processes user questions and generates AI Guru answers.
"""

from typing import Dict, Optional
from src.guru.context_builder import build_context
from src.guru.ai_guru import ask_guru_ai
from src.db.database import SessionLocal
from src.db.models import BirthDetail, Question, User


def process_question(user: User, question: str) -> Dict:
    """
    Phase 14: Process a user question and generate AI Guru answer.
    
    Args:
        user: User object
        question: User's question in natural language
    
    Returns:
        Dictionary with question and answer
    """
    db = SessionLocal()
    
    try:
        # Get user's birth data
        birth_data = db.query(BirthDetail).filter(BirthDetail.user_id == user.id).first()
        
        if not birth_data:
            return {
                "error": "Birth data not found",
                "message": "Please save your birth details first to use Ask the Guru feature."
            }
        
        # Build complete astrological context
        context = build_context(birth_data)
        
        # Get AI Guru answer
        answer = ask_guru_ai(question, context)
        
        # Store question and answer in database
        question_entry = Question(
            user_id=user.id,
            question=question,
            answer=answer
        )
        db.add(question_entry)
        db.commit()
        
        return {
            "success": True,
            "question": question,
            "answer": answer,
            "question_id": question_entry.id,
            "created_at": question_entry.created_at.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        return {
            "error": "Failed to process question",
            "message": str(e)
        }
    
    finally:
        db.close()


def get_user_questions(user_id: int, limit: int = 50) -> list:
    """
    Phase 14: Get user's question history.
    
    Args:
        user_id: User ID
        limit: Maximum number of questions to return
    
    Returns:
        List of question dictionaries
    """
    db = SessionLocal()
    
    try:
        questions = db.query(Question).filter(
            Question.user_id == user_id
        ).order_by(
            Question.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": q.id,
                "question": q.question,
                "answer": q.answer,
                "created_at": q.created_at.isoformat() if q.created_at else None
            }
            for q in questions
        ]
    
    except Exception as e:
        return []
    
    finally:
        db.close()

