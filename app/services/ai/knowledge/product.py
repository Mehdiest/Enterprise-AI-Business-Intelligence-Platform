"""
Product knowledge builder.
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

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
        db: Session,
    ):
        self.db = db

    def build(
        self,
    ) -> list[KnowledgeDocument]:

        rows = (
            self.db.query(
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
            .all()
        )

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