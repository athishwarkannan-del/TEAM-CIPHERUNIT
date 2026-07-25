"""
MuleTrace AI — Victim Complaint Schemas.

Pydantic schemas for the public complaint submission endpoint.
"""

from __future__ import annotations
from typing import Optional


from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class IncidentType(str, Enum):
    """Types of incidents that can be reported."""
    PHISHING = "PHISHING"
    DIGITAL_ARREST = "DIGITAL_ARREST"
    UPI_FRAUD = "UPI_FRAUD"
    INVESTMENT_SCAM = "INVESTMENT_SCAM"
    JOB_FRAUD = "JOB_FRAUD"
    LOAN_FRAUD = "LOAN_FRAUD"
    OTHER = "OTHER"


class VictimComplaintSubmit(BaseModel):
    """Payload for submitting a new victim complaint."""

    transaction_id: str = Field(..., max_length=100, description="Unique transaction reference (UTR/RRN)")
    victim_name: str = Field(..., max_length=200, description="Full name of the victim")
    victim_email: EmailStr = Field(..., description="Email address of the victim")
    victim_phone: Optional[str] = Field(default=None, max_length=15, description="Phone number of the victim")
    incident_type: IncidentType = Field(..., description="Category of the fraud incident")
    amount_lost: Optional[float] = Field(default=None, ge=0.0, description="Amount lost in local currency")
    incident_date: Optional[datetime] = Field(default=None, description="When the incident occurred")
    description: str = Field(..., max_length=2000, description="Detailed narrative of the incident")


class VictimComplaintResponse(BaseModel):
    """Response returned to the victim after submission."""

    success: bool = True
    complaint_number: str = Field(..., description="Tracking ID for the complaint")
    status: str = Field(default="RECEIVED", description="Current status of the complaint")
    message: str = "Complaint submitted successfully."
