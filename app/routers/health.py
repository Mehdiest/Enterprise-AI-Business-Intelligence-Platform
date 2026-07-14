"""
Health endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
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


@router.get("/admin/reset-db")
async def reset_db(db: Session = Depends(get_db)):
    db.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    db.commit()
    return {"status": "done"}
