"""
FastAPI server in test mode (no database required)
Stores quizzes in memory for demonstration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, List
import json

from config import settings
from schemas import QuizGenerateRequest, QuizResponse, QuestionSchema
from utils import scrape_wikipedia, generate_quiz_with_llm

# In-memory storage (for testing)
quizzes_db: Dict[str, dict] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ API started (test mode - no database)")
    yield
    print("API shutdown")

app = FastAPI(
    title="Wiki Quiz Hub API",
    description="Generate quizzes from Wikipedia articles",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "test (in-memory)"}

@app.get("/api")
async def api_root():
    return {
        "message": "Wiki Quiz Hub API",
        "docs": "/docs",
        "quizzes_in_memory": len(quizzes_db)
    }

@app.get("/api/quizzes", response_model=dict)
async def list_quizzes():
    quizzes = list(quizzes_db.values())
    return {
        "total": len(quizzes),
        "quizzes": quizzes
    }

@app.get("/api/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str):
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return QuizResponse(**quizzes_db[quiz_id])

@app.post("/api/quizzes/generate", response_model=QuizResponse)
async def generate_quiz(request: QuizGenerateRequest):
    """
    Generate a quiz from a Wikipedia article URL
    """
    print(f"📝 Generating quiz for: {request.url}")
    
    # Check if already exists
    if request.url in quizzes_db:
        print(f"✅ Quiz already exists")
        return QuizResponse(**quizzes_db[request.url])
    
    try:
        # Scrape Wikipedia
        article_data = scrape_wikipedia(request.url)
        print(f"✅ Scraped article: {article_data['title']}")
        
        # Generate quiz with LLM
        quiz_data = generate_quiz_with_llm(
            title=article_data["title"],
            content=article_data["content"][:3000],  # Limit content
            num_questions=request.num_questions
        )
        
        # Convert questions to schema
        questions = [
            QuestionSchema(
                question=q["question"],
                options=q["options"],
                answer=q["answer"],
                difficulty=q.get("difficulty", "medium"),
                explanation=q.get("explanation", "")
            )
            for q in quiz_data.get("questions", [])
        ]
        
        # Store quiz
        quiz_response = QuizResponse(
            id=len(quizzes_db) + 1,
            url=request.url,
            title=quiz_data.get("title", article_data["title"]),
            summary=quiz_data.get("summary", article_data.get("summary", "")),
            questions=questions,
            key_entities=quiz_data.get("key_entities", []),
            sections=quiz_data.get("sections", []),
            related_topics=quiz_data.get("related_topics", [])
        )
        
        quizzes_db[request.url] = quiz_response.model_dump()
        print(f"✅ Quiz generated with {len(questions)} questions")
        return quiz_response
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
