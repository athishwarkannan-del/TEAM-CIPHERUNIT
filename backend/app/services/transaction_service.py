"""
MuleTrace AI — Transaction Service.

Business logic service for financial transaction processing and retrieval.
"""

import uuid
from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.transaction import TransactionCreate, TransactionFilterParams, TransactionRead


class TransactionService:
    """Service handling transaction operations."""

    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self.transaction_repo = transaction_repo

    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> TransactionRead | None:
        """Fetch single transaction by UUID."""
        tx = await self.transaction_repo.get_by_id(transaction_id)
        if not tx:
            return None
        return TransactionRead.model_validate(tx)

    async def get_transactions_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: TransactionFilterParams | None = None,
    ) -> PaginatedResponse[TransactionRead]:
        """Fetch paginated transactions matching filter parameters."""
        skip = (page - 1) * page_size
        channel = filters.channel if filters else None
        min_amt = filters.min_amount if filters else None
        max_amt = filters.max_amount if filters else None
        start_dt = filters.start_date if filters else None
        end_dt = filters.end_date if filters else None
        sender_id = filters.sender_account_id if filters else None
        receiver_id = filters.receiver_account_id if filters else None

        items = await self.transaction_repo.get_multi(
            skip=skip,
            limit=page_size,
            channel=channel,
            min_amount=min_amt,
            max_amount=max_amt,
            start_date=start_dt,
            end_date=end_dt,
            sender_account_id=sender_id,
            receiver_account_id=receiver_id,
        )

        total_items = await self.transaction_repo.count(
            channel=channel,
            min_amount=min_amt,
            max_amount=max_amt,
            start_date=start_dt,
            end_date=end_dt,
            sender_account_id=sender_id,
            receiver_account_id=receiver_id,
        )

        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        tx_reads = [TransactionRead.model_validate(item) for item in items]

        return PaginatedResponse(
            data=tx_reads,
            pagination=PaginationMeta(
                total_items=total_items,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
        )

    async def create_transaction(self, payload: TransactionCreate) -> TransactionRead:
        """Record new transaction."""
        tx_data = payload.model_dump()
        tx_obj = Transaction(**tx_data)
        created = await self.transaction_repo.create(tx_obj)
        return TransactionRead.model_validate(created)
