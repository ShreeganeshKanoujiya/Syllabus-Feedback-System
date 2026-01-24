from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
import models
from database import SessionLocal
from jose import JWTError
from auth import verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/admin") 
templates = Jinja2Templates(directory="app/templates")

# DB DEPENDENCY
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT AUTH DEPENDENCY
def admin_required(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
        request.state.admin_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# Admin login
@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

# LOGIN ACTION (JWT)
@router.post("/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(models.AdminUser).filter(
        models.AdminUser.username == username
    ).first()

    if not admin or not verify_password(password, admin.password):
        return templates.TemplateResponse(
            "admin_login.html",
            {
                "request": request,
                "error": "Invalid username or password"
            },
            status_code=401
        )

    token = create_access_token({"sub": str(admin.admin_id)})

    response = RedirectResponse(
        url="/admin/dashboard",
        status_code=status.HTTP_302_FOUND
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,     # True in production (HTTPS)
        samesite="lax"
    )

    return response

# LOGOUT
@router.get("/logout")
async def admin_logout():
    response = RedirectResponse("/admin/login")
    response.delete_cookie("access_token")
    return response

# DASHBOARD
@router.get("/dashboard", response_class=HTMLResponse)  
async def admin_dashboard(
    request: Request,
    stakeholder_id: int | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(admin_required)
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