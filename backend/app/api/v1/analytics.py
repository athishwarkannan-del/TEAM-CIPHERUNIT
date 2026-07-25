"""
MuleTrace AI — Analytics Endpoints.

API endpoints for financial crime visual analytics.
"""

from __future__ import annotations


from fastapi import APIRouter, Depends
from app.api.dependencies import get_analytics_service
from app.schemas.analytics import AnalyticsOverviewResponse
from app.schemas.common import BaseResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=BaseResponse[AnalyticsOverviewResponse])
async def get_analytics_overview(
    service: AnalyticsService = Depends(get_analytics_service),
) -> BaseResponse[AnalyticsOverviewResponse]:
    """Retrieve financial crime analytics (channel distributions, volume trends, geo clusters)."""
    data = await service.get_analytics_overview()
    return BaseResponse(
        success=True,
        message="Analytics data fetched successfully",
        data=data,
    )
