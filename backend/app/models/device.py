"""
MuleTrace AI — Device Model.

Represents physical devices used to access bank accounts.
Critical for Shared Device pattern detection.
"""

from __future__ import annotations
from typing import Optional


import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Device(Base, TimestampMixin):
    """Device entity.

    Tracks hardware identifiers, OS, app version, and associated accounts
    to identify device sharing across multiple suspected mule accounts.
    """

    __tablename__ = "devices"

    device_fingerprint: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Unique hardware/browser fingerprint",
    )
    device_model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Device brand/model (e.g. Samsung Galaxy S23)",
    )
    os_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Operating system & version",
    )
    app_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Banking app version",
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last active timestamp for this device",
    )
    shared_account_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Number of distinct accounts linked to this device",
    )

    # ── Foreign Keys ──────────────────────────────────────────────────
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Associated account ID",
    )

    # ── Relationships ──────────────────────────────────────────────────
    account: Mapped["Account"] = relationship(  # noqa: F821
        "Account",
        back_populates="devices",
    )

    def __repr__(self) -> str:
        return f"<Device(fingerprint={self.device_fingerprint}, model={self.device_model})>"
