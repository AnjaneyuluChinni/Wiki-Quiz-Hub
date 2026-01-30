"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
from datetime import datetime


class KeyEntities(BaseModel):
    """Key entities extracted from article."""
    people: List[str] = []
    organizations: List[str] = []
    locations: List[str] = []


class QuestionSchema(BaseModel):
    """Question schema for quiz."""
    question: str
    options: List[str]
    answer: str
    difficulty: str
    explanation: str
    
    class Config:
        from_attributes = True


class QuizGenerateRequest(BaseModel):
    """Request to generate a quiz from a Wikipedia URL."""
    url: HttpUrl


class QuizResponse(BaseModel):
    """Quiz response with all details."""
    id: int
    url: str
    title: str
    summary: str
    key_entities: KeyEntities
    sections: List[str]
    related_topics: List[str]
    questions: List[QuestionSchema]
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizListResponse(BaseModel):
    """Quiz list item response."""
    id: int
    url: str
    title: str
    summary: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LLMQuizOutput(BaseModel):
    """Expected output structure from LLM."""
    summary: str
    key_entities: KeyEntities
    sections: List[str]
    related_topics: List[str]
    quiz: List[QuestionSchema]


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    status_code: int = 400
