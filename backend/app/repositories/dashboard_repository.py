"""
MuleTrace AI — Dashboard Repository.

Provides aggregate statistical queries for the SOC Dashboard overview.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.alert import Alert
from app.models.transaction import Transaction


class DashboardRepository:
    """Repository executing high-level aggregate queries for the dashboard."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_24h_transaction_count(self) -> int:
        """Count total transactions executed in the last 24 hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        stmt = select(func.count(Transaction.id)).where(Transaction.timestamp >= cutoff)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_flagged_mule_count(self) -> int:
        """Count accounts marked as flagged mules."""
        stmt = select(func.count(Account.id)).where(Account.is_flagged_mule == True)  # noqa: E712
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_active_alerts_count(self) -> int:
        """Count unclosed alerts."""
        stmt = select(func.count(Alert.id)).where(
            Alert.alert_status.in_(["NEW", "UNDER_INVESTIGATION", "ESCALATED"])
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_total_volume_at_risk(self) -> float:
        """Sum total amount of transactions flagged with high risk."""
        stmt = select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
            Transaction.risk_score >= 80
        )
        result = await self.session.execute(stmt)
        return float(result.scalar_one())

    async def get_risk_distribution(self) -> dict[str, int]:
        """Group account counts by risk level."""
        stmt = select(Account.risk_level, func.count(Account.id)).group_by(Account.risk_level)
        result = await self.session.execute(stmt)
        rows = result.all()

        counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for level, count in rows:
            if level in counts:
                counts[level] = count
        return counts
