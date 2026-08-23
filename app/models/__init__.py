"""
Model package.

Importing every ORM model here ensures each table is registered on
`Base.metadata` as soon as `app.models` is imported. This is what lets Alembic
autogenerate "see" the full schema (and keeps the migration drift test honest).
"""

from .conversation import ConversationTurn
from .user import User
from .warehouse import (
    AuditMixin,
    DimChannel,
    DimCustomer,
    DimDate,
    DimProduct,
    DimRegion,
    FactSales,
)

__all__ = [
    "ConversationTurn",
    "User",
    "AuditMixin",
    "DimCustomer",
    "DimProduct",
    "DimRegion",
    "DimChannel",
    "DimDate",
    "FactSales",
]
