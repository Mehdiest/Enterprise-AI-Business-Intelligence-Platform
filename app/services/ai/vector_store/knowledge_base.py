"""
Knowledge base builder.

Converts warehouse records into structured
knowledge documents for semantic retrieval.
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.warehouse import (
    DimProduct,
    FactSales,
)
from app.schemas.knowledge import KnowledgeDocument


class KnowledgeBaseBuilder:
    """
    Builds enterprise knowledge objects.
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

        for index, row in enumerate(
            rows,
            start=1,
        ):

            sales = float(
                row.sales
            )

            documents.append(

                KnowledgeDocument(

                    id=str(index),

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