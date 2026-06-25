"""
Dashboard API endpoints.

Provides analytics and KPI data for
BI dashboards, Power BI consumers,
and future AI insight services.
"""

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.dashboard import (
    KPIResponse,
    RegionSalesResponse,
    ProductSalesResponse,
    MonthlySalesResponse,
    ChartDatasetResponse,
    ExecutiveSummaryResponse,
)

from app.services.analytics.kpi import KPIService
from app.services.analytics.stats import AnalyticsService
from app.services.analytics.charts import ChartService

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
):
    """
    Return top-level KPI metrics.
    """

    service = KPIService(db)

    return service.get_kpis()


@router.get(
    "/sales-by-region",
    response_model=list[RegionSalesResponse],
)
def sales_by_region(
    db: Session = Depends(get_db),
):
    """
    Return sales aggregated by region.
    """

    service = AnalyticsService(db)

    return service.sales_by_region()


@router.get(
    "/top-products",
    response_model=list[ProductSalesResponse],
)
def top_products(
    db: Session = Depends(get_db),
):
    """
    Return top-selling products.
    """

    service = AnalyticsService(db)

    return service.top_products()


@router.get(
    "/monthly-sales",
    response_model=list[MonthlySalesResponse],
)
def monthly_sales(
    db: Session = Depends(get_db),
):
    """
    Return sales trend over time.
    """

    service = AnalyticsService(db)

    return service.monthly_sales()


@router.get(
    "/chart/sales-by-region",
    response_model=ChartDatasetResponse,
)
def sales_by_region_chart(
    db: Session = Depends(get_db),
):
    """
    Chart-ready sales by region dataset.
    """

    service = ChartService(db)

    return service.sales_by_region_chart()


@router.get(
    "/chart/top-products",
    response_model=ChartDatasetResponse,
)
def top_products_chart(
    db: Session = Depends(get_db),
):
    """
    Chart-ready top products dataset.
    """

    service = ChartService(db)

    return service.top_products_chart()


@router.get(
    "/chart/monthly-sales",
    response_model=ChartDatasetResponse,
)
def monthly_sales_chart(
    db: Session = Depends(get_db),
):
    """
    Chart-ready monthly sales dataset.
    """

    service = ChartService(db)

    return service.monthly_sales_chart()


@router.get(
    "/chart/executive-summary",
    response_model=ExecutiveSummaryResponse,
)
def executive_summary(
    db: Session = Depends(get_db),
):
    """
    Executive dashboard summary.
    """

    service = ChartService(db)

    return service.executive_summary()