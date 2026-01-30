"""
CRUD operations for database interactions.
"""
from sqlalchemy.orm import Session
from models import Quiz, Question
from schemas import KeyEntities, QuestionSchema
from typing import List, Optional, Dict, Any


def create_quiz(
    db: Session,
    url: str,
    title: str,
    summary: str,
    key_entities: Dict[str, Any],
    sections: List[str],
    related_topics: List[str],
    questions: List[Dict[str, Any]],
    raw_html: Optional[str] = None,
) -> Quiz:
    """
    Create a new quiz with associated questions.
    """
    # Check if quiz already exists for this URL (caching bonus feature)
    existing = db.query(Quiz).filter(Quiz.url == url).first()
    if existing:
        return existing
    
    # Create quiz
    db_quiz = Quiz(
        url=url,
        title=title,
        summary=summary,
        key_entities=key_entities,
        sections=sections,
        related_topics=related_topics,
        raw_html=raw_html,
    )
    db.add(db_quiz)
    db.flush()  # Flush to get the quiz ID
    
    # Create questions
    for q in questions:
        db_question = Question(
            quiz_id=db_quiz.id,
            question=q["question"],
            options=q["options"],
            answer=q["answer"],
            difficulty=q.get("difficulty", "medium"),
            explanation=q.get("explanation", ""),
        )
        db.add(db_question)
    
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_quiz(db: Session, quiz_id: int) -> Optional[Quiz]:
    """Get a quiz by ID with its questions."""
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


def get_quizzes(db: Session, skip: int = 0, limit: int = 100) -> List[Quiz]:
    """Get all quizzes."""
    return db.query(Quiz).offset(skip).limit(limit).all()


def get_quiz_by_url(db: Session, url: str) -> Optional[Quiz]:
    """Get a quiz by URL."""
    return db.query(Quiz).filter(Quiz.url == url).first()


def delete_quiz(db: Session, quiz_id: int) -> bool:
    """Delete a quiz by ID."""
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz:
        db.delete(db_quiz)
        db.commit()
        return True
    return False
