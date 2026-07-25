"""
MuleTrace AI — Alert Schemas.

Pydantic schemas for suspicious activity Alert management and triage actions.
"""

from __future__ import annotations
from typing import Optional


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
    description: Optional[str] = None


class AlertCreate(AlertBase):
    """Payload for generating an alert."""

    account_id: uuid.UUID
    case_id: Optional[uuid.UUID] = None
    triggered_at: Optional[datetime] = None


class AlertTriageUpdate(BaseModel):
    """Payload for updating an alert triage status."""

    alert_status: str = Field(
        ...,
        description="NEW, UNDER_INVESTIGATION, ESCALATED, CLOSED_FALSE_POSITIVE, CLOSED_CONFIRMED",
    )
    notes: Optional[str] = Field(default=None, description="Triage note or explanation")
    case_id: Optional[uuid.UUID] = Field(default=None, description="Optionally attach to case")


class AlertRead(AlertBase):
    """Schema for returning alert details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    case_id: Optional[uuid.UUID] = None
    alert_status: str
    triggered_at: datetime
    created_at: datetime
    updated_at: datetime
