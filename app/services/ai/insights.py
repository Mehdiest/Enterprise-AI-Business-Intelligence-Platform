"""Async business insight queries."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import DimProduct, DimRegion, FactSales


class InsightService:
    """Create warehouse-derived business insights."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_insight(self) -> dict:
        """Return the highest-contributing region insight."""
        total_sales = await self._total_sales()
        top_region = await self._top_region()
        if top_region is None:
            return {"insight": "No sales data available."}

        region_name, region_sales = top_region
        contribution = self._contribution(region_sales, total_sales)
        return {
            "insight": (
                f"{region_name} region generated {contribution:.1f}% of total sales "
                "and is currently the top-performing region."
            )
        }

    async def executive_summary(self) -> dict:
        """Return the aggregate revenue summary."""
        total_sales = await self._total_sales()
        order_count = await self._order_count()
        return {
            "summary": (
                f"The business generated {total_sales:,.0f} in revenue across "
                f"{order_count} sales transactions."
            )
        }

    async def sales_narrative(self) -> dict:
        """Return the top product narrative."""
        product_name = await self._top_product_name()
        if product_name is None:
            return {"narrative": "No sales activity detected."}
        return {
            "narrative": (
                f"{product_name} is currently the strongest product in the portfolio."
            )
        }

    async def _total_sales(self) -> float:
        statement = select(func.coalesce(func.sum(FactSales.amount), 0))
        sales_value = (await self.db.execute(statement)).scalar_one()
        return float(sales_value)

    async def _order_count(self) -> int:
        statement = select(func.count(FactSales.id))
        return (await self.db.execute(statement)).scalar_one()

    async def _top_region(self) -> tuple[str, float] | None:
        statement = (
            select(DimRegion.region_name, func.sum(FactSales.amount).label("sales"))
            .join(FactSales, FactSales.region_id == DimRegion.id)
            .group_by(DimRegion.region_name)
            .order_by(func.sum(FactSales.amount).desc())
            .limit(1)
        )
        region_row = (await self.db.execute(statement)).first()
        return (region_row[0], float(region_row[1])) if region_row else None

    async def _top_product_name(self) -> str | None:
        statement = (
            select(DimProduct.product_name)
            .join(FactSales, FactSales.product_id == DimProduct.id)
            .group_by(DimProduct.product_name)
            .order_by(func.sum(FactSales.amount).desc())
            .limit(1)
        )
        return (await self.db.execute(statement)).scalar_one_or_none()

    @staticmethod
    def _contribution(region_sales: float, total_sales: float) -> float:
        return region_sales / total_sales * 100 if total_sales else 0
