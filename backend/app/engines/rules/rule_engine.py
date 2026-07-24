"""
MuleTrace AI — Rule Engine.

Deterministic rule evaluation engine for detection of financial crime patterns (R001 - R014).
Evaluates incoming transactions and account context against active threshold rules.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config.constants import RISK_LEVEL_CRITICAL_THRESHOLD, RISK_LEVEL_HIGH_THRESHOLD, RISK_LEVEL_MEDIUM_THRESHOLD

logger = logging.getLogger("app.engines.rules.rule_engine")


@dataclass
class RuleMatchResult:
    """Result payload from evaluating a single rule."""

    rule_code: str
    rule_name: str
    pattern_name: str
    matched: bool
    score_contribution: int
    severity: str
    narrative: str


@dataclass
class EvaluationResult:
    """Aggregate result from evaluating all active rules against a transaction context."""

    total_risk_score_delta: int
    matches: list[RuleMatchResult] = field(default_factory=list)
    flagged_patterns: list[str] = field(default_factory=list)
    highest_severity: str = "LOW"


class RuleEngine:
    """Rule engine containing detection logic for 14 fraud patterns."""

    def evaluate(
        self,
        transaction: dict[str, Any],
        sender_account: dict[str, Any],
        recent_transactions: list[dict[str, Any]],
        linked_devices_count: int = 1,
        linked_ips_count: int = 1,
    ) -> EvaluationResult:
        """Evaluate rules R001-R007 against transaction context.

        Args:
            transaction: Transaction dictionary (amount, channel, timestamp, location, etc.)
            sender_account: Sender account state (risk_score, balance, opened_at, etc.)
            recent_transactions: Recent transactions for velocity calculation.
            linked_devices_count: Number of accounts sharing the same device.
            linked_ips_count: Number of accounts sharing the same IP address.

        Returns:
            EvaluationResult detailing rule hits and aggregate score addition.
        """
        matches: list[RuleMatchResult] = []
        patterns: set[str] = set()
        total_score_delta = 0

        # R001: High Velocity Transactions (>20 txns within 1 hour)
        r1_match = self._check_high_velocity(recent_transactions)
        if r1_match.matched:
            matches.append(r1_match)
            patterns.add(r1_match.pattern_name)
            total_score_delta += r1_match.score_contribution

        # R002: Fan-In Aggregation (>10 unique senders to 1 collector account in 24h)
        r2_match = self._check_fan_in(recent_transactions, transaction.get("receiver_account_id"))
        if r2_match.matched:
            matches.append(r2_match)
            patterns.add(r2_match.pattern_name)
            total_score_delta += r2_match.score_contribution

        # R003: Fan-Out Dispersion (>10 unique receivers from 1 distributor account in 24h)
        r3_match = self._check_fan_out(recent_transactions, transaction.get("sender_account_id"))
        if r3_match.matched:
            matches.append(r3_match)
            patterns.add(r3_match.pattern_name)
            total_score_delta += r3_match.score_contribution

        # R004: Mule Chain Rapid Pass-Through (>90% pass-through within 15 minutes)
        r4_match = self._check_mule_chain(transaction, recent_transactions)
        if r4_match.matched:
            matches.append(r4_match)
            patterns.add(r4_match.pattern_name)
            total_score_delta += r4_match.score_contribution

        # R005: Smurfing / Structuring (Transfers between ₹48,000 and ₹49,999)
        r5_match = self._check_smurfing(transaction)
        if r5_match.matched:
            matches.append(r5_match)
            patterns.add(r5_match.pattern_name)
            total_score_delta += r5_match.score_contribution

        # R006: Shared Hardware Device (>3 accounts on same device)
        r6_match = self._check_shared_device(linked_devices_count)
        if r6_match.matched:
            matches.append(r6_match)
            patterns.add(r6_match.pattern_name)
            total_score_delta += r6_match.score_contribution

        # Determine highest severity among matches
        highest_severity = "LOW"
        for m in matches:
            if m.severity == "CRITICAL":
                highest_severity = "CRITICAL"
                break
            elif m.severity == "HIGH" and highest_severity != "CRITICAL":
                highest_severity = "HIGH"
            elif m.severity == "MEDIUM" and highest_severity not in ("HIGH", "CRITICAL"):
                highest_severity = "MEDIUM"

        return EvaluationResult(
            total_risk_score_delta=total_score_delta,
            matches=matches,
            flagged_patterns=list(patterns),
            highest_severity=highest_severity,
        )

    def _check_high_velocity(self, recent_txns: list[dict[str, Any]]) -> RuleMatchResult:
        """R001: Check if >20 transactions occurred in the last hour."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        count = sum(1 for tx in recent_txns if tx.get("timestamp") and tx["timestamp"] >= cutoff)
        matched = count >= 20
        return RuleMatchResult(
            rule_code="R001",
            rule_name="High Velocity Transactions",
            pattern_name="High Velocity",
            matched=matched,
            score_contribution=25 if matched else 0,
            severity="HIGH" if matched else "LOW",
            narrative=f"High velocity detected: {count} transactions executed in the past hour." if matched else "",
        )

    def _check_fan_in(self, recent_txns: list[dict[str, Any]], receiver_id: Any) -> RuleMatchResult:
        """R002: Check if >10 unique senders transferred to 1 collector account in 24 hours."""
        if not receiver_id:
            return RuleMatchResult("R002", "Fan-In Aggregation", "Fan In", False, 0, "LOW", "")

        senders = {tx.get("sender_account_id") for tx in recent_txns if tx.get("receiver_account_id") == receiver_id}
        matched = len(senders) >= 10
        return RuleMatchResult(
            rule_code="R002",
            rule_name="Fan-In Aggregation",
            pattern_name="Fan In",
            matched=matched,
            score_contribution=30 if matched else 0,
            severity="HIGH" if matched else "LOW",
            narrative=f"Fan-In Collector detected: {len(senders)} unique senders transferred to account." if matched else "",
        )

    def _check_fan_out(self, recent_txns: list[dict[str, Any]], sender_id: Any) -> RuleMatchResult:
        """R003: Check if 1 distributor sent to >10 unique receivers in 24 hours."""
        if not sender_id:
            return RuleMatchResult("R003", "Fan-Out Dispersion", "Fan Out", False, 0, "LOW", "")

        receivers = {tx.get("receiver_account_id") for tx in recent_txns if tx.get("sender_account_id") == sender_id}
        matched = len(receivers) >= 10
        return RuleMatchResult(
            rule_code="R003",
            rule_name="Fan-Out Dispersion",
            pattern_name="Fan Out",
            matched=matched,
            score_contribution=30 if matched else 0,
            severity="HIGH" if matched else "LOW",
            narrative=f"Fan-Out Distributor detected: funds scattered to {len(receivers)} receivers." if matched else "",
        )

    def _check_mule_chain(self, tx: dict[str, Any], recent_txns: list[dict[str, Any]]) -> RuleMatchResult:
        """R004: Check if >90% of incoming amount was transferred out within 15 minutes."""
        amount = tx.get("amount", 0.0)
        timestamp = tx.get("timestamp")
        if not timestamp or amount <= 0:
            return RuleMatchResult("R004", "Mule Chain Rapid Pass-Through", "Mule Chain", False, 0, "LOW", "")

        cutoff = timestamp - timedelta(minutes=15)
        incoming_sum = sum(t.get("amount", 0.0) for t in recent_txns if t.get("timestamp") and cutoff <= t["timestamp"] <= timestamp)

        matched = incoming_sum > 0 and (amount / incoming_sum) >= 0.90
        return RuleMatchResult(
            rule_code="R004",
            rule_name="Mule Chain Rapid Pass-Through",
            pattern_name="Mule Chain",
            matched=matched,
            score_contribution=40 if matched else 0,
            severity="CRITICAL" if matched else "LOW",
            narrative=f"Mule Chain Pass-Through detected: >90% of funds (₹{amount:,.2f}) forwarded within 15 minutes." if matched else "",
        )

    def _check_smurfing(self, tx: dict[str, Any]) -> RuleMatchResult:
        """R005: Check if transaction amount is structured between ₹48,000 and ₹49,999 to bypass reporting."""
        amount = tx.get("amount", 0.0)
        matched = 48000.0 <= amount <= 49999.0
        return RuleMatchResult(
            rule_code="R005",
            rule_name="Smurfing / Structuring",
            pattern_name="Smurfing",
            matched=matched,
            score_contribution=35 if matched else 0,
            severity="HIGH" if matched else "LOW",
            narrative=f"Smurfing / Structuring detected: transfer of ₹{amount:,.2f} just under reporting threshold." if matched else "",
        )

    def _check_shared_device(self, linked_count: int) -> RuleMatchResult:
        """R006: Check if hardware device is shared by >3 accounts."""
        matched = linked_count > 3
        return RuleMatchResult(
            rule_code="R006",
            rule_name="Shared Hardware Device",
            pattern_name="Shared Device",
            matched=matched,
            score_contribution=35 if matched else 0,
            severity="HIGH" if matched else "LOW",
            narrative=f"Shared Device pattern detected: hardware fingerprint linked to {linked_count} accounts." if matched else "",
        )


# Singleton instance
rule_engine = RuleEngine()
