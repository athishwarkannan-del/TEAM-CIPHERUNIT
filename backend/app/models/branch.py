"""
MuleTrace AI — Branch Model.

Represents a bank branch. Accounts are associated with branches
for geographic analysis and branch-level risk aggregation.

Branch is created first because Account depends on it via foreign key.
"""

from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Branch(Base, TimestampMixin):
    """Bank branch entity.

    Used for geographic intelligence — correlating transaction patterns
    with branch locations to detect impossible travel and regional
    mule account clusters.
    """

    __tablename__ = "branches"

    branch_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique branch code",
    )
    branch_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Branch display name",
    )
    bank_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Parent bank name",
    )
    ifsc_code: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False,
        index=True,
        comment="IFSC code (11 characters)",
    )
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="City where branch is located",
    )
    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="State where branch is located",
    )
    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Full branch address",
    )
    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Branch latitude for geo intelligence",
    )
    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Branch longitude for geo intelligence",
    )

    # ── Relationships ──────────────────────────────────────────────────
    accounts: Mapped[list["Account"]] = relationship(  # noqa: F821
        "Account",
        back_populates="branch",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Branch(code={self.branch_code}, name={self.branch_name}, ifsc={self.ifsc_code})>"
