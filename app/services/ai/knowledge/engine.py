"""
Enterprise Knowledge Engine.

Coordinates all knowledge builders and
produces a unified knowledge collection.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.schemas.knowledge import KnowledgeDocument

from app.services.ai.knowledge.product import (
    ProductKnowledgeBuilder,
)

from app.services.ai.knowledge.region import (
    RegionKnowledgeBuilder,
)

from app.services.ai.knowledge.kpi import (
    KPIKnowledgeBuilder,
)


class KnowledgeEngine:
    """
    Enterprise knowledge orchestrator.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.builders = [

            ProductKnowledgeBuilder(db),

            RegionKnowledgeBuilder(db),

            KPIKnowledgeBuilder(db),

        ]

    def build(
        self,
    ) -> list[KnowledgeDocument]:

        documents: list[
            KnowledgeDocument
        ] = []

        for builder in self.builders:

            documents.extend(
                builder.build()
            )

        return documents