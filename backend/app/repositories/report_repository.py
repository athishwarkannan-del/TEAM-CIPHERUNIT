"""
MuleTrace AI — Report Repository.

Handles database operations for compliance Report entities.
"""

import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report


class ReportRepository:
    """Repository managing Report database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, report_id: uuid.UUID) -> Report | None:
        """Fetch report by UUID."""
        stmt = select(Report).where(Report.id == report_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(self, report_number: str) -> Report | None:
        """Fetch report by report reference number."""
        stmt = select(Report).where(Report.report_number == report_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 20,
        report_type: str | None = None,
        case_id: uuid.UUID | None = None,
    ) -> Sequence[Report]:
        """Fetch paginated reports."""
        stmt = select(Report)

        if report_type:
            stmt = stmt.where(Report.report_type == report_type)
        if case_id:
            stmt = stmt.where(Report.case_id == case_id)

        stmt = stmt.offset(skip).limit(limit).order_by(Report.generated_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(
        self,
        report_type: str | None = None,
        case_id: uuid.UUID | None = None,
    ) -> int:
        """Count total reports."""
        stmt = select(func.count(Report.id))

        if report_type:
            stmt = stmt.where(Report.report_type == report_type)
        if case_id:
            stmt = stmt.where(Report.case_id == case_id)

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, report: Report) -> Report:
        """Persist a new report."""
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report
