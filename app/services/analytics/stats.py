"""Async dashboard aggregations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import DimDate, DimProduct, DimRegion, FactSales


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sales_by_region(self) -> list[dict]:
        statement = (
            select(DimRegion.region_name, func.sum(FactSales.amount).label("sales"))
            .join(FactSales, FactSales.region_id == DimRegion.id)
            .group_by(DimRegion.region_name)
            .order_by(func.sum(FactSales.amount).desc())
        )
        return [
            {"region": region, "sales": float(sales)}
            for region, sales in (await self.db.execute(statement)).all()
        ]

    async def top_products(self, limit: int = 10) -> list[dict]:
        statement = (
            select(DimProduct.product_name, func.sum(FactSales.amount).label("sales"))
            .join(FactSales, FactSales.product_id == DimProduct.id)
            .group_by(DimProduct.product_name)
            .order_by(func.sum(FactSales.amount).desc())
            .limit(limit)
        )
        return [
            {"product": product, "sales": float(sales)}
            for product, sales in (await self.db.execute(statement)).all()
        ]

    async def monthly_sales(self) -> list[dict]:
        statement = (
            select(DimDate.full_date, func.sum(FactSales.amount).label("sales"))
            .join(FactSales, FactSales.date_id == DimDate.id)
            .group_by(DimDate.full_date)
            .order_by(DimDate.full_date)
        )
        return [
            {"month": str(day), "sales": float(sales)}
            for day, sales in (await self.db.execute(statement)).all()
        ]
