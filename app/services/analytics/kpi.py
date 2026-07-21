"""Async KPI calculations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import DimProduct, DimRegion, FactSales


class KPIService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_kpis(self) -> dict:
        total_sales = (
            await self.db.execute(select(func.coalesce(func.sum(FactSales.amount), 0)))
        ).scalar_one()
        total_orders = (
            await self.db.execute(select(func.count(FactSales.id)))
        ).scalar_one()
        top_region = await self._top_name(
            DimRegion.region_name, FactSales.region_id, DimRegion.id
        )
        top_product = await self._top_name(
            DimProduct.product_name, FactSales.product_id, DimProduct.id
        )
        return {
            "total_sales": round(float(total_sales), 2),
            "total_orders": total_orders,
            "average_order_value": round(float(total_sales) / total_orders, 2)
            if total_orders
            else 0,
            "top_region": top_region,
            "top_product": top_product,
        }

    async def _top_name(self, name_column, fact_fk, dimension_id) -> str:
        statement = (
            select(name_column)
            .join(FactSales, fact_fk == dimension_id)
            .group_by(name_column)
            .order_by(func.sum(FactSales.amount).desc())
            .limit(1)
        )
        return (await self.db.execute(statement)).scalar_one_or_none() or "N/A"
