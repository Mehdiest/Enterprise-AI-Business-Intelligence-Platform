"""In-memory sliding-window rate limiter for auth endpoints.

Single-process only; use a Redis-backed store for multi-instance deployments.
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

_MAX_ATTEMPTS = 10
_WINDOW_SECONDS = 60

_attempts: dict[str, list[float]] = defaultdict(list)
_last_sweep = 0.0


def auth_rate_limit(request: Request) -> None:
    """Raise 429 after too many auth attempts from one client IP."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    _sweep_expired(now)

    cutoff = now - _WINDOW_SECONDS
    fresh = [ts for ts in _attempts[client_ip] if ts > cutoff]
    if len(fresh) >= _MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again later.",
        )

    fresh.append(now)
    _attempts[client_ip] = fresh


def _sweep_expired(now: float) -> None:
    """Drop expired IP buckets, at most once per window, to bound memory."""
    global _last_sweep
    if now - _last_sweep < _WINDOW_SECONDS:
        return

    _last_sweep = now
    cutoff = now - _WINDOW_SECONDS
    for ip in list(_attempts):
        if not any(ts > cutoff for ts in _attempts[ip]):
            del _attempts[ip]
