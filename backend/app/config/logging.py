"""
MuleTrace AI — Logging Configuration.

Configures Python's built-in logging module for the entire application.
Called once during application startup via the lifespan handler.

Two output modes:
    - "json"  → Structured JSON logs for production (machine-parseable)
    - "text"  → Human-readable logs for local development

Usage:
    from app.config.logging import configure_logging
    configure_logging()  # Call once at startup
"""

import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for production environments.

    Outputs each log entry as a single JSON line, compatible with
    ELK Stack, CloudWatch, Datadog, and other log aggregation tools.

    Example output:
        {"timestamp":"2025-01-15T10:30:00Z","level":"INFO","logger":"app.services.dashboard","message":"Dashboard data loaded","request_id":"abc-123"}
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string."""
        import json

        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request_id if available (set by RequestIDMiddleware)
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        # Include exception info if present
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "message": str(record.exc_info[1]),
            }

        # Include extra fields passed via logger.info("msg", extra={...})
        for key in ("module", "funcName", "lineno"):
            log_entry[key] = getattr(record, key, None)

        return json.dumps(log_entry, default=str)


class TextFormatter(logging.Formatter):
    """Human-readable log formatter for local development.

    Example output:
        2025-01-15 10:30:00 | INFO     | app.services.dashboard | Dashboard data loaded
    """

    FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        super().__init__(fmt=self.FORMAT, datefmt=self.DATE_FORMAT)


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure the root logger for the entire application.

    This function should be called exactly once during application startup.
    It configures the root logger and sets appropriate formatters based
    on the environment.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Output format — "json" for production, "text" for development.
    """
    # Resolve the logging level from string to constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Select formatter based on configuration
    if log_format == "json":
        console_handler.setFormatter(JsonFormatter())
    else:
        console_handler.setFormatter(TextFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove any existing handlers to prevent duplicate logs on reload
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if log_level == "DEBUG" else logging.WARNING
    )
    logging.getLogger("neo4j").setLevel(logging.WARNING)

    # Log the configuration itself
    logger = logging.getLogger("app.config.logging")
    logger.info(
        "Logging configured — level=%s, format=%s",
        log_level,
        log_format,
    )
