"""End-to-end flow tests."""

from __future__ import annotations


def test_full_user_journey(client, sample_csv):
    """Register → Login → Ingest CSV → Query KPIs → Ask Copilot."""

    # Register
    res = client.post(
        "/auth/register",
        json={
            "full_name": "E2E User",
            "email": "e2e@test.com",
            "password": "E2EPass@123",
        },
    )
    assert res.status_code == 200

    # Login
    res = client.post(
        "/auth/login",
        data={"username": "e2e@test.com", "password": "E2EPass@123"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    # Ingest CSV
    with open(sample_csv, "rb") as f:
        res = client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )
    assert res.status_code == 200
    assert res.json()["rows_loaded"] > 0

    # KPIs
    res = client.get("/dashboard/kpis")
    assert res.status_code == 200

    # Copilot
    res = client.post(
        "/copilot/query",
        json={"question": "What are the top products by revenue?"},
    )
    assert res.status_code == 200
    assert len(res.json()["answer"]) > 0


def test_unauthorized_access_blocked(client):
    """All protected endpoints block unauthenticated requests."""
    endpoints = [
        ("GET", "/auth/me"),
        ("POST", "/copilot/query"),
        ("POST", "/ingest/csv"),
        ("GET", "/dashboard/kpis"),
    ]
    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={})
        assert res.status_code in (401, 422), f"{method} {path} should be protected"


def test_health_always_accessible(client):
    for path in ["/health", "/live", "/ready", "/"]:
        res = client.get(path)
        assert res.status_code == 200, f"{path} should be public"
