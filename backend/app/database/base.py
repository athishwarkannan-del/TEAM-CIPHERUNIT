"""
MuleTrace AI — SQLAlchemy Declarative Base & Common Mixins.

Defines the base class that ALL ORM models inherit from, plus a
TimestampMixin that automatically adds UUID primary key, created_at,
updated_at, and status columns to every table.

Architecture:
    Every model in app/models/ inherits from Base.
    Every model automatically gets: id (UUID), created_at, updated_at, status.
    Alembic discovers all models through Base.metadata.

Usage:
    from app.database.base import Base, TimestampMixin

    class Account(Base, TimestampMixin):
        __tablename__ = "accounts"
        account_number = Column(String(20), unique=True, nullable=False)
"""

from __future__ import annotations


import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class.

    All ORM models must inherit from this class.
    Alembic uses Base.metadata to auto-detect schema changes.
    """

    pass


class TimestampMixin:
    """Mixin that adds standard audit columns to every model.

    Columns added:
        id          — UUID v4 primary key (generated server-side)
        created_at  — Timestamp of row creation (UTC, immutable)
        updated_at  — Timestamp of last update (UTC, auto-updated)
        status      — Record status (active, inactive, deleted, flagged, etc.)

    These columns exist on EVERY table in the MuleTrace AI database,
    providing consistent audit trails for a financial crime platform.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        index=True,
        comment="Unique identifier (UUID v4)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        nullable=False,
        index=True,
        comment="Record creation timestamp (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Last update timestamp (UTC)",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        server_default=text("'active'"),
        nullable=False,
        index=True,
        comment="Record status (active, inactive, deleted, flagged, frozen, under_review)",
    )
