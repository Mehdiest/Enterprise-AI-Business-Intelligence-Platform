"""Global exception middleware that hides internal errors from clients."""

from __future__ import annotations

import logging
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Catch unhandled exceptions and return a safe, traceable response."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception:
            logger.exception(
                "Unhandled exception | request_id=%s | path=%s",
                request_id,
                request.url.path,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error.",
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )
