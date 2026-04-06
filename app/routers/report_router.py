"""
Report Router — /api/reports/*   (admin / librarian)

GET /api/reports/summary    — library-wide stats       (admin)
GET /api/reports/popular    — most borrowed books      (admin/librarian)
GET /api/reports/overdue    — currently overdue borrows(admin/librarian)
GET /api/reports/members    — active members           (admin/librarian)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.report_service import ReportService
from app.dependencies.auth import admin_only, admin_or_librarian

router = APIRouter(tags=["Reports"])


@router.get("/summary", summary="Library-wide statistics (admin)")
def summary(db: Session = Depends(get_db), _=Depends(admin_only)):
    """
    Returns:
    - **total_books** — number of distinct titles
    - **total_borrow_records** — all-time borrow count
    - **overdue_borrows** — currently overdue
    - **total_users** — registered users
    """
    return {"success": True, "data": ReportService(db).library_summary()}


@router.get("/popular", summary="Most borrowed books (admin/librarian)")
def popular_books(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    _=Depends(admin_or_librarian),
):
    return {"success": True, "data": ReportService(db).most_borrowed_books(limit=limit)}


@router.get("/overdue", summary="Currently overdue borrows (admin/librarian)")
def overdue(db: Session = Depends(get_db), _=Depends(admin_or_librarian)):
    return {"success": True, "data": ReportService(db).overdue_books()}


@router.get("/members", summary="Members with active borrows (admin/librarian)")
def active_members(db: Session = Depends(get_db), _=Depends(admin_or_librarian)):
    return {"success": True, "data": ReportService(db).active_members()}
