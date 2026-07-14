"""Application entry point."""

import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.models.user import User  # noqa: F401 — register model
from app.models.warehouse import *  # noqa: F401,F403 — register models

from app.middleware import (
    ExceptionMiddleware,
    LoggingMiddleware,
    RequestIDMiddleware,
    TimingMiddleware,
)
from app.routers.ai import router as ai_router
from app.routers.auth import router as auth_router
from app.routers.copilot import router as copilot_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.routers.ingest import router as ingest_router

logger = logging.getLogger(__name__)

if not settings.is_production:
    Base.metadata.create_all(bind=engine)
else:
    logger.info("Production mode — schema managed via Alembic.")

app = FastAPI(
    title=settings.project_name,
    version="1.0.3",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ExceptionMiddleware)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "application": settings.project_name,
    }


app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(dashboard_router)
app.include_router(ai_router)
app.include_router(copilot_router)
app.include_router(health_router)
