"""
MuleTrace AI — Health Check Endpoint Tests.

Tests system status and health endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient) -> None:
    """Test GET /api/v1/health returns 200 OK with healthy status."""
    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "data" in data
    assert data["data"]["status"] == "healthy"
    assert "version" in data["data"]


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient) -> None:
    """Test GET / root endpoint returns application metadata."""
    response = await async_client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "docs" in data
