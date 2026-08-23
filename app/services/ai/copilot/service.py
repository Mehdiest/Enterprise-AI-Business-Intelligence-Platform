"""Enterprise AI Copilot service."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.copilot.engine import CopilotEngine
from app.services.ai.copilot.memory import MemoryService
from app.services.ai.copilot.models import (
    CopilotRequest,
    CopilotResponse,
)


class CopilotService:
    """Execute Copilot requests with persistent conversation memory."""

    def __init__(self) -> None:
        self.memory = MemoryService()

    async def ask(
        self,
        request: CopilotRequest,
        db: AsyncSession | None = None,
    ) -> CopilotResponse:
        """Run the pipeline and persist the turn for the session."""
        session_id = request.session_id or self.memory.create_session()

        await self.memory.add_message(session_id, "user", request.question)

        engine = CopilotEngine(db=db)
        response = await engine.process(request, session_id=session_id)
        response.session_id = session_id

        await self.memory.add_message(session_id, "assistant", response.answer)

        return response