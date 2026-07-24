"""
MuleTrace AI — Analytics Repository.

Handles aggregation and time-series query operations for financial crime analytics.
"""

from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


class AnalyticsRepository:
    """Repository for execution of analytics, time-series, and channel breakdown queries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_channel_volume_breakdown(self) -> Sequence[tuple[str, int, float]]:
        """Group transaction counts and total amounts by channel (UPI, NEFT, IMPS, RTGS)."""
        stmt = (
            select(
                Transaction.channel,
                func.count(Transaction.id).label("txn_count"),
                func.coalesce(func.sum(Transaction.amount), 0.0).label("total_amount"),
            )
            .group_by(Transaction.channel)
            .order_by(func.sum(Transaction.amount).desc())
        )
        result = await self.session.execute(stmt)
        return result.all()
