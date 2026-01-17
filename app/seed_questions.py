
import sys
import os
# Add 'app' directory to sys.path so 'from database import ...' works inside models.py
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))


from database import SessionLocal, engine
from models import SyllabusQuestion
from sqlalchemy.orm import Session


def seed_questions():
    db = SessionLocal()
    questions = [
        "The faculty explains concepts clearly.",
        "The course material is helpful and clear.",
        "The faculty encourages questions and interaction.",
        "Assignments and assessments are clear and fair.",
        "Overall satisfaction with the course."
    ]
    
    print("Seeding questions...")
    try:
        # Check if questions exist
        existing = db.query(SyllabusQuestion).count()
        if existing > 0:
            print(f"Questions already exist ({existing}). Skipping seed.")
        else:
            for q_text in questions:
                q = SyllabusQuestion(text=q_text)
                db.add(q)
            db.commit()
            print("Questions seeded successfully.")
    except Exception as e:
        print(f"Error seeding questions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()
