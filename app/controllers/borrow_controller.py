"""
Borrow Controller — /api/borrows/*

POST   /api/borrows                   — borrow a book        (member)
PATCH  /api/borrows/<id>/return       — return a book        (member)
GET    /api/borrows/my                — my borrow history    (any auth)
GET    /api/borrows                   — all borrows          (admin, librarian)
GET    /api/borrows/<id>              — single record        (admin, librarian, or owner)
"""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.services.borrow_service import BorrowService
from app.schemas.borrow_schema import BorrowCreateSchema, BorrowOutputSchema
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import pagination_meta
from app.middleware.auth_middleware import jwt_required_with_roles, get_current_user

borrow_bp = Blueprint("borrows", __name__)

_create_schema = BorrowCreateSchema()
_out_schema = BorrowOutputSchema()
_borrow_service = BorrowService()


@borrow_bp.post("/")
@jwt_required_with_roles("member", "admin", "librarian")
def borrow_book():
    """
    Borrow a book.
    Request body: { book_id }
    """
    json_data = request.get_json(silent=True) or {}
    errors = _create_schema.validate(json_data)
    if errors:
        return error_response("Validation failed.", 422, errors)

    user_id = int(get_jwt_identity())
    data = _create_schema.load(json_data)
    try:
        record = _borrow_service.borrow_book(user_id=user_id, book_id=data["book_id"])
        return success_response(_out_schema.dump(record), "Book borrowed successfully.", 201)
    except ValueError as exc:
        return error_response(str(exc), 400)


@borrow_bp.patch("/<int:borrow_id>/return")
@jwt_required_with_roles("member", "admin", "librarian")
def return_book(borrow_id: int):
    """Return a borrowed book; a fine is created if overdue."""
    user_id = int(get_jwt_identity())
    try:
        record = _borrow_service.return_book(borrow_id=borrow_id, user_id=user_id)
        return success_response(_out_schema.dump(record), "Book returned successfully.")
    except ValueError as exc:
        return error_response(str(exc), 400)


@borrow_bp.get("/my")
@jwt_required_with_roles()
def my_borrows():
    """Get the current user's borrow history (paginated)."""
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = _borrow_service.get_user_borrows(user_id, page=page, per_page=per_page)
    items = [_out_schema.dump(r) for r in pagination.items]
    return paginated_response(items, pagination_meta(pagination))


@borrow_bp.get("/")
@jwt_required_with_roles("admin", "librarian")
def all_borrows():
    """List all borrow records — admin/librarian only."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = _borrow_service.get_all_borrows(page=page, per_page=per_page)
    items = [_out_schema.dump(r) for r in pagination.items]
    return paginated_response(items, pagination_meta(pagination))


@borrow_bp.get("/<int:borrow_id>")
@jwt_required_with_roles("admin", "librarian")
def get_borrow(borrow_id: int):
    from app.repositories.borrow_repository import BorrowRepository
    repo = BorrowRepository()
    record = repo.get_by_id(borrow_id)
    if not record:
        return error_response("Borrow record not found.", 404)
    return success_response(_out_schema.dump(record))
