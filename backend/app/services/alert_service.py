"""
MuleTrace AI — Alert Service.

Business logic service for managing suspicious activity alerts and triage workflow.
"""

from __future__ import annotations
from typing import Optional


import uuid
from app.models.alert import Alert
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertCreate, AlertRead, AlertTriageUpdate
from app.schemas.common import PaginatedResponse, PaginationMeta


class AlertService:
    """Service orchestrating alert triage workflow and notifications."""

    def __init__(self, alert_repo: AlertRepository) -> None:
        self.alert_repo = alert_repo

    async def get_alert_by_id(self, alert_id: uuid.UUID) -> Optional[AlertRead]:
        """Fetch alert by UUID."""
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            return None
        return AlertRead.model_validate(alert)

    async def get_alerts_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        severity: Optional[str] = None,
        alert_status: Optional[str] = None,
        pattern_type: Optional[str] = None,
        account_id: Optional[uuid.UUID] = None,
    ) -> PaginatedResponse[AlertRead]:
        """Fetch paginated alert queue."""
        skip = (page - 1) * page_size
        items = await self.alert_repo.get_multi(
            skip=skip,
            limit=page_size,
            severity=severity,
            alert_status=alert_status,
            pattern_type=pattern_type,
            account_id=account_id,
        )
        total_items = await self.alert_repo.count(
            severity=severity,
            alert_status=alert_status,
            pattern_type=pattern_type,
            account_id=account_id,
        )

        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        alert_reads = [AlertRead.model_validate(item) for item in items]

        return PaginatedResponse(
            data=alert_reads,
            pagination=PaginationMeta(
                total_items=total_items,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
        )

    async def create_alert(self, payload: AlertCreate) -> AlertRead:
        """Generate new alert."""
        data = payload.model_dump()
        alert_obj = Alert(**data)
        created = await self.alert_repo.create(alert_obj)
        return AlertRead.model_validate(created)

    async def triage_alert(self, alert_id: uuid.UUID, payload: AlertTriageUpdate) -> Optional[AlertRead]:
        """Update triage status of an alert."""
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            return None

        alert.alert_status = payload.alert_status
        if payload.case_id:
            alert.case_id = payload.case_id

        updated = await self.alert_repo.update(alert)
        return AlertRead.model_validate(updated)
