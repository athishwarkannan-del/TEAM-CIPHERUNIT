"""
MuleTrace AI — Dashboard Endpoint.

Serves the main SOC Investigation Dashboard payload.
"""

from __future__ import annotations


from fastapi import APIRouter, Depends
from app.api.dependencies import get_dashboard_service
from app.schemas.common import BaseResponse
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=BaseResponse[DashboardOverviewResponse])
async def get_dashboard_overview(
    service: DashboardService = Depends(get_dashboard_service),
) -> BaseResponse[DashboardOverviewResponse]:
    """Retrieve SOC Investigation Dashboard overview metrics, KPIs, and recent alerts."""
    data = await service.get_dashboard_overview()
    return BaseResponse(
        success=True,
        message="Dashboard overview fetched successfully",
        data=data,
    )
