"""
MuleTrace AI — Rule Model.

Represents detection rules used by the Rule Engine to flag suspicious patterns.
"""

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class Rule(Base, TimestampMixin):
    """Rule Engine rule entity.

    Defines threshold parameters, detection logic scope, and risk weight for pattern detection.
    """

    __tablename__ = "rules"

    rule_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique rule code (e.g. R001, R002)",
    )
    rule_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Human-readable rule name",
    )
    pattern_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Associated pattern (High Velocity, Fan In, Circular Loop, etc.)",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Rule rationale and detection criteria",
    )
    risk_score_contribution: Mapped[int] = mapped_column(
        Integer,
        default=20,
        nullable=False,
        comment="Points added to risk score upon rule match",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Toggle state for rule evaluation",
    )
    threshold_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Numeric threshold for rule trigger",
    )
    time_window_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Time window window in minutes for velocity evaluation",
    )

    def __repr__(self) -> str:
        return f"<Rule(code={self.rule_code}, name={self.rule_name}, active={self.is_active})>"
