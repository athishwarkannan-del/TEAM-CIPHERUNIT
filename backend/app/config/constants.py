"""
MuleTrace AI — Application Constants.

Static, application-wide values that do NOT come from environment variables.
These are architectural decisions that remain consistent across all environments.

Usage:
    from app.config.constants import API_V1_PREFIX, DEFAULT_PAGE_SIZE
"""

from __future__ import annotations


# -----------------------------------------------------------------------------
# API Versioning
# -----------------------------------------------------------------------------
API_V1_PREFIX: str = "/api/v1"

# -----------------------------------------------------------------------------
# Pagination
# -----------------------------------------------------------------------------
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100
MIN_PAGE_SIZE: int = 1

# -----------------------------------------------------------------------------
# Date & Time Formats
# -----------------------------------------------------------------------------
DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT: str = "%Y-%m-%d"
TIME_FORMAT: str = "%H:%M:%S"

# -----------------------------------------------------------------------------
# Risk Scoring
# -----------------------------------------------------------------------------
RISK_SCORE_MIN: int = 0
RISK_SCORE_MAX: int = 100
RISK_LEVEL_LOW_THRESHOLD: int = 30
RISK_LEVEL_MEDIUM_THRESHOLD: int = 60
RISK_LEVEL_HIGH_THRESHOLD: int = 80
RISK_LEVEL_CRITICAL_THRESHOLD: int = 90

# -----------------------------------------------------------------------------
# Transaction Channels
# -----------------------------------------------------------------------------
CHANNEL_UPI: str = "UPI"
CHANNEL_NEFT: str = "NEFT"
CHANNEL_IMPS: str = "IMPS"
CHANNEL_RTGS: str = "RTGS"

SUPPORTED_CHANNELS: list[str] = [
    CHANNEL_UPI,
    CHANNEL_NEFT,
    CHANNEL_IMPS,
    CHANNEL_RTGS,
]

# -----------------------------------------------------------------------------
# Currency
# -----------------------------------------------------------------------------
DEFAULT_CURRENCY: str = "INR"
CTR_THRESHOLD_AMOUNT: float = 1_000_000.00  # ₹10 Lakh — Cash Transaction Report
STR_THRESHOLD_AMOUNT: float = 50_000.00  # ₹50K — Suspicious threshold baseline

# -----------------------------------------------------------------------------
# Alert Configuration
# -----------------------------------------------------------------------------
MAX_ALERTS_PER_PAGE: int = 50
ALERT_AUTO_ESCALATION_HOURS: int = 24

# -----------------------------------------------------------------------------
# Graph Engine
# -----------------------------------------------------------------------------
MAX_GRAPH_DEPTH: int = 10
MAX_GRAPH_NODES_DISPLAY: int = 500
DEFAULT_COMMUNITY_ALGORITHM: str = "louvain"

# -----------------------------------------------------------------------------
# Application Metadata
# -----------------------------------------------------------------------------
APP_TITLE: str = "MuleTrace AI"
APP_DESCRIPTION: str = (
    "Cross-Channel Mule Account Detection & Financial Crime Investigation Platform. "
    "AI-powered graph intelligence for banking fraud investigation."
)
APP_CONTACT: dict[str, str] = {
    "name": "Team CipherUnit",
    "url": "https://github.com/athishwarkannan-del/TEAM-CIPHERUNIT",
}
APP_LICENSE: dict[str, str] = {
    "name": "AGPL-3.0",
    "url": "https://www.gnu.org/licenses/agpl-3.0.html",
}
