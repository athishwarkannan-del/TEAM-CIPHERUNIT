"""
MuleTrace AI — PostgreSQL Connection Manager.

Creates and manages the async SQLAlchemy engine and session factory.
All database interactions flow through the session factory created here.

Architecture:
    - Engine is created once at application startup.
    - Session factory produces new AsyncSession instances per request.
    - Connection pooling is configured for production workloads.
    - dispose_engine() is called during application shutdown.

Usage:
    from app.database.postgres import async_session_factory, init_engine, dispose_engine
"""

import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import settings

logger = logging.getLogger("app.database.postgres")

# ---------------------------------------------------------------------------
# Engine — created lazily via init_engine(), used throughout the app.
# ---------------------------------------------------------------------------
_engine: AsyncEngine | None = None

# ---------------------------------------------------------------------------
# Session Factory — produces AsyncSession instances for each request.
# ---------------------------------------------------------------------------
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> AsyncEngine:
    """Initialize the async SQLAlchemy engine with connection pooling.

    This function is called once during application startup (via lifespan).
    It creates the engine with production-grade pool settings.

    Returns:
        The initialized AsyncEngine instance.
    """
    global _engine, async_session_factory

    logger.info(
        "Initializing PostgreSQL engine — DSN=%s",
        settings.postgres_dsn.split("@")[-1] if "@" in settings.postgres_dsn else settings.postgres_dsn,
    )

    # Configure SSL mode for cloud PostgreSQL providers (Supabase / Neon / RDS)
    connect_args = {}
    if "supabase.com" in settings.postgres_dsn or "pooler" in settings.postgres_dsn or settings.DATABASE_URL:
        connect_args["ssl"] = "require"

    _engine = create_async_engine(
        settings.postgres_dsn,
        echo=settings.POSTGRES_ECHO,
        # Connection pool settings for production
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections every 30 minutes
        pool_pre_ping=True,  # Verify connections before use
        connect_args=connect_args,
    )

    async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    logger.info("PostgreSQL engine initialized successfully")
    return _engine


def get_engine() -> AsyncEngine:
    """Get the current async engine instance.

    Raises:
        RuntimeError: If the engine has not been initialized.
    """
    if _engine is None:
        msg = (
            "PostgreSQL engine is not initialized. "
            "Call init_engine() during application startup."
        )
        raise RuntimeError(msg)
    return _engine


async def dispose_engine() -> None:
    """Dispose of the engine and close all pooled connections.

    Called during application shutdown to cleanly release resources.
    """
    global _engine, async_session_factory

    if _engine is not None:
        logger.info("Disposing PostgreSQL engine")
        await _engine.dispose()
        _engine = None
        async_session_factory = None
        logger.info("PostgreSQL engine disposed")
