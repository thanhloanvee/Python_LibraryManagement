"""
Book Controller — /api/books/*

GET    /api/books              — search/list books (any authenticated user)
GET    /api/books/<id>         — book detail
POST   /api/books              — add book      (admin, librarian)
PUT    /api/books/<id>         — update book   (admin, librarian)
DELETE /api/books/<id>         — delete book   (admin)
"""

from flask import Blueprint, request
from app.services.book_service import BookService
from app.schemas.book_schema import BookCreateSchema, BookUpdateSchema, BookOutputSchema
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import pagination_meta
from app.middleware.auth_middleware import jwt_required_with_roles

book_bp = Blueprint("books", __name__)

_create_schema = BookCreateSchema()
_update_schema = BookUpdateSchema()
_out_schema = BookOutputSchema()
_book_service = BookService()


@book_bp.get("/")
@jwt_required_with_roles()
def list_books():
    """
    Search books by query string and/or category.
    Query params: q (search term), category, page, per_page
    """
    q = request.args.get("q", "")
    category = request.args.get("category")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    pagination = _book_service.search_books(query=q, category=category, page=page, per_page=per_page)
    items = [_out_schema.dump(b) for b in pagination.items]
    return paginated_response(items, pagination_meta(pagination))


@book_bp.get("/<int:book_id>")
@jwt_required_with_roles()
def get_book(book_id: int):
    try:
        book = _book_service.get_book(book_id)
        return success_response(_out_schema.dump(book))
    except ValueError as exc:
        return error_response(str(exc), 404)


@book_bp.post("/")
@jwt_required_with_roles("admin", "librarian")
def add_book():
    json_data = request.get_json(silent=True) or {}
    errors = _create_schema.validate(json_data)
    if errors:
        return error_response("Validation failed.", 422, errors)

    data = _create_schema.load(json_data)
    try:
        book = _book_service.add_book(**data)
        return success_response(_out_schema.dump(book), "Book added.", 201)
    except ValueError as exc:
        return error_response(str(exc), 409)


@book_bp.put("/<int:book_id>")
@jwt_required_with_roles("admin", "librarian")
def update_book(book_id: int):
    json_data = request.get_json(silent=True) or {}
    errors = _update_schema.validate(json_data)
    if errors:
        return error_response("Validation failed.", 422, errors)

    data = _update_schema.load(json_data)
    try:
        book = _book_service.update_book(book_id, **data)
        return success_response(_out_schema.dump(book), "Book updated.")
    except ValueError as exc:
        return error_response(str(exc), 400)


@book_bp.delete("/<int:book_id>")
@jwt_required_with_roles("admin")
def delete_book(book_id: int):
    try:
        _book_service.delete_book(book_id)
        return success_response(message="Book deleted.")
    except ValueError as exc:
        return error_response(str(exc), 400)
