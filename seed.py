"""
seed.py — Seeds the database with a default admin user.

Usage:
    python seed.py

Safe to run multiple times — checks for existing admin before creating.
"""

import bcrypt
from app.database import SessionLocal, create_tables
from app.models.user import User, RoleEnum


ADMIN_USERNAME = "admin"
ADMIN_EMAIL    = "admin@library.com"
ADMIN_PASSWORD = "Admin1234"


def seed() -> None:
    print("Creating tables (if not exist)...")
    create_tables()

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.role == RoleEnum.ADMIN).first()
        if existing:
            print(f"Admin already exists: {existing.email}")
            return

        password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=password_hash,
            role=RoleEnum.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("=" * 50)
        print("Admin user created successfully!")
        print(f"  Email   : {ADMIN_EMAIL}")
        print(f"  Password: {ADMIN_PASSWORD}")
        print("  Role    : admin")
        print("=" * 50)
        print("\nSwagger UI: http://127.0.0.1:5000/docs")
        print("Login API : POST http://127.0.0.1:5000/api/auth/login")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
