"""
MuleTrace AI — Transaction Service.

Business logic service for financial transaction processing, risk engine evaluation,
and Neo4j graph synchronization.
"""

from __future__ import annotations
from typing import Optional


import uuid
from app.engines.graph.graph_builder import graph_builder
from app.engines.ml.xgboost_model import ml_engine
from app.engines.rules.rule_engine import rule_engine
from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.transaction import TransactionCreate, TransactionFilterParams, TransactionRead


class TransactionService:
    """Service handling transaction processing and intelligence integration."""

    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self.transaction_repo = transaction_repo

    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Optional[TransactionRead]:
        """Fetch single transaction by UUID."""
        tx = await self.transaction_repo.get_by_id(transaction_id)
        if not tx:
            return None
        return TransactionRead.model_validate(tx)

    async def get_transactions_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[TransactionFilterParams] = None,
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
        """Record new transaction, evaluate Rule & ML engines, and sync to graph."""
        tx_data = payload.model_dump()

        # 1. Rule Engine Evaluation
        rule_res = rule_engine.evaluate(
            transaction=tx_data,
            sender_account={},
            recent_transactions=[],
        )

        # 2. ML Engine Risk Prediction
        ml_res = ml_engine.predict_transaction_risk(tx_data)

        # 3. Combine scores (Weighted average: 60% Rule Engine + 40% ML Engine)
        computed_risk = int(round(0.6 * rule_res.total_risk_score_delta + 0.4 * ml_res.predicted_risk_score))
        computed_risk = min(99, max(0, computed_risk))

        tx_data["risk_score"] = computed_risk
        if rule_res.flagged_patterns:
            tx_data["flagged_pattern"] = ", ".join(rule_res.flagged_patterns)

        # 4. Save to PostgreSQL (Supabase)
        tx_obj = Transaction(**tx_data)
        created = await self.transaction_repo.create(tx_obj)

        # 5. Asynchronously sync to Neo4j Graph
        await graph_builder.sync_transaction(tx_data)

        return TransactionRead.model_validate(created)
