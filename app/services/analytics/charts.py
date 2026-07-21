from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics.kpi import KPIService
from app.services.analytics.stats import AnalyticsService


class ChartService:
    def __init__(self, db: AsyncSession):
        self.analytics, self.kpis = AnalyticsService(db), KPIService(db)

    async def sales_by_region_chart(self):
        data = await self.analytics.sales_by_region()
        return {
            "chart_type": "bar",
            "title": "Sales by Region",
            "labels": [x["region"] for x in data],
            "values": [x["sales"] for x in data],
        }

    async def top_products_chart(self):
        data = await self.analytics.top_products()
        return {
            "chart_type": "bar",
            "title": "Top Products",
            "labels": [x["product"] for x in data],
            "values": [x["sales"] for x in data],
        }

    async def monthly_sales_chart(self):
        data = await self.analytics.monthly_sales()
        return {
            "chart_type": "line",
            "title": "Monthly Sales",
            "labels": [x["month"] for x in data],
            "values": [x["sales"] for x in data],
        }

    async def executive_summary(self):
        return {
            **(await self.kpis.get_kpis()),
            "generated_at": datetime.now(UTC).isoformat(),
        }
