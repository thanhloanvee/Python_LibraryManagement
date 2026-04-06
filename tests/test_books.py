"""Unit tests for book management endpoints."""

import pytest
from tests.conftest import get_token


def _add_book(client, token, **kwargs):
    payload = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "total_quantity": 3,
        **kwargs,
    }
    return client.post(
        "/api/books/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )


class TestAddBook:

    def test_admin_can_add_book(self, client, admin_user):
        token = get_token(client, "admin@test.com")
        resp = _add_book(client, token)
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["available_quantity"] == 3
        assert data["total_quantity"] == 3

    def test_librarian_can_add_book(self, client, librarian_user):
        token = get_token(client, "librarian@test.com")
        resp = _add_book(client, token, title="Refactoring")
        assert resp.status_code == 201

    def test_member_cannot_add_book(self, client, member_user):
        token = get_token(client, "member@test.com")
        resp = _add_book(client, token)
        assert resp.status_code == 403

    def test_duplicate_isbn_rejected(self, client, admin_user):
        token = get_token(client, "admin@test.com")
        _add_book(client, token, isbn="978-0132350884")
        resp = _add_book(client, token, title="Other Book", isbn="978-0132350884")
        assert resp.status_code == 409


class TestSearchBooks:

    def test_search_by_title(self, client, admin_user):
        token = get_token(client, "admin@test.com")
        _add_book(client, token, title="Python Tricks")
        resp = client.get(
            "/api/books/?q=python",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        items = resp.json()["data"]
        assert any("Python" in b["title"] for b in items)

    def test_unauth_cannot_list(self, client):
        resp = client.get("/api/books/")
        assert resp.status_code == 401


class TestUpdateBook:

    def test_update_title(self, client, admin_user):
        token = get_token(client, "admin@test.com")
        created = _add_book(client, token).json()["data"]
        resp = client.put(
            f"/api/books/{created['id']}",
            json={"title": "Updated Title"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "Updated Title"


class TestDeleteBook:

    def test_admin_can_delete(self, client, admin_user):
        token = get_token(client, "admin@test.com")
        book_id = _add_book(client, token).json()["data"]["id"]
        resp = client.delete(
            f"/api/books/{book_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    def test_cannot_delete_borrowed_book(self, client, admin_user, member_user):
        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        book_id = _add_book(client, admin_token).json()["data"]["id"]
        # Borrow the book
        client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        # Attempt delete — should fail
        resp = client.delete(
            f"/api/books/{book_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400
