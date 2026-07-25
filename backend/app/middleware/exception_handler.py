"""
MuleTrace AI — Global Exception Handlers.

Catches uncaught exceptions and domain errors, serializing them into standardized ErrorResponse JSON payloads.
"""

from __future__ import annotations


import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import MuleTraceException
from app.schemas.common import ErrorDetail, ErrorResponse

logger = logging.getLogger("app.middleware.exception_handler")


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with FastAPI application instance."""

    @app.exception_handler(MuleTraceException)
    async def domain_exception_handler(request: Request, exc: MuleTraceException) -> JSONResponse:
        logger.warning("Domain exception caught: %s (code: %s)", exc.message, exc.error_code)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                message=exc.message,
                error_code=exc.error_code,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            ErrorDetail(
                loc=[str(i) for i in err["loc"]],
                msg=err["msg"],
                type=err["type"],
            )
            for err in exc.errors()
        ]
        logger.warning("Validation error on %s: %s", request.url.path, details)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                success=False,
                message="Request payload validation failed",
                error_code="VALIDATION_ERROR",
                details=details,
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                success=False,
                message=str(exc.detail),
                error_code=f"HTTP_{exc.status_code}",
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                message="An unexpected internal server error occurred",
                error_code="INTERNAL_SERVER_ERROR",
            ).model_dump(),
        )
