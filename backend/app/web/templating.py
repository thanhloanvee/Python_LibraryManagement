"""Jinja2 template engine instance + helper."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from fastapi import Request, Response
from fastapi.templating import Jinja2Templates

import datetime
import json

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def _tojson_filter(value) -> str:
    """Safe JSON serialiser for Jinja2 (handles date/datetime/Enum/Pydantic)."""
    def default(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if hasattr(obj, "model_dump"):  # Pydantic v2
            return obj.model_dump()
        if hasattr(obj, "value"):  # Enum
            return obj.value
        raise TypeError(f"Not serialisable: {type(obj)}")
    return json.dumps(value, default=default)

templates.env.filters["tojson"] = _tojson_filter
templates.env.globals["min"] = min
templates.env.globals["max"] = max
templates.env.globals["range"] = range

def set_flash(response: Response, message: str, category: str = "success") -> None:
    """Encode and store a flash message in a short-lived httponly cookie."""
    data = base64.b64encode(
        json.dumps({"msg": message, "cat": category}).encode()
    ).decode()
    response.set_cookie("flash", data, httponly=True, max_age=10, samesite="lax")


def _read_flash(request: Request) -> dict | None:
    raw = request.cookies.get("flash")
    if not raw:
        return None
    try:
        return json.loads(base64.b64decode(raw))
    except Exception:
        return None


def render(
    template_name: str,
    ctx: dict,
    request: Request,
    status_code: int = 200,
) -> templates.TemplateResponse:
    """Render a Jinja2 template.

    Automatically:
    - injects ``request`` into context (required by Jinja2)
    - reads and clears the flash cookie
    - makes ``user`` available if set on request.state
    """
    flash = _read_flash(request)
    context = {
        "flash": flash,
        "current_user": getattr(request.state, "user", None),
        "now": datetime.date.today(),
        **ctx,
    }
    # Starlette ≥ 0.38: TemplateResponse(request, name, context=..., status_code=...)
    # request is injected into context automatically by Starlette (setdefault).
    response = templates.TemplateResponse(
        request,
        template_name,
        context=context,
        status_code=status_code,
    )
    if flash:
        response.delete_cookie("flash")
    return response
