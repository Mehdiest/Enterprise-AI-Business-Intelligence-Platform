"""
Enterprise AI response pipeline.
"""

from __future__ import annotations

from app.services.ai.copilot.models import (
    SourceReference,
)
from app.services.ai.copilot.response.citation import (
    CitationEngine,
)
from app.services.ai.copilot.response.confidence import (
    ConfidenceEngine,
)
from app.services.ai.copilot.response.formatter import (
    ResponseFormatter,
)
from app.services.ai.copilot.response.guard import (
    HallucinationGuard,
)
from app.services.ai.copilot.response.models import (
    StructuredResponse,
)
from app.services.ai.copilot.response.validator import (
    ResponseValidator,
)


class ResponsePipeline:

    def __init__(self):

        self.citation = CitationEngine()

        self.confidence = (
            ConfidenceEngine()
        )

        self.validator = (
            ResponseValidator()
        )

        self.guard = (
            HallucinationGuard()
        )

        self.formatter = (
            ResponseFormatter()
        )

    def process(
        self,
        *,
        answer: str,
        confidence: float,
        sources: list[SourceReference],
    ) -> StructuredResponse:

        citations = (
            self.citation.build(
                sources
            )
        )

        final_confidence = (
            self.confidence.calculate(
                intent_confidence=confidence,
                sources=sources,
            )
        )

        structured = (
            self.formatter.format(
                answer=answer,
                confidence=final_confidence,
                citations=citations,
            )
        )

        valid, validation = (
            self.validator.validate(
                structured.answer
            )
        )

        guard = (
            self.guard.inspect(
                answer=structured.answer,
                citations=structured.citations,
            )
        )

        structured.validated = valid

        structured.warnings.extend(
            validation
        )

        structured.warnings.extend(
            guard
        )

        return structured