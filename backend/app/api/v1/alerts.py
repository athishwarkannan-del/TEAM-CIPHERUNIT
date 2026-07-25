"""
MuleTrace AI — Alerts Endpoints.

API endpoints for suspicious activity alert triage and management.
"""

from __future__ import annotations
from typing import Optional


import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_alert_service
from app.schemas.alert import AlertCreate, AlertRead, AlertTriageUpdate
from app.schemas.common import BaseResponse, PaginatedResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=PaginatedResponse[AlertRead])
async def list_alerts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    severity: Optional[str] = Query(default=None),
    alert_status: Optional[str] = Query(default=None),
    pattern_type: Optional[str] = Query(default=None),
    account_id: Optional[uuid.UUID] = Query(default=None),
    service: AlertService = Depends(get_alert_service),
) -> PaginatedResponse[AlertRead]:
    """Retrieve suspicious activity alert queue with severity and triage status filters."""
    return await service.get_alerts_paginated(
        page=page,
        page_size=page_size,
        severity=severity,
        alert_status=alert_status,
        pattern_type=pattern_type,
        account_id=account_id,
    )


@router.get("/{alert_id}", response_model=BaseResponse[AlertRead])
async def get_alert_by_id(
    alert_id: uuid.UUID,
    service: AlertService = Depends(get_alert_service),
) -> BaseResponse[AlertRead]:
    """Fetch alert details by UUID."""
    alert = await service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' not found",
        )
    return BaseResponse(
        success=True,
        message="Alert details fetched successfully",
        data=alert,
    )


@router.post("", response_model=BaseResponse[AlertRead], status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: AlertCreate,
    service: AlertService = Depends(get_alert_service),
) -> BaseResponse[AlertRead]:
    """Generate a new suspicious activity alert."""
    created = await service.create_alert(payload)
    return BaseResponse(
        success=True,
        message="Alert created successfully",
        data=created,
    )


@router.patch("/{alert_id}/triage", response_model=BaseResponse[AlertRead])
async def triage_alert(
    alert_id: uuid.UUID,
    payload: AlertTriageUpdate,
    service: AlertService = Depends(get_alert_service),
) -> BaseResponse[AlertRead]:
    """Update triage status (e.g. ESCALATED, CLOSED_FALSE_POSITIVE, UNDER_INVESTIGATION)."""
    updated = await service.triage_alert(alert_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' not found",
        )
    return BaseResponse(
        success=True,
        message="Alert triage status updated successfully",
        data=updated,
    )
