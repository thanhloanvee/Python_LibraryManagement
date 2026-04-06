"""
Auth Router — /api/auth/*

POST /api/auth/register   — create account
POST /api/auth/login      — get JWT tokens
POST /api/auth/refresh    — renew access token
POST /api/auth/logout     — client-side token discard
GET  /api/auth/me         — current user profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import jwt as pyjwt

from app.database import get_db
from app.config import get_settings
from app.services.auth_service import AuthService
from app.schemas.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
)
from app.dependencies.auth import get_current_user, security
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(tags=["Authentication"])
settings = get_settings()


@router.post("/register", status_code=201, summary="Register a new account")
def register(body: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user and return JWT tokens immediately.

    - **username**: 3–64 chars (letters, digits, `-`, `_`)
    - **email**: valid email address
    - **password**: minimum 8 characters
    - **role**: `member` (default) | `librarian` | `admin`
    """
    service = AuthService(db)
    try:
        service.register(
            username=body.username,
            email=body.email,
            password=body.password,
            role=body.role,
        )
        tokens = service.login(body.email, body.password)
        return {"success": True, "message": "Registration successful.", "data": tokens}
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/login", summary="Login and get JWT tokens")
def login(body: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password and receive access/refresh tokens.
    """
    service = AuthService(db)
    try:
        tokens = service.login(email=body.email, password=body.password)
        return {"success": True, "message": "Login successful.", "data": tokens}
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/refresh", summary="Refresh access token")
def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Pass the **refresh token** in the `Authorization: Bearer` header
    to get a new access token.
    """
    try:
        payload = pyjwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except pyjwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {exc}")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token.")

    service = AuthService(db)
    try:
        result = service.refresh_access_token(int(payload["sub"]))
        return {"success": True, "message": "Token refreshed.", "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/logout", summary="Logout (client-side token discard)")
def logout(current_user=Depends(get_current_user)):
    """
    Stateless logout — the client must discard its tokens.
    A production system would add the JTI to a blocklist here.
    """
    return {"success": True, "message": "Logged out successfully."}


@router.get("/me", response_model=None, summary="Get current user profile")
def me(current_user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return {"success": True, "data": current_user.to_dict()}
