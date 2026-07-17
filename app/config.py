"""
Application configuration loaded from environment.
"""

from __future__ import annotations

import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

logger = logging.getLogger(__name__)

_UNSAFE_SECRETS = {
    "",
    "change-this-secret-key",
    "super-secret-key-change-this",
    "change_this_secret_key",
    "my_super_secret_key",
    "replace-with-a-random-48-byte-token",
}


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # ==========================================================
    # Application
    # ==========================================================

    project_name: str = "Enterprise AI Business Intelligence Platform"

    api_v1_prefix: str = "/api/v1"

    app_env: str = "development"

    # ==========================================================
    # Database
    # ==========================================================

    postgres_host: str

    postgres_port: int

    postgres_db: str

    postgres_user: str

    postgres_password: str

    # ==========================================================
    # Authentication
    # ==========================================================

    secret_key: str

    algorithm: str = "HS256"

    access_token_expire_minutes: int = 60

    refresh_token_expire_days: int = 7

    # ==========================================================
    # CORS
    # ==========================================================

    cors_origins: str = "*"

    # ==========================================================
    # Upload
    # ==========================================================

    max_upload_mb: int = 10

    # ==========================================================
    # AI
    # ==========================================================

    openai_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    @property
    def is_production(self) -> bool:
        """
        Return True when running in production.
        """

        return (
            self.app_env.strip().lower()
            == "production"
        )

    @property
    def database_url(self) -> str:
        """
        SQLAlchemy PostgreSQL connection URL.
        """

        return (
            f"postgresql+psycopg2://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        """
        Parse CORS origins.
        """

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        """
        Reject insecure SECRET_KEY values in production.
        """

        if self.secret_key.strip() not in _UNSAFE_SECRETS:
            return self

        if self.is_production:

            raise ValueError(
                "SECRET_KEY is insecure. "
                "Set a strong random value before deployment."
            )

        logger.warning(
            "Using insecure SECRET_KEY. "
            "Allowed only in development."
        )

        return self


settings = Settings()