"""
MuleTrace AI — Analytics Schemas.

Pydantic schemas for analytics queries, volume trends, channel breakdowns, and geo heatmaps.
"""

from __future__ import annotations


from pydantic import BaseModel, Field


class ChannelVolume(BaseModel):
    """Volume and transaction count per payment channel."""

    channel: str
    transaction_count: int
    total_amount_inr: float
    mule_percentage: float = 0.0


class TimeSeriesDataPoint(BaseModel):
    """Time-series entry for volume trends."""

    timestamp: str
    total_volume: float
    flagged_volume: float
    alert_count: int


class GeoCluster(BaseModel):
    """Geographic cluster point for heat maps."""

    city: str
    state: str
    latitude: float
    longitude: float
    active_mules_count: int
    total_alert_count: int


class AnalyticsOverviewResponse(BaseModel):
    """Complete analytics response structure."""

    time_series: list[TimeSeriesDataPoint] = Field(default_factory=list)
    channel_breakdown: list[ChannelVolume] = Field(default_factory=list)
    geo_clusters: list[GeoCluster] = Field(default_factory=list)
