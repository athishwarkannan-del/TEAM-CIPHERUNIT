"""
MuleTrace AI — Settings Configuration Unit Tests.

Tests configuration settings loading, computed properties, and validation rules.
"""

import pytest
from app.config.settings import Settings


def test_settings_defaults() -> None:
    """Test default application settings values."""
    test_settings = Settings()

    assert test_settings.APP_NAME == "MuleTrace AI"
    assert test_settings.APP_PORT == 8000
    assert test_settings.is_development is True or test_settings.is_production is False


def test_postgres_dsn_computation() -> None:
    """Test computed async and sync PostgreSQL DSN strings."""
    test_settings = Settings(
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_DB="test_db",
    )

    assert test_settings.postgres_dsn == "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
    assert test_settings.postgres_dsn_sync == "postgresql://test_user:test_password@localhost:5432/test_db"


def test_invalid_log_level_validation() -> None:
    """Test that invalid LOG_LEVEL raises ValueError during settings initialization."""
    with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
        Settings(LOG_LEVEL="INVALID_LEVEL")
