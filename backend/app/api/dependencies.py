"""
MuleTrace AI — API Dependencies.

FastAPI dependency providers for Repositories and Services.
Constructs service instances per-request with injected AsyncSession database handles.
"""

from __future__ import annotations


from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.account_repository import AccountRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.account_service import AccountService
from app.services.alert_service import AlertService
from app.services.analytics_service import AnalyticsService
from app.services.dashboard_service import DashboardService
from app.services.report_service import ReportService
from app.services.transaction_service import TransactionService


# ── Repository Dependencies ──────────────────────────────────────────────

def get_account_repository(db: AsyncSession = Depends(get_db)) -> AccountRepository:
    return AccountRepository(db)


def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db)


def get_dashboard_repository(db: AsyncSession = Depends(get_db)) -> DashboardRepository:
    return DashboardRepository(db)


def get_analytics_repository(db: AsyncSession = Depends(get_db)) -> AnalyticsRepository:
    return AnalyticsRepository(db)


def get_alert_repository(db: AsyncSession = Depends(get_db)) -> AlertRepository:
    return AlertRepository(db)


def get_report_repository(db: AsyncSession = Depends(get_db)) -> ReportRepository:
    return ReportRepository(db)


# ── Service Dependencies ─────────────────────────────────────────────────

def get_dashboard_service(
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repository),
    alert_repo: AlertRepository = Depends(get_alert_repository),
) -> DashboardService:
    return DashboardService(dashboard_repo=dashboard_repo, alert_repo=alert_repo)


def get_account_service(
    account_repo: AccountRepository = Depends(get_account_repository),
) -> AccountService:
    return AccountService(account_repo=account_repo)


def get_transaction_service(
    tx_repo: TransactionRepository = Depends(get_transaction_repository),
) -> TransactionService:
    return TransactionService(transaction_repo=tx_repo)


def get_alert_service(
    alert_repo: AlertRepository = Depends(get_alert_repository),
) -> AlertService:
    return AlertService(alert_repo=alert_repo)


def get_analytics_service(
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository),
) -> AnalyticsService:
    return AnalyticsService(analytics_repo=analytics_repo)


def get_report_service(
    report_repo: ReportRepository = Depends(get_report_repository),
) -> ReportService:
    return ReportService(report_repo=report_repo)


def get_victim_complaint_service(
    report_repo: ReportRepository = Depends(get_report_repository),
) -> "VictimComplaintService":
    from app.services.victim_complaint_service import VictimComplaintService
    return VictimComplaintService(report_repo=report_repo)
