"""
MuleTrace AI — CORS Middleware Setup.

Configures Cross-Origin Resource Sharing (CORS) rules for frontend client connections.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings


def setup_cors(app: FastAPI) -> None:
    """Register CORSMiddleware with origins from settings."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
