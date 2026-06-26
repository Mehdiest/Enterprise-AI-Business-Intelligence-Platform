"""
Enterprise AI Copilot service.

Provides a single entry point for
all AI assistant interactions.
"""

from __future__ import annotations

from app.services.ai.copilot.engine import (
    CopilotEngine,
)

from app.services.ai.copilot.models import (
    CopilotRequest,
    CopilotResponse,
)


class CopilotService:
    """
    High-level facade for the AI Copilot.

    This class hides the internal
    orchestration pipeline from the
    rest of the application.
    """

    @staticmethod
    def ask(
        request: CopilotRequest,
    ) -> CopilotResponse:
        """
        Process a user request.

        Parameters
        ----------
        request:
            User question.

        Returns
        -------
        CopilotResponse
        """

        return (
            CopilotEngine()
            .process(request)
        )