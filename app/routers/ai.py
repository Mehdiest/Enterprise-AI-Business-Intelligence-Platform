"""
AI API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies.rbac import (
    require_admin,
)

from app.schemas.ai import (
    InsightResponse,
    ExecutiveSummaryAIResponse,
    SalesNarrativeResponse,
)

from app.services.ai import (
    InsightService,
)

from app.services.ai.copilot import (
    CopilotService,
)

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
def copilot(
    request: CopilotRequest,
    current_user=Depends(require_admin),
):
    """
    Enterprise AI Copilot endpoint.
    """

    service = CopilotService()

    return service.ask(
        request,
    )


@router.get(
    "/insights",
    response_model=InsightResponse,
)
def get_insights(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Generate AI insights.
    """

    return InsightService(
        db,
    ).generate_insight()


@router.get(
    "/executive-summary",
    response_model=ExecutiveSummaryAIResponse,
)
def executive_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Generate executive summary.
    """

    return InsightService(
        db,
    ).executive_summary()


@router.get(
    "/sales-narrative",
    response_model=SalesNarrativeResponse,
)
def sales_narrative(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Generate sales narrative.
    """

    return InsightService(
        db,
    ).sales_narrative()