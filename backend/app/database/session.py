"""
MuleTrace AI — Database Session Dependencies.

Provides FastAPI dependency injection functions that supply database
sessions to API routes. This is the ONLY module that routes should
use to obtain database access.

Architecture:
    Routes declare dependencies → FastAPI injects sessions automatically.
    Sessions are created per-request and cleaned up after the response.

    Example route:
        @router.get("/accounts")
        async def get_accounts(db: AsyncSession = Depends(get_db)):
            return await account_service.get_all(db)

Usage:
    from app.database.session import get_db, get_neo4j_session
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.neo4j import neo4j_manager
from app.database.postgres import async_session_factory

logger = logging.getLogger("app.database.session")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async PostgreSQL session for a single request.

    This is a FastAPI dependency. It creates a new session at the
    start of a request and ensures it is closed after the response
    is sent — even if an exception occurs.

    The session uses the following transaction strategy:
        - Autocommit is OFF — you must explicitly commit.
        - On success: commit is the caller's responsibility.
        - On exception: the session is rolled back and closed.

    Yields:
        AsyncSession: A SQLAlchemy async session.

    Raises:
        RuntimeError: If the session factory has not been initialized.

    Usage:
        @router.get("/accounts")
        async def list_accounts(db: AsyncSession = Depends(get_db)):
            ...
    """
    if async_session_factory is None:
        msg = (
            "Database session factory is not initialized. "
            "Ensure init_engine() was called during application startup."
        )
        raise RuntimeError(msg)

    session = async_session_factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_neo4j_session() -> AsyncGenerator:
    """Provide a Neo4j async session for a single request.

    This is a FastAPI dependency. It creates a Neo4j session
    and ensures cleanup after the request completes.

    Yields:
        neo4j.AsyncSession: A Neo4j async session.

    Raises:
        RuntimeError: If the Neo4j driver is not connected.

    Usage:
        @router.get("/graph")
        async def get_graph(neo4j: AsyncSession = Depends(get_neo4j_session)):
            result = await neo4j.run("MATCH (n:Account) RETURN n LIMIT 10")
    """
    async with neo4j_manager.get_session() as session:
        yield session
