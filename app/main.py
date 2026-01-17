from fastapi import FastAPI, Request, HTTPException, Depends, status, Form
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import re
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer, literal

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
async def get_form(
    request: Request,
    form_name: str,
    db: Session = Depends(get_db)
):
    # Map form names to stakeholder_type values
    stakeholder_map = {
        "studentfeedback": "STUDENT",
        "parentfeedback": "PARENT",
        "alumnifeedback": "ALUMNI",
        "internalfaculty": "TEACHER",
        "externalfaculty": "OUTSIDE_TEACHER",
        "industryrep": "EMPLOYER"
    }

    stakeholder = stakeholder_map.get(form_name)

    if stakeholder is None:
        raise HTTPException(status_code=404, detail="Invalid feedback form")

    # Fetch questions directly using normalized columns
    questions = (
        db.query(models.SyllabusQuestion)
        .filter(models.SyllabusQuestion.stakeholder_type == stakeholder)
        .order_by(models.SyllabusQuestion.id)
        .all()
    )

    return templates.TemplateResponse(
        f"feedbackForms/{form_name}.html",
        {
            "request": request,
            "questions": questions,
            "form_name": form_name
        }
    )

@app.post("/submit-feedback")
async def submit_feedback(
    request: Request,
    db: Session = Depends(get_db)
):
    form = await request.form()

    # 1️⃣ Get or create feedback session
    feedback_session = (
        db.query(models.FeedbackSession)
        .filter(models.FeedbackSession.session_name == "Default Session")
        .first()
    )

    if not feedback_session:
        feedback_session = models.FeedbackSession(session_name="Default Session")
        db.add(feedback_session)
        db.commit()
        db.refresh(feedback_session)

    # 2️⃣ Resolve stakeholder_type from form_name
    form_name = form.get("form_name")

    stakeholder_map = {
        "studentfeedback": "STUDENT",
        "parentfeedback": "PARENT",
        "alumnifeedback": "ALUMNI",
        "internalfaculty": "TEACHER",
        "externalfaculty": "OUTSIDE_TEACHER",
        "industryrep": "EMPLOYER"
    }

    stakeholder_type = stakeholder_map.get(form_name)
    if not stakeholder_type:
        raise HTTPException(status_code=400, detail="Invalid form")

    stakeholder = (
        db.query(models.Stakeholder)
        .filter(models.Stakeholder.stakeholder_type == stakeholder_type)
        .first()
    )

    if not stakeholder:
        stakeholder = models.Stakeholder(stakeholder_type=stakeholder_type)
        db.add(stakeholder)
        db.commit()
        db.refresh(stakeholder)

    # 3️⃣ Create person entry (no hard-coded name fields)
    person = models.StakeholderPersonalInfo(
        session_id=feedback_session.session_id,
        stakeholder_id=stakeholder.stakeholder_id,
        name="N/A",               # optional placeholder
        association_name=None     # optional placeholder
    )
    db.add(person)
    db.flush()  # IMPORTANT: get person_id without committing

    # 4️⃣ Save ALL answers dynamically
    for key, value in form.items():
        if key.startswith("q_"):
            try:
                question_id = int(key.split("_")[1])
            except ValueError:
                continue

            db.add(
                models.FeedbackAnswer(
                    person_id=person.person_id,
                    question_id=question_id,
                    answer_text=str(value)
                )
            )

    db.commit()

    return RedirectResponse(url="/submitted-feedback", status_code=303)

@app.get("/submitted-feedback", response_class=HTMLResponse)
async def submit_conf(request: Request):
    return templates.TemplateResponse("thankyou.html", {"request": request})


# Admin login
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    stakeholder_id: int | None = None,
    db: Session = Depends(get_db)
):
    # Sidebar stakeholders
    stakeholders = db.query(models.Stakeholder).all()

    # -----------------------------
    # TOTAL UNIQUE RESPONDENTS
    # -----------------------------
    total_query = (
        db.query(func.count(func.distinct(models.FeedbackAnswer.person_id)))
        .join(
            models.StakeholderPersonalInfo,
            models.FeedbackAnswer.person_id == models.StakeholderPersonalInfo.person_id
        )
    )

    if stakeholder_id is not None:
        total_query = total_query.filter(
            models.StakeholderPersonalInfo.stakeholder_id == stakeholder_id
        )

    total_feedback = total_query.scalar()

    # -----------------------------
    # CASE 1: ALL STAKEHOLDERS
    # -----------------------------
    if stakeholder_id is None:
        raw_results = (
            db.query(
                models.Stakeholder.stakeholder_type.label("stakeholder"),
                func.avg(
                    cast(models.FeedbackAnswer.answer_text, Integer)
                ).label("average_score")
            )
            .join(
                models.StakeholderPersonalInfo,
                models.Stakeholder.stakeholder_id == models.StakeholderPersonalInfo.stakeholder_id
            )
            .join(
                models.FeedbackAnswer,
                models.StakeholderPersonalInfo.person_id == models.FeedbackAnswer.person_id
            )
            .join(
                models.SyllabusQuestion,
                models.FeedbackAnswer.question_id == models.SyllabusQuestion.id
            )
            .filter(models.SyllabusQuestion.category == "SYLLABUS")
            .group_by(models.Stakeholder.stakeholder_id)
            .order_by(models.Stakeholder.stakeholder_type)
            .all()
        )

        results = [
            {
                "label": row.stakeholder,
                "average_score": round(float(row.average_score), 2)
            }
            for row in raw_results
        ]

        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request,
                "mode": "ALL",
                "total_feedback": total_feedback,
                "results": results,
                "stakeholders": stakeholders,
                "selected_stakeholder": None
            }
        )

    # -----------------------------
    # CASE 2: SINGLE STAKEHOLDER
    # -----------------------------
    raw_results = (
        db.query(
            func.concat("q", models.SyllabusQuestion.id).label("question"),
            func.count(models.FeedbackAnswer.answer_id).label("responses"),
            func.avg(
                cast(models.FeedbackAnswer.answer_text, Integer)
            ).label("average_score")
        )
        .join(
            models.SyllabusQuestion,
            models.FeedbackAnswer.question_id == models.SyllabusQuestion.id
        )
        .join(
            models.StakeholderPersonalInfo,
            models.FeedbackAnswer.person_id == models.StakeholderPersonalInfo.person_id
        )
        .filter(
            models.SyllabusQuestion.category == "SYLLABUS",
            models.StakeholderPersonalInfo.stakeholder_id == stakeholder_id
        )
        .group_by(models.SyllabusQuestion.id)
        .order_by(models.SyllabusQuestion.id)
        .all()
    )

    results = [
        {
            "question": row.question,
            "responses": int(row.responses),
            "average_score": round(float(row.average_score), 2)
        }
        for row in raw_results
    ]

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "mode": "SINGLE",
            "total_feedback": total_feedback,
            "results": results,
            "stakeholders": stakeholders,
            "selected_stakeholder": stakeholder_id
        }
    )