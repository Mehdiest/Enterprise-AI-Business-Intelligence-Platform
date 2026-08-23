"""Expose liveness, readiness, and health endpoints."""

import logging

from fastapi import APIRouter, Response, status

from app.monitoring import HealthChecker

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Monitoring"],
)


@router.get("/health")
async def health(response: Response) -> dict:
    """Report service health and mark the response unavailable when degraded."""
    try:
        health_status = await HealthChecker.status()

        if not health_status["database"]:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return health_status
    except Exception as e:
        logger.exception("Health check failed")
        # Return 200 with unhealthy status rather than crashing
        return {
            "status": "unhealthy",
            "database": False,
            "metrics": {},
            "error": str(e),
        }


@router.get("/live")
async def live() -> dict:
    return {"status": "alive"}


@router.get("/ready")
async def ready(response: Response) -> dict:
    """Report readiness based on database availability."""
    database_ok = await HealthChecker.database()

    if not database_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {"ready": database_ok}
