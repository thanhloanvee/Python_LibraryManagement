"""Borrowing workflow tests."""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_user_and_login


async def _create_book(client, headers) -> int:
    resp = await client.post(
        "/api/v1/books",
        json={
            "title": "Borrowable Book",
            "author": "Test Author",
            "quantity": 5,
            "available_quantity": 5,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _get_reader_id(client, headers) -> int:
    resp = await client.get("/api/v1/auth/me", headers=headers)
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_issue_and_return_book(client: AsyncClient, db_session: AsyncSession):
    """Happy path: librarian issues and then returns a book."""
    lib_headers = await create_user_and_login(
        client, username="lib_borrow", role="librarian", db=db_session
    )
    reader_headers = await create_user_and_login(
        client, username="reader_borrow", role="reader", db=db_session
    )
    reader_id = await _get_reader_id(client, reader_headers)
    book_id = await _create_book(client, lib_headers)

    # Issue
    issue_resp = await client.post(
        "/api/v1/borrowings",
        json={"user_id": reader_id, "book_id": book_id},
        headers=lib_headers,
    )
    assert issue_resp.status_code == 201
    borrowing_id = issue_resp.json()["id"]
    assert issue_resp.json()["status"] == "borrowed"

    # Book available_quantity should decrease
    book_resp = await client.get(f"/api/v1/books/{book_id}")
    assert book_resp.json()["available_quantity"] == 4

    # Return
    return_resp = await client.post(
        f"/api/v1/borrowings/{borrowing_id}/return",
        json={"book_condition": "good", "librarian_notes": "In perfect condition"},
        headers=lib_headers,
    )
    assert return_resp.status_code == 200
    assert return_resp.json()["status"] == "returned"

    # Book available_quantity should increase back
    book_resp2 = await client.get(f"/api/v1/books/{book_id}")
    assert book_resp2.json()["available_quantity"] == 5


@pytest.mark.asyncio
async def test_cannot_borrow_unavailable_book(
    client: AsyncClient, db_session: AsyncSession
):
    lib_headers = await create_user_and_login(
        client, username="lib_unavail", role="librarian", db=db_session
    )
    reader_headers = await create_user_and_login(
        client, username="reader_unavail", role="reader", db=db_session
    )
    reader_id = await _get_reader_id(client, reader_headers)

    # Create book with 0 available
    create_resp = await client.post(
        "/api/v1/books",
        json={
            "title": "Unavailable Book",
            "author": "Author",
            "quantity": 1,
            "available_quantity": 0,
            "status": "available",
        },
        headers=lib_headers,
    )
    book_id = create_resp.json()["id"]

    issue_resp = await client.post(
        "/api/v1/borrowings",
        json={"user_id": reader_id, "book_id": book_id},
        headers=lib_headers,
    )
    assert issue_resp.status_code == 422


@pytest.mark.asyncio
async def test_reader_cannot_see_others_borrowings(
    client: AsyncClient, db_session: AsyncSession
):
    """Reader A cannot see Reader B's borrowing."""
    lib_headers = await create_user_and_login(
        client, username="lib_rbac", role="librarian", db=db_session
    )
    reader_a_headers = await create_user_and_login(
        client, username="reader_a", role="reader", db=db_session
    )
    reader_b_headers = await create_user_and_login(
        client, username="reader_b", role="reader", db=db_session
    )
    reader_a_id = await _get_reader_id(client, reader_a_headers)
    book_id = await _create_book(client, lib_headers)

    issue_resp = await client.post(
        "/api/v1/borrowings",
        json={"user_id": reader_a_id, "book_id": book_id},
        headers=lib_headers,
    )
    borrowing_id = issue_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/borrowings/{borrowing_id}", headers=reader_b_headers
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_renewal_respects_max_renewals(
    client: AsyncClient, db_session: AsyncSession
):
    """Renewal fails after MAX_RENEWALS attempts."""
    lib_headers = await create_user_and_login(
        client, username="lib_renew", role="librarian", db=db_session
    )
    reader_headers = await create_user_and_login(
        client, username="reader_renew", role="reader", db=db_session
    )
    reader_id = await _get_reader_id(client, reader_headers)
    book_id = await _create_book(client, lib_headers)

    issue_resp = await client.post(
        "/api/v1/borrowings",
        json={"user_id": reader_id, "book_id": book_id},
        headers=lib_headers,
    )
    borrowing_id = issue_resp.json()["id"]

    # Renew MAX_RENEWALS=2 times (should succeed)
    for i in range(2):
        renew_resp = await client.post(
            f"/api/v1/borrowings/{borrowing_id}/renew",
            json={"extend_days": 7},
            headers=reader_headers,
        )
        assert renew_resp.status_code == 200, f"Renewal {i+1} failed: {renew_resp.text}"

    # 3rd renewal should fail
    third_resp = await client.post(
        f"/api/v1/borrowings/{borrowing_id}/renew",
        json={"extend_days": 7},
        headers=reader_headers,
    )
    assert third_resp.status_code == 422
