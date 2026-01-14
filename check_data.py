
import sys
import os
# Add 'app' to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from database import SessionLocal
import models

def check_data():
    db = SessionLocal()
    try:
        # Check People
        people = db.query(models.StakeholderPersonalInfo).all()
        print(f"\n--- StakeholderPersonalInfo ({len(people)} records) ---")
        for p in people:
            print(f"ID: {p.person_id}, Name: {p.name}, Association: {p.association_name}")

        # Check Answers
        answers = db.query(models.FeedbackAnswer).all()
        print(f"\n--- FeedbackAnswer ({len(answers)} records) ---")
        for a in answers:
            print(f"Answer ID: {a.answer_id}, Person ID: {a.person_id}, Question ID: {a.question_id}, Text: {a.answer_text}")

        # Check Questions
        questions = db.query(models.SyllabusQuestion).all()
        print(f"\n--- SyllabusQuestion ({len(questions)} records) ---")
        for q in questions:
            print(f"ID: {q.id}, Text: {q.text}")

    except Exception as e:
        print(f"Error checking data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
