"""
Knowledge document schema.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class KnowledgeDocument(BaseModel):
    """
    Enterprise knowledge object.
    """

    id: str

    text: str

    entity: str

    entity_type: str

    metric: str

    value: float

    metadata: dict[str, Any]