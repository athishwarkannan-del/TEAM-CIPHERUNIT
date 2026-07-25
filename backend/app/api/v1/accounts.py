"""
MuleTrace AI — Accounts Endpoints.

API endpoints for bank account lookup, creation, search, and updates.
"""

from __future__ import annotations
from typing import Optional


import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_account_service
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.schemas.common import BaseResponse, PaginatedResponse
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=PaginatedResponse[AccountRead])
async def list_accounts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    risk_level: Optional[str] = Query(default=None),
    is_flagged_mule: Optional[bool] = Query(default=None),
    service: AccountService = Depends(get_account_service),
) -> PaginatedResponse[AccountRead]:
    """List monitored bank accounts with optional risk level and mule flag filters."""
    return await service.get_accounts_paginated(
        page=page,
        page_size=page_size,
        risk_level=risk_level,
        is_flagged_mule=is_flagged_mule,
    )


@router.get("/{account_id}", response_model=BaseResponse[AccountRead])
async def get_account_by_id(
    account_id: uuid.UUID,
    service: AccountService = Depends(get_account_service),
) -> BaseResponse[AccountRead]:
    """Retrieve detailed account profile by UUID."""
    account = await service.get_account_by_id(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID '{account_id}' not found",
        )
    return BaseResponse(
        success=True,
        message="Account details fetched successfully",
        data=account,
    )


@router.post("", response_model=BaseResponse[AccountRead], status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    service: AccountService = Depends(get_account_service),
) -> BaseResponse[AccountRead]:
    """Register a new bank account for monitoring."""
    created = await service.create_account(payload)
    return BaseResponse(
        success=True,
        message="Account created successfully",
        data=created,
    )


@router.patch("/{account_id}", response_model=BaseResponse[AccountRead])
async def update_account(
    account_id: uuid.UUID,
    payload: AccountUpdate,
    service: AccountService = Depends(get_account_service),
) -> BaseResponse[AccountRead]:
    """Update account profile or risk classification state."""
    updated = await service.update_account(account_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID '{account_id}' not found",
        )
    return BaseResponse(
        success=True,
        message="Account updated successfully",
        data=updated,
    )
