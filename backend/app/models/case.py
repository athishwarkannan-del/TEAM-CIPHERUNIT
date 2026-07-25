"""
MuleTrace AI — Case Model.

Represents an investigation case opened by a fraud analyst or investigator.
Groups related alerts, accounts, and evidence into an actionable investigation.
"""

from __future__ import annotations
from typing import Optional


from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Case(Base, TimestampMixin):
    """Investigation Case entity.

    Tracks investigation cases, assigned investigator IDs, case status,
    priority, and evidence notes.
    """

    __tablename__ = "cases"

    case_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique case reference (e.g. CAS-2025-0045)",
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Case subject / title",
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default="MEDIUM",
        nullable=False,
        index=True,
        comment="Case priority (LOW, MEDIUM, HIGH, CRITICAL)",
    )
    case_status: Mapped[str] = mapped_column(
        String(30),
        default="OPEN",
        nullable=False,
        index=True,
        comment="Case status (OPEN, IN_PROGRESS, PENDING_REVIEW, CLOSED_CONFIRMED, CLOSED_FALSE_POSITIVE)",
    )
    assigned_investigator_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="ID of the assigned analyst/investigator",
    )
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Case creation timestamp",
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Case closure timestamp",
    )
    summary_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Investigator findings & summary notes",
    )

    # ── Relationships ──────────────────────────────────────────────────
    alerts: Mapped[list["Alert"]] = relationship(  # noqa: F821
        "Alert",
        back_populates="case",
    )
    reports: Mapped[list["Report"]] = relationship(  # noqa: F821
        "Report",
        back_populates="case",
    )

    def __repr__(self) -> str:
        return f"<Case(number={self.case_number}, status={self.case_status}, priority={self.priority})>"
