"""Tests for /copilot endpoints."""

from __future__ import annotations


def test_copilot_query_success(authorized_client):
    res = authorized_client.post(
        "/copilot/query",
        json={"question": "What are the top products by revenue?"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], float)
    assert "sources" in data


def test_copilot_query_unauthenticated(client):
    res = client.post(
        "/copilot/query",
        json={"question": "What are the top products by revenue?"},
    )
    assert res.status_code == 401


def test_copilot_query_missing_question(authorized_client):
    res = authorized_client.post("/copilot/query", json={})
    assert res.status_code == 422


def test_copilot_query_empty_question(authorized_client):
    res = authorized_client.post(
        "/copilot/query",
        json={"question": ""},
    )
    assert res.status_code in (200, 422)


def test_copilot_confidence_range(authorized_client):
    res = authorized_client.post(
        "/copilot/query",
        json={"question": "Show me sales by region"},
    )
    assert res.status_code == 200
    confidence = res.json()["confidence"]
    assert 0.0 <= confidence <= 1.0


def test_copilot_answer_is_string(authorized_client):
    res = authorized_client.post(
        "/copilot/query",
        json={"question": "What is the total revenue?"},
    )
    assert res.status_code == 200
    assert isinstance(res.json()["answer"], str)
    assert len(res.json()["answer"]) > 0
