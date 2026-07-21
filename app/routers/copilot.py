"""
Enterprise Copilot Router.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.copilot import (
    CopilotRequest,
    CopilotResponse,
    SourceItem,
)

from app.services.ai.copilot.service import (
    CopilotService,
)

router = APIRouter(
    prefix="/copilot",
    tags=["Enterprise Copilot"],
)

service = CopilotService()


@router.post(
    "/query",
    response_model=CopilotResponse,
)
async def query(
    request: CopilotRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Enterprise AI Copilot endpoint.
    """

    response = await service.ask(request)

    return CopilotResponse(
        answer=response.answer,
        confidence=response.confidence,
        sources=[
            SourceItem(
                id=s.id,
                text=s.text,
                score=s.score,
            )
            for s in response.sources
        ],
    )