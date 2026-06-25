"""
Chart dataset builders.

Transforms analytics data into
frontend and Power BI friendly formats.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.services.analytics.kpi import KPIService
from app.services.analytics.stats import AnalyticsService


class ChartService:
    """
    Build chart-ready datasets.
    """

    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsService(db)
        self.kpis = KPIService(db)

    def sales_by_region_chart(self) -> dict:

        data = self.analytics.sales_by_region()

        return {
            "chart_type": "bar",
            "title": "Sales by Region",
            "labels": [
                item["region"]
                for item in data
            ],
            "values": [
                item["sales"]
                for item in data
            ],
        }

    def top_products_chart(self) -> dict:

        data = self.analytics.top_products()

        return {
            "chart_type": "bar",
            "title": "Top Products",
            "labels": [
                item["product"]
                for item in data
            ],
            "values": [
                item["sales"]
                for item in data
            ],
        }

    def monthly_sales_chart(self) -> dict:

        data = self.analytics.monthly_sales()

        return {
            "chart_type": "line",
            "title": "Monthly Sales",
            "labels": [
                item["month"]
                for item in data
            ],
            "values": [
                item["sales"]
                for item in data
            ],
        }

    def executive_summary(self) -> dict:

        kpis = self.kpis.get_kpis()

        return {
            **kpis,
            "generated_at": datetime.utcnow().isoformat(),
        }