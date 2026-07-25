"""
MuleTrace AI — Request ID Middleware.

Generates or forwards a unique X-Request-ID header for every HTTP request.
Enables distributed tracing across log aggregators.
"""

from __future__ import annotations


import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware attaching X-Request-ID header to request state and response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
