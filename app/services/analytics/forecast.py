"""
Forecasting service.

Provides predictive analytics and
revenue forecasting for BI consumers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.warehouse import (
    FactSales,
    DimDate,
)


class ForecastService:
    """
    Predictive analytics service.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def _load_daily_sales(
        self,
    ) -> pd.DataFrame:

        rows = (
            self.db.query(
                DimDate.full_date,
                func.sum(
                    FactSales.amount
                ).label("sales"),
            )
            .join(
                FactSales,
                FactSales.date_id == DimDate.id,
            )
            .group_by(
                DimDate.full_date
            )
            .order_by(
                DimDate.full_date
            )
            .all()
        )

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(
            rows,
            columns=[
                "date",
                "sales",
            ],
        )

    def revenue_forecast(
        self,
        forecast_days: int = 30,
    ) -> dict:

        df = self._load_daily_sales()

        if len(df) < 5:
            return {
                "forecast_days": forecast_days,
                "predicted_revenue": 0.0,
                "trend": "insufficient_data",
            }

        df["day_index"] = np.arange(
            len(df)
        )

        x = df[["day_index"]]

        y = df["sales"].astype(float)

        model = LinearRegression()

        model.fit(
            x,
            y,
        )

        future_index = np.arange(
            len(df),
            len(df) + forecast_days,
        ).reshape(-1, 1)

        prediction = model.predict(
            future_index
        )

        total_revenue = max(
            float(prediction.sum()),
            0.0,
        )

        trend = (
            "upward"
            if float(model.coef_[0]) > 0
            else "downward"
        )

        return {
            "forecast_days": forecast_days,
            "predicted_revenue": round(
                total_revenue,
                2,
            ),
            "trend": trend,
        }

    def growth_forecast(self) -> dict:

        df = self._load_daily_sales()

        if len(df) < 2:
            return {
                "historical_growth": 0.0,
                "predicted_growth": 0.0,
            }

        first = float(
            df["sales"].iloc[0]
        )

        last = float(
            df["sales"].iloc[-1]
        )

        historical_growth = (
            ((last - first) / first) * 100
            if first > 0
            else 0.0
        )

        predicted_growth = (
            historical_growth * 1.15
        )

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

    def executive_forecast(self) -> dict:

        revenue = self.revenue_forecast()

        growth = self.growth_forecast()

        recommendation = (
            "Increase inventory planning and monitor top-performing regions."
            if revenue["trend"] == "upward"
            else "Review sales performance and marketing strategy."
        )

        return {
            "sales_forecast": revenue[
                "predicted_revenue"
            ],
            "growth_forecast": growth[
                "predicted_growth"
            ],
            "recommendation": recommendation,
        }