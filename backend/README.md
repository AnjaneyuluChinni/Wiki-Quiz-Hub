# Wiki Quiz Hub - FastAPI Backend

A production-ready FastAPI backend for generating AI-powered quizzes from Wikipedia articles.

## Tech Stack

- **Framework:** FastAPI 0.104.1 (Python 3.9+)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Scraping:** BeautifulSoup4
- **LLM:** OpenAI API or Google Gemini (with fallback to dummy data)
- **Validation:** Pydantic v2

## Features

✅ Generate quizzes from Wikipedia article URLs  
✅ AI-powered question generation (5-10 questions per article)  
✅ Extract key entities, sections, and related topics  
✅ Store and retrieve quiz history  
✅ Caching to prevent duplicate scraping  
✅ Store raw HTML for reference (bonus feature)  
✅ Full error handling and validation  
✅ RESTful API with OpenAPI documentation  
✅ CORS enabled for frontend integration  

## Project Structure

```
backend/
├── main.py              # FastAPI application and routes
├── config.py            # Configuration and settings
├── database.py          # Database setup and session management
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic request/response schemas
├── crud.py              # Database operations (Create, Read)
├── utils.py             # Scraping, LLM integration utilities
├── seed_database.py     # Sample data seeding script
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip or conda

### 1. Clone the Repository

```bash
cd backend
```

### 2. Create Virtual Environment

**Using venv:**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**Using conda:**
```bash
conda create -n wiki-quiz python=3.9
conda activate wiki-quiz
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

Create a PostgreSQL database:

```sql
CREATE DATABASE wiki_quiz;
CREATE USER wiki_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE wiki_quiz TO wiki_user;
```

### 5. Setup Environment Variables

Create `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://wiki_user:your_secure_password@localhost:5432/wiki_quiz

# API Keys (choose one - leave blank to use dummy data)
OPENAI_API_KEY=sk_your_openai_key_here
# OR
GOOGLE_API_KEY=your_google_generativeai_key_here

# Application Settings
DEBUG=False
```

### 6. Initialize Database

```bash
python seed_database.py
```

This will create all tables and populate sample data.

## Running Locally

### Development Mode

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy"
}
```

### Generate Quiz

```bash
POST /api/quizzes/generate
Content-Type: application/json

{
  "url": "https://en.wikipedia.org/wiki/Alan_Turing"
}
```

Response (201 Created):
```json
{
  "id": 1,
  "url": "https://en.wikipedia.org/wiki/Alan_Turing",
  "title": "Alan Turing",
  "summary": "...",
  "key_entities": {
    "people": [...],
    "organizations": [...],
    "locations": [...]
  },
  "sections": [...],
  "related_topics": [...],
  "questions": [
    {
      "question": "...",
      "options": [...],
      "answer": "...",
      "difficulty": "easy|medium|hard",
      "explanation": "..."
    }
  ],
  "created_at": "2024-01-30T10:00:00"
}
```

### List All Quizzes

```bash
GET /api/quizzes?skip=0&limit=100
```

Response (200 OK):
```json
[
  {
    "id": 1,
    "url": "https://en.wikipedia.org/wiki/Alan_Turing",
    "title": "Alan Turing",
    "summary": "...",
    "created_at": "2024-01-30T10:00:00"
  }
]
```

### Get Quiz by ID

```bash
GET /api/quizzes/{quiz_id}
```

Response (200 OK):
```json
{
  "id": 1,
  "url": "https://en.wikipedia.org/wiki/Alan_Turing",
  "title": "Alan Turing",
  "summary": "...",
  "key_entities": {...},
  "sections": [...],
  "related_topics": [...],
  "questions": [...],
  "created_at": "2024-01-30T10:00:00"
}
```

## Testing Endpoints

### Using curl

```bash
# Generate quiz
curl -X POST http://localhost:8000/api/quizzes/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Marie_Curie"}'

# List quizzes
curl http://localhost:8000/api/quizzes

# Get specific quiz
curl http://localhost:8000/api/quizzes/1
```

### Using Python requests

```python
import requests

# Generate quiz
response = requests.post(
    "http://localhost:8000/api/quizzes/generate",
    json={"url": "https://en.wikipedia.org/wiki/Python_(programming_language)"}
)
print(response.json())

# List quizzes
response = requests.get("http://localhost:8000/api/quizzes")
print(response.json())
```

## Deployment to Render

### 1. Prepare Repository

Ensure you have:
- `backend/requirements.txt` ✅
- `backend/main.py` ✅
- `backend/.env.example` ✅
- GitHub account with the code pushed

### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### 3. Deploy Backend Service

1. Click **New +** → **Web Service**
2. Select your repository
3. Configure:
   - **Name:** `wiki-quiz-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`
   - **Instance Type:** Free (or upgrade as needed)

4. Click **Create Web Service**

### 4. Add PostgreSQL Database

1. Click **New +** → **PostgreSQL**
2. Configure:
   - **Name:** `wiki-quiz-db`
   - **Region:** Same as API service
   - **PostgreSQL Version:** 14
   - **Instance Type:** Free

3. Click **Create Database**

### 5. Configure Environment Variables

In the Web Service settings (Environment):

```
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/wiki_quiz
OPENAI_API_KEY=sk_your_key
DEBUG=False
```

Get the database connection string from the PostgreSQL service details.

### 6. Deploy Frontend to Render (Optional)

Frontend should make API calls to: `https://wiki-quiz-api.onrender.com`

Update the API endpoint in your React app:

```typescript
// In client/src/lib/queryClient.ts or API config
const API_BASE = import.meta.env.VITE_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://wiki-quiz-api.onrender.com'
    : 'http://localhost:8000');
```

### 7. Monitor Deployment

- **Logs:** Available in Render dashboard
- **Metrics:** CPU, memory, request count
- **Custom Domain:** Add in service settings

### Troubleshooting Render Deployment

**Issue:** "ModuleNotFoundError"
- Solution: Ensure all dependencies are in `requirements.txt`

**Issue:** Database connection failed
- Solution: Check `DATABASE_URL` in environment variables
- Verify PostgreSQL instance is in same region

**Issue:** Cold start takes long
- Solution: Use paid instance for faster response times

## LLM Integration

### Using OpenAI API

1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk_your_key_here
   ```
3. Uses GPT-3.5-turbo by default

### Using Google Gemini API

1. Get API key from [makersuite.google.com](https://makersuite.google.com)
2. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_key_here
   ```
3. Uses Gemini Pro model

### Without API Keys

The system will work with dummy data for testing. This allows full UI/UX testing without spending API credits.

## Database Schema

### quizzes table
```sql
CREATE TABLE quizzes (
  id SERIAL PRIMARY KEY,
  url VARCHAR(2048) UNIQUE NOT NULL,
  title VARCHAR(255) NOT NULL,
  summary TEXT NOT NULL,
  key_entities JSONB NOT NULL,
  sections JSONB NOT NULL,
  related_topics JSONB NOT NULL,
  raw_html TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### questions table
```sql
CREATE TABLE questions (
  id SERIAL PRIMARY KEY,
  quiz_id INTEGER NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  options JSONB NOT NULL,
  answer VARCHAR(500) NOT NULL,
  difficulty VARCHAR(20) NOT NULL,
  explanation TEXT NOT NULL
);
```

## Sample API Responses

See `sample_data/` folder for example JSON outputs from different Wikipedia articles.

## File Structure for Submission

```
Wiki-Quiz-Hub/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── utils.py
│   ├── seed_database.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md (this file)
├── client/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── sample_data/
│   ├── alan_turing.json
│   ├── marie_curie.json
│   └── python_programming.json
└── DEPLOYMENT.md (deployment guide)
```

## Key Features Implemented

### Core Requirements ✅
- ✅ FastAPI backend
- ✅ PostgreSQL database
- ✅ Wikipedia scraping with BeautifulSoup
- ✅ LLM integration (OpenAI/Gemini)
- ✅ Quiz generation (5-10 questions)
- ✅ Key entity extraction
- ✅ Related topics suggestion
- ✅ Quiz history storage
- ✅ RESTful API

### Bonus Features ✅
- ✅ URL caching (prevent duplicate scraping)
- ✅ Raw HTML storage
- ✅ Environment-based configuration
- ✅ Comprehensive error handling
- ✅ Sample data seeding
- ✅ Full API documentation
- ✅ Render deployment guide

## Error Handling

The API handles:
- Invalid URLs
- Failed network requests
- Missing article content
- LLM generation failures (falls back to dummy data)
- Database errors
- Validation errors with clear messages

## Performance Considerations

- **Caching:** Duplicate URLs return cached quiz without re-scraping
- **Content Limits:** Article content limited to 15K characters for LLM efficiency
- **Connection Pooling:** SQLAlchemy pool configured for concurrent requests
- **Async:** FastAPI's async support for non-blocking I/O

## Contributing

To add new features:

1. Create new models in `models.py`
2. Add schemas in `schemas.py`
3. Add CRUD operations in `crud.py`
4. Add routes in `main.py`
5. Add utilities in `utils.py` if needed

## License

MIT License - See LICENSE file

## Support

For issues or questions:
1. Check API docs at `/docs`
2. Review error messages in logs
3. Test with sample URLs provided
4. Verify database connection

## Version History

- **v1.0.0** (2024-01-30) - Initial release with full FastAPI implementation
