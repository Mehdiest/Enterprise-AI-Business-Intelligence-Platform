"""
Dashboard response schemas.

These schemas define the contract between the analytics
layer and dashboard/API consumers.
"""

from pydantic import BaseModel
from pydantic import Field


class KPIResponse(BaseModel):
    """
    Top-level KPI metrics.
    """

    total_sales: float = Field(..., ge=0)

    total_orders: int = Field(..., ge=0)

    average_order_value: float = Field(..., ge=0)

    top_region: str

    top_product: str


class RegionSalesResponse(BaseModel):
    """
    Sales aggregated by region.
    """

    region: str

    sales: float = Field(..., ge=0)


class ProductSalesResponse(BaseModel):
    """
    Sales aggregated by product.
    """

    product: str

    sales: float = Field(..., ge=0)


class MonthlySalesResponse(BaseModel):
    """
    Monthly sales trend.
    """

    month: str

    sales: float = Field(..., ge=0)


class ChartDatasetResponse(BaseModel):
    """
    Generic chart dataset.
    """

    chart_type: str

    title: str

    labels: list[str]

    values: list[float]


class ExecutiveSummaryResponse(BaseModel):
    """
    Executive dashboard summary.
    """

    total_sales: float

    total_orders: int

    average_order_value: float

    top_region: str

    top_product: str

    generated_at: str