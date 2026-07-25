"""
MuleTrace AI — Report Schemas.

Pydantic schemas for STR / CTR compliance report generation and retrieval.
"""

from __future__ import annotations
from typing import Optional


import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReportGenerateRequest(BaseModel):
    """Payload for requesting report generation."""

    report_type: str = Field(..., description="STR, CTR, CYBERCRIME_SUMMARY, EXECUTIVE_BRIEF")
    title: str = Field(..., max_length=200, description="Report document title")
    case_id: Optional[uuid.UUID] = Field(default=None, description="Optional case link")
    include_graph_visualization: bool = Field(default=True)
    summary_notes: Optional[str] = None


class ReportRead(BaseModel):
    """Schema for returning generated report metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    report_number: str
    report_type: str
    title: str
    generated_at: datetime
    file_path: Optional[str] = None
    summary_text: Optional[str] = None
    case_id: Optional[uuid.UUID] = None
    created_at: datetime
    status: str
