"""
SQLAlchemy models for Quiz and Question entities.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime


class Quiz(Base):
    """Quiz model representing a Wikipedia article quiz."""
    
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    key_entities = Column(
        JSON,
        nullable=False,
        default={"people": [], "organizations": [], "locations": []}
    )
    sections = Column(JSON, nullable=False, default=[])
    related_topics = Column(JSON, nullable=False, default=[])
    raw_html = Column(Text, nullable=True)  # Bonus: store raw HTML
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationship to questions
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    """Question model representing a quiz question."""
    
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # Array of 4 options
    answer = Column(String(500), nullable=False)
    difficulty = Column(String(20), nullable=False, default="medium")  # easy, medium, hard
    explanation = Column(Text, nullable=False)
    
    # Relationship to quiz
    quiz = relationship("Quiz", back_populates="questions")
