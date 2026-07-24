"""
MuleTrace AI — Geo Intelligence Endpoints.

API endpoints for geographic analysis and impossible travel detection.
"""

from fastapi import APIRouter
from app.schemas.common import BaseResponse

router = APIRouter(prefix="/geo", tags=["Geo Intelligence"])


@router.get("", response_model=BaseResponse[dict])
async def get_geo_intelligence() -> BaseResponse[dict]:
    """Retrieve geo intelligence heatmaps and impossible travel markers."""
    return BaseResponse(
        success=True,
        message="Geospatial intelligence metrics fetched successfully",
        data={
            "impossible_travel_alerts": [
                {
                    "account_number": "XXXX9876",
                    "origin": "Mumbai",
                    "destination": "Delhi",
                    "distance_km": 1400,
                    "time_gap_minutes": 15,
                    "flagged": True,
                }
            ],
            "regional_clusters": [
                {"city": "Mumbai", "mule_count": 34, "lat": 19.0760, "lng": 72.8777},
                {"city": "Delhi", "mule_count": 28, "lat": 28.7041, "lng": 77.1025},
            ],
        },
    )
