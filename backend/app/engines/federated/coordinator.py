"""
MuleTrace AI — Phase 1: Federated Learning Coordinator.

Central aggregation server managing the federated learning lifecycle:
    - Bank registration and authentication
    - Training round initiation and orchestration
    - FedAvg weight aggregation across participating banks
    - Global model versioning and distribution

The coordinator NEVER receives raw transaction data. It only processes
encrypted/noisy model weight deltas submitted by participating banks.
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

import numpy as np

from app.engines.federated.privacy import dp_engine, secure_agg_engine
from app.engines.federated.schemas import (
    BankRegistrationRequest,
    BankRegistrationResponse,
    BankStatus,
    CrossBankAlertSeverity,
    FederatedPlatformStatus,
    GlobalModelResponse,
    InitiateRoundRequest,
    InitiateRoundResponse,
    ModelWeightUpload,
    RegisteredBankInfo,
    TrainingRoundInfo,
    TrainingRoundStatus,
)

logger = logging.getLogger("app.engines.federated.coordinator")


class FederatedCoordinator:
    """Central coordinator for privacy-preserving federated graph learning.

    Implements Federated Averaging (FedAvg) with differential privacy:

        w_global^{t+1} = Σ (n_k / n) · w_k^{t}

    where n_k is the number of local samples at bank k and n is the total.
    """

    def __init__(self) -> None:
        # Bank registry
        self._banks: dict[str, dict[str, Any]] = {}
        self._bank_tokens: dict[str, str] = {}  # token -> bank_id

        # Training rounds
        self._rounds: list[TrainingRoundInfo] = []
        self._current_round: TrainingRoundInfo | None = None
        self._round_contributions: dict[str, list[ModelWeightUpload]] = {}

        # Global model state
        self._global_weights: dict[str, list[list[float]]] = {}
        self._global_biases: dict[str, list[float]] = {}
        self._global_model_version: str = "v0.0.0"

        # Platform metrics
        self._started_at = datetime.now(timezone.utc)
        self._total_cross_bank_alerts = 0

    # ------------------------------------------------------------------
    # Bank Registration
    # ------------------------------------------------------------------

    def register_bank(self, request: BankRegistrationRequest) -> BankRegistrationResponse:
        """Register a new bank as a federated learning participant.

        Each bank receives a unique API token for subsequent calls.
        """
        # Check for duplicate
        for bid, info in self._banks.items():
            if info["bank_code"] == request.bank_code:
                logger.warning("Bank %s already registered", request.bank_code)
                return BankRegistrationResponse(
                    bank_id=bid,
                    bank_code=request.bank_code,
                    bank_name=info["bank_name"],
                    status=BankStatus(info["status"]),
                    registered_at=info["registered_at"],
                    api_token=info["api_token"],
                )

        bank_id = f"BANK-{uuid.uuid4().hex[:12].upper()}"
        api_token = f"fl_{secrets.token_urlsafe(32)}"
        now = datetime.now(timezone.utc)

        self._banks[bank_id] = {
            "bank_id": bank_id,
            "bank_code": request.bank_code,
            "bank_name": request.bank_name,
            "endpoint_url": request.endpoint_url,
            "public_key_pem": request.public_key_pem,
            "status": BankStatus.ACTIVE.value,
            "registered_at": now,
            "last_contribution_at": None,
            "total_rounds_participated": 0,
            "local_account_count": request.local_account_count,
            "local_transaction_count": request.local_transaction_count,
            "api_token": api_token,
        }
        self._bank_tokens[api_token] = bank_id

        logger.info("Registered bank %s (%s) with ID %s", request.bank_name, request.bank_code, bank_id)

        return BankRegistrationResponse(
            bank_id=bank_id,
            bank_code=request.bank_code,
            bank_name=request.bank_name,
            status=BankStatus.ACTIVE,
            registered_at=now,
            api_token=api_token,
        )

    def get_registered_banks(self) -> list[RegisteredBankInfo]:
        """List all registered banks (without sensitive tokens)."""
        return [
            RegisteredBankInfo(
                bank_id=info["bank_id"],
                bank_code=info["bank_code"],
                bank_name=info["bank_name"],
                status=BankStatus(info["status"]),
                registered_at=info["registered_at"],
                last_contribution_at=info.get("last_contribution_at"),
                total_rounds_participated=info.get("total_rounds_participated", 0),
                local_account_count=info.get("local_account_count", 0),
                local_transaction_count=info.get("local_transaction_count", 0),
            )
            for info in self._banks.values()
        ]

    def validate_token(self, token: str) -> str | None:
        """Validate an API token and return the associated bank_id."""
        return self._bank_tokens.get(token)

    # ------------------------------------------------------------------
    # Training Round Management
    # ------------------------------------------------------------------

    def initiate_round(self, request: InitiateRoundRequest) -> InitiateRoundResponse:
        """Initiate a new federated training round."""
        active_count = sum(1 for b in self._banks.values() if b["status"] == BankStatus.ACTIVE.value)

        round_number = len(self._rounds) + 1
        round_id = f"ROUND-{round_number:04d}-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc)

        round_info = TrainingRoundInfo(
            round_id=round_id,
            round_number=round_number,
            status=TrainingRoundStatus.COLLECTING,
            initiated_at=now,
            participating_banks=[],
            total_samples=0,
            aggregated_loss=0.0,
            global_model_version=self._global_model_version,
            privacy_budget_consumed=0.0,
        )

        self._current_round = round_info
        self._rounds.append(round_info)
        self._round_contributions[round_id] = []

        logger.info(
            "Initiated federated round %s (#%d) — min_participants=%d, ε=%.2f, δ=%.2e",
            round_id, round_number, request.min_participants, request.dp_epsilon, request.dp_delta,
        )

        return InitiateRoundResponse(
            round_id=round_id,
            round_number=round_number,
            status=TrainingRoundStatus.COLLECTING,
            initiated_at=now,
            min_participants=request.min_participants,
            target_epochs=request.target_epochs,
            dp_epsilon=request.dp_epsilon,
            dp_delta=request.dp_delta,
        )

    def get_current_round(self) -> TrainingRoundInfo | None:
        """Get the currently active training round."""
        return self._current_round

    def get_round_history(self) -> list[TrainingRoundInfo]:
        """Get all training rounds."""
        return list(self._rounds)

    # ------------------------------------------------------------------
    # Weight Upload & FedAvg Aggregation
    # ------------------------------------------------------------------

    def receive_weight_update(self, upload: ModelWeightUpload) -> dict[str, Any]:
        """Receive a weight update from a participating bank.

        The weights should already have DP noise applied by the bank's
        local trainer before upload.
        """
        if self._current_round is None:
            return {"error": "No active training round", "accepted": False}

        round_id = self._current_round.round_id
        if upload.round_id != round_id:
            return {"error": f"Round mismatch: expected {round_id}", "accepted": False}

        # Record contribution
        self._round_contributions[round_id].append(upload)

        if upload.bank_id not in self._current_round.participating_banks:
            self._current_round.participating_banks.append(upload.bank_id)

        # Update bank metadata
        if upload.bank_id in self._banks:
            self._banks[upload.bank_id]["last_contribution_at"] = datetime.now(timezone.utc)
            self._banks[upload.bank_id]["total_rounds_participated"] += 1

        self._current_round.total_samples += upload.local_sample_count
        self._current_round.privacy_budget_consumed += upload.dp_epsilon_spent

        logger.info(
            "Received weight update from bank %s for round %s — %d samples, loss=%.4f",
            upload.bank_id, round_id, upload.local_sample_count, upload.local_loss,
        )

        return {
            "accepted": True,
            "round_id": round_id,
            "total_contributions": len(self._round_contributions[round_id]),
            "total_samples": self._current_round.total_samples,
        }

    def aggregate_weights(self) -> GlobalModelResponse | None:
        """Perform Federated Averaging (FedAvg) on all received weight updates.

        w_global = Σ (n_k / n_total) * w_k

        Returns the aggregated global model weights.
        """
        if self._current_round is None:
            return None

        round_id = self._current_round.round_id
        contributions = self._round_contributions.get(round_id, [])

        if not contributions:
            logger.warning("No contributions received for round %s", round_id)
            return None

        self._current_round.status = TrainingRoundStatus.AGGREGATING

        total_samples = sum(c.local_sample_count for c in contributions)
        if total_samples == 0:
            total_samples = len(contributions)

        # Collect all layer names from first contribution
        layer_names = list(contributions[0].layer_weights.keys())
        bias_names = list(contributions[0].layer_biases.keys())

        # Weighted average of weight matrices
        aggregated_weights: dict[str, np.ndarray] = {}
        for layer in layer_names:
            weighted_sum = None
            for contrib in contributions:
                weight_fraction = contrib.local_sample_count / total_samples
                arr = np.array(contrib.layer_weights[layer], dtype=np.float64)
                if weighted_sum is None:
                    weighted_sum = arr * weight_fraction
                else:
                    weighted_sum += arr * weight_fraction
            if weighted_sum is not None:
                aggregated_weights[layer] = weighted_sum

        # Weighted average of bias vectors
        aggregated_biases: dict[str, np.ndarray] = {}
        for layer in bias_names:
            weighted_sum = None
            for contrib in contributions:
                if layer in contrib.layer_biases:
                    weight_fraction = contrib.local_sample_count / total_samples
                    arr = np.array(contrib.layer_biases[layer], dtype=np.float64)
                    if weighted_sum is None:
                        weighted_sum = arr * weight_fraction
                    else:
                        weighted_sum += arr * weight_fraction
            if weighted_sum is not None:
                aggregated_biases[layer] = weighted_sum

        # Update global model
        self._global_weights = {k: v.tolist() for k, v in aggregated_weights.items()}
        self._global_biases = {k: v.tolist() for k, v in aggregated_biases.items()}

        round_number = self._current_round.round_number
        self._global_model_version = f"v1.{round_number}.0"

        # Compute aggregated loss
        agg_loss = sum(c.local_loss * c.local_sample_count for c in contributions) / total_samples

        # Finalize round
        now = datetime.now(timezone.utc)
        self._current_round.status = TrainingRoundStatus.COMPLETED
        self._current_round.completed_at = now
        self._current_round.aggregated_loss = agg_loss
        self._current_round.global_model_version = self._global_model_version

        logger.info(
            "FedAvg aggregation complete — round %s, participants=%d, total_samples=%d, agg_loss=%.4f, model=%s",
            round_id, len(contributions), total_samples, agg_loss, self._global_model_version,
        )

        response = GlobalModelResponse(
            round_id=round_id,
            round_number=round_number,
            layer_weights=self._global_weights,
            layer_biases=self._global_biases,
            total_participants=len(contributions),
            total_samples=total_samples,
            aggregated_loss=agg_loss,
            aggregated_at=now,
        )

        # Clear current round
        self._current_round = None

        return response

    def get_global_model(self) -> GlobalModelResponse | None:
        """Get the latest aggregated global model weights."""
        if not self._global_weights:
            return None

        last_round = self._rounds[-1] if self._rounds else None
        return GlobalModelResponse(
            round_id=last_round.round_id if last_round else "INITIAL",
            round_number=last_round.round_number if last_round else 0,
            layer_weights=self._global_weights,
            layer_biases=self._global_biases,
            total_participants=len(self._banks),
            total_samples=last_round.total_samples if last_round else 0,
            aggregated_loss=last_round.aggregated_loss if last_round else 0.0,
            aggregated_at=last_round.completed_at or datetime.now(timezone.utc) if last_round else datetime.now(timezone.utc),
        )

    # ------------------------------------------------------------------
    # Platform Status
    # ------------------------------------------------------------------

    def get_platform_status(self) -> FederatedPlatformStatus:
        """Get the overall status of the federated learning platform."""
        active_count = sum(1 for b in self._banks.values() if b["status"] == BankStatus.ACTIVE.value)
        elapsed = (datetime.now(timezone.utc) - self._started_at).total_seconds()

        return FederatedPlatformStatus(
            is_active=True,
            registered_banks=len(self._banks),
            active_banks=active_count,
            total_training_rounds=len(self._rounds),
            current_round=self._current_round,
            global_model_version=self._global_model_version,
            total_cross_bank_alerts=self._total_cross_bank_alerts,
            total_privacy_budget_consumed=dp_engine.accountant.total_epsilon_spent,
            platform_uptime_seconds=elapsed,
        )

    def increment_cross_bank_alerts(self, count: int = 1) -> None:
        """Increment the cross-bank alert counter."""
        self._total_cross_bank_alerts += count


# Singleton instance
coordinator = FederatedCoordinator()
