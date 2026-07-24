"""
MuleTrace AI — SOC Dashboard Endpoint Tests.

Tests Dashboard Overview API payload structure and response schema.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_dashboard_overview(async_client: AsyncClient) -> None:
    """Test GET /api/v1/dashboard returns 200 OK with KPIs and risk distribution."""
    response = await async_client.get("/api/v1/dashboard")

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert "data" in payload

    dashboard_data = payload["data"]
    assert "kpis" in dashboard_data
    assert "risk_distribution" in dashboard_data
    assert "top_patterns" in dashboard_data
    assert "recent_alerts" in dashboard_data

    kpis = dashboard_data["kpis"]
    assert "total_transactions_24h" in kpis
    assert "flagged_mule_accounts" in kpis
    assert "active_alerts_count" in kpis
    assert "total_volume_at_risk_inr" in kpis

    risk_dist = dashboard_data["risk_distribution"]
    assert "low" in risk_dist
    assert "medium" in risk_dist
    assert "high" in risk_dist
    assert "critical" in risk_dist
