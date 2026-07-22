"""Tests for /dashboard endpoints."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_kpis_returns_200(authorized_client):
    res = await authorized_client.get("/dashboard/kpis")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_kpis_schema(authorized_client):
    res = await authorized_client.get("/dashboard/kpis")
    data = res.json()

    assert "total_sales" in data
    assert "total_orders" in data
    assert "average_order_value" in data
    assert "top_region" in data
    assert "top_product" in data


@pytest.mark.asyncio
async def test_sales_by_region(authorized_client):
    res = await authorized_client.get("/dashboard/sales-by-region")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_top_products(authorized_client):
    res = await authorized_client.get("/dashboard/top-products")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_monthly_sales(authorized_client):
    res = await authorized_client.get("/dashboard/monthly-sales")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_chart_sales_by_region(authorized_client):
    res = await authorized_client.get("/dashboard/chart/sales-by-region")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_chart_top_products(authorized_client):
    res = await authorized_client.get("/dashboard/chart/top-products")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_chart_monthly_sales(authorized_client):
    res = await authorized_client.get("/dashboard/chart/monthly-sales")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_executive_summary(authorized_client):
    res = await authorized_client.get("/dashboard/chart/executive-summary")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_forecast_requires_admin(authorized_client):
    res = await authorized_client.get("/dashboard/forecast/revenue")
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_forecast_revenue(admin_client):
    res = await admin_client.get("/dashboard/forecast/revenue")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_forecast_growth(admin_client):
    res = await admin_client.get("/dashboard/forecast/growth")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_forecast_executive(admin_client):
    res = await admin_client.get("/dashboard/forecast/executive-forecast")
    assert res.status_code == 200