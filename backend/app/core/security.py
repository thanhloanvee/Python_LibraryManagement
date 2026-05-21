"""Security utilities: password hashing, JWT token creation/verification."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings

settings = get_settings()

def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt.

    bcrypt 4.x enforces the 72-byte limit strictly, so we truncate before
    hashing to keep behaviour consistent across all input lengths.
    """
    secret = plain_password.encode("utf-8")[:72]
    return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    secret = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(secret, hashed_password.encode("utf-8"))


def create_access_token(
    subject: str | int,
    extra_claims: Dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str | int) -> str:
    """Create a long-lived refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token.

    Raises:
        InvalidTokenError: if the token is invalid or expired.
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )


def verify_access_token(token: str) -> Dict[str, Any]:
    """Decode and assert token is of type 'access'.

    Raises:
        InvalidTokenError: on invalid/expired token or wrong type.
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid token type")
    return payload


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Decode and assert token is of type 'refresh'.

    Raises:
        InvalidTokenError: on invalid/expired token or wrong type.
    """
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid token type")
    return payload
