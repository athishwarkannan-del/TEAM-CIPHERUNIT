"""
MuleTrace AI — Transaction Model.

Represents financial transactions across channels (UPI, NEFT, IMPS, RTGS).
Stores amounts, channels, timestamps, sender/receiver references, and risk indicators.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    """Financial Transaction entity.

    Tracks transaction flow between sender and receiver accounts, payment channel,
    geo-location, device fingerprint, and risk assessment scores.
    """

    __tablename__ = "transactions"

    transaction_ref: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique transaction reference number (e.g., UTR / RRN)",
    )
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Payment channel (UPI, NEFT, IMPS, RTGS)",
    )
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
        comment="Transaction amount in local currency",
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
        comment="Currency code",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Transaction execution timestamp",
    )
    location_city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Transaction origination city",
    )
    location_state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Transaction origination state",
    )
    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Geo latitude",
    )
    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Geo longitude",
    )
    ip_address_str: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        index=True,
        comment="IP address string at time of transaction",
    )
    device_fingerprint: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Device hardware/browser fingerprint",
    )
    risk_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Transaction-level risk score (0-100)",
    )
    flagged_pattern: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Detected pattern name (e.g. Mule Chain, Fan In)",
    )
    narrative: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Transaction description or remarks",
    )

    # ── Foreign Keys ──────────────────────────────────────────────────
    sender_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Sender account ID",
    )
    receiver_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Receiver account ID",
    )

    # ── Relationships ──────────────────────────────────────────────────
    sender_account: Mapped["Account"] = relationship(  # noqa: F821
        "Account",
        foreign_keys=[sender_account_id],
        back_populates="outgoing_transactions",
    )
    receiver_account: Mapped["Account"] = relationship(  # noqa: F821
        "Account",
        foreign_keys=[receiver_account_id],
        back_populates="incoming_transactions",
    )

    def __repr__(self) -> str:
        return f"<Transaction(ref={self.transaction_ref}, amount={self.amount}, channel={self.channel})>"
