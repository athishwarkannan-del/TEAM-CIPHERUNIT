"""
MuleTrace AI — Transaction Schemas.

Pydantic schemas for Transaction data validation, filters, and API serialization.
"""

from __future__ import annotations
from typing import Optional


import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    """Base transaction attributes."""

    transaction_ref: str = Field(..., max_length=100, description="UTR or Reference No")
    channel: str = Field(..., description="Payment channel (UPI, NEFT, IMPS, RTGS)")
    amount: float = Field(..., gt=0, description="Amount in local currency")
    currency: str = Field(default="INR", max_length=3)
    timestamp: datetime = Field(..., description="Transaction execution timestamp")
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    ip_address_str: Optional[str] = None
    device_fingerprint: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Payload for recording a transaction."""

    sender_account_id: uuid.UUID
    receiver_account_id: uuid.UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    narrative: Optional[str] = None


class TransactionRead(TransactionBase):
    """Schema for returning transaction details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sender_account_id: uuid.UUID
    receiver_account_id: uuid.UUID
    risk_score: int = Field(ge=0, le=100)
    flagged_pattern: Optional[str] = None
    narrative: Optional[str] = None
    created_at: datetime
    status: str


class TransactionFilterParams(BaseModel):
    """Filter criteria for searching transactions."""

    channel: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    flagged_only: bool = False
    sender_account_id: Optional[uuid.UUID] = None
    receiver_account_id: Optional[uuid.UUID] = None
