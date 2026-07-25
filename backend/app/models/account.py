"""
MuleTrace AI — Account Model.

Represents a customer bank account being monitored for mule activity.
Stores account profile information, risk score, and relationships.
"""

from __future__ import annotations
from typing import Optional


import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Account(Base, TimestampMixin):
    """Bank Account entity.

    Core node in graph analysis and risk scoring. Tracks account type,
    balance, risk score, associated branch, devices, IP addresses,
    and transactions.
    """

    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="check_risk_score_range"),
    )

    account_number: Mapped[str] = mapped_column(
        String(34),
        unique=True,
        nullable=False,
        index=True,
        comment="Account number (IBAN / Account No)",
    )
    customer_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Associated customer/CIF ID",
    )
    customer_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Account holder full name",
    )
    account_type: Mapped[str] = mapped_column(
        String(50),
        default="savings",
        nullable=False,
        comment="Account type (savings, current, salary, wallet)",
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
        comment="Currency code (ISO 4217)",
    )
    balance: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="Current ledger balance",
    )
    risk_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Dynamic risk score (0-100)",
    )
    risk_level: Mapped[str] = mapped_column(
        String(20),
        default="LOW",
        nullable=False,
        index=True,
        comment="Risk level (LOW, MEDIUM, HIGH, CRITICAL)",
    )
    is_flagged_mule: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
        comment="Flagged as confirmed or suspected mule account",
    )
    opened_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Account opening timestamp",
    )

    # ── Foreign Keys ──────────────────────────────────────────────────
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Home branch ID",
    )

    # ── Relationships ──────────────────────────────────────────────────
    branch: Mapped["Optional[Branch]"] = relationship(  # noqa: F821
        "Branch",
        back_populates="accounts",
    )
    outgoing_transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction",
        foreign_keys="Transaction.sender_account_id",
        back_populates="sender_account",
        lazy="selectin",
    )
    incoming_transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction",
        foreign_keys="Transaction.receiver_account_id",
        back_populates="receiver_account",
        lazy="selectin",
    )
    devices: Mapped[list["Device"]] = relationship(  # noqa: F821
        "Device",
        back_populates="account",
        cascade="all, delete-orphan",
    )
    ip_addresses: Mapped[list["IPAddress"]] = relationship(  # noqa: F821
        "IPAddress",
        back_populates="account",
        cascade="all, delete-orphan",
    )
    beneficiaries: Mapped[list["Beneficiary"]] = relationship(  # noqa: F821
        "Beneficiary",
        back_populates="account",
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["Alert"]] = relationship(  # noqa: F821
        "Alert",
        back_populates="account",
    )

    def __repr__(self) -> str:
        return f"<Account(number={self.account_number}, name={self.customer_name}, risk_score={self.risk_score})>"
