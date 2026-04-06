"""
Auth Controller — /api/auth/*

POST /api/auth/register   — create account
POST /api/auth/login      — get tokens
POST /api/auth/refresh    — get new access token
POST /api/auth/logout     — client-side token discard (stateless)
GET  /api/auth/me         — current user profile
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService
from app.schemas.user_schema import UserRegisterSchema, UserLoginSchema, UserOutputSchema
from app.utils.response import success_response, error_response
from app.middleware.auth_middleware import jwt_required_with_roles, get_current_user

auth_bp = Blueprint("auth", __name__)

_register_schema = UserRegisterSchema()
_login_schema = UserLoginSchema()
_user_out_schema = UserOutputSchema()
_auth_service = AuthService()


@auth_bp.post("/register")
def register():
    """
    Register a new user account.
    ---
    Request body: { username, email, password, role? }
    Response 201: { access_token, refresh_token, user }
    """
    json_data = request.get_json(silent=True) or {}
    errors = _register_schema.validate(json_data)
    if errors:
        return error_response("Validation failed.", 422, errors)

    data = _register_schema.load(json_data)
    try:
        user = _auth_service.register(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            role=data.get("role", "member"),
        )
        # Log the new user in immediately
        tokens = _auth_service.login(data["email"], data["password"])
        return success_response(tokens, "Registration successful.", 201)
    except ValueError as exc:
        return error_response(str(exc), 409)


@auth_bp.post("/login")
def login():
    """
    Authenticate a user and return JWT tokens.
    ---
    Request body: { email, password }
    Response 200: { access_token, refresh_token, user }
    """
    json_data = request.get_json(silent=True) or {}
    errors = _login_schema.validate(json_data)
    if errors:
        return error_response("Validation failed.", 422, errors)

    data = _login_schema.load(json_data)
    try:
        tokens = _auth_service.login(data["email"], data["password"])
        return success_response(tokens, "Login successful.")
    except ValueError as exc:
        return error_response(str(exc), 401)


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """
    Issue a new access token using a valid refresh token.
    Requires: Authorization: Bearer <refresh_token>
    """
    user_id = int(get_jwt_identity())
    try:
        result = _auth_service.refresh_access_token(user_id)
        return success_response(result, "Token refreshed.")
    except ValueError as exc:
        return error_response(str(exc), 401)


@auth_bp.post("/logout")
@jwt_required_with_roles()
def logout():
    """
    Logout endpoint.
    Since we use stateless JWT, the client is responsible for
    discarding the tokens.  A production system would add the JTI
    to a blocklist here.
    """
    return success_response(message="Logged out successfully.")


@auth_bp.get("/me")
@jwt_required_with_roles()
def me():
    """Return the currently authenticated user's profile."""
    user = get_current_user()
    if not user:
        return error_response("User not found.", 404)
    return success_response(_user_out_schema.dump(user))
