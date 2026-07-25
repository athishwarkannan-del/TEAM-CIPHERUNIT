"""
MuleTrace AI — Account Repository.

Handles all SQL database interactions for Account entities.
"""

from __future__ import annotations


import uuid
from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountRepository:
    """Repository for managing Account database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, account_id: uuid.UUID) -> Optional[Account]:
        """Fetch account by primary key UUID."""
        stmt = select(Account).where(Account.id == account_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Fetch account by account number."""
        stmt = select(Account).where(Account.account_number == account_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 20,
        risk_level: Optional[str] = None,
        is_flagged_mule: Optional[bool] = None,
    ) -> Sequence[Account]:
        """Fetch paginated list of accounts with optional filters."""
        stmt = select(Account)
        if risk_level:
            stmt = stmt.where(Account.risk_level == risk_level)
        if is_flagged_mule is not None:
            stmt = stmt.where(Account.is_flagged_mule == is_flagged_mule)

        stmt = stmt.offset(skip).limit(limit).order_by(Account.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(
        self,
        risk_level: Optional[str] = None,
        is_flagged_mule: Optional[bool] = None,
    ) -> int:
        """Count total matching accounts."""
        stmt = select(func.count(Account.id))
        if risk_level:
            stmt = stmt.where(Account.risk_level == risk_level)
        if is_flagged_mule is not None:
            stmt = stmt.where(Account.is_flagged_mule == is_flagged_mule)

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, account: Account) -> Account:
        """Persist a new account."""
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def update(self, account: Account) -> Account:
        """Save updates to an existing account."""
        await self.session.commit()
        await self.session.refresh(account)
        return account
