"""
MuleTrace AI — Dashboard Schemas.

Pydantic schemas for the main SOC Investigation Dashboard overview and metrics.
"""

from __future__ import annotations


from pydantic import BaseModel, Field
from app.schemas.alert import AlertRead


class KPIOverview(BaseModel):
    """High-level system KPIs for SOC Dashboard."""

    total_transactions_24h: int = Field(default=0, description="Total transaction volume in last 24h")
    flagged_mule_accounts: int = Field(default=0, description="Total active flagged mule accounts")
    active_alerts_count: int = Field(default=0, description="Count of open unhandled alerts")
    total_volume_at_risk_inr: float = Field(default=0.0, description="Total flagged transaction value")


class RiskDistribution(BaseModel):
    """Distribution of monitored accounts across risk levels."""

    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class PatternHitSummary(BaseModel):
    """Summary of fraud pattern matches."""

    pattern_name: str
    hit_count: int
    severity: str


class DashboardOverviewResponse(BaseModel):
    """Complete response payload for GET /api/v1/dashboard."""

    kpis: KPIOverview
    risk_distribution: RiskDistribution
    top_patterns: list[PatternHitSummary] = Field(default_factory=list)
    recent_alerts: list[AlertRead] = Field(default_factory=list)
