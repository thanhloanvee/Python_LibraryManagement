"""
Pagination helpers — replaces Flask-SQLAlchemy's db.paginate().
Works with plain SQLAlchemy sessions.
"""

from sqlalchemy import select, func
from sqlalchemy.orm import Session


def paginate_query(db: Session, stmt, page: int = 1, per_page: int = 20) -> dict:
    """
    Execute a SELECT statement with LIMIT/OFFSET and return a
    pagination dict compatible with the existing response format.
    """
    # Count total rows
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    # Fetch the page
    offset = (page - 1) * per_page
    items = db.execute(stmt.offset(offset).limit(per_page)).scalars().all()

    total_pages = max(1, -(-total // per_page))  # ceiling division

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def pagination_meta(page_result: dict) -> dict:
    """Extract the metadata dict (without items) for API responses."""
    return {
        "page": page_result["page"],
        "per_page": page_result["per_page"],
        "total_items": page_result["total"],
        "total_pages": page_result["total_pages"],
        "has_next": page_result["has_next"],
        "has_prev": page_result["has_prev"],
    }
