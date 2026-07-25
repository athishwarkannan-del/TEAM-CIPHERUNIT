"""
MuleTrace AI — FastAPI Main Entrypoint.

Production-grade FastAPI application initialization with lifespan context manager,
logging setup, database initialization, CORS, middleware, and OpenAPI configuration.
"""

from __future__ import annotations


from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

from app.api.v1.router import api_v1_router
from app.config.constants import API_V1_PREFIX, APP_DESCRIPTION, APP_TITLE
from app.config.logging import configure_logging
from app.config.settings import settings
from app.database.neo4j import neo4j_manager
from app.database.postgres import dispose_engine, init_engine
from app.middleware.cors import setup_cors
from app.middleware.exception_handler import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown hooks."""
    # ── Startup ──────────────────────────────────────────────────────────
    configure_logging(log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    init_engine()
    await neo4j_manager.connect()

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    await neo4j_manager.disconnect()
    await dispose_engine()


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_url=f"{API_V1_PREFIX}/openapi.json",
    docs_url=f"{API_V1_PREFIX}/docs",
    redoc_url=f"{API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# ── Middleware Registration ──────────────────────────────────────────────
setup_cors(app)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
register_exception_handlers(app)

# Include master v1 API router under /api/v1
app.include_router(api_v1_router, prefix=API_V1_PREFIX)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint redirecting to docs summary."""
    return {
        "title": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{API_V1_PREFIX}/docs",
        "status": "healthy",
    }
