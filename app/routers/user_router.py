"""
User Router — /api/users/*   (Admin-only)

GET    /api/users              — paginated list of all users
GET    /api/users/{id}         — single user
PATCH  /api/users/{id}/status  — activate / deactivate
DELETE /api/users/{id}         — delete user
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.user_service import UserService
from app.schemas.user_schema import UserStatusUpdateRequest
from app.dependencies.auth import admin_only
from app.utils.pagination import pagination_meta

router = APIRouter(tags=["Users"])


@router.get("/", summary="List all users (admin)")
def list_users(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    _=Depends(admin_only),
):
    result = UserService(db).get_all_users(page=page, per_page=per_page)
    items = [u.to_dict() for u in result["items"]]
    return {"success": True, "data": items, "meta": pagination_meta(result)}


@router.get("/{user_id}", summary="Get user by ID (admin)")
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    try:
        return {"success": True, "data": UserService(db).get_user_by_id(user_id).to_dict()}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{user_id}/status", summary="Activate or deactivate a user (admin)")
def update_status(
    user_id: int,
    body: UserStatusUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(admin_only),
):
    try:
        user = UserService(db).set_active_status(user_id, body.is_active)
        verb = "activated" if user.is_active else "deactivated"
        return {"success": True, "message": f"User {verb}.", "data": user.to_dict()}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{user_id}", summary="Delete a user (admin)")
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    try:
        UserService(db).delete_user(user_id)
        return {"success": True, "message": "User deleted."}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
