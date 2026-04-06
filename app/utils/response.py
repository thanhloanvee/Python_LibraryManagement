"""
Standard API response helpers.
FastAPI returns dicts directly (no Flask jsonify needed).
These helpers keep a consistent envelope across all endpoints.
"""

from typing import Any, Optional


def success_response(data: Any = None, message: str = "Success") -> dict:
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return body


def error_response(message: str, errors: Optional[Any] = None) -> dict:
    body = {"success": False, "message": message}
    if errors is not None:
        body["errors"] = errors
    return body


def paginated_response(items: list, meta: dict, message: str = "Success") -> dict:
    return {"success": True, "message": message, "data": items, "meta": meta}
