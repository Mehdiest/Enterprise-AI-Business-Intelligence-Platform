"""
Global exception middleware.

Production-grade exception handling.

Goals
-----
- Never leak internal exception details.
- Log full traceback for developers.
- Return safe error messages to clients.
- Attach request id for troubleshooting.
"""

from __future__ import annotations

import logging
import traceback
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    Global exception middleware.

    Catches every unhandled exception and prevents
    sensitive information from being returned
    to API consumers.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
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

            logger.debug(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error.",
                    "request_id": request_id,
                },
                headers={
                    "X-Request-ID": request_id,
                },
            )