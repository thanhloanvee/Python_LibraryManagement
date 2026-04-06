"""
Report Controller — /api/reports/*   (admin, librarian)

GET /api/reports/summary     — library-wide stats
GET /api/reports/popular     — most borrowed books
GET /api/reports/overdue     — currently overdue borrows
GET /api/reports/members     — active members with borrows
"""

from flask import Blueprint, request
from app.services.report_service import ReportService
from app.utils.response import success_response
from app.middleware.auth_middleware import jwt_required_with_roles

report_bp = Blueprint("reports", __name__)
_report_service = ReportService()


@report_bp.get("/summary")
@jwt_required_with_roles("admin")
def summary():
    """High-level library statistics."""
    data = _report_service.library_summary()
    return success_response(data)


@report_bp.get("/popular")
@jwt_required_with_roles("admin", "librarian")
def popular_books():
    """Most borrowed books."""
    limit = request.args.get("limit", 10, type=int)
    data = _report_service.most_borrowed_books(limit=limit)
    return success_response(data)


@report_bp.get("/overdue")
@jwt_required_with_roles("admin", "librarian")
def overdue():
    """All currently overdue borrow records."""
    data = _report_service.overdue_books()
    return success_response(data)


@report_bp.get("/members")
@jwt_required_with_roles("admin", "librarian")
def active_members():
    """Members who currently have borrowed books."""
    data = _report_service.active_members()
    return success_response(data)
