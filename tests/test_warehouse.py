"""Warehouse model import tests."""

from __future__ import annotations

from app.models.warehouse import DimCustomer


def test_model_import():
    assert DimCustomer is not None