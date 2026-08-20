"""Shared application settings wrapping project config."""

from __future__ import annotations

from app.config import settings as project_settings

from .environment import Environment

_ENV_MAP = {
    "development": Environment.DEVELOPMENT,
    "testing": Environment.TESTING,
    "staging": Environment.STAGING,
    "production": Environment.PRODUCTION,
}


class Settings:
    """Expose project settings behind a stable interface."""

    @property
    def project_name(self) -> str:
        return project_settings.project_name

    @property
    def database_url(self) -> str:
        return project_settings.database_url

    @property
    def environment(self) -> Environment:
        return _ENV_MAP.get(
            project_settings.app_env.strip().lower(),
            Environment.DEVELOPMENT,
        )

    @property
    def debug(self) -> bool:
        return self.environment == Environment.DEVELOPMENT


settings = Settings()
