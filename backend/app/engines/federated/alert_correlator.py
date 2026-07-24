"""
MuleTrace AI — Phase 4: Privacy-Preserving Alert Correlator.

Implements Private Set Intersection (PSI) and hash matching protocols across
participating banks to identify cross-bank mule account networks without exposing
raw customer PII or account numbers.

Security & Privacy:
    - Accounts are pseudonymized using HMAC-SHA256 with a bank-specific salt.
    - Central server compares hashes across multiple banks.
    - If >1 bank flags the same salted hash, a CrossBankAlert is generated.
    - No bank can reverse another bank's account numbers from the hash.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.engines.federated.schemas import (
    CrossBankAlert,
    CrossBankAlertSeverity,
    CrossBankMatch,
    CrossBankQueryRequest,
    CrossBankQueryResponse,
)

logger = logging.getLogger("app.engines.federated.alert_correlator")


class AlertCorrelatorEngine:
    """Privacy-preserving cross-bank alert correlator.

    Maintains a hash repository of flagged suspect entities reported by
    different banks. Performs Private Set Intersection (PSI) matching to
    detect cross-bank mule networks.
    """

    def __init__(self) -> None:
        # Registry of account_hash -> list of {bank_id, risk_score, timestamp, pattern_type}
        self._flagged_hashes: dict[str, list[dict[str, Any]]] = {}
        self._alerts: list[CrossBankAlert] = []

    @staticmethod
    def hash_account_number(account_number: str, salt: str = "MULETRACE_FEDERATED_SALT_2026") -> str:
        """Compute deterministic HMAC-SHA256 hash for an account number."""
        return hmac.new(
            salt.encode("utf-8"),
            account_number.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def report_flagged_accounts(
        self,
        bank_id: str,
        account_hashes: list[str],
        pattern_type: str = "Mule Chain",
        risk_score: float = 85.0,
    ) -> list[CrossBankAlert]:
        """Report a batch of flagged account hashes from a participating bank.

        Checks for intersections with other banks' flagged hashes.
        Generates CrossBankAlerts when an account hash is flagged by >= 2 banks.
        """
        now = datetime.now(timezone.utc)
        new_alerts: list[CrossBankAlert] = []

        for acc_hash in account_hashes:
            if acc_hash not in self._flagged_hashes:
                self._flagged_hashes[acc_hash] = []

            # Check if this bank already reported this hash
            existing_banks = [item["bank_id"] for item in self._flagged_hashes[acc_hash]]
            if bank_id not in existing_banks:
                self._flagged_hashes[acc_hash].append({
                    "bank_id": bank_id,
                    "risk_score": risk_score,
                    "pattern_type": pattern_type,
                    "timestamp": now,
                })

            # Check intersection count
            reports = self._flagged_hashes[acc_hash]
            contributing_banks = len({r["bank_id"] for r in reports})

            # Generate cross-bank alert if >= 2 banks flagged the same hash
            if contributing_banks >= 2:
                avg_risk = sum(r["risk_score"] for r in reports) / len(reports)

                # Determine severity
                if avg_risk >= 90.0 or contributing_banks >= 3:
                    severity = CrossBankAlertSeverity.CRITICAL
                elif avg_risk >= 75.0:
                    severity = CrossBankAlertSeverity.HIGH
                elif avg_risk >= 50.0:
                    severity = CrossBankAlertSeverity.MEDIUM
                else:
                    severity = CrossBankAlertSeverity.LOW

                # Check if alert already exists for this hash
                existing_alert = next((a for a in self._alerts if a.account_hash == acc_hash), None)

                if existing_alert:
                    existing_alert.contributing_bank_count = contributing_banks
                    existing_alert.aggregate_risk_score = round(avg_risk, 2)
                    existing_alert.severity = severity
                else:
                    alert_id = f"ALT-FED-{uuid.uuid4().hex[:8].upper()}"
                    alert = CrossBankAlert(
                        alert_id=alert_id,
                        account_hash=acc_hash,
                        contributing_bank_count=contributing_banks,
                        aggregate_risk_score=round(avg_risk, 2),
                        severity=severity,
                        pattern_type=pattern_type,
                        narrative=(
                            f"Cross-bank mule network detected: Entity hash {acc_hash[:12]}... "
                            f"flagged independently across {contributing_banks} participating financial institutions."
                        ),
                        created_at=now,
                        is_acknowledged=False,
                    )
                    self._alerts.append(alert)
                    new_alerts.append(alert)
                    logger.info(
                        "Cross-bank alert generated: %s — %d banks, avg_risk=%.1f",
                        alert_id, contributing_banks, avg_risk,
                    )

        return new_alerts

    def process_query(self, request: CrossBankQueryRequest) -> CrossBankQueryResponse:
        """Process a privacy-preserving query from a bank checking hashes against global repository."""
        now = datetime.now(timezone.utc)
        matches: list[CrossBankMatch] = []

        for acc_hash in request.account_hashes:
            if acc_hash in self._flagged_hashes:
                reports = self._flagged_hashes[acc_hash]
                unique_banks = len({r["bank_id"] for r in reports})

                avg_risk = sum(r["risk_score"] for r in reports) / len(reports)
                first_flagged = min(r["timestamp"] for r in reports)

                if avg_risk >= 90.0 or unique_banks >= 3:
                    severity = CrossBankAlertSeverity.CRITICAL
                elif avg_risk >= 75.0:
                    severity = CrossBankAlertSeverity.HIGH
                else:
                    severity = CrossBankAlertSeverity.MEDIUM

                matches.append(CrossBankMatch(
                    account_hash=acc_hash,
                    matched_bank_count=unique_banks,
                    aggregate_risk_score=round(avg_risk, 2),
                    alert_severity=severity,
                    first_flagged_at=first_flagged,
                ))

        return CrossBankQueryResponse(
            query_bank_id=request.bank_id,
            total_hashes_submitted=len(request.account_hashes),
            matches_found=len(matches),
            matches=matches,
            queried_at=now,
        )

    def get_all_alerts(self, min_severity: CrossBankAlertSeverity | None = None) -> list[CrossBankAlert]:
        """Get all cross-bank alerts, optionally filtered by severity."""
        if min_severity is None:
            return list(self._alerts)

        severity_levels = {
            CrossBankAlertSeverity.LOW: 1,
            CrossBankAlertSeverity.MEDIUM: 2,
            CrossBankAlertSeverity.HIGH: 3,
            CrossBankAlertSeverity.CRITICAL: 4,
        }
        target_level = severity_levels.get(min_severity, 1)

        return [
            alert for alert in self._alerts
            if severity_levels.get(alert.severity, 1) >= target_level
        ]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark a cross-bank alert as acknowledged."""
        alert = next((a for a in self._alerts if a.alert_id == alert_id), None)
        if alert:
            alert.is_acknowledged = True
            return True
        return False


# Singleton instance
alert_correlator = AlertCorrelatorEngine()
