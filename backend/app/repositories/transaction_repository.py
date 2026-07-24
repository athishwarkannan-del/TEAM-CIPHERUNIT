"""
MuleTrace AI — Transaction Repository.

Handles database access operations for Transaction entities.
"""

import uuid
from datetime import datetime
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


class TransactionRepository:
    """Repository for Transaction database queries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, transaction_id: uuid.UUID) -> Transaction | None:
        """Fetch transaction by UUID."""
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ref(self, transaction_ref: str) -> Transaction | None:
        """Fetch transaction by reference UTR."""
        stmt = select(Transaction).where(Transaction.transaction_ref == transaction_ref)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 20,
        channel: str | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        sender_account_id: uuid.UUID | None = None,
        receiver_account_id: uuid.UUID | None = None,
    ) -> Sequence[Transaction]:
        """Fetch paginated transactions matching filter criteria."""
        stmt = select(Transaction)

        if channel:
            stmt = stmt.where(Transaction.channel == channel)
        if min_amount is not None:
            stmt = stmt.where(Transaction.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Transaction.amount <= max_amount)
        if start_date:
            stmt = stmt.where(Transaction.timestamp >= start_date)
        if end_date:
            stmt = stmt.where(Transaction.timestamp <= end_date)
        if sender_account_id:
            stmt = stmt.where(Transaction.sender_account_id == sender_account_id)
        if receiver_account_id:
            stmt = stmt.where(Transaction.receiver_account_id == receiver_account_id)

        stmt = stmt.offset(skip).limit(limit).order_by(Transaction.timestamp.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(
        self,
        channel: str | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        sender_account_id: uuid.UUID | None = None,
        receiver_account_id: uuid.UUID | None = None,
    ) -> int:
        """Count total transactions matching filters."""
        stmt = select(func.count(Transaction.id))

        if channel:
            stmt = stmt.where(Transaction.channel == channel)
        if min_amount is not None:
            stmt = stmt.where(Transaction.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Transaction.amount <= max_amount)
        if start_date:
            stmt = stmt.where(Transaction.timestamp >= start_date)
        if end_date:
            stmt = stmt.where(Transaction.timestamp <= end_date)
        if sender_account_id:
            stmt = stmt.where(Transaction.sender_account_id == sender_account_id)
        if receiver_account_id:
            stmt = stmt.where(Transaction.receiver_account_id == receiver_account_id)

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, transaction: Transaction) -> Transaction:
        """Persist new transaction."""
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction
