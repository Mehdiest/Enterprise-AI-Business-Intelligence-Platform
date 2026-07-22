"""Authentication endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_register_success(client, test_user):
    res = await client.post("/auth/register", json=test_user)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_register_missing_fields(client):
    res = await client.post("/auth/register", json={"email": "test@test.com"})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_duplicate_email(client, registered_user):
    res = await client.post(
        "/auth/register",
        json={
            "full_name": "Test",
            "email": registered_user["email"],
            "password": "Password@123",
        },
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client, registered_user):
    res = await client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    res = await client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": "WrongPass@123",
        },
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client):
    res = await client.post(
        "/auth/login",
        data={"username": "unknown@test.com", "password": "Pass@123"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    res = await client.get("/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(authorized_client):
    res = await authorized_client.get("/auth/me")
    assert res.status_code == 200
    assert "email" in res.json()


@pytest.mark.asyncio
async def test_me_invalid_token(client):
    client.headers.update({"Authorization": "Bearer invalid"})
    res = await client.get("/auth/me")
    assert res.status_code == 401