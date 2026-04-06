"""Unit tests for report endpoints."""

import pytest
from tests.conftest import get_token


class TestReports:

    def _setup(self, client):
        """Create an admin, add a book, borrow it, return it."""
        from tests.conftest import get_token
        admin_token = get_token(client, "admin@test.com")
        client.post(
            "/api/books/",
            json={"title": "Popular Book", "author": "Famous Author", "total_quantity": 5},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        return admin_token

    def test_summary_admin_only(self, client, admin_user):
        token = get_token(client, "admin@test.com")
        resp = client.get("/api/reports/summary", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "total_books" in data
        assert "total_users" in data

    def test_summary_member_forbidden(self, client, member_user):
        token = get_token(client, "member@test.com")
        resp = client.get("/api/reports/summary", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_popular_books_returns_list(self, client, admin_user):
        token = self._setup(client)
        resp = client.get("/api/reports/popular", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)

    def test_overdue_list(self, client, admin_user):
        token = get_token(client, "admin@test.com")
        resp = client.get("/api/reports/overdue", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)
