from fastapi import FastAPI, Request, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

# Create the tables in MySQL automatically based on models.py
models.Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal() # Create a new session 
    try:
        yield db
    finally:
        db.close() # Ensure session closes after the request


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
async def get_form(request: Request, form_name: str):
    return templates.TemplateResponse(f"feedbackForms/{form_name}.html", {"request": request})

@app.get("/submitted-feedback", response_class=HTMLResponse)
async def submit_form(request: Request):
    return templates.TemplateResponse("thankyou.html", {"request": request})

# Admin login
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

# @app.get("/admin/dashboard", response_class=HTMLResponse)
# async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
#     # Fetch data to display on dashboard
#     total_feedback = db.query(models.FeedbackAnswer).count()
#     stakeholders = db.query(models.Stakeholder).all()
    
#     return templates.TemplateResponse("admin_dashboard.html", {
#         "request": request, 
#         "total_feedback": total_feedback,
#         "stakeholders": stakeholders
#     })


# Example: A route that uses the database
@app.get("/stakeholders")
def get_stakeholders(db: Session = Depends(get_db)):
    # Query all stakeholders from the database table 
    return db.query(models.Stakeholder).all()