"""
MuleTrace AI — Schemas Package.

Exports all Pydantic v2 schemas for API validation and serialization.
"""

from __future__ import annotations


from app.schemas.account import (
    AccountCreate,
    AccountRead,
    AccountRiskSummary,
    AccountUpdate,
)
from app.schemas.alert import (
    AlertCreate,
    AlertRead,
    AlertTriageUpdate,
)
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    ChannelVolume,
    GeoCluster,
    TimeSeriesDataPoint,
)
from app.schemas.common import (
    BaseResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    PaginationParams,
)
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    KPIOverview,
    PatternHitSummary,
    RiskDistribution,
)
from app.schemas.report import (
    ReportGenerateRequest,
    ReportRead,
)
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilterParams,
    TransactionRead,
)

__all__ = [
    "BaseResponse",
    "PaginationParams",
    "PaginationMeta",
    "PaginatedResponse",
    "ErrorDetail",
    "ErrorResponse",
    "AccountCreate",
    "AccountUpdate",
    "AccountRead",
    "AccountRiskSummary",
    "TransactionCreate",
    "TransactionRead",
    "TransactionFilterParams",
    "KPIOverview",
    "RiskDistribution",
    "PatternHitSummary",
    "DashboardOverviewResponse",
    "ChannelVolume",
    "TimeSeriesDataPoint",
    "GeoCluster",
    "AnalyticsOverviewResponse",
    "AlertCreate",
    "AlertTriageUpdate",
    "AlertRead",
    "ReportGenerateRequest",
    "ReportRead",
]
