"""
Web-layer auth dependencies using httponly cookie JWT.

Cookie → JWT → User ORM instance
"""
from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_access_token
from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus
from app.repositories.user import UserRepository
from app.web.exceptions import WebAuthRequired, WebForbidden


async def get_optional_web_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Return the current user from cookie JWT, or None if not logged in."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = verify_access_token(token)
        user_id = int(payload.get("sub", 0))
        user = await UserRepository(db).get_by_id(user_id)
        if user and user.status == UserStatus.ACTIVE:
            request.state.user = user
            return user
    except Exception:
        pass
    return None


async def require_web_auth(
    user: User | None = Depends(get_optional_web_user),
) -> User:
    """Require a logged-in user; redirect to /login if not."""
    if user is None:
        raise WebAuthRequired()
    return user


def require_role(*roles: UserRole):
    """Dependency factory: require the user to have one of the given roles."""
    async def _check(user: User = Depends(require_web_auth)) -> User:
        if user.role not in roles:
            raise WebForbidden(
                f"Required role(s): {', '.join(r.value for r in roles)}"
            )
        return user
    return _check


# Pre-built guards
require_reader    = require_role(UserRole.READER, UserRole.LIBRARIAN, UserRole.ADMIN)
require_librarian = require_role(UserRole.LIBRARIAN, UserRole.ADMIN)
require_admin     = require_role(UserRole.ADMIN)
