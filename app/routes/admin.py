from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
import models
from database import SessionLocal
from jose import JWTError
from auth import verify_password, create_access_token, decode_access_token
import re, csv, io

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
    stream: str | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(admin_required)
):
    # -----------------------------
    # SIDEBAR STAKEHOLDERS
    # -----------------------------
    stakeholders = db.query(models.Stakeholder).order_by(
        models.Stakeholder.stakeholder_type
    ).all()

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

    if stakeholder_id:
        total_query = total_query.filter(
            models.StakeholderPersonalInfo.stakeholder_id == stakeholder_id
        )

    total_feedback = total_query.scalar() or 0

    # =========================================================
    # CASE 1: ALL STAKEHOLDERS (CUMULATIVE BAR CHART)
    # =========================================================

    if stakeholder_id is None:
        raw_results = (
            db.query(
                models.Stakeholder.stakeholder_type.label("stakeholder"),
                func.avg(
                    cast(models.FeedbackAnswer.answer_text, Integer)
                ).label("average_score")
            )
            .select_from(models.Stakeholder)
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
                "label": r.stakeholder,  # ← FIX HERE
                "average_score": round(float(r.average_score), 2)
            }
            for r in raw_results
        ]

        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request,
                "mode": "ALL",
                "results": results,
                "total_feedback": total_feedback,
                "stakeholders": stakeholders,
                "selected_stakeholder": None
            }
        )

    # =========================================================
    # CASE 2: SINGLE STAKEHOLDER
    # =========================================================

    stakeholder = db.query(models.Stakeholder).filter(
        models.Stakeholder.stakeholder_id == stakeholder_id
    ).first()

    # -----------------------------
    # SYLLABUS QUESTIONS (ORDERED)
    # -----------------------------
    syllabus_questions = (
        db.query(models.SyllabusQuestion)
        .filter(
            models.SyllabusQuestion.category == "SYLLABUS",
            models.SyllabusQuestion.stakeholder_type == stakeholder.stakeholder_type
        )
        .order_by(models.SyllabusQuestion.id)
        .all()
    )

    qid_to_qnum = {
        q.id: f"q{i+1}"
        for i, q in enumerate(syllabus_questions)
    }

    question_numbers = list(qid_to_qnum.values())

    # -----------------------------
    # BAR CHART DATA
    # -----------------------------
    raw_results = (
        db.query(
            models.FeedbackAnswer.question_id,
            func.count(models.FeedbackAnswer.answer_id).label("responses"),
            func.avg(cast(models.FeedbackAnswer.answer_text, Integer)).label("average_score")
        )
        .join(models.StakeholderPersonalInfo)
        .join(models.SyllabusQuestion)
        .filter(
            models.StakeholderPersonalInfo.stakeholder_id == stakeholder_id,
            models.SyllabusQuestion.category == "SYLLABUS"
        )
        .group_by(models.FeedbackAnswer.question_id)
        .order_by(models.FeedbackAnswer.question_id)
        .all()
    )

    results = [
        {
            "question": qid_to_qnum.get(r.question_id),
            "responses": int(r.responses),
            "average_score": round(float(r.average_score), 2)
        }
        for r in raw_results
        if r.question_id in qid_to_qnum
    ]

    # -----------------------------
    # DEMOGRAPHIC QUESTIONS
    # -----------------------------
    demographic_questions = (
        db.query(models.SyllabusQuestion)
        .filter(
            models.SyllabusQuestion.category == "DEMOGRAPHIC",
            models.SyllabusQuestion.stakeholder_type == stakeholder.stakeholder_type
        )
        .order_by(models.SyllabusQuestion.id)
        .all()
    )

    demographic_headers = []

    demo_qid_to_key = {}

    for q in demographic_questions:
        # Remove tags like [STUDENT][DEMOGRAPHIC]
        clean_label = re.sub(r"\[.*?\]", "", q.text).strip()

        # Normalize key (safe dict key)
        key = (
            clean_label
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
        )

        demographic_headers.append({
            "label": clean_label,
            "key": key,
            "question_id": q.id
        })

        demo_qid_to_key[q.id] = key

    # -----------------------------
    # STREAM OPTIONS (COURSE)
    # -----------------------------
    stream_options = (
        db.query(models.FeedbackAnswer.answer_text)
        .join(models.SyllabusQuestion)
        .join(models.StakeholderPersonalInfo)
        .filter(
            models.SyllabusQuestion.category == "DEMOGRAPHIC",
            models.SyllabusQuestion.text.ilike("%course%"),
            models.StakeholderPersonalInfo.stakeholder_id == stakeholder_id
        )
        .distinct()
        .all()
    )
    stream_options = [s[0] for s in stream_options]

    # -----------------------------
    # FETCH ALL ANSWERS
    # -----------------------------
    answers_query = (
        db.query(
            models.StakeholderPersonalInfo.person_id,
            models.StakeholderPersonalInfo.name,
            models.FeedbackAnswer.question_id,
            models.FeedbackAnswer.answer_text
        )
        .join(models.FeedbackAnswer)
        .filter(models.StakeholderPersonalInfo.stakeholder_id == stakeholder_id)
        .order_by(
            models.StakeholderPersonalInfo.person_id,
            models.FeedbackAnswer.question_id
        )
    )

    answers = answers_query.all()

    # -----------------------------
    # PIVOT TABLE
    # -----------------------------
    row_map = {}

    for r in answers:
        row = row_map.setdefault(r.person_id, {
            "person_id": r.person_id,
            "name": r.name
        })

        # DEMOGRAPHIC
        if r.question_id in demo_qid_to_key:
            row[demo_qid_to_key[r.question_id]] = r.answer_text

        # SYLLABUS
        if r.question_id in qid_to_qnum:
            row[qid_to_qnum[r.question_id]] = r.answer_text

    responses_table = list(row_map.values())

    # -----------------------------
    # APPLY STREAM FILTER (FIXED)
    # -----------------------------
    if stream:
        def matches_stream(row):
            for k, v in row.items():
                if "course" in k or "program" in k or "stream" in k:
                    return v == stream
            return False

        responses_table = [
            r for r in responses_table
            if matches_stream(r)
        ]

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "mode": "SINGLE",
            "results": results,
            "questions": syllabus_questions,
            "question_numbers": question_numbers,
            "responses_table": responses_table,
            "stream_options": stream_options,
            "selected_stream": stream,
            "total_feedback": total_feedback,
            "stakeholders": stakeholders,
            "selected_stakeholder": stakeholder_id,
            "demographic_headers": demographic_headers,
        }
    )


@router.post("/update-responses")
async def update_demographic_responses(
    updates: list[dict],
    db: Session = Depends(get_db)
):
    for item in updates:
        person_id = item["person_id"]
        question_id = item["question_id"]
        value = item["value"]

        # Ensure question is DEMOGRAPHIC
        question = db.query(models.SyllabusQuestion).filter(
            models.SyllabusQuestion.id == question_id,
            models.SyllabusQuestion.category == "DEMOGRAPHIC"
        ).first()

        if not question:
            continue  # ❌ silently ignore non-demographic edits

        answer = db.query(models.FeedbackAnswer).filter(
            models.FeedbackAnswer.person_id == person_id,
            models.FeedbackAnswer.question_id == question_id
        ).first()

        if answer:
            answer.answer_text = value

    db.commit()
    return {"status": "ok"}



@router.get("/export/stakeholder")
def export_stakeholder_csv(
    stakeholder_id: int,
    stream: str | None = None,
    db: Session = Depends(get_db)
):
    stakeholder = db.query(models.Stakeholder).filter(
        models.Stakeholder.stakeholder_id == stakeholder_id
    ).first()

    if not stakeholder:
        return {"error": "Invalid stakeholder"}

    # -----------------------------
    # DEMOGRAPHIC QUESTIONS
    # -----------------------------
    demographic_questions = (
        db.query(models.SyllabusQuestion)
        .filter(
            models.SyllabusQuestion.category == "DEMOGRAPHIC",
            models.SyllabusQuestion.stakeholder_type == stakeholder.stakeholder_type
        )
        .order_by(models.SyllabusQuestion.id)
        .all()
    )

    demo_qid_to_key = {}
    demo_headers = []

    for q in demographic_questions:
        label = re.sub(r"\[.*?\]", "", q.text).strip()
        key = label.lower().replace(" ", "_").replace("/", "_")
        demo_qid_to_key[q.id] = key
        demo_headers.append(label)

    # -----------------------------
    # SYLLABUS QUESTIONS
    # -----------------------------
    syllabus_questions = (
        db.query(models.SyllabusQuestion)
        .filter(
            models.SyllabusQuestion.category == "SYLLABUS",
            models.SyllabusQuestion.stakeholder_type == stakeholder.stakeholder_type
        )
        .order_by(models.SyllabusQuestion.id)
        .all()
    )

    qid_to_qnum = {q.id: f"q{i+1}" for i, q in enumerate(syllabus_questions)}
    syllabus_headers = list(qid_to_qnum.values())

    # -----------------------------
    # FETCH ANSWERS
    # -----------------------------
    answers = (
        db.query(
            models.StakeholderPersonalInfo.person_id,
            models.StakeholderPersonalInfo.name,
            models.FeedbackAnswer.question_id,
            models.FeedbackAnswer.answer_text
        )
        .join(models.FeedbackAnswer)
        .filter(models.StakeholderPersonalInfo.stakeholder_id == stakeholder_id)
        .order_by(
            models.StakeholderPersonalInfo.person_id,
            models.FeedbackAnswer.question_id
        )
        .all()
    )

    rows = {}

    for a in answers:
        row = rows.setdefault(a.person_id, {
            "person_id": a.person_id,
            "name": a.name
        })

        if a.question_id in demo_qid_to_key:
            row[demo_qid_to_key[a.question_id]] = a.answer_text

        if a.question_id in qid_to_qnum:
            row[qid_to_qnum[a.question_id]] = a.answer_text

    data = list(rows.values())

    # -----------------------------
    # STREAM FILTER
    # -----------------------------
    if stream:
        def match_stream(row):
            for k, v in row.items():
                if "course" in k or "program" in k or "stream" in k:
                    return v == stream
            return False

        data = [r for r in data if match_stream(r)]

    # -----------------------------
    # CSV BUILD
    # -----------------------------
    output = io.StringIO()
    writer = csv.writer(output)

    header = ["Person ID", "Name"] + demo_headers + syllabus_headers
    writer.writerow(header)

    for r in data:
        row = [
            r.get("person_id"),
            r.get("name")
        ]
        for q in demo_qid_to_key.values():
            row.append(r.get(q, ""))
        for q in syllabus_headers:
            row.append(r.get(q, ""))
        writer.writerow(row)

    output.seek(0)

    filename = f"{stakeholder.stakeholder_type}_responses.csv"

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/export/all")
def export_all_csv(db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)

    # CSV header
    writer.writerow([
        "Stakeholder",
        "Person ID",
        "Name",
        "Question",
        "Answer"
    ])

    rows = (
        db.query(
            models.Stakeholder.stakeholder_type.label("stakeholder"),
            models.StakeholderPersonalInfo.person_id,
            models.StakeholderPersonalInfo.name,
            models.SyllabusQuestion.text,
            models.FeedbackAnswer.answer_text
        )
        .select_from(models.Stakeholder)   # ✅ EXPLICIT ROOT
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
        .order_by(
            models.Stakeholder.stakeholder_type,
            models.StakeholderPersonalInfo.person_id,
            models.SyllabusQuestion.id
        )
        .all()
    )

    for r in rows:
        clean_question = re.sub(r"\[.*?\]", "", r.text).strip()
        writer.writerow([
            r.stakeholder,
            r.person_id,
            r.name,
            clean_question,
            r.answer_text
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=all_stakeholders_responses.csv"
        }
    )


