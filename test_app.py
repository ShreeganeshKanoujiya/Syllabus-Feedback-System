
import sys
import os
# Add 'app' to sys.path at the beginning to prioritize it over root directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from fastapi.testclient import TestClient
from main import app
import models
from database import SessionLocal, engine

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_get_form():
    response = client.get("/feedback/studentfeedback")
    assert response.status_code == 200
    assert "Student Feedback Form" in response.text
    # Check if questions are rendered (assuming seeded)
    assert "1. The faculty explains concepts clearly." in response.text

def test_submit_feedback():
    # Prepare form data
    data = {
        "form_name": "studentfeedback",
        "name": "Test Student",
        "association_name": "CS Dept",
        # Assuming question IDs 1-5 exist from seed
        "q_1": "5",
        "q_2": "4",
        "q_3": "5",
        "q_4": "3",
        "q_5": "5"
    }
    
    # Submit
    response = client.post("/submit-feedback", data=data, follow_redirects=False)
    
    # Check redirect
    assert response.status_code == 303
    assert response.headers["location"] == "/submitted-feedback"
    
    # Verify DB
    db = SessionLocal()
    try:
        # Check Personal Info
        person = db.query(models.StakeholderPersonalInfo).filter_by(name="Test Student").first()
        assert person is not None
        assert person.association_name == "CS Dept"
        
        # Check Answers
        answers = db.query(models.FeedbackAnswer).filter_by(person_id=person.person_id).all()
        assert len(answers) >= 5
    finally:
        db.close()
    
    print("All tests passed!")

if __name__ == "__main__":
    test_get_form()
    test_submit_feedback()
