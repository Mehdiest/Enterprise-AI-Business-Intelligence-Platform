"""End-to-end flow tests."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.user import User


@pytest.mark.asyncio
async def test_full_user_journey(client, db, sample_csv):
    """Register, promote to admin, login, ingest, verify KPIs and copilot."""
    res = await client.post(
        "/auth/register",
        json={
            "full_name": "E2E User",
            "email": "e2e@test.com",
            "password": "E2EPass@123",
        },
    )
    assert res.status_code == 200

    result = await db.execute(select(User).where(User.email == "e2e@test.com"))
    user = result.scalar_one_or_none()

    user.role = "admin"
    await db.commit()
    await db.refresh(user)

    res = await client.post(
        "/auth/login",
        data={"username": "e2e@test.com", "password": "E2EPass@123"},
    )
    assert res.status_code == 200

    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    with open(sample_csv, "rb") as f:
        res = await client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )
    assert res.status_code == 200
    assert res.json()["rows_loaded"] > 0

    res = await client.get("/dashboard/kpis")
    assert res.status_code == 200

    res = await client.post(
        "/copilot/query",
        json={"question": "What are the top products by revenue?"},
    )
    assert res.status_code == 200
    assert len(res.json()["answer"]) > 0


@pytest.mark.asyncio
async def test_unauthorized_access_blocked(client):
    """Protected endpoints require authentication."""
    endpoints = [
        ("GET", "/auth/me"),
        ("POST", "/copilot/query"),
        ("POST", "/ingest/csv"),
        ("GET", "/dashboard/kpis"),
    ]

    for method, path in endpoints:
        if method == "GET":
            res = await client.get(path)
        else:
            res = await client.post(path, json={})
        
        assert res.status_code in (401, 422)


@pytest.mark.asyncio
async def test_health_always_accessible(client):
    paths = ["/health", "/live", "/ready", "/"]
    
    for path in paths:
        res = await client.get(path)
        assert res.status_code == 200