"""
MuleTrace AI — Report Service.

Business logic service for regulatory compliance report generation (STR/CTR).
"""

from __future__ import annotations
from typing import Optional


import uuid
from app.models.report import Report
from app.repositories.report_repository import ReportRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.report import ReportGenerateRequest, ReportRead


class ReportService:
    """Service handling compliance report requests."""

    def __init__(self, report_repo: ReportRepository) -> None:
        self.report_repo = report_repo

    async def get_report_by_id(self, report_id: uuid.UUID) -> Optional[ReportRead]:
        """Fetch report by UUID."""
        report = await self.report_repo.get_by_id(report_id)
        if not report:
            return None
        return ReportRead.model_validate(report)

    async def get_reports_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        report_type: Optional[str] = None,
        case_id: Optional[uuid.UUID] = None,
    ) -> PaginatedResponse[ReportRead]:
        """Fetch paginated report list."""
        skip = (page - 1) * page_size
        items = await self.report_repo.get_multi(
            skip=skip,
            limit=page_size,
            report_type=report_type,
            case_id=case_id,
        )
        total_items = await self.report_repo.count(
            report_type=report_type,
            case_id=case_id,
        )

        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        report_reads = [ReportRead.model_validate(item) for item in items]

        return PaginatedResponse(
            data=report_reads,
            pagination=PaginationMeta(
                total_items=total_items,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
        )

    async def generate_report(self, payload: ReportGenerateRequest) -> ReportRead:
        """Generate regulatory compliance report artifact."""
        report_num = f"{payload.report_type}-2025-{uuid.uuid4().hex[:6].upper()}"
        summary = (
            f"Regulatory {payload.report_type} compliance report generated automatically for investigation. "
            f"{payload.summary_notes or ''}"
        )

        report_obj = Report(
            report_number=report_num,
            report_type=payload.report_type,
            title=payload.title,
            case_id=payload.case_id,
            file_path=f"/exports/reports/{report_num}.pdf",
            summary_text=summary,
        )
        created = await self.report_repo.create(report_obj)
        return ReportRead.model_validate(created)
