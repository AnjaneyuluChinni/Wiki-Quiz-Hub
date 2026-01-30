"""
Sample data generation for testing and submission.
Run this script to populate the database with sample quizzes.
"""
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, init_db
import crud


SAMPLE_QUIZZES = [
    {
        "url": "https://en.wikipedia.org/wiki/Alan_Turing",
        "title": "Alan Turing",
        "summary": "Alan Mathison Turing was an English mathematician, computer scientist, logician, cryptanalyst, philosopher, and theoretical biologist who made influential contributions to multiple scientific and mathematical fields.",
        "key_entities": {
            "people": ["Alan Turing", "Alonzo Church", "John von Neumann", "Christopher Strachey"],
            "organizations": ["University of Cambridge", "Bletchley Park", "University of Manchester", "Princeton Institute"],
            "locations": ["United Kingdom", "Paddington", "Cambridge", "Manchester"]
        },
        "sections": ["Early life and education", "World War II", "Post-war work", "Death and legacy"],
        "related_topics": ["Cryptography", "Enigma machine", "Computability theory", "Artificial intelligence", "Turing test"],
        "questions": [
            {
                "question": "At which university did Alan Turing study?",
                "options": ["Harvard University", "University of Cambridge", "Oxford University", "Princeton University"],
                "answer": "University of Cambridge",
                "difficulty": "easy",
                "explanation": "Turing studied mathematics at King's College, Cambridge."
            },
            {
                "question": "What was Alan Turing's main contribution to World War II?",
                "options": ["Atomic bomb research", "Breaking the Enigma code", "Inventing radar", "Designing jet engines"],
                "answer": "Breaking the Enigma code",
                "difficulty": "medium",
                "explanation": "Turing worked at Bletchley Park on breaking the German Enigma cipher."
            },
            {
                "question": "What is the 'Turing Test' designed to measure?",
                "options": ["Mathematical ability", "Machine intelligence", "Computational speed", "Memory capacity"],
                "answer": "Machine intelligence",
                "difficulty": "medium",
                "explanation": "The Turing Test proposed by Alan Turing is a measure of machine intelligence and whether a machine can exhibit intelligent behavior indistinguishable from humans."
            },
            {
                "question": "What field did Turing contribute to after World War II?",
                "options": ["Political science", "Computer science and AI", "Biology only", "Physics"],
                "answer": "Computer science and AI",
                "difficulty": "hard",
                "explanation": "After WWII, Turing worked on the Manchester Mark 1, one of the earliest stored-program computers, and pioneered the field of artificial intelligence."
            }
        ]
    },
    {
        "url": "https://en.wikipedia.org/wiki/Marie_Curie",
        "title": "Marie Curie",
        "summary": "Marie Salomea Curie was a Polish and naturalized-French physicist and chemist who conducted pioneering research on radioactivity and was the first woman to win a Nobel Prize.",
        "key_entities": {
            "people": ["Marie Curie", "Pierre Curie", "Albert Einstein", "Dmitri Mendeleev"],
            "organizations": ["University of Paris", "Sorbonne", "Institut du Radium", "Nobel Prize Committee"],
            "locations": ["Poland", "France", "Paris"]
        },
        "sections": ["Early life", "Scientific career", "Radioactivity research", "Nobel Prize", "Legacy"],
        "related_topics": ["Radioactivity", "Nuclear physics", "Polonium", "Radium", "Women in science"],
        "questions": [
            {
                "question": "In which country was Marie Curie born?",
                "options": ["France", "Germany", "Poland", "Austria"],
                "answer": "Poland",
                "difficulty": "easy",
                "explanation": "Marie Curie was born in Warsaw, Poland in 1867."
            },
            {
                "question": "What element did Marie Curie discover?",
                "options": ["Uranium", "Polonium", "Oxygen", "Hydrogen"],
                "answer": "Polonium",
                "difficulty": "medium",
                "explanation": "Marie Curie discovered polonium and named it after her native country Poland."
            },
            {
                "question": "How many Nobel Prizes did Marie Curie win?",
                "options": ["One", "Two", "Three", "Four"],
                "answer": "Two",
                "difficulty": "medium",
                "explanation": "Marie Curie won the Nobel Prize in Physics (1903, shared with Pierre Curie) and the Nobel Prize in Chemistry (1911)."
            }
        ]
    },
    {
        "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "title": "Python (programming language)",
        "summary": "Python is an interpreted, high-level, general-purpose programming language emphasizing code readability and simplicity, widely used in web development, data science, and artificial intelligence.",
        "key_entities": {
            "people": ["Guido van Rossum", "Barry Warsaw", "Ned Batchelder"],
            "organizations": ["Python Software Foundation", "Google", "Facebook", "Netflix"],
            "locations": ["Netherlands", "United States"]
        },
        "sections": ["History", "Design philosophy", "Features", "Usage", "Community"],
        "related_topics": ["Programming languages", "Computer science", "Data science", "Web development", "Open source"],
        "questions": [
            {
                "question": "Who created Python?",
                "options": ["Guido van Rossum", "Bjarne Stroustrup", "Dennis Ritchie", "Mark Lutz"],
                "answer": "Guido van Rossum",
                "difficulty": "easy",
                "explanation": "Guido van Rossum created Python in 1989 and is often referred to as the language's 'benevolent dictator for life.'"
            },
            {
                "question": "In what year was Python first released?",
                "options": ["1989", "1991", "1995", "2000"],
                "answer": "1991",
                "difficulty": "medium",
                "explanation": "Python 0.9.0, the first released version, was published in February 1991."
            },
            {
                "question": "Which Python concept emphasizes code readability?",
                "options": ["Performance optimization", "PEP 20 - Zen of Python", "Memory management", "Threading"],
                "answer": "PEP 20 - Zen of Python",
                "difficulty": "hard",
                "explanation": "The Zen of Python (PEP 20) emphasizes readability and simplicity as core design principles."
            }
        ]
    }
]


def seed_database():
    """Seed the database with sample quizzes."""
    db = SessionLocal()
    try:
        for quiz_data in SAMPLE_QUIZZES:
            questions = quiz_data.pop("questions")
            
            # Check if already exists
            existing = crud.get_quiz_by_url(db, quiz_data["url"])
            if existing:
                print(f"Quiz already exists: {quiz_data['title']}")
                continue
            
            # Create quiz
            quiz = crud.create_quiz(
                db=db,
                **quiz_data,
                questions=questions
            )
            print(f"Created quiz: {quiz.title} (ID: {quiz.id})")
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding sample data...")
    seed_database()
    print("Done!")
