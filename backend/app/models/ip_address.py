"""
MuleTrace AI — IP Address Model.

Represents IP addresses used during account operations.
Used for Shared IP and Impossible Travel pattern detection.
"""

from __future__ import annotations
from typing import Optional


import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class IPAddress(Base, TimestampMixin):
    """IP Address entity.

    Tracks IP geolocation, ISP, proxy/VPN status, and account associations.
    """

    __tablename__ = "ip_addresses"

    ip_str: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        index=True,
        comment="IPv4 or IPv6 address string",
    )
    isp: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Internet Service Provider",
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Geo city",
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Geo country",
    )
    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Geo latitude",
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Geo longitude",
    )
    is_vpn_or_proxy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indicates whether IP is a known VPN, proxy, or TOR exit node",
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last active timestamp for this IP",
    )
    associated_accounts_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Count of distinct accounts accessing from this IP",
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
        back_populates="ip_addresses",
    )

    def __repr__(self) -> str:
        return f"<IPAddress(ip={self.ip_str}, city={self.city}, vpn={self.is_vpn_or_proxy})>"
