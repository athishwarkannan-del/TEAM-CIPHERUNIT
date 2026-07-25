"""
MuleTrace AI — Beneficiary Model.

Represents registered beneficiaries for accounts.
Used for Shared Beneficiary pattern detection.
"""

from __future__ import annotations
from typing import Optional


import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Beneficiary(Base, TimestampMixin):
    """Beneficiary entity.

    Tracks added beneficiaries, IFSC codes, bank names, and creation timestamps.
    """

    __tablename__ = "beneficiaries"

    beneficiary_account_number: Mapped[str] = mapped_column(
        String(34),
        nullable=False,
        index=True,
        comment="Beneficiary account number",
    )
    beneficiary_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Beneficiary name",
    )
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Target bank name",
    )
    ifsc_code: Mapped[Optional[str]] = mapped_column(
        String(11),
        nullable=True,
        index=True,
        comment="IFSC code",
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when beneficiary was registered",
    )

    # ── Foreign Keys ──────────────────────────────────────────────────
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Account that added this beneficiary",
    )

    # ── Relationships ──────────────────────────────────────────────────
    account: Mapped["Account"] = relationship(  # noqa: F821
        "Account",
        back_populates="beneficiaries",
    )

    def __repr__(self) -> str:
        return f"<Beneficiary(account_number={self.beneficiary_account_number}, name={self.beneficiary_name})>"
