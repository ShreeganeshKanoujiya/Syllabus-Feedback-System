
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from database import SessionLocal
import models

def check_stakeholders():
    db = SessionLocal()
    try:
        print("\n=== Table: stakeholders (Types) ===")
        types = db.query(models.Stakeholder).all()
        for t in types:
            print(f"ID: {t.stakeholder_id} | Type: {t.stakeholder_type}")
            
        print("\n=== Table: stakeholder_personal_info (Actual People) ===")
        people = db.query(models.StakeholderPersonalInfo).all()
        for p in people:
            print(f"ID: {p.person_id} | Name: {p.name} | Linked to StakeholderTypeID: {p.stakeholder_id}")

    finally:
        db.close()

if __name__ == "__main__":
    check_stakeholders()
