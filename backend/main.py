"""
Main FastAPI application.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from config import settings
from database import get_db, init_db
from schemas import (
    QuizGenerateRequest, QuizResponse, QuizListResponse, ErrorResponse
)
from models import Quiz
import crud
from utils import scrape_wikipedia, generate_quiz_with_llm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Wiki Quiz Hub - Generate quizzes from Wikipedia articles using AI"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Wiki Quiz Hub API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post(
    "/api/quizzes/generate",
    response_model=QuizResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a quiz from a Wikipedia article URL.
    
    - **url**: Wikipedia article URL
    
    Returns:
    - Quiz with questions, entities, related topics, and more
    """
    try:
        url = str(request.url)
        
        # Check if quiz already exists (caching feature)
        existing_quiz = crud.get_quiz_by_url(db, url)
        if existing_quiz:
            logger.info(f"Quiz already exists for URL: {url}")
            return QuizResponse.model_validate(existing_quiz)
        
        logger.info(f"Starting quiz generation for URL: {url}")
        
        # 1. Scrape Wikipedia
        logger.info("Scraping Wikipedia...")
        scraped_data = scrape_wikipedia(url)
        
        # 2. Generate quiz with LLM
        logger.info("Generating quiz with LLM...")
        llm_output = generate_quiz_with_llm(
            scraped_data["title"],
            scraped_data["content"]
        )
        
        # 3. Save to database
        logger.info("Saving quiz to database...")
        db_quiz = crud.create_quiz(
            db=db,
            url=url,
            title=scraped_data["title"],
            summary=llm_output["summary"],
            key_entities=llm_output["key_entities"],
            sections=llm_output["sections"],
            related_topics=llm_output["related_topics"],
            questions=llm_output["quiz"],
            raw_html=scraped_data.get("raw_html"),
        )
        
        logger.info(f"Quiz generated successfully with ID: {db_quiz.id}")
        return QuizResponse.model_validate(db_quiz)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz"
        )


@app.get(
    "/api/quizzes",
    response_model=List[QuizListResponse],
    responses={500: {"model": ErrorResponse}}
)
async def list_quizzes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of all quizzes.
    
    - **skip**: Number of quizzes to skip (default: 0)
    - **limit**: Maximum number of quizzes to return (default: 100)
    
    Returns:
    - List of quizzes with basic information
    """
    try:
        quizzes = crud.get_quizzes(db, skip=skip, limit=limit)
        return [QuizListResponse.model_validate(q) for q in quizzes]
    except Exception as e:
        logger.error(f"Error listing quizzes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quizzes"
        )


@app.get(
    "/api/quizzes/{quiz_id}",
    response_model=QuizResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific quiz by ID with all questions.
    
    - **quiz_id**: Quiz ID
    
    Returns:
    - Quiz with all details and questions
    """
    try:
        quiz = crud.get_quiz(db, quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} not found"
            )
        return QuizResponse.model_validate(quiz)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quiz"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
