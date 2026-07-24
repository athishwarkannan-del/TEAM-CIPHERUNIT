"""
MuleTrace AI — Database Package.

Provides database connectivity for PostgreSQL (SQLAlchemy) and Neo4j.

Exports:
    Base            — SQLAlchemy declarative base (all models inherit this)
    TimestampMixin  — Adds UUID pk, created_at, updated_at, status to models
    init_engine     — Initialize PostgreSQL async engine (call at startup)
    dispose_engine  — Dispose PostgreSQL engine (call at shutdown)
    neo4j_manager   — Neo4j driver manager singleton
    get_db          — FastAPI dependency for PostgreSQL sessions
    get_neo4j_session — FastAPI dependency for Neo4j sessions
"""

from app.database.base import Base, TimestampMixin
from app.database.neo4j import neo4j_manager
from app.database.postgres import dispose_engine, init_engine
from app.database.session import get_db, get_neo4j_session

__all__ = [
    "Base",
    "TimestampMixin",
    "init_engine",
    "dispose_engine",
    "neo4j_manager",
    "get_db",
    "get_neo4j_session",
]
