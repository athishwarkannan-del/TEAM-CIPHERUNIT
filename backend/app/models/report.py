"""
MuleTrace AI — Report Model.

Represents compliance reports generated for regulatory submission (STR / CTR / Cybercrime Reports).
"""

from __future__ import annotations
from typing import Optional


import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    """Compliance Report entity.

    Tracks generated Suspicious Transaction Reports (STR), Cash Transaction Reports (CTR),
    and regulatory export payloads.
    """

    __tablename__ = "reports"

    report_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique report reference (e.g. STR-2025-0089)",
    )
    report_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="Report type (STR, CTR, CYBERCRIME_SUMMARY, EXECUTIVE_BRIEF)",
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Report document title",
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Generation timestamp",
    )
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Stored PDF/JSON report artifact path or URL",
    )
    summary_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="LLM-generated executive narrative",
    )

    # ── Foreign Keys ──────────────────────────────────────────────────
    case_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Associated case ID",
    )

    # ── Relationships ──────────────────────────────────────────────────
    case: Mapped["Optional[Case]"] = relationship(  # noqa: F821
        "Case",
        back_populates="reports",
    )

    def __repr__(self) -> str:
        return f"<Report(number={self.report_number}, type={self.report_type})>"
