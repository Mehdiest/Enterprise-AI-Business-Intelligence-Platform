"""
Forecast response schemas.
"""

from pydantic import BaseModel
from pydantic import Field


class RevenueForecastResponse(BaseModel):
    """
    Revenue forecast output.
    """

    forecast_days: int = Field(..., ge=1)

    predicted_revenue: float = Field(..., ge=0)

    trend: str


class GrowthForecastResponse(BaseModel):
    """
    Growth prediction output.
    """

    historical_growth: float

    predicted_growth: float


class ExecutiveForecastResponse(BaseModel):
    """
    Executive forecasting summary.
    """

    sales_forecast: float

    growth_forecast: float

    recommendation: str