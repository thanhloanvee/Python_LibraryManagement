"""Authentication endpoint tests."""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_user_and_login


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, db_session: AsyncSession):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Secure@123",
            "full_name": "New User",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["role"] == "reader"
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "username": "dupuser",
        "email": "dup1@example.com",
        "password": "Secure@123",
        "full_name": "Dup User",
    }
    await client.post("/api/v1/auth/register", json=payload)

    payload["email"] = "dup2@example.com"
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422
    assert "username" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_username_pattern(client: AsyncClient, db_session):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "bad user!",
            "email": "bad@example.com",
            "password": "Secure@123",
            "full_name": "Bad",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    headers = await create_user_and_login(
        client, username="logintest", db=db_session
    )
    assert "Bearer" in headers["Authorization"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session: AsyncSession):
    await create_user_and_login(
        client, username="wrongpw", db=db_session
    )
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpw", "password": "WrongPassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, db_session: AsyncSession):
    headers = await create_user_and_login(
        client, username="me_user", db=db_session
    )
    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "me_user"


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, db_session: AsyncSession):
    headers = await create_user_and_login(
        client, username="changepw_user", db=db_session
    )
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "Test@123456", "new_password": "NewPass@789"},
        headers=headers,
    )
    assert resp.status_code == 200

    # Old password should no longer work
    resp2 = await client.post(
        "/api/v1/auth/login",
        data={"username": "changepw_user", "password": "Test@123456"},
    )
    assert resp2.status_code == 401
