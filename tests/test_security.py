"""Tests for security layer."""

from __future__ import annotations


def test_protected_endpoint_without_token(client):
    res = client.post(
        "/copilot/query",
        json={"question": "test"},
    )
    assert res.status_code == 401


def test_protected_endpoint_with_bad_token(client):
    client.headers.update({"Authorization": "Bearer badtoken"})
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_protected_endpoint_with_malformed_header(client):
    client.headers.update({"Authorization": "NotBearer token"})
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_ingest_requires_auth(client, sample_csv):
    with open(sample_csv, "rb") as f:
        res = client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )
    assert res.status_code == 401


def test_stack_trace_not_exposed(client):
    """Exception middleware must not leak tracebacks."""
    res = client.get("/nonexistent-endpoint-xyz")
    assert res.status_code == 404
    body = res.text
    assert "Traceback" not in body
    assert "File " not in body


def test_health_is_public(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_root_is_public(client):
    res = client.get("/")
    assert res.status_code == 200
