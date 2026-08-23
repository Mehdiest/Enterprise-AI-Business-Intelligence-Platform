"""Application configuration loaded from environment variables."""

from __future__ import annotations

import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    """Settings loaded from environment variables."""

    project_name: str = "Enterprise AI Business Intelligence Platform"
    app_version: str = "1.1.0"
    api_v1_prefix: str = "/api/v1"
    app_env: str = "development"

    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    cors_origins: str = "*"

    max_upload_mb: int = 10

    openai_api_key: str = ""
    memory_ttl_seconds: int = 86_400
    memory_database_path: str = ".memory.sqlite3"

    sql_statement_timeout_ms: int = 30_000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    @property
    def is_production(self) -> bool:
        """Return True when running in production."""
        return self.app_env.strip().lower() == "production"

    @property
    def database_url(self) -> str:
        """SQLAlchemy PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        """Return CORS origins parsed from the comma-separated whitelist."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def cors_allow_all(self) -> bool:
        """Return True when the origin whitelist is the wildcard."""
        return self.cors_origin_list == ["*"]

    @model_validator(mode="after")
    def validate_secret_key(self) -> Settings:
        """Reject insecure SECRET_KEY values in production."""
        if self.secret_key.strip() not in _UNSAFE_SECRETS:
            return self

        if self.is_production:
            raise ValueError(
                "SECRET_KEY is insecure. Set a strong random value before deployment."
            )

        logger.warning("Using insecure SECRET_KEY. Allowed only in development.")
        return self

    @model_validator(mode="after")
    def validate_cors(self) -> Settings:
        """Warn about wildcard CORS origin in production but allow it for flexibility."""
        if not self.cors_allow_all:
            return self

        if self.is_production:
            logger.warning(
                "CORS open to all origins ('*') in production. "
                "Consider setting an explicit comma-separated origin whitelist."
            )
            # Allow but warn - useful for APIs that need broad access
            return self

        logger.warning("CORS open to all origins ('*'); credentials disabled.")
        return self


settings = Settings()
