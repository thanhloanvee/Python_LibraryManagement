"""Unit tests for authentication endpoints."""

import pytest
from tests.conftest import get_token


class TestRegister:

    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "Secure1234",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["user"]["role"] == "member"

    def test_register_duplicate_email(self, client, member_user):
        resp = client.post("/api/auth/register", json={
            "username": "other",
            "email": "member@test.com",     # already registered
            "password": "Secure1234",
        })
        assert resp.status_code == 409

    def test_register_duplicate_username(self, client, member_user):
        resp = client.post("/api/auth/register", json={
            "username": "member1",           # taken
            "email": "unique@test.com",
            "password": "Secure1234",
        })
        assert resp.status_code == 409

    def test_register_short_password(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "short",
            "email": "short@test.com",
            "password": "abc",              # too short
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "badmail",
            "email": "not-an-email",
            "password": "Secure1234",
        })
        assert resp.status_code == 422


class TestLogin:

    def test_login_success(self, client, member_user):
        resp = client.post("/api/auth/login", json={
            "email": "member@test.com",
            "password": "Password123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()["data"]

    def test_login_wrong_password(self, client, member_user):
        resp = client.post("/api/auth/login", json={
            "email": "member@test.com",
            "password": "Wrong999",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "ghost@test.com",
            "password": "Password123",
        })
        assert resp.status_code == 401

    def test_login_inactive_user(self, client, member_user):
        from tests.conftest import TestingSessionLocal
        db = TestingSessionLocal()
        member_user.is_active = False
        db.add(member_user)
        db.commit()
        db.close()
        resp = client.post("/api/auth/login", json={
            "email": "member@test.com",
            "password": "Password123",
        })
        assert resp.status_code == 401


class TestMe:

    def test_me_authenticated(self, client, member_user):
        token = get_token(client, "member@test.com")
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["data"]["email"] == "member@test.com"

    def test_me_no_token(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401
