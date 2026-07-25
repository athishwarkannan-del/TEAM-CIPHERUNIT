"""
MuleTrace AI — Investigations Endpoints.

API endpoints for investigation case management and evidence tracking.
"""

from __future__ import annotations


from fastapi import APIRouter
from app.schemas.common import BaseResponse

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("", response_model=BaseResponse[dict])
async def list_investigations() -> BaseResponse[dict]:
    """List active investigation cases and assigned analyst workloads."""
    return BaseResponse(
        success=True,
        message="Active investigation cases retrieved successfully",
        data={
            "cases": [
                {
                    "case_number": "CAS-2025-0045",
                    "title": "Mule Ring Operation — Western Region",
                    "priority": "CRITICAL",
                    "case_status": "IN_PROGRESS",
                    "assigned_investigator_id": "INV-882",
                    "alerts_count": 8,
                }
            ]
        },
    )
