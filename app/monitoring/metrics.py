"""Process-level application metrics."""

from __future__ import annotations

import platform
import time

from app.config import settings


class MetricsCollector:
    """Collect lightweight runtime metrics."""

    started_at = time.time()

    @classmethod
    def collect(cls) -> dict:
        return {
            "python": platform.python_version(),
            "platform": platform.system(),
            "uptime_seconds": round(time.time() - cls.started_at, 2),
            "environment": settings.app_env,
            "version": settings.app_version,
        }
