"""
MuleTrace AI — Victim Complaint Service.

Business logic for handling incoming victim complaints from the public User Portal.
Stores complaints as Report entities with report_type="VICTIM_COMPLAINT".
"""

from __future__ import annotations


import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.report import Report
from app.repositories.report_repository import ReportRepository
from app.schemas.victim_complaint import VictimComplaintSubmit, VictimComplaintResponse


class VictimComplaintService:
    """Service handling public victim complaint submissions."""

    def __init__(self, report_repo: ReportRepository) -> None:
        self.report_repo = report_repo

    async def submit_complaint(self, payload: VictimComplaintSubmit) -> VictimComplaintResponse:
        """Process and store a new victim complaint."""
        
        # 1. Generate unique complaint tracking number
        complaint_number = f"CMP-2025-{uuid.uuid4().hex[:6].upper()}"
        
        # 2. Build structured JSON payload for summary_text
        complaint_data = {
            "transaction_id": payload.transaction_id,
            "victim_name": payload.victim_name,
            "victim_email": payload.victim_email,
            "victim_phone": payload.victim_phone,
            "incident_type": payload.incident_type.value,
            "amount_lost": payload.amount_lost,
            "incident_date": payload.incident_date.isoformat() if payload.incident_date else None,
            "description": payload.description,
        }
        summary_text = json.dumps(complaint_data, indent=2)
        
        # 3. Create Report object
        report = Report(
            report_number=complaint_number,
            report_type="VICTIM_COMPLAINT",
            title=f"Victim Complaint: {payload.incident_type.value} — {payload.victim_name}",
            summary_text=summary_text,
            status="active",
            generated_at=datetime.now(timezone.utc)
        )
        
        # 4. Save to database via ReportRepository
        await self.report_repo.create(report)
        
        # 5. Return success response
        return VictimComplaintResponse(
            success=True,
            complaint_number=complaint_number,
            status="RECEIVED",
            message="Complaint submitted successfully and is under review."
        )

    async def get_complaint_status(self, complaint_number: str) -> dict[str, Any]:
        """Fetch basic status of a submitted complaint for the victim."""
        report = await self.report_repo.get_by_number(complaint_number)
        
        if not report or report.report_type != "VICTIM_COMPLAINT":
            return {"success": False, "message": "Complaint not found."}
            
        return {
            "success": True,
            "complaint_number": report.report_number,
            "status": report.status,
            "title": report.title,
            "submitted_at": report.generated_at.isoformat()
        }

    async def list_complaints_by_email(self, email: str) -> list[dict[str, Any]]:
        """Return all complaints submitted by a victim email address.

        Deserializes the summary_text JSON for each report and returns
        a structured list for the User Portal's complaint history view.
        """
        reports = await self.report_repo.get_victim_complaints_by_email(email)
        results = []
        for report in reports:
            data: dict[str, Any] = {}
            if report.summary_text:
                try:
                    data = json.loads(report.summary_text)
                except (json.JSONDecodeError, ValueError):
                    data = {}
            results.append({
                "complaint_number": report.report_number,
                "title": report.title,
                "status": report.status or "SUBMITTED",
                "submitted_at": report.generated_at.isoformat(),
                "transaction_id": data.get("transaction_id"),
                "victim_name": data.get("victim_name"),
                "victim_email": data.get("victim_email"),
                "victim_phone": data.get("victim_phone"),
                "incident_type": data.get("incident_type"),
                "incident_date": data.get("incident_date"),
                "amount_lost": data.get("amount_lost"),
                "description": data.get("description"),
            })
        return results
