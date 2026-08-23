"""
Region knowledge builder.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import (
    DimRegion,
    FactSales,
)
from app.schemas.knowledge import (
    KnowledgeDocument,
)
from app.services.ai.knowledge.base import (
    BaseKnowledgeBuilder,
)


class RegionKnowledgeBuilder(
    BaseKnowledgeBuilder,
):
    """
    Builds region knowledge documents.
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
                DimRegion.region_name,
                func.sum(
                    FactSales.amount
                ).label(
                    "sales"
                ),
            )
            .join(
                FactSales,
                FactSales.region_id == DimRegion.id,
            )
            .group_by(
                DimRegion.region_name
            )
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        documents: list[
            KnowledgeDocument
        ] = []

        if not rows:
            return documents

        highest_sales = max(
            float(row.sales)
            for row in rows
        )

        for row in rows:

            sales = float(
                row.sales
            )

            slug = (
                row.region_name
                .lower()
                .replace(
                    " ",
                    "_",
                )
            )

            if sales == highest_sales:

                text = (
                    f"{row.region_name} region generated "
                    f"{sales:.2f} dollars in sales and is "
                    f"currently the highest-performing region."
                )

            else:

                text = (
                    f"{row.region_name} region generated "
                    f"{sales:.2f} dollars in sales."
                )

            documents.append(

                KnowledgeDocument(

                    id=f"region:{slug}",

                    text=text,

                    entity=row.region_name,

                    entity_type="region",

                    metric="sales",

                    value=sales,

                    metadata={

                        "currency": "USD",

                    },

                )

            )

        return documents