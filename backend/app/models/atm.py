"""
MuleTrace AI — ATM Model.

Represents Automated Teller Machines (ATMs).
Used for cash-out tracking and geographic analysis.
"""

from __future__ import annotations


from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class ATM(Base, TimestampMixin):
    """ATM entity.

    Tracks ATM terminal ID, location coordinates, bank owner, and city.
    """

    __tablename__ = "atms"

    terminal_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique ATM Terminal ID",
    )
    bank_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Bank managing this ATM",
    )
    location_name: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
        comment="ATM location display name",
    )
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="City",
    )
    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="State",
    )
    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Latitude",
    )
    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Longitude",
    )

    def __repr__(self) -> str:
        return f"<ATM(terminal_id={self.terminal_id}, location={self.location_name}, city={self.city})>"
