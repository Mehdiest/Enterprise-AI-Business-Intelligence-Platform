"""Expose liveness, readiness, and health endpoints."""

from fastapi import APIRouter, Response, status

from app.monitoring import HealthChecker

router = APIRouter(
    prefix="",
    tags=["Monitoring"],
)


@router.get("/health")
async def health(response: Response) -> dict:
    """Report service health and mark the response unavailable when degraded."""
    health_status = await HealthChecker.status()

    if not health_status["database"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status


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
