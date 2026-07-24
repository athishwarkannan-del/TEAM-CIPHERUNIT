"""
MuleTrace AI — Reports Endpoints.

API endpoints for STR/CTR compliance report generation and retrieval.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_report_service
from app.schemas.common import BaseResponse, PaginatedResponse
from app.schemas.report import ReportGenerateRequest, ReportRead
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Compliance Reports"])


@router.get("", response_model=PaginatedResponse[ReportRead])
async def list_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    report_type: str | None = Query(default=None),
    case_id: uuid.UUID | None = Query(default=None),
    service: ReportService = Depends(get_report_service),
) -> PaginatedResponse[ReportRead]:
    """Retrieve list of generated STR/CTR regulatory compliance reports."""
    return await service.get_reports_paginated(
        page=page,
        page_size=page_size,
        report_type=report_type,
        case_id=case_id,
    )


@router.get("/{report_id}", response_model=BaseResponse[ReportRead])
async def get_report_by_id(
    report_id: uuid.UUID,
    service: ReportService = Depends(get_report_service),
) -> BaseResponse[ReportRead]:
    """Fetch report details by UUID."""
    report = await service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found",
        )
    return BaseResponse(
        success=True,
        message="Report details fetched successfully",
        data=report,
    )


@router.post("", response_model=BaseResponse[ReportRead], status_code=status.HTTP_201_CREATED)
async def generate_report(
    payload: ReportGenerateRequest,
    service: ReportService = Depends(get_report_service),
) -> BaseResponse[ReportRead]:
    """Trigger regulatory compliance report (STR / CTR) generation."""
    created = await service.generate_report(payload)
    return BaseResponse(
        success=True,
        message="Report generated successfully",
        data=created,
    )
