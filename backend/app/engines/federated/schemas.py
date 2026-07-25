"""
MuleTrace AI — Federated Graph Learning Schemas.

Pydantic models for the federated learning API endpoints covering bank
registration, weight exchange, training round coordination, and
privacy-preserving cross-bank alert correlation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class BankStatus(str, Enum):
    """Registration status of a participating bank."""
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class TrainingRoundStatus(str, Enum):
    """Lifecycle status of a federated training round."""
    INITIATED = "INITIATED"
    COLLECTING = "COLLECTING"
    AGGREGATING = "AGGREGATING"
    DISTRIBUTING = "DISTRIBUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CrossBankAlertSeverity(str, Enum):
    """Severity of a cross-bank correlation alert."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ---------------------------------------------------------------------------
# Bank Registration
# ---------------------------------------------------------------------------

class BankRegistrationRequest(BaseModel):
    """Request payload when a bank registers as a federated participant."""
    bank_code: str = Field(..., min_length=3, max_length=20, description="Unique bank identifier (e.g. 'SBI', 'HDFC')")
    bank_name: str = Field(..., min_length=2, max_length=100)
    endpoint_url: str = Field(..., description="Callback URL for the bank's local trainer endpoint")
    public_key_pem: str = Field(default="", description="PEM-encoded public key for secure aggregation")
    local_account_count: int = Field(default=0, ge=0, description="Number of accounts in this bank's local graph")
    local_transaction_count: int = Field(default=0, ge=0, description="Number of transactions in this bank's local graph")


class BankRegistrationResponse(BaseModel):
    """Response after successful bank registration."""
    bank_id: str
    bank_code: str
    bank_name: str
    status: BankStatus
    registered_at: datetime
    api_token: str = Field(..., description="Bearer token for subsequent API calls")


class RegisteredBankInfo(BaseModel):
    """Public information about a registered bank participant."""
    bank_id: str
    bank_code: str
    bank_name: str
    status: BankStatus
    registered_at: datetime
    last_contribution_at: Optional[datetime] = None
    total_rounds_participated: int = 0
    local_account_count: int = 0
    local_transaction_count: int = 0


# ---------------------------------------------------------------------------
# Model Weight Exchange
# ---------------------------------------------------------------------------

class ModelWeightUpload(BaseModel):
    """Encrypted model weight deltas uploaded by a participating bank."""
    bank_id: str
    round_id: str
    layer_weights: dict[str, list[list[float]]] = Field(
        ..., description="Dictionary mapping layer names to 2D weight matrices"
    )
    layer_biases: dict[str, list[float]] = Field(
        default_factory=dict, description="Dictionary mapping layer names to bias vectors"
    )
    local_sample_count: int = Field(..., ge=1, description="Number of local training samples used")
    local_loss: float = Field(default=0.0, description="Training loss on local data")
    local_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Training accuracy on local data")
    dp_epsilon_spent: float = Field(default=0.0, ge=0.0, description="Differential privacy budget consumed")
    dp_noise_scale: float = Field(default=0.0, ge=0.0, description="Scale of Gaussian noise applied")


class GlobalModelResponse(BaseModel):
    """Aggregated global model weights returned to participating banks."""
    round_id: str
    round_number: int
    layer_weights: dict[str, list[list[float]]]
    layer_biases: dict[str, list[float]]
    total_participants: int
    total_samples: int
    aggregated_loss: float
    aggregated_at: datetime


# ---------------------------------------------------------------------------
# Training Rounds
# ---------------------------------------------------------------------------

class TrainingRoundInfo(BaseModel):
    """Information about a single federated training round."""
    round_id: str
    round_number: int
    status: TrainingRoundStatus
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    participating_banks: list[str] = Field(default_factory=list)
    total_samples: int = 0
    aggregated_loss: float = 0.0
    global_model_version: str = ""
    privacy_budget_consumed: float = 0.0


class InitiateRoundRequest(BaseModel):
    """Request to initiate a new federated training round."""
    min_participants: int = Field(default=2, ge=2, description="Minimum banks required to proceed")
    target_epochs: int = Field(default=5, ge=1, le=50, description="Local training epochs per bank")
    learning_rate: float = Field(default=0.01, gt=0.0, le=1.0)
    dp_epsilon: float = Field(default=1.0, gt=0.0, description="Differential privacy epsilon budget per round")
    dp_delta: float = Field(default=1e-5, gt=0.0, lt=1.0, description="Differential privacy delta parameter")


class InitiateRoundResponse(BaseModel):
    """Response after initiating a new federated training round."""
    round_id: str
    round_number: int
    status: TrainingRoundStatus
    initiated_at: datetime
    min_participants: int
    target_epochs: int
    dp_epsilon: float
    dp_delta: float


# ---------------------------------------------------------------------------
# Privacy-Preserving Cross-Bank Query (PSI)
# ---------------------------------------------------------------------------

class CrossBankQueryRequest(BaseModel):
    """Privacy-preserving query using hashed account identifiers."""
    bank_id: str
    account_hashes: list[str] = Field(
        ..., min_length=1, max_length=500,
        description="List of SHA-256 hashes of (account_number + bank_salt)"
    )


class CrossBankMatch(BaseModel):
    """A single cross-bank hash match result."""
    account_hash: str
    matched_bank_count: int = Field(..., description="Number of banks that flagged this hash")
    aggregate_risk_score: float = Field(..., ge=0.0, le=100.0)
    alert_severity: CrossBankAlertSeverity
    first_flagged_at: datetime


class CrossBankQueryResponse(BaseModel):
    """Response containing privacy-preserving cross-bank matches."""
    query_bank_id: str
    total_hashes_submitted: int
    matches_found: int
    matches: list[CrossBankMatch]
    queried_at: datetime


# ---------------------------------------------------------------------------
# Cross-Bank Alerts
# ---------------------------------------------------------------------------

class CrossBankAlert(BaseModel):
    """Alert generated when multiple banks flag the same hashed entity."""
    alert_id: str
    account_hash: str
    contributing_bank_count: int
    aggregate_risk_score: float
    severity: CrossBankAlertSeverity
    pattern_type: str
    narrative: str
    created_at: datetime
    is_acknowledged: bool = False


# ---------------------------------------------------------------------------
# Federated Platform Status
# ---------------------------------------------------------------------------

class FederatedPlatformStatus(BaseModel):
    """Overall status of the federated learning platform."""
    is_active: bool
    registered_banks: int
    active_banks: int
    total_training_rounds: int
    current_round: Optional[TrainingRoundInfo] = None
    global_model_version: str
    total_cross_bank_alerts: int
    total_privacy_budget_consumed: float
    platform_uptime_seconds: float
