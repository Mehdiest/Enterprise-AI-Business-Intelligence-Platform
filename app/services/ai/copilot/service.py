"""
Enterprise AI Copilot.
"""

from __future__ import annotations

from app.services.ai.copilot.engine import CopilotEngine
from app.services.ai.copilot.models import (
    CopilotRequest,
    CopilotResponse,
)


class CopilotService:
    """
    Enterprise AI Copilot.
    """

    def __init__(self) -> None:
        self.engine = CopilotEngine()

    async def ask(
        self,
        request: CopilotRequest,
    ) -> CopilotResponse:
        """
        Execute the Copilot request.
        """

        return await self.engine.process(request)