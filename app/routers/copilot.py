"""
Enterprise Copilot Router.
"""

from __future__ import annotations

from app.schemas.copilot import (
    CopilotRequest,
    CopilotResponse,
    SourceItem,
)

from fastapi import APIRouter

from app.schemas.copilot import (
    CopilotRequest,
    CopilotResponse,
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
def query(
    request: CopilotRequest,
):

    response = service.ask(
        request,
    )

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