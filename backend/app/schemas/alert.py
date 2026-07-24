"""
MuleTrace AI — Alert Schemas.

Pydantic schemas for suspicious activity Alert management and triage actions.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AlertBase(BaseModel):
    """Base fields for Alert."""

    alert_number: str = Field(..., description="Unique alert reference string")
    title: str = Field(..., description="Alert headline")
    pattern_type: str = Field(..., description="Pattern code / name")
    severity: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    risk_score: int = Field(ge=0, le=100)
    description: str | None = None


class AlertCreate(AlertBase):
    """Payload for generating an alert."""

    account_id: uuid.UUID
    case_id: uuid.UUID | None = None
    triggered_at: datetime | None = None


class AlertTriageUpdate(BaseModel):
    """Payload for updating an alert triage status."""

    alert_status: str = Field(
        ...,
        description="NEW, UNDER_INVESTIGATION, ESCALATED, CLOSED_FALSE_POSITIVE, CLOSED_CONFIRMED",
    )
    notes: str | None = Field(default=None, description="Triage note or explanation")
    case_id: uuid.UUID | None = Field(default=None, description="Optionally attach to case")


class AlertRead(AlertBase):
    """Schema for returning alert details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    case_id: uuid.UUID | None = None
    alert_status: str
    triggered_at: datetime
    created_at: datetime
    updated_at: datetime
