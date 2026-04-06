"""
pytest fixtures for FastAPI tests.
Uses an in-memory SQLite database; each test function gets a clean DB.
"""

import pytest
import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app import create_app
from app.database import Base, get_db
from app.models.user import User, RoleEnum

# ── In-memory test engine ─────────────────────────────────────────

# Use a named file-based SQLite DB so all connections share the same data.
# It is deleted and recreated per test function.
TEST_DATABASE_URL = "sqlite:///./test_library.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Dependency override — yields a test session."""
    db: Session = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── App & client fixtures ──────────────────────────────────────────

@pytest.fixture(scope="session")
def fastapi_app():
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture(scope="function")
def client(fastapi_app):
    """Fresh tables + TestClient per test function."""
    Base.metadata.create_all(bind=test_engine)
    with TestClient(fastapi_app) as c:
        yield c
    Base.metadata.drop_all(bind=test_engine)


# ── Pre-built users ──────────────────────────────────────────────

def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def _make_user(role: RoleEnum, username: str, email: str, password: str = "Password123") -> User:
    db: Session = TestingSessionLocal()
    user = User(
        username=username,
        email=email,
        password_hash=_hash(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture()
def admin_user(client):
    return _make_user(RoleEnum.ADMIN, "adminuser", "admin@test.com")


@pytest.fixture()
def librarian_user(client):
    return _make_user(RoleEnum.LIBRARIAN, "librarian1", "librarian@test.com")


@pytest.fixture()
def member_user(client):
    return _make_user(RoleEnum.MEMBER, "member1", "member@test.com")


# ── Helper ────────────────────────────────────────────────────────

def get_token(client: TestClient, email: str, password: str = "Password123") -> str:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["data"]["access_token"]
