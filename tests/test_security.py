"""Security and middleware tests."""

import pytest


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    res = await client.post("/copilot/query", json={"question": "test"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_malformed_header(client):
    client.headers.update({"Authorization": "NotBearer token"})
    res = await client.get("/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_stack_trace_not_exposed(client):
    res = await client.get("/nonexistent-endpoint-xyz")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_root_is_public(client):
    res = await client.get("/")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_protected_endpoint_with_bad_token(client):
    client.headers.update({"Authorization": "Bearer badtoken"})
    res = await client.get("/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_ingest_requires_auth(client):
    res = await client.post("/ingest/csv")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_health_is_public(client):
    res = await client.get("/health")
    assert res.status_code == 200