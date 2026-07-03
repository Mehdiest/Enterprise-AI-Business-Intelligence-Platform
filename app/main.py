from app.config import settings

from app.database import Base, engine

from app.models.user import User
from app.models.warehouse import *

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI

from app.routers.ingest import router as ingest_router
from app.routers.dashboard import router as dashboard_router
from app.routers.ai import router as ai_router
from app.routers.health import router as health_router
from app.routers.copilot import router as copilot_router
from app.routers.auth import router as auth_router

from app.middleware import (
    LoggingMiddleware,
    TimingMiddleware,
    RequestIDMiddleware,
    ExceptionMiddleware,
)

app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
)

app.add_middleware(ExceptionMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "application": settings.project_name,
    }


app.include_router(ingest_router)
app.include_router(dashboard_router)
app.include_router(ai_router)
app.include_router(health_router)
app.include_router(copilot_router)
app.include_router(auth_router)