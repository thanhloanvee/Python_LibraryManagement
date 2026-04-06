"""
Authentication middleware / decorators.

Usage:
    @jwt_required_with_roles("admin", "librarian")
    def my_view():
        user = get_current_user()
        ...
"""

from functools import wraps
from flask import current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from app.utils.response import error_response


def jwt_required_with_roles(*allowed_roles: str):
    """
    Decorator that:
    1. Validates the JWT (401 if missing/invalid/expired).
    2. Checks the user's role against allowed_roles (403 if not allowed).
    3. Checks the user's is_active flag (403 if deactivated).

    If allowed_roles is empty, any authenticated user is permitted.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Step 1: Validate JWT
            try:
                verify_jwt_in_request()
            except Exception as exc:
                return error_response(str(exc), 401)

            claims = get_jwt()
            role = claims.get("role", "")
            is_active = claims.get("is_active", True)

            # Step 2: Check active flag
            if not is_active:
                return error_response("Your account has been deactivated.", 403)

            # Step 3: Role check
            if allowed_roles and role not in allowed_roles:
                return error_response(
                    f"Access denied. Required roles: {', '.join(allowed_roles)}.", 403
                )

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def roles_required(*allowed_roles: str):
    """Alias kept for readability at call sites."""
    return jwt_required_with_roles(*allowed_roles)


def get_current_user():
    """
    Fetch the User model instance from the database for the JWT identity.
    Must be called inside a request context where JWT has been verified.
    """
    from app.models.user import User
    from app.extensions import db
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    return user
