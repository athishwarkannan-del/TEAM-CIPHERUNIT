"""
MuleTrace AI — Application Settings.

Centralized configuration using Pydantic Settings.
All values are loaded from environment variables or .env file.
Validated and type-cast at application startup — fails fast on misconfiguration.

Usage:
    from app.config.settings import settings
    print(settings.APP_NAME)
"""

from __future__ import annotations


from pathlib import Path
from typing import Optional, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Pydantic Settings automatically reads from .env file and environment
    variables. Environment variables take precedence over .env values.
    All fields are validated at startup — the app will not start with
    invalid configuration.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    APP_NAME: str = "MuleTrace AI"
    APP_VERSION: str = "1.0.0-alpha"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # -------------------------------------------------------------------------
    # PostgreSQL (Supabase / Managed / Local)
    # -------------------------------------------------------------------------
    DATABASE_URL: Optional[str] = None
    DIRECT_URL: Optional[str] = None
    DATABASE_URL_SYNC: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "muletrace_db"
    POSTGRES_USER: str = "muletrace_user"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_ECHO: bool = False

    # -------------------------------------------------------------------------
    # Neo4j
    # -------------------------------------------------------------------------
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "changeme"
    NEO4J_DATABASE: str = "neo4j"

    # -------------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------------
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # -------------------------------------------------------------------------
    # Computed Properties
    # -------------------------------------------------------------------------
    @property
    def postgres_dsn(self) -> str:
        """Build async PostgreSQL connection string for SQLAlchemy.

        Prefers DIRECT_URL (port 5432 direct connection) or DATABASE_URL.
        Ensures postgresql+asyncpg:// driver prefix.
        """
        raw_url = self.DIRECT_URL or self.DATABASE_URL
        if raw_url:
            base_url = raw_url.split("?")[0] if "?" in raw_url else raw_url
            if base_url.startswith("postgresql://"):
                base_url = base_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif base_url.startswith("postgres://"):
                base_url = base_url.replace("postgres://", "postgresql+asyncpg://", 1)
            return base_url

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def postgres_dsn_sync(self) -> str:
        """Build sync PostgreSQL connection string for Alembic migrations.

        Prefers DIRECT_URL (Supabase migration port 5432) or DATABASE_URL_SYNC / DATABASE_URL.
        Ensures standard postgresql:// driver prefix for Alembic.
        """
        sync_url = self.DIRECT_URL or self.DATABASE_URL_SYNC or self.DATABASE_URL
        if sync_url:
            url = sync_url.split("?")[0] if "?" in sync_url else sync_url
            if url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
            elif url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url

        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV == "development"

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Ensure LOG_LEVEL is a valid Python logging level."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper_value = value.upper()
        if upper_value not in allowed:
            msg = f"LOG_LEVEL must be one of {allowed}, got '{value}'"
            raise ValueError(msg)
        return upper_value

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        """Ensure APP_ENV is a recognized environment name."""
        allowed = {"development", "staging", "production", "testing"}
        if value.lower() not in allowed:
            msg = f"APP_ENV must be one of {allowed}, got '{value}'"
            raise ValueError(msg)
        return value.lower()

    @field_validator("LOG_FORMAT")
    @classmethod
    def validate_log_format(cls, value: str) -> str:
        """Ensure LOG_FORMAT is either 'json' or 'text'."""
        allowed = {"json", "text"}
        if value.lower() not in allowed:
            msg = f"LOG_FORMAT must be one of {allowed}, got '{value}'"
            raise ValueError(msg)
        return value.lower()


# ---------------------------------------------------------------------------
# Singleton instance — import this throughout the application.
# ---------------------------------------------------------------------------
settings = Settings()
