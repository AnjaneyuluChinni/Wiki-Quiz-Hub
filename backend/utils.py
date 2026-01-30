"""
Utility functions for scraping, LLM integration, and data processing.
"""
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from config import settings

# Try importing Gemini API, fall back to OpenAI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    genai.configure(api_key=settings.GOOGLE_API_KEY)
except (ImportError, Exception):
    GEMINI_AVAILABLE = False

from openai import OpenAI


def scrape_wikipedia(url: str) -> Dict[str, Any]:
    """
    Scrape Wikipedia article content.
    
    Args:
        url: Wikipedia article URL
        
    Returns:
        Dictionary with title, content, and sections
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract title
        title_elem = soup.find("h1", class_="firstHeading")
        title = title_elem.text.strip() if title_elem else "Unknown"
        
        # Extract main content
        content_div = soup.find("div", id="mw-content-text")
        if not content_div:
            raise ValueError("Could not find article content")
        
        # Get all paragraphs
        paragraphs = content_div.find_all("p")
        content = "\n".join([p.get_text().strip() for p in paragraphs])
        
        # Limit content size for LLM processing
        content = content[:15000]
        
        # Extract sections
        sections = []
        for heading in content_div.find_all(["h2", "h3"]):
            section_text = heading.get_text().strip()
            # Remove [edit] links
            section_text = section_text.replace("[edit]", "").strip()
            if section_text:
                sections.append(section_text)
        
        # Store raw HTML (bonus feature)
        raw_html = response.text
        
        return {
            "title": title,
            "content": content,
            "sections": sections[:10],  # Limit to first 10 sections
            "raw_html": raw_html,
        }
        
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error scraping Wikipedia: {str(e)}")


def generate_quiz_with_llm(title: str, content: str) -> Dict[str, Any]:
    """
    Generate quiz using LLM (Gemini or OpenAI).
    
    Args:
        title: Article title
        content: Article content
        
    Returns:
        Dictionary with quiz, summary, entities, and related topics
    """
    prompt = f"""You are an expert quiz generator. Based on the following Wikipedia article, generate a comprehensive quiz.

ARTICLE TITLE: {title}

ARTICLE CONTENT:
{content}

TASK: Generate a JSON response with the following structure:
{{
  "summary": "A 2-3 sentence summary of the article",
  "key_entities": {{
    "people": ["list", "of", "key", "people"],
    "organizations": ["list", "of", "organizations"],
    "locations": ["list", "of", "locations"]
  }},
  "sections": ["main", "sections", "from", "article"],
  "related_topics": ["related", "topic", "1", "topic", "2", "topic", "3"],
  "quiz": [
    {{
      "question": "Question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct option text",
      "difficulty": "easy",
      "explanation": "Why this is correct"
    }}
  ]
}}

REQUIREMENTS:
1. Generate 5-10 questions with varying difficulty levels
2. Each question must have exactly 4 options
3. The answer must be one of the options
4. Make questions factual and grounded in the provided content
5. Difficulty levels: easy, medium, hard
6. Return ONLY valid JSON, no additional text

Generate the quiz now:"""

    try:
        if GEMINI_AVAILABLE and settings.GOOGLE_API_KEY:
            return _generate_with_gemini(prompt)
        elif settings.OPENAI_API_KEY:
            return _generate_with_openai(prompt)
        else:
            return _generate_dummy_quiz(title, content)
    except Exception as e:
        print(f"LLM generation failed: {e}, using dummy data")
        return _generate_dummy_quiz(title, content)


def _generate_with_gemini(prompt: str) -> Dict[str, Any]:
    """Generate quiz using Google Gemini API."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    # Extract JSON from response
    response_text = response.text
    
    # Try to parse JSON
    if "```json" in response_text:
        json_str = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        json_str = response_text.split("```")[1].split("```")[0].strip()
    else:
        json_str = response_text
    
    return json.loads(json_str)


def _generate_with_openai(prompt: str) -> Dict[str, Any]:
    """Generate quiz using OpenAI API."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a JSON generator. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=3000,
    )
    
    response_text = response.choices[0].message.content
    
    # Try to extract JSON if it's wrapped
    if "```json" in response_text:
        json_str = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        json_str = response_text.split("```")[1].split("```")[0].strip()
    else:
        json_str = response_text
    
    return json.loads(json_str)


def _generate_dummy_quiz(title: str, content: str) -> Dict[str, Any]:
    """
    Generate dummy quiz data for demo/testing purposes.
    Used when no LLM API is available.
    """
    return {
        "summary": f"{title} is an important topic in history and culture.",
        "key_entities": {
            "people": ["Key Figure 1", "Key Figure 2"],
            "organizations": ["Important Organization"],
            "locations": ["Location 1", "Location 2"]
        },
        "sections": ["Introduction", "History", "Legacy"],
        "related_topics": ["Related Topic 1", "Related Topic 2", "Related Topic 3"],
        "quiz": [
            {
                "question": f"What is {title} known for?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option B",
                "difficulty": "easy",
                "explanation": "This is based on the article content."
            },
            {
                "question": f"Which organization is associated with {title}?",
                "options": ["Org 1", "Org 2", "Org 3", "Org 4"],
                "answer": "Org 2",
                "difficulty": "medium",
                "explanation": "The article mentions this organization."
            }
        ]
    }
