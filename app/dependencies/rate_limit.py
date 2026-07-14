"""In-memory sliding-window rate limiter for login endpoint.

For multi-instance deployments, replace with a Redis-backed store.
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

_MAX_ATTEMPTS = 10
_WINDOW_SECONDS = 60

_attempts: dict[str, list[float]] = defaultdict(list)


def login_rate_limit(request: Request) -> None:
    """Dependency — raises 429 after too many login attempts from one IP."""

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _WINDOW_SECONDS

    bucket = _attempts[client_ip]
    _attempts[client_ip] = [ts for ts in bucket if ts > window_start]

    if len(_attempts[client_ip]) >= _MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )

    _attempts[client_ip].append(now)
