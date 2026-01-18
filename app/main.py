from fastapi import FastAPI, Depends
from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from routes import client, admin

app = FastAPI()
# Include Routers
app.include_router(client.router)
app.include_router(admin.router)

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