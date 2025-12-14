"""
Phase 17: Long Chat Engine for Guru Conversation 2.0

Processes multi-turn conversations with memory.
"""

from typing import Dict, List
from src.guru2.context_manager import build_full_context
from src.guru2.ai_engine_v2 import guru_ai_v2
from src.db.database import SessionLocal
from src.db.models import BirthDetail, Question, User


def get_conversation_history(user_id: int, limit: int = 10) -> List[Dict]:
    """
    Phase 17: Get user's conversation history.
    
    Args:
        user_id: User ID
        limit: Maximum number of conversations to return
    
    Returns:
        List of conversation dictionaries
    """
    db = SessionLocal()
    
    try:
        questions = db.query(Question).filter(
            Question.user_id == user_id
        ).order_by(
            Question.created_at.desc()
        ).limit(limit).all()
        
        # Reverse to get chronological order
        history = [
            {
                "q": q.question,
                "a": q.answer,
                "timestamp": q.created_at.isoformat() if q.created_at else None
            }
            for q in reversed(questions)
        ]
        
        return history
    
    except Exception as e:
        return []
    
    finally:
        db.close()


def process_long_chat(user: User, question: str) -> Dict:
    """
    Phase 17: Process a question in long conversation mode.
    
    Args:
        user: User object
        question: User's question
    
    Returns:
        Dictionary with question and comprehensive answer
    """
    db = SessionLocal()
    
    try:
        # Get user's birth data
        birth_data = db.query(BirthDetail).filter(BirthDetail.user_id == user.id).first()
        
        if not birth_data:
            return {
                "error": "Birth data not found",
                "message": "Please save your birth details first to use Guru Conversation 2.0."
            }
        
        # Build complete context with events
        context = build_full_context(birth_data)
        
        # Get conversation history
        history = get_conversation_history(user.id, limit=10)
        
        # Get AI Guru answer with memory
        answer = guru_ai_v2(question, context, history)
        
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
            "created_at": question_entry.created_at.isoformat(),
            "events_detected": {
                "bad_events": len(context.get("events", {}).get("bad_events", [])),
                "good_events": len(context.get("events", {}).get("good_events", [])),
                "day_status": context.get("events", {}).get("day_status", "normal")
            },
            "conversation_context": {
                "total_previous_questions": len(history),
                "dasha_period": context.get("dasha", {}).get("current_dasha", {}).get("dasha_lord", "Unknown"),
                "current_nakshatra": context.get("panchang", {}).get("nakshatra", {}).get("name", "Unknown")
            }
        }
    
    except Exception as e:
        db.rollback()
        return {
            "error": "Failed to process question",
            "message": str(e)
        }
    
    finally:
        db.close()

