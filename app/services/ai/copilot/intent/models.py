"""
Intent domain models.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class IntentType(str, Enum):
    """
    Supported business intents.
    """

    SALES_ANALYSIS = "sales_analysis"
    PRODUCT_ANALYSIS = "product_analysis"
    REGIONAL_ANALYSIS = "regional_analysis"
    KPI_LOOKUP = "kpi_lookup"
    SUMMARY = "summary"
    TREND_ANALYSIS = "trend_analysis"
    GENERAL = "general"


class IntentResult(BaseModel):
    """
    Intent classification result.
    """

    intent: IntentType

    confidence: float

    reason: str