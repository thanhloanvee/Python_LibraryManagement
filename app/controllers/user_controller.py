"""
User Controller — /api/users/*   (Admin-only)

GET    /api/users              — list all users (paginated)
GET    /api/users/<id>         — get single user
PATCH  /api/users/<id>/status  — activate / deactivate
DELETE /api/users/<id>         — delete user
"""

from flask import Blueprint, request
from app.services.user_service import UserService
from app.schemas.user_schema import UserOutputSchema, UserUpdateSchema
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import pagination_meta
from app.middleware.auth_middleware import jwt_required_with_roles

user_bp = Blueprint("users", __name__)

_user_out_schema = UserOutputSchema()
_update_schema = UserUpdateSchema()
_user_service = UserService()


@user_bp.get("/")
@jwt_required_with_roles("admin")
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = _user_service.get_all_users(page=page, per_page=per_page)
    items = [_user_out_schema.dump(u) for u in pagination.items]
    return paginated_response(items, pagination_meta(pagination))


@user_bp.get("/<int:user_id>")
@jwt_required_with_roles("admin")
def get_user(user_id: int):
    try:
        user = _user_service.get_user_by_id(user_id)
        return success_response(_user_out_schema.dump(user))
    except ValueError as exc:
        return error_response(str(exc), 404)


@user_bp.patch("/<int:user_id>/status")
@jwt_required_with_roles("admin")
def update_status(user_id: int):
    """Activate or deactivate a user account."""
    json_data = request.get_json(silent=True) or {}
    errors = _update_schema.validate(json_data)
    if errors:
        return error_response("Validation failed.", 422, errors)

    data = _update_schema.load(json_data)
    try:
        user = _user_service.set_active_status(user_id, data["is_active"])
        status = "activated" if user.is_active else "deactivated"
        return success_response(_user_out_schema.dump(user), f"User {status}.")
    except ValueError as exc:
        return error_response(str(exc), 404)


@user_bp.delete("/<int:user_id>")
@jwt_required_with_roles("admin")
def delete_user(user_id: int):
    try:
        _user_service.delete_user(user_id)
        return success_response(message="User deleted.")
    except ValueError as exc:
        return error_response(str(exc), 400)
