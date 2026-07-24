"""
MuleTrace AI — API v1 Master Router.

Combines all v1 sub-routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.accounts import router as accounts_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.geo import router as geo_router
from app.api.v1.graph import router as graph_router
from app.api.v1.health import router as health_router
from app.api.v1.investigations import router as investigations_router
from app.api.v1.reports import router as reports_router
from app.api.v1.transactions import router as transactions_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(accounts_router)
api_v1_router.include_router(transactions_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(graph_router)
api_v1_router.include_router(geo_router)
api_v1_router.include_router(investigations_router)
api_v1_router.include_router(reports_router)
