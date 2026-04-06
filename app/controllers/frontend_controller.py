"""
Frontend Controller — serves Jinja2 HTML pages at /

All HTML pages load the REST API via fetch() in main.js;
the server just delivers the shell templates.
"""

from flask import Blueprint, render_template

frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.get("/")
def index():
    return render_template("dashboard.html")


@frontend_bp.get("/login")
def login_page():
    return render_template("login.html")


@frontend_bp.get("/books")
def books_page():
    return render_template("books.html")


@frontend_bp.get("/borrows")
def borrows_page():
    return render_template("borrows.html")
