"""
Forecasting service.

Provides predictive analytics and
revenue forecasting for BI consumers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import (
    DimDate,
    FactSales,
)


class ForecastService:
    """
    Predictive analytics service.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def _load_daily_sales(
        self,
    ) -> pd.DataFrame:

        statement = (
            select(DimDate.full_date, func.sum(FactSales.amount).label("sales"))
            .join(FactSales, FactSales.date_id == DimDate.id)
            .group_by(DimDate.full_date)
            .order_by(DimDate.full_date)
        )
        rows = (await self.db.execute(statement)).all()

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(
            rows,
            columns=[
                "date",
                "sales",
            ],
        )

    async def revenue_forecast(
        self,
        forecast_days: int = 30,
    ) -> dict:
        sales_frame = await self._load_daily_sales()
        if len(sales_frame) < 5:
            return {
                "forecast_days": forecast_days,
                "predicted_revenue": 0.0,
                "trend": "insufficient_data",
            }
        predicted_revenue, trend = self._predict_revenue(sales_frame, forecast_days)
        return {
            "forecast_days": forecast_days,
            "predicted_revenue": round(predicted_revenue, 2),
            "trend": trend,
        }

    @staticmethod
    def _predict_revenue(sales_frame: pd.DataFrame, forecast_days: int) -> tuple[float, str]:
        sales_frame["day_index"] = np.arange(len(sales_frame))
        model = LinearRegression().fit(
            sales_frame[["day_index"]], sales_frame["sales"].astype(float)
        )
        future_days = np.arange(
            len(sales_frame), len(sales_frame) + forecast_days
        ).reshape(-1, 1)
        predicted_revenue = max(float(model.predict(future_days).sum()), 0.0)
        trend = "upward" if float(model.coef_[0]) > 0 else "downward"
        return predicted_revenue, trend

    async def growth_forecast(self) -> dict:

        df = await self._load_daily_sales()

        if len(df) < 2:
            return {
                "historical_growth": 0.0,
                "predicted_growth": 0.0,
            }

        first = float(df["sales"].iloc[0])

        last = float(df["sales"].iloc[-1])

        historical_growth = ((last - first) / first) * 100 if first > 0 else 0.0

        predicted_growth = historical_growth * 1.15

        return {
            "historical_growth": round(
                historical_growth,
                2,
            ),
            "predicted_growth": round(
                predicted_growth,
                2,
            ),
        }

    async def executive_forecast(self) -> dict:

        revenue = await self.revenue_forecast()

        growth = await self.growth_forecast()

        recommendation = (
            "Increase inventory planning and monitor top-performing regions."
            if revenue["trend"] == "upward"
            else "Review sales performance and marketing strategy."
        )

        return {
            "sales_forecast": revenue["predicted_revenue"],
            "growth_forecast": growth["predicted_growth"],
            "recommendation": recommendation,
        }
