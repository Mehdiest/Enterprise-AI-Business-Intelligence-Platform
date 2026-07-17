"""Tests for /ingest endpoints."""

from __future__ import annotations

import io


def test_ingest_csv_success(authorized_client, sample_csv):
    with open(sample_csv, "rb") as f:
        res = authorized_client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["rows_loaded"] > 0


def test_ingest_csv_unauthenticated(client, sample_csv):
    with open(sample_csv, "rb") as f:
        res = client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )
    assert res.status_code == 401


def test_ingest_wrong_extension(authorized_client, tmp_path):
    f = tmp_path / "data.txt"
    f.write_text("some text")
    with open(f, "rb") as fp:
        res = authorized_client.post(
            "/ingest/csv",
            files={"file": ("data.txt", fp, "text/plain")},
        )
    assert res.status_code == 400


def test_ingest_empty_csv(authorized_client, tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("")
    with open(f, "rb") as fp:
        res = authorized_client.post(
            "/ingest/csv",
            files={"file": ("empty.csv", fp, "text/csv")},
        )
    assert res.status_code in (400, 422, 500)


def test_ingest_csv_rows_received(authorized_client, sample_csv):
    with open(sample_csv, "rb") as f:
        res = authorized_client.post(
            "/ingest/csv",
            files={"file": ("sales.csv", f, "text/csv")},
        )
    assert res.status_code == 200
    assert res.json()["rows_received"] == 2
