"""
FastAPI Auth Dependencies — JWT decode + role-based access control.

Usage in routers:
    @router.get("/", dependencies=[Depends(RoleChecker("admin"))])
    or
    @router.get("/")
    def view(current_user: User = Depends(RoleChecker("admin", "librarian"))):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import jwt as pyjwt

from app.config import get_settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=True)
settings = get_settings()


def decode_token(token: str) -> dict:
    """Decode and verify a JWT; raise 401 on failure."""
    try:
        payload = pyjwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except pyjwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the JWT bearer token → User model.
    Raises 401 if token is invalid, 403 if account is deactivated.
    """
    payload = decode_token(credentials.credentials)

    # Reject refresh tokens on protected endpoints
    if payload.get("type") == "refresh":
        raise HTTPException(status_code=401, detail="Use the access token, not the refresh token.")

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated.")
    return user


class RoleChecker:
    """
    Callable dependency that validates JWT AND role in one step.

    Usage:
        any_auth   = RoleChecker()                           # any role
        admin_only = RoleChecker("admin")                    # admin
        staff      = RoleChecker("admin", "librarian")       # admin or librarian
    """

    def __init__(self, *allowed_roles: str) -> None:
        self.allowed_roles = set(allowed_roles)

    def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:
        if self.allowed_roles and current_user.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(sorted(self.allowed_roles))}.",
            )
        return current_user


# ── Pre-built checkers used across routers ────────────────────────
any_authenticated   = RoleChecker()
admin_only          = RoleChecker("admin")
admin_or_librarian  = RoleChecker("admin", "librarian")
all_roles           = RoleChecker("admin", "librarian", "member")
