"""
MuleTrace AI — Health Check Endpoint.

Returns system health, status, and uptime metrics.
"""

from __future__ import annotations


from fastapi import APIRouter
from app.schemas.common import BaseResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=BaseResponse[dict[str, str]])
async def health_check() -> BaseResponse[dict[str, str]]:
    """System health check endpoint."""
    return BaseResponse(
        success=True,
        message="MuleTrace AI Backend Operational",
        data={
            "status": "healthy",
            "version": "1.0.0-alpha",
            "environment": "development",
        },
    )
