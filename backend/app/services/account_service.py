"""
MuleTrace AI — Account Service.

Business logic service for bank account management and risk assessment lookup.
"""

from __future__ import annotations
from typing import Optional


import uuid
from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.schemas.common import PaginatedResponse, PaginationMeta


class AccountService:
    """Service handling account operations."""

    def __init__(self, account_repo: AccountRepository) -> None:
        self.account_repo = account_repo

    async def get_account_by_id(self, account_id: uuid.UUID) -> Optional[AccountRead]:
        """Get single account by UUID."""
        account = await self.account_repo.get_by_id(account_id)
        if not account:
            return None
        return AccountRead.model_validate(account)

    async def get_accounts_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        risk_level: Optional[str] = None,
        is_flagged_mule: Optional[bool] = None,
    ) -> PaginatedResponse[AccountRead]:
        """Fetch paginated account list with filter metadata."""
        skip = (page - 1) * page_size
        items = await self.account_repo.get_multi(
            skip=skip,
            limit=page_size,
            risk_level=risk_level,
            is_flagged_mule=is_flagged_mule,
        )
        total_items = await self.account_repo.count(
            risk_level=risk_level,
            is_flagged_mule=is_flagged_mule,
        )

        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        account_reads = [AccountRead.model_validate(item) for item in items]

        return PaginatedResponse(
            data=account_reads,
            pagination=PaginationMeta(
                total_items=total_items,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
        )

    async def create_account(self, payload: AccountCreate) -> AccountRead:
        """Create new account record."""
        account_data = payload.model_dump()
        account_obj = Account(**account_data)
        created = await self.account_repo.create(account_obj)
        return AccountRead.model_validate(created)

    async def update_account(self, account_id: uuid.UUID, payload: AccountUpdate) -> Optional[AccountRead]:
        """Update existing account profile or risk state."""
        account = await self.account_repo.get_by_id(account_id)
        if not account:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)

        updated = await self.account_repo.update(account)
        return AccountRead.model_validate(updated)
