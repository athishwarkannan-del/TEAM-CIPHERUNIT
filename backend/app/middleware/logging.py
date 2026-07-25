"""
MuleTrace AI — Logging Middleware.

Intercepts HTTP traffic and logs method, path, response status, latency, and request ID.
"""

from __future__ import annotations


import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("app.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP Access Logging Middleware."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", "unknown")

        response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "HTTP %s %s -> %d [%.2fms] (req_id: %s)",
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
            request_id,
        )

        response.headers["X-Process-Time-MS"] = f"{process_time_ms:.2f}"
        return response
