"""Tests for /auth endpoints."""

from __future__ import annotations


def test_register_success(client, test_user):
    res = client.post("/auth/register", json=test_user)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]
    assert "id" in data


def test_register_duplicate_email(client, test_user):
    client.post("/auth/register", json=test_user)
    res = client.post("/auth/register", json=test_user)
    assert res.status_code == 400


def test_register_missing_fields(client):
    res = client.post("/auth/register", json={"email": "x@x.com"})
    assert res.status_code == 422


def test_login_success(client, registered_user):
    res = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client, registered_user):
    res = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": "wrongpassword",
        },
    )
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post(
        "/auth/login",
        data={"username": "nobody@test.com", "password": "pass"},
    )
    assert res.status_code == 401


def test_me_authenticated(authorized_client, registered_user):
    res = authorized_client.get("/auth/me")
    assert res.status_code == 200
    assert res.json()["email"] == registered_user["email"]


def test_me_unauthenticated(client):
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_me_invalid_token(client):
    client.headers.update({"Authorization": "Bearer invalidtoken"})
    res = client.get("/auth/me")
    assert res.status_code == 401
