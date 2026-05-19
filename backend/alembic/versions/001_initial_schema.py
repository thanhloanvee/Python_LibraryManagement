"""
Initial database schema.

Revision ID: 001
Revises:
Create Date: 2026-05-17
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column(
            "role",
            sa.Enum("reader", "librarian", "admin", name="userrole"),
            nullable=False,
            server_default="reader",
        ),
        sa.Column(
            "status",
            sa.Enum("0", "10", name="userstatus"),
            nullable=False,
            server_default="10",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # categories
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    # books
    op.create_table(
        "books",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("isbn", sa.String(20), unique=True, nullable=True),
        sa.Column("publisher", sa.String(255), nullable=True),
        sa.Column("publication_year", sa.SmallInteger, nullable=True),
        sa.Column(
            "language",
            sa.Enum("vi", "en", name="booklanguage"),
            nullable=False,
            server_default="vi",
        ),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("cover_image", sa.String(255), nullable=True),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("available_quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "status",
            sa.Enum("available", "damaged", "lost", name="bookstatus"),
            nullable=False,
            server_default="available",
        ),
        sa.Column(
            "category_id",
            sa.Integer,
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_author", "books", ["author"])
    op.create_index("ix_books_isbn", "books", ["isbn"], unique=True)

    # borrowings
    op.create_table(
        "borrowings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "book_id",
            sa.Integer,
            sa.ForeignKey("books.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("borrow_date", sa.Date, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("return_date", sa.Date, nullable=True),
        sa.Column(
            "status",
            sa.Enum("borrowed", "returned", "overdue", name="borrowingstatus"),
            nullable=False,
            server_default="borrowed",
        ),
        sa.Column(
            "book_condition",
            sa.Enum("good", "fair", "poor", "damaged", name="bookcondition"),
            nullable=True,
        ),
        sa.Column("renewed_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("fine_amount", sa.Float, nullable=False, server_default="0"),
        sa.Column("fine_paid", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("librarian_notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_borrowings_user_id", "borrowings", ["user_id"])
    op.create_index("ix_borrowings_book_id", "borrowings", ["book_id"])
    op.create_index("ix_borrowings_status", "borrowings", ["status"])

    # reviews
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "book_id",
            sa.Integer,
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rating", sa.SmallInteger, nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum("0", "1", name="reviewstatus"),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "book_id", name="uq_review_user_book"),
    )
    op.create_index("ix_reviews_book_id", "reviews", ["book_id"])
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("borrowings")
    op.drop_table("books")
    op.drop_table("categories")
    op.drop_table("users")
