"""
MuleTrace AI — Alert Repository.

Database operations for suspicious activity Alert entities.
"""

import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert


class AlertRepository:
    """Repository managing Alert database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, alert_id: uuid.UUID) -> Alert | None:
        """Fetch alert by UUID."""
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(self, alert_number: str) -> Alert | None:
        """Fetch alert by alert reference string."""
        stmt = select(Alert).where(Alert.alert_number == alert_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 20,
        severity: str | None = None,
        alert_status: str | None = None,
        pattern_type: str | None = None,
        account_id: uuid.UUID | None = None,
    ) -> Sequence[Alert]:
        """Fetch paginated alerts with filtering."""
        stmt = select(Alert)

        if severity:
            stmt = stmt.where(Alert.severity == severity)
        if alert_status:
            stmt = stmt.where(Alert.alert_status == alert_status)
        if pattern_type:
            stmt = stmt.where(Alert.pattern_type == pattern_type)
        if account_id:
            stmt = stmt.where(Alert.account_id == account_id)

        stmt = stmt.offset(skip).limit(limit).order_by(Alert.triggered_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(
        self,
        severity: str | None = None,
        alert_status: str | None = None,
        pattern_type: str | None = None,
        account_id: uuid.UUID | None = None,
    ) -> int:
        """Count total alerts matching criteria."""
        stmt = select(func.count(Alert.id))

        if severity:
            stmt = stmt.where(Alert.severity == severity)
        if alert_status:
            stmt = stmt.where(Alert.alert_status == alert_status)
        if pattern_type:
            stmt = stmt.where(Alert.pattern_type == pattern_type)
        if account_id:
            stmt = stmt.where(Alert.account_id == account_id)

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, alert: Alert) -> Alert:
        """Persist new alert."""
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def update(self, alert: Alert) -> Alert:
        """Save updates to alert."""
        await self.session.commit()
        await self.session.refresh(alert)
        return alert
