"""Unit tests for borrow/return workflow and fine calculation."""

import pytest
from datetime import datetime, timedelta, timezone
from tests.conftest import get_token


def _add_book(client, token, qty=3):
    resp = client.post(
        "/api/books/",
        json={"title": "Test Book", "author": "Author A", "total_quantity": qty},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["data"]["id"]


class TestBorrowBook:

    def test_member_can_borrow(self, client, admin_user, member_user):
        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        book_id = _add_book(client, admin_token)

        resp = client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["status"] == "borrowed"
        assert data["due_date"] is not None

    def test_available_quantity_decrements(self, client, admin_user, member_user):
        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        book_id = _add_book(client, admin_token, qty=2)

        client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        resp = client.get(
            f"/api/books/{book_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.json()["data"]["available_quantity"] == 1

    def test_cannot_borrow_unavailable_book(self, client, admin_user, member_user):
        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        book_id = _add_book(client, admin_token, qty=1)

        client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        # Second borrow of same (now out-of-stock) book
        resp = client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resp.status_code == 400

    def test_borrow_limit_enforced(self, client, admin_user, member_user):
        from app.config import get_settings
        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        limit = get_settings().MAX_BORROW_LIMIT

        # Add limit+1 books and borrow all up to limit
        for _ in range(limit):
            book_id = _add_book(client, admin_token)
            client.post(
                "/api/borrows/",
                json={"book_id": book_id},
                headers={"Authorization": f"Bearer {member_token}"},
            )

        # The next borrow should fail
        extra_book = _add_book(client, admin_token)
        resp = client.post(
            "/api/borrows/",
            json={"book_id": extra_book},
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resp.status_code == 400
        assert "limit" in resp.json()["detail"].lower()


class TestReturnBook:

    def test_on_time_return_no_fine(self, client, admin_user, member_user):
        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        book_id = _add_book(client, admin_token)

        borrow_id = client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        ).json()["data"]["id"]

        resp = client.patch(
            f"/api/borrows/{borrow_id}/return",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["status"] == "returned"
        assert data["fine"] is None or data["fine"]["amount"] == 0.0

    def test_overdue_return_creates_fine(self, client, admin_user, member_user):
        """Simulate an overdue return by backdating the due_date."""
        from app.models.borrow import BorrowRecord
        from tests.conftest import TestingSessionLocal

        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        book_id = _add_book(client, admin_token)

        borrow_id = client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        ).json()["data"]["id"]

        # Backdate due_date by 5 days to simulate overdue
        db = TestingSessionLocal()
        record = db.get(BorrowRecord, borrow_id)
        record.due_date = datetime.now(timezone.utc) - timedelta(days=5)
        db.commit()
        db.close()

        resp = client.patch(
            f"/api/borrows/{borrow_id}/return",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resp.status_code == 200
        fine = resp.json()["data"]["fine"]
        assert fine is not None
        assert fine["overdue_days"] >= 5
        assert fine["amount"] >= 5.0

    def test_available_quantity_increments_on_return(self, client, admin_user, member_user):
        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        book_id = _add_book(client, admin_token, qty=1)

        borrow_id = client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        ).json()["data"]["id"]

        client.patch(
            f"/api/borrows/{borrow_id}/return",
            headers={"Authorization": f"Bearer {member_token}"},
        )

        book_resp = client.get(
            f"/api/books/{book_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert book_resp.json()["data"]["available_quantity"] == 1

    def test_double_return_rejected(self, client, admin_user, member_user):
        admin_token  = get_token(client, "admin@test.com")
        member_token = get_token(client, "member@test.com")
        book_id = _add_book(client, admin_token)

        borrow_id = client.post(
            "/api/borrows/",
            json={"book_id": book_id},
            headers={"Authorization": f"Bearer {member_token}"},
        ).json()["data"]["id"]

        client.patch(
            f"/api/borrows/{borrow_id}/return",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        # Second return must be rejected
        resp = client.patch(
            f"/api/borrows/{borrow_id}/return",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert resp.status_code == 400
