"""Role-Based Access Control (RBAC) dependencies.

Usage in routers:
    @router.post("/books", dependencies=[Depends(require_librarian)])
    @router.delete("/users/{id}", dependencies=[Depends(require_admin)])
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole


def _role_checker(*allowed_roles: UserRole):
    """Factory that returns a FastAPI dependency checking the user's role."""

    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. Required role(s): "
                    f"{', '.join(r.value for r in allowed_roles)}"
                ),
            )
        return current_user

    return _check


require_authenticated = get_current_user

# Reader and above  (reader | librarian | admin)
require_reader = _role_checker(UserRole.READER, UserRole.LIBRARIAN, UserRole.ADMIN)

# Librarian and above  (librarian | admin)
require_librarian = _role_checker(UserRole.LIBRARIAN, UserRole.ADMIN)

# Admin only
require_admin = _role_checker(UserRole.ADMIN)
