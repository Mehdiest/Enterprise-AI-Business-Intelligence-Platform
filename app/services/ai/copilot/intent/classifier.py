"""
Rule-based intent classifier.
"""

from __future__ import annotations

from app.services.ai.copilot.intent.base import (
    BaseIntentClassifier,
)

from app.services.ai.copilot.intent.models import (
    IntentResult,
    IntentType,
)


class RuleBasedIntentClassifier(
    BaseIntentClassifier,
):
    """
    Enterprise rule-based classifier.
    """

    def classify(
        self,
        question: str,
    ) -> IntentResult:

        q = question.lower()

        if any(
            word in q
            for word in (
                "top",
                "best",
                "highest",
                "product",
            )
        ):
            return IntentResult(
                intent=IntentType.PRODUCT_ANALYSIS,
                confidence=0.95,
                reason="Matched product keywords.",
            )

        if any(
            word in q
            for word in (
                "sales",
                "revenue",
                "income",
            )
        ):
            return IntentResult(
                intent=IntentType.SALES_ANALYSIS,
                confidence=0.95,
                reason="Matched sales keywords.",
            )

        if any(
            word in q
            for word in (
                "region",
                "north",
                "south",
                "east",
                "west",
            )
        ):
            return IntentResult(
                intent=IntentType.REGIONAL_ANALYSIS,
                confidence=0.95,
                reason="Matched regional keywords.",
            )

        if any(
            word in q
            for word in (
                "kpi",
                "metric",
                "average",
            )
        ):
            return IntentResult(
                intent=IntentType.KPI_LOOKUP,
                confidence=0.90,
                reason="Matched KPI keywords.",
            )

        if any(
            word in q
            for word in (
                "summary",
                "summarize",
            )
        ):
            return IntentResult(
                intent=IntentType.SUMMARY,
                confidence=0.90,
                reason="Matched summary keywords.",
            )

        if any(
            word in q
            for word in (
                "trend",
                "growth",
                "decline",
            )
        ):
            return IntentResult(
                intent=IntentType.TREND_ANALYSIS,
                confidence=0.90,
                reason="Matched trend keywords.",
            )

        return IntentResult(
            intent=IntentType.GENERAL,
            confidence=0.50,
            reason="No business rule matched.",
        )