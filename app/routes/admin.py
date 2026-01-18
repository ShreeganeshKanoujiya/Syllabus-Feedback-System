from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
import models
from database import SessionLocal

router = APIRouter(prefix="/admin") # All routes here start with /admin
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Admin login
@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
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