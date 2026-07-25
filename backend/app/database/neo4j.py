"""
MuleTrace AI — Neo4j Connection Manager.

Manages the Neo4j async driver lifecycle for graph database operations.
The graph engine (engines/graph/) uses Neo4j for transaction graph
construction, community detection, and path analysis.

Architecture:
    - Driver is created once at application startup.
    - Sessions are created per-request via get_session().
    - Driver is closed during application shutdown.
    - All graph queries go through this module.

Usage:
    from app.database.neo4j import neo4j_manager

    async with neo4j_manager.get_session() as session:
        result = await session.run("MATCH (n) RETURN n LIMIT 10")
"""

from __future__ import annotations


import logging
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from app.config.settings import settings

logger = logging.getLogger("app.database.neo4j")


class Neo4jManager:
    """Manages the Neo4j async driver lifecycle.

    This class follows the singleton pattern — a single instance
    (neo4j_manager) is created at module level and shared across
    the application.

    The Neo4j driver handles its own internal connection pooling,
    so we only need one driver instance per application.
    """

    def __init__(self) -> None:
        self._driver: Optional[AsyncDriver] = None

    async def connect(self) -> None:
        """Initialize the Neo4j async driver.

        Called once during application startup via the lifespan handler.
        Verifies connectivity by running a test query.
        """
        logger.info(
            "Connecting to Neo4j — uri=%s, user=%s",
            settings.NEO4J_URI,
            settings.NEO4J_USER,
        )

        self._driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            max_connection_pool_size=50,
            connection_acquisition_timeout=30.0,
        )

        # Verify connectivity
        try:
            await self._driver.verify_connectivity()
            server_info = await self._driver.get_server_info()
            logger.info(
                "Neo4j connected — server=%s, protocol=%s",
                server_info.agent,
                server_info.protocol_version,
            )
        except Exception as e:
            logger.warning(
                "Neo4j connectivity check failed (%s) — graph features will be unavailable. "
                "Ensure Neo4j is running at %s",
                e,
                settings.NEO4J_URI,
            )

    async def disconnect(self) -> None:
        """Close the Neo4j driver and release all connections.

        Called during application shutdown via the lifespan handler.
        """
        if self._driver is not None:
            logger.info("Disconnecting from Neo4j")
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j driver closed")

    @property
    def driver(self) -> AsyncDriver:
        """Get the current Neo4j driver instance.

        Raises:
            RuntimeError: If the driver has not been initialized.
        """
        if self._driver is None:
            msg = (
                "Neo4j driver is not initialized. "
                "Call neo4j_manager.connect() during application startup."
            )
            raise RuntimeError(msg)
        return self._driver

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a Neo4j async session as a context manager.

        Yields:
            An AsyncSession bound to the configured database.
        """
        # For Neo4j AuraDB cloud instances, omit explicit database name to use default database
        if "databases.neo4j.io" in settings.NEO4J_URI:
            session = self.driver.session()
        else:
            session = self.driver.session(database=settings.NEO4J_DATABASE)

        try:
            yield session
        finally:
            await session.close()

    @property
    def is_connected(self) -> bool:
        """Check if the Neo4j driver is initialized."""
        return self._driver is not None


# Singleton instance — import this throughout the application.
neo4j_manager = Neo4jManager()
