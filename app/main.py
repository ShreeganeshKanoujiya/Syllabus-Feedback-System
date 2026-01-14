from fastapi import FastAPI, Request, HTTPException, Depends, status, Form
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import re
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Mount static files for images and JS
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure Jinja2 to look in the templates folder
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # This serves your landing page as the home page
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/select-category", response_class=HTMLResponse)
async def select_category(request: Request):
    return templates.TemplateResponse("categoryselection.html", {"request": request})

@app.get("/feedback/{form_name}", response_class=HTMLResponse)
async def get_form(request: Request, form_name: str, db: Session = Depends(get_db)):
    questions = db.query(models.SyllabusQuestion).all()
    
    # Map form names to Database Tags
    tag_map = {
        "studentfeedback": "[STUDENT]",
        "parentfeedback": "[PARENT]",
        "alumnifeedback": "[ALUMNI]",
        "internalfaculty": "[TEACHER]",
        "externalfaculty": "[TEACHER]", 
        "industryrep": "[INDUSTRY]" 
    }
    
    target_tag = tag_map.get(form_name)
    
    filtered_questions = []
    if target_tag:
        for q in questions:
            # Filter Logic: Must have the relevant TAG and NOT be [DEMOGRAPHIC]
            if target_tag in q.text and "[DEMOGRAPHIC]" not in q.text:
                # Clean text: Remove tags like [STUDENT][SYLLABUS]
                clean_text = re.sub(r'^(\[[^\]]+\])+\s*', '', q.text)
                
                # Pass simple object or dict that template can access with .id and .text
                # Using a simple class to ensure dot notation works in Jinja2
                class QuestionObj:
                    def __init__(self, id, text):
                        self.id = id
                        self.text = text
                
                filtered_questions.append(QuestionObj(q.id, clean_text))
    
    return templates.TemplateResponse(f"feedbackForms/{form_name}.html", {
        "request": request, 
        "questions": filtered_questions,
        "form_name": form_name
    })

@app.post("/submit-feedback")
async def submit_feedback(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    association_name: str = Form(None),
    form_name: str = Form(...)
):
    # 1. Get or Create Session (for now simple logic: find 'Default' or create one)
    # Ideally should come from some context, but we'll use a placeholder or create new
    feedback_session = db.query(models.FeedbackSession).filter(models.FeedbackSession.session_name == "Default Session").first()
    if not feedback_session:
        feedback_session = models.FeedbackSession(session_name="Default Session")
        db.add(feedback_session)
        db.commit()
        db.refresh(feedback_session)
    
    # 2. Identify Stakeholder Type from form_name
    # Mapping form_name to stakeholder_type (simplified)
    # studentfeedback -> Student, etc.
    stakeholder_type_map = {
        "studentfeedback": "Student",
        "parentfeedback": "Parent",
        "alumnifeedback": "Alumni",
        "internalfaculty": "Faculty",
        "externalfaculty": "Faculty",
        "industryrep": "Industry"
    }
    sType = stakeholder_type_map.get(form_name, "Unknown")
    
    stakeholder = db.query(models.Stakeholder).filter(models.Stakeholder.stakeholder_type == sType).first()
    if not stakeholder:
        stakeholder = models.Stakeholder(stakeholder_type=sType)
        db.add(stakeholder)
        db.commit()
        db.refresh(stakeholder)

    # 3. Save Personal Info
    person = models.StakeholderPersonalInfo(
        session_id=feedback_session.session_id,
        stakeholder_id=stakeholder.stakeholder_id,
        name=name,
        association_name=association_name
    )
    db.add(person)
    db.commit()
    db.refresh(person)

    # 4. Save Answers
    # The form sends radio entries like q_1=5, q_2=4 where 1,2 are question IDs.
    form_data = await request.form()
    
    for key, value in form_data.items():
        if key.startswith("q_"):
            try:
                q_id = int(key.split("_")[1])
                answer = models.FeedbackAnswer(
                    person_id=person.person_id,
                    question_id=q_id,
                    answer_text=str(value)
                )
                db.add(answer)
            except ValueError:
                continue

    db.commit()
    
    return RedirectResponse(url="/submitted-feedback", status_code=303)

@app.get("/submitted-feedback", response_class=HTMLResponse)
async def submit_conf(request: Request):
    return templates.TemplateResponse("thankyou.html", {"request": request})

# Admin login
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})