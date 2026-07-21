"""Async dashboard endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.rbac import require_admin, require_viewer
from app.schemas.dashboard import (
    ChartDatasetResponse,
    ExecutiveSummaryResponse,
    KPIResponse,
    MonthlySalesResponse,
    ProductSalesResponse,
    RegionSalesResponse,
)
from app.schemas.forecast import (
    ExecutiveForecastResponse,
    GrowthForecastResponse,
    RevenueForecastResponse,
)
from app.services.analytics.charts import ChartService
from app.services.analytics.forecast import ForecastService
from app.services.analytics.kpi import KPIService
from app.services.analytics.stats import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_viewer)
):
    return await KPIService(db).get_kpis()


@router.get("/sales-by-region", response_model=list[RegionSalesResponse])
async def sales_by_region(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_viewer)
):
    return await AnalyticsService(db).sales_by_region()


@router.get("/top-products", response_model=list[ProductSalesResponse])
async def top_products(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_viewer)
):
    return await AnalyticsService(db).top_products()


@router.get("/monthly-sales", response_model=list[MonthlySalesResponse])
async def monthly_sales(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_viewer)
):
    return await AnalyticsService(db).monthly_sales()


@router.get("/chart/sales-by-region", response_model=ChartDatasetResponse)
async def sales_by_region_chart(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_viewer)
):
    return await ChartService(db).sales_by_region_chart()


@router.get("/chart/top-products", response_model=ChartDatasetResponse)
async def top_products_chart(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_viewer)
):
    return await ChartService(db).top_products_chart()


@router.get("/chart/monthly-sales", response_model=ChartDatasetResponse)
async def monthly_sales_chart(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_viewer)
):
    return await ChartService(db).monthly_sales_chart()


@router.get("/chart/executive-summary", response_model=ExecutiveSummaryResponse)
async def executive_summary(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_viewer)
):
    return await ChartService(db).executive_summary()


@router.get("/forecast/revenue", response_model=RevenueForecastResponse)
async def revenue_forecast(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)
):
    return await ForecastService(db).revenue_forecast()


@router.get("/forecast/growth", response_model=GrowthForecastResponse)
async def growth_forecast(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)
):
    return await ForecastService(db).growth_forecast()


@router.get("/forecast/executive-forecast", response_model=ExecutiveForecastResponse)
async def executive_forecast(
    db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)
):
    return await ForecastService(db).executive_forecast()
