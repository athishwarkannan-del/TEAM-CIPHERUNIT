"""
MuleTrace AI — Pytest Configuration & Fixtures.

Provides shared pytest fixtures including async_client for testing FastAPI endpoints.
"""

from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an AsyncClient instance bound to the FastAPI application.

    Yields:
        AsyncClient instance for executing async HTTP test requests.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
