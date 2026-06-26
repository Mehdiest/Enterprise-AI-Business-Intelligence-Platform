"""
KPI knowledge builder.
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.warehouse import (
    DimProduct,
    DimRegion,
    FactSales,
)

from app.schemas.knowledge import (
    KnowledgeDocument,
)

from app.services.ai.knowledge.base import (
    BaseKnowledgeBuilder,
)


class KPIKnowledgeBuilder(
    BaseKnowledgeBuilder,
):
    """
    Builds executive KPI knowledge.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def build(
        self,
    ) -> list[KnowledgeDocument]:

        documents: list[
            KnowledgeDocument
        ] = []

        total_sales = float(

            self.db.query(
                func.sum(
                    FactSales.amount
                )
            ).scalar()
            or 0

        )

        total_orders = int(

            self.db.query(
                func.count(
                    FactSales.id
                )
            ).scalar()
            or 0

        )

        average_order = (

            total_sales / total_orders
            if total_orders
            else 0

        )

        top_product = (

            self.db.query(

                DimProduct.product_name,

                func.sum(
                    FactSales.amount
                ).label(
                    "sales"
                ),

            )

            .join(
                FactSales,
                FactSales.product_id == DimProduct.id,
            )

            .group_by(
                DimProduct.product_name
            )

            .order_by(
                func.sum(
                    FactSales.amount
                ).desc()
            )

            .first()

        )

        top_region = (

            self.db.query(

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

            .order_by(
                func.sum(
                    FactSales.amount
                ).desc()
            )

            .first()

        )

        documents.append(

            KnowledgeDocument(

                id="kpi:total_sales",

                text=f"Total sales are {total_sales:.2f} dollars.",

                entity="Total Sales",

                entity_type="kpi",

                metric="total_sales",

                value=total_sales,

                metadata={
                    "currency": "USD",
                },

            )

        )

        documents.append(

            KnowledgeDocument(

                id="kpi:total_orders",

                text=f"Total completed orders are {total_orders}.",

                entity="Total Orders",

                entity_type="kpi",

                metric="orders",

                value=float(total_orders),

                metadata={},

            )

        )

        documents.append(

            KnowledgeDocument(

                id="kpi:average_order_value",

                text=(
                    f"Average order value is "
                    f"{average_order:.2f} dollars."
                ),

                entity="Average Order Value",

                entity_type="kpi",

                metric="average_order_value",

                value=average_order,

                metadata={
                    "currency": "USD",
                },

            )

        )

        if top_product:

            documents.append(

                KnowledgeDocument(

                    id="kpi:top_product",

                    text=(
                        f"{top_product.product_name} is currently "
                        f"the best-selling product."
                    ),

                    entity=top_product.product_name,

                    entity_type="product",

                    metric="top_product",

                    value=float(top_product.sales),

                    metadata={},

                )

            )

        if top_region:

            documents.append(

                KnowledgeDocument(

                    id="kpi:top_region",

                    text=(
                        f"{top_region.region_name} is currently "
                        f"the highest-performing region."
                    ),

                    entity=top_region.region_name,

                    entity_type="region",

                    metric="top_region",

                    value=float(top_region.sales),

                    metadata={},

                )

            )

        return documents