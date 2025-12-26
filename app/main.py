from fastapi import FastAPI, Request, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# import models
# from database import engine, SessionLocal
# from sqlalchemy.orm import Session

app = FastAPI()

# models.Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal
#     try:
#         yield db
#     finally:
#         db.close()

# db_dependency = Annotated(Session, Depends(get_db))

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