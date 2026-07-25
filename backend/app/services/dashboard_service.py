"""
MuleTrace AI — Dashboard Service.

Business logic service for assembling the SOC Investigation Dashboard overview.
"""

from __future__ import annotations


from app.repositories.alert_repository import AlertRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.alert import AlertRead
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    KPIOverview,
    PatternHitSummary,
    RiskDistribution,
)


class DashboardService:
    """Service orchestrating dashboard metrics and alerts overview."""

    def __init__(
        self,
        dashboard_repo: DashboardRepository,
        alert_repo: AlertRepository,
    ) -> None:
        self.dashboard_repo = dashboard_repo
        self.alert_repo = alert_repo

    async def get_dashboard_overview(self) -> DashboardOverviewResponse:
        """Assemble full dashboard response containing KPIs, risk breakdown, and recent alerts."""
        tx_count = await self.dashboard_repo.get_24h_transaction_count()
        mule_count = await self.dashboard_repo.get_flagged_mule_count()
        active_alerts = await self.dashboard_repo.get_active_alerts_count()
        vol_at_risk = await self.dashboard_repo.get_total_volume_at_risk()
        dist_counts = await self.dashboard_repo.get_risk_distribution()

        recent_alerts_orm = await self.alert_repo.get_multi(limit=5)
        recent_alerts = [AlertRead.model_validate(a) for a in recent_alerts_orm]

        # Top pattern hits mock summary if empty or based on active rules
        top_patterns = [
            PatternHitSummary(pattern_name="Mule Chain", hit_count=42, severity="CRITICAL"),
            PatternHitSummary(pattern_name="Fan-In Collector", hit_count=28, severity="HIGH"),
            PatternHitSummary(pattern_name="Shared Device", hit_count=19, severity="HIGH"),
            PatternHitSummary(pattern_name="High Velocity", hit_count=15, severity="MEDIUM"),
            PatternHitSummary(pattern_name="Smurfing (Structuring)", hit_count=11, severity="HIGH"),
        ]

        return DashboardOverviewResponse(
            kpis=KPIOverview(
                total_transactions_24h=tx_count,
                flagged_mule_accounts=mule_count,
                active_alerts_count=active_alerts,
                total_volume_at_risk_inr=vol_at_risk,
            ),
            risk_distribution=RiskDistribution(
                low=dist_counts.get("LOW", 0),
                medium=dist_counts.get("MEDIUM", 0),
                high=dist_counts.get("HIGH", 0),
                critical=dist_counts.get("CRITICAL", 0),
            ),
            top_patterns=top_patterns,
            recent_alerts=recent_alerts,
        )
