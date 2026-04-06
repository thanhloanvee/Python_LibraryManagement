"""
Frontend Router — serves Jinja2 HTML pages at /
All data is loaded client-side via fetch() calls to /api/*.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Frontend"], include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.get("/books", response_class=HTMLResponse)
def books_page(request: Request):
    return templates.TemplateResponse(request, "books.html")


@router.get("/borrows", response_class=HTMLResponse)
def borrows_page(request: Request):
    return templates.TemplateResponse(request, "borrows.html")
