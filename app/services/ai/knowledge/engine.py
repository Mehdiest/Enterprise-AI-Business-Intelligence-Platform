"""
Enterprise Knowledge Engine.

Coordinates all knowledge builders and
produces a unified knowledge collection.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.knowledge import KnowledgeDocument
from app.services.ai.knowledge.kpi import (
    KPIKnowledgeBuilder,
)
from app.services.ai.knowledge.product import (
    ProductKnowledgeBuilder,
)
from app.services.ai.knowledge.region import (
    RegionKnowledgeBuilder,
)


class KnowledgeEngine:
    """
    Enterprise knowledge orchestrator.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.builders = [

            ProductKnowledgeBuilder(db),

            RegionKnowledgeBuilder(db),

            KPIKnowledgeBuilder(db),

        ]

    async def build(
        self,
    ) -> list[KnowledgeDocument]:

        documents: list[
            KnowledgeDocument
        ] = []

        for builder in self.builders:

            documents.extend(
                await builder.build()
            )

        return documents