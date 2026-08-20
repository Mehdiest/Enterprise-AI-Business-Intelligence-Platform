"""Request logging middleware."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger("RequestLogger")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log each request's method, path, and response status."""

    async def dispatch(self, request, call_next):
        logger.info("%s %s", request.method, request.url.path)
        response = await call_next(request)
        logger.info(
            "%s %s -> %s",
            request.method,
            request.url.path,
            response.status_code,
        )
        return response
