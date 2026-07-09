"""
AI API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies.auth import get_current_user
from app.models.user import User

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
    current_user: User = Depends(get_current_user),
):
    """
    Enterprise AI Copilot endpoint.
    """

    service = CopilotService()

    return service.ask(
        request
    )


@router.get(
    "/insights",
    response_model=InsightResponse,
)
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate AI insights.
    """

    return InsightService(
        db
    ).generate_insight()


@router.get(
    "/executive-summary",
    response_model=ExecutiveSummaryAIResponse,
)
def executive_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate executive summary.
    """

    return InsightService(
        db
    ).executive_summary()


@router.get(
    "/sales-narrative",
    response_model=SalesNarrativeResponse,
)
def sales_narrative(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate sales narrative.
    """

    return InsightService(
        db
    ).sales_narrative()