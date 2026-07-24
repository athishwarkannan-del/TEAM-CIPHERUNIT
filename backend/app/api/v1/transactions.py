"""
MuleTrace AI — Transactions Endpoints.

API endpoints for searching, retrieving, and recording cross-channel transactions.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_transaction_service
from app.schemas.common import BaseResponse, PaginatedResponse
from app.schemas.transaction import TransactionCreate, TransactionFilterParams, TransactionRead
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=PaginatedResponse[TransactionRead])
async def list_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    channel: str | None = Query(default=None),
    min_amount: float | None = Query(default=None),
    max_amount: float | None = Query(default=None),
    sender_account_id: uuid.UUID | None = Query(default=None),
    receiver_account_id: uuid.UUID | None = Query(default=None),
    service: TransactionService = Depends(get_transaction_service),
) -> PaginatedResponse[TransactionRead]:
    """Search and filter transactions across payment channels (UPI, NEFT, IMPS, RTGS)."""
    filters = TransactionFilterParams(
        channel=channel,
        min_amount=min_amount,
        max_amount=max_amount,
        sender_account_id=sender_account_id,
        receiver_account_id=receiver_account_id,
    )
    return await service.get_transactions_paginated(
        page=page,
        page_size=page_size,
        filters=filters,
    )


@router.get("/{transaction_id}", response_model=BaseResponse[TransactionRead])
async def get_transaction_by_id(
    transaction_id: uuid.UUID,
    service: TransactionService = Depends(get_transaction_service),
) -> BaseResponse[TransactionRead]:
    """Retrieve transaction details by UUID."""
    tx = await service.get_transaction_by_id(transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found",
        )
    return BaseResponse(
        success=True,
        message="Transaction details fetched successfully",
        data=tx,
    )


@router.post("", response_model=BaseResponse[TransactionRead], status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
) -> BaseResponse[TransactionRead]:
    """Record a new cross-channel transaction for risk processing."""
    created = await service.create_transaction(payload)
    return BaseResponse(
        success=True,
        message="Transaction recorded successfully",
        data=created,
    )
