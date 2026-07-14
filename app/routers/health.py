"""
Health endpoints.
"""
from fastapi import APIRouter
from app.monitoring import HealthChecker

router = APIRouter(
    prefix="",
    tags=["Monitoring"],
)


@router.get("/health")
def health():
    return HealthChecker.status()


@router.get("/live")
def live():
    return {"status": "alive"}


@router.get("/ready")
def ready():
    data = HealthChecker.status()
    return {"ready": data["database"]}


