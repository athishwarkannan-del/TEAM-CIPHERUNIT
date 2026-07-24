"""
MuleTrace AI — Transaction Schemas.

Pydantic schemas for Transaction data validation, filters, and API serialization.
"""

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
    location_city: str | None = None
    location_state: str | None = None
    ip_address_str: str | None = None
    device_fingerprint: str | None = None


class TransactionCreate(TransactionBase):
    """Payload for recording a transaction."""

    sender_account_id: uuid.UUID
    receiver_account_id: uuid.UUID
    latitude: float | None = None
    longitude: float | None = None
    narrative: str | None = None


class TransactionRead(TransactionBase):
    """Schema for returning transaction details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sender_account_id: uuid.UUID
    receiver_account_id: uuid.UUID
    risk_score: int = Field(ge=0, le=100)
    flagged_pattern: str | None = None
    narrative: str | None = None
    created_at: datetime
    status: str


class TransactionFilterParams(BaseModel):
    """Filter criteria for searching transactions."""

    channel: str | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    flagged_only: bool = False
    sender_account_id: uuid.UUID | None = None
    receiver_account_id: uuid.UUID | None = None
