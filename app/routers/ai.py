"""
AI API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.rbac import require_admin
from app.schemas.ai import (
    ExecutiveSummaryAIResponse,
    InsightResponse,
    SalesNarrativeResponse,
)
from app.services.ai import InsightService
from app.services.ai.copilot import CopilotService
from app.services.ai.copilot.models import (
    CopilotRequest,
    CopilotResponse,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/copilot",
    response_model=CopilotResponse,
)
async def copilot(
    request: CopilotRequest,
    current_user=Depends(require_admin),
):
    """
    Enterprise AI Copilot endpoint.
    """

    service = CopilotService()

    return await service.ask(request)


@router.get(
    "/insights",
    response_model=InsightResponse,
)
async def get_insights(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Generate AI insights.
    """

    return await InsightService(db).generate_insight()


@router.get(
    "/executive-summary",
    response_model=ExecutiveSummaryAIResponse,
)
async def executive_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Generate executive summary.
    """

    return await InsightService(db).executive_summary()


@router.get(
    "/sales-narrative",
    response_model=SalesNarrativeResponse,
)
async def sales_narrative(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Generate sales narrative.
    """

    return await InsightService(db).sales_narrative()