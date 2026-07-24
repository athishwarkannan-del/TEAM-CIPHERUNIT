"""
MuleTrace AI — Account Schemas.

Pydantic schemas for Account data validation, creation, update, and response serialization.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AccountBase(BaseModel):
    """Base fields for Account."""

    account_number: str = Field(..., max_length=34, description="Account IBAN or number")
    customer_id: str = Field(..., max_length=50, description="Customer CIF ID")
    customer_name: str = Field(..., max_length=200, description="Account holder name")
    account_type: str = Field(default="savings", description="Account type (savings, current, wallet)")
    currency: str = Field(default="INR", max_length=3, description="Currency code")
    balance: float = Field(default=0.0, description="Ledger balance")


class AccountCreate(AccountBase):
    """Payload for creating an account."""

    branch_id: uuid.UUID | None = Field(default=None, description="Home branch UUID")
    opened_at: datetime | None = Field(default=None, description="Opening date")


class AccountUpdate(BaseModel):
    """Payload for updating an account."""

    customer_name: str | None = None
    account_type: str | None = None
    balance: float | None = None
    risk_score: int | None = Field(default=None, ge=0, le=100)
    risk_level: str | None = None
    is_flagged_mule: bool | None = None
    status: str | None = None


class AccountRead(AccountBase):
    """Schema for returning account data."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    is_flagged_mule: bool
    branch_id: uuid.UUID | None = None
    opened_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    status: str


class AccountRiskSummary(BaseModel):
    """Account risk assessment snapshot."""

    account_id: uuid.UUID
    account_number: str
    risk_score: int
    risk_level: str
    top_flagged_patterns: list[str] = Field(default_factory=list)
    total_alerts_count: int = 0
