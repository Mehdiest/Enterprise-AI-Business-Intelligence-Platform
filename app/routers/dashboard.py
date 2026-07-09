"""
Dashboard API endpoints.

Provides analytics, charts, KPI data,
and predictive forecasting services.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.dashboard import (
    KPIResponse,
    RegionSalesResponse,
    ProductSalesResponse,
    MonthlySalesResponse,
    ChartDatasetResponse,
    ExecutiveSummaryResponse,
)

from app.schemas.forecast import (
    RevenueForecastResponse,
    GrowthForecastResponse,
    ExecutiveForecastResponse,
)

from app.services.analytics.kpi import KPIService
from app.services.analytics.stats import AnalyticsService
from app.services.analytics.charts import ChartService
from app.services.analytics.forecast import ForecastService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/kpis",
    response_model=KPIResponse,
)
def get_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return KPIService(db).get_kpis()


@router.get(
    "/sales-by-region",
    response_model=list[RegionSalesResponse],
)
def sales_by_region(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService(db).sales_by_region()


@router.get(
    "/top-products",
    response_model=list[ProductSalesResponse],
)
def top_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService(db).top_products()


@router.get(
    "/monthly-sales",
    response_model=list[MonthlySalesResponse],
)
def monthly_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService(db).monthly_sales()


@router.get(
    "/chart/sales-by-region",
    response_model=ChartDatasetResponse,
)
def sales_by_region_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ChartService(db).sales_by_region_chart()


@router.get(
    "/chart/top-products",
    response_model=ChartDatasetResponse,
)
def top_products_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ChartService(db).top_products_chart()


@router.get(
    "/chart/monthly-sales",
    response_model=ChartDatasetResponse,
)
def monthly_sales_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ChartService(db).monthly_sales_chart()


@router.get(
    "/chart/executive-summary",
    response_model=ExecutiveSummaryResponse,
)
def executive_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ChartService(db).executive_summary()


@router.get(
    "/forecast/revenue",
    response_model=RevenueForecastResponse,
)
def revenue_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ForecastService(db).revenue_forecast()


@router.get(
    "/forecast/growth",
    response_model=GrowthForecastResponse,
)
def growth_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ForecastService(db).growth_forecast()


@router.get(
    "/forecast/executive-forecast",
    response_model=ExecutiveForecastResponse,
)
def executive_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ForecastService(db).executive_forecast()