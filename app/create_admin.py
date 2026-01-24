from database import SessionLocal
from passlib.context import CryptContext
import models

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

db = SessionLocal()

password_hash = "Admin123"   # can be ANY length now

admin = models.AdminUser(
    username="admin",
    password=pwd_context.hash(password_hash)
)

db.add(admin)
db.commit()
db.close()

print("Admin created successfully")
