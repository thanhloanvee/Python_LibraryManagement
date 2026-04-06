"""
AuthService — registration, login, and JWT generation.

Uses PyJWT directly (no Flask-JWT-Extended).
"""

import logging
from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import bcrypt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User, RoleEnum
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:

    def __init__(self, db: Session) -> None:
        self._user_repo = UserRepository(db)

    # ── Register ──────────────────────────────────────────────────

    def register(self, username: str, email: str, password: str, role: str = "member") -> User:
        """
        Create a new user account.
        Raises ValueError if username/email are already taken.
        """
        if self._user_repo.username_exists(username):
            raise ValueError(f"Username '{username}' is already taken.")
        if self._user_repo.email_exists(email):
            raise ValueError(f"Email '{email}' is already registered.")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=RoleEnum(role),
        )
        self._user_repo.add(user)
        self._user_repo.commit()
        logger.info("New user registered: %s (%s)", username, role)
        return user

    # ── Login ─────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> dict:
        """Validate credentials and return JWT tokens."""
        user = self._user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password.")
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            raise ValueError("Invalid email or password.")
        if not user.is_active:
            raise ValueError("Your account has been deactivated. Contact an administrator.")
        tokens = self._create_tokens(user)
        logger.info("User logged in: %s", user.email)
        return tokens

    # ── Token helpers ─────────────────────────────────────────────

    def _create_tokens(self, user: User) -> dict:
        now = datetime.now(timezone.utc)
        access_payload = {
            "sub": str(user.id),
            "role": user.role.value,
            "username": user.username,
            "is_active": user.is_active,
            "type": "access",
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES),
            "iat": now,
        }
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRES_DAYS),
            "iat": now,
        }
        access_token = pyjwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        refresh_token = pyjwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }

    def refresh_access_token(self, user_id: int) -> dict:
        """Issue a new access token using a valid refresh token."""
        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or deactivated.")
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "role": user.role.value,
            "username": user.username,
            "is_active": user.is_active,
            "type": "access",
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES),
            "iat": now,
        }
        access_token = pyjwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return {"access_token": access_token}
