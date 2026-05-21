"""Book endpoint tests."""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_user_and_login


@pytest.mark.asyncio
async def test_list_books_public(client: AsyncClient, db_session: AsyncSession):
    """Public endpoint — no auth required."""
    resp = await client.get("/api/v1/books")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "meta" in data


@pytest.mark.asyncio
async def test_create_book_requires_librarian(client: AsyncClient, db_session: AsyncSession):
    """Reader cannot create books."""
    headers = await create_user_and_login(
        client, username="reader_book", role="reader", db=db_session
    )
    resp = await client.post(
        "/api/v1/books",
        json={"title": "Test Book", "author": "Test Author", "quantity": 1, "available_quantity": 1},
        headers=headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_and_get_book(client: AsyncClient, db_session: AsyncSession):
    """Librarian creates a book; verify it can be retrieved."""
    headers = await create_user_and_login(
        client, username="librarian_book", role="librarian", db=db_session
    )
    create_resp = await client.post(
        "/api/v1/books",
        json={
            "title": "FastAPI Handbook",
            "author": "Sebastián Ramírez",
            "isbn": "978-0-00-000001-0",
            "quantity": 3,
            "available_quantity": 3,
            "language": "en",
            "status": "available",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    book_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/books/{book_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "FastAPI Handbook"


@pytest.mark.asyncio
async def test_available_quantity_cannot_exceed_total(
    client: AsyncClient, db_session: AsyncSession
):
    """Pydantic schema enforces available_quantity <= quantity."""
    headers = await create_user_and_login(
        client, username="librarian_q", role="librarian", db=db_session
    )
    resp = await client.post(
        "/api/v1/books",
        json={
            "title": "Bad Book",
            "author": "Author",
            "quantity": 2,
            "available_quantity": 5,  # violates rule
        },
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_delete_book_with_no_active_borrowings(
    client: AsyncClient, db_session: AsyncSession
):
    headers = await create_user_and_login(
        client, username="admin_del", role="admin", db=db_session
    )
    create_resp = await client.post(
        "/api/v1/books",
        json={"title": "Deletable Book", "author": "Author", "quantity": 1, "available_quantity": 1},
        headers=headers,
    )
    book_id = create_resp.json()["id"]
    del_resp = await client.delete(f"/api/v1/books/{book_id}", headers=headers)
    assert del_resp.status_code == 200


@pytest.mark.asyncio
async def test_book_search_filter(client: AsyncClient, db_session: AsyncSession):
    """Search filter works (ilike on title + author)."""
    headers = await create_user_and_login(
        client, username="librarian_search", role="librarian", db=db_session
    )
    await client.post(
        "/api/v1/books",
        json={"title": "Python Deep Dive", "author": "Fred Baptiste", "quantity": 2, "available_quantity": 2},
        headers=headers,
    )
    resp = await client.get("/api/v1/books?search=python+deep")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] >= 1
