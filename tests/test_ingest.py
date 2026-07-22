"""Tests for /ingest endpoints."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_ingest_csv_success(admin_client, sample_csv):
    with open(sample_csv, "rb") as f:
        res = await admin_client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )

    assert res.status_code == 200

    data = res.json()

    assert data["success"] is True
    assert data["rows_loaded"] > 0


@pytest.mark.asyncio
async def test_ingest_csv_unauthenticated(client, sample_csv):
    with open(sample_csv, "rb") as f:
        res = await client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_ingest_csv_forbidden_for_viewer(authorized_client, sample_csv):
    with open(sample_csv, "rb") as f:
        res = await authorized_client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )

    assert res.status_code == 403


@pytest.mark.asyncio
async def test_ingest_wrong_extension(admin_client, tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_text("some text")

    with open(file_path, "rb") as fp:
        res = await admin_client.post(
            "/ingest/csv",
            files={"file": ("data.txt", fp, "text/plain")},
        )

    assert res.status_code == 400


@pytest.mark.asyncio
async def test_ingest_empty_csv(admin_client, tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")

    with open(file_path, "rb") as fp:
        res = await admin_client.post(
            "/ingest/csv",
            files={"file": ("empty.csv", fp, "text/csv")},
        )

    assert res.status_code in (400, 422, 500)


@pytest.mark.asyncio
async def test_ingest_csv_rows_received(admin_client, sample_csv):
    with open(sample_csv, "rb") as f:
        res = await admin_client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )

    assert res.status_code == 200
    assert res.json()["rows_received"] == 2