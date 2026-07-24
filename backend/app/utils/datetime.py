"""
MuleTrace AI — Datetime Helper Utilities.

Standardized UTC timezone handling, ISO-8601 formatting, and duration math.
"""

from datetime import datetime, timedelta, timezone


def now_utc() -> datetime:
    """Get current timestamp in timezone-aware UTC.

    Returns:
        datetime object with UTC timezone.
    """
    return datetime.now(timezone.utc)


def format_iso(dt: datetime) -> str:
    """Format datetime object into ISO-8601 string.

    Args:
        dt: Datetime object.

    Returns:
        ISO formatted string (e.g. '2025-01-15T10:30:00Z').
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def parse_iso(iso_str: str) -> datetime:
    """Parse ISO-8601 string into timezone-aware UTC datetime object.

    Args:
        iso_str: ISO string.

    Returns:
        UTC datetime object.
    """
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def get_time_window_start(hours: int = 24) -> datetime:
    """Get UTC timestamp for N hours ago from current time.

    Args:
        hours: Number of hours in the past.

    Returns:
        UTC datetime object marking the start of the time window.
    """
    return now_utc() - timedelta(hours=hours)
