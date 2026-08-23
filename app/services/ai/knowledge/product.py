"""
Product knowledge builder.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import (
    DimProduct,
    FactSales,
)
from app.schemas.knowledge import (
    KnowledgeDocument,
)
from app.services.ai.knowledge.base import (
    BaseKnowledgeBuilder,
)


class ProductKnowledgeBuilder(
    BaseKnowledgeBuilder
):
    """
    Builds product knowledge documents.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def build(
        self,
    ) -> list[KnowledgeDocument]:

        stmt = (
            select(
                DimProduct.product_name,
                func.sum(
                    FactSales.amount
                ).label("sales"),
            )
            .join(
                FactSales,
                FactSales.product_id == DimProduct.id,
            )
            .group_by(
                DimProduct.product_name,
            )
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        documents: list[
            KnowledgeDocument
        ] = []

        for row in rows:

            sales = float(
                row.sales
            )

            product_slug = (
                row.product_name
                .lower()
                .replace(
                    " ",
                    "_",
                )
            )

            documents.append(

                KnowledgeDocument(

                    id=f"product:{product_slug}",

                    text=(
                        f"{row.product_name} "
                        f"generated total sales "
                        f"of {sales:.2f} dollars."
                    ),

                    entity=row.product_name,

                    entity_type="product",

                    metric="sales",

                    value=sales,

                    metadata={
                        "currency": "USD",
                    },

                )

            )

        return documents