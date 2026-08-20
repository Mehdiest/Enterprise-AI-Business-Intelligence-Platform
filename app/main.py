"""Application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.middleware import (
    ExceptionMiddleware,
    LoggingMiddleware,
    RequestIDMiddleware,
    TimingMiddleware,
)
from app.models.user import User  # noqa: F401 — register model for ORM mapping
from app.models.warehouse import *  # noqa: F401,F403 — register models for ORM mapping
from app.routers.ai import router as ai_router
from app.routers.auth import router as auth_router
from app.routers.copilot import router as copilot_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.routers.ingest import router as ingest_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application lifecycle.

    Schema management is owned exclusively by Alembic migrations
    (``alembic upgrade head``). The application NEVER creates tables at
    runtime — in any environment — so that a deployment's schema is always
    deterministic and reviewable. This handler only disposes the database
    engine cleanly on shutdown.
    """
    logger.info(
        "Application startup: schema is managed by Alembic migrations "
        "(run `alembic upgrade head` before serving traffic)."
    )
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.project_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=not settings.cors_allow_all,
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
