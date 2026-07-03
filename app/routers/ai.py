"""
AI API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

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
):

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
):

    return InsightService(
        db
    ).generate_insight()


@router.get(
    "/executive-summary",
    response_model=ExecutiveSummaryAIResponse,
)
def executive_summary(
    db: Session = Depends(get_db),
):

    return InsightService(
        db
    ).executive_summary()


@router.get(
    "/sales-narrative",
    response_model=SalesNarrativeResponse,
)
def sales_narrative(
    db: Session = Depends(get_db),
):

    return InsightService(
        db
    ).sales_narrative()