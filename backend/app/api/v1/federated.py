"""
MuleTrace AI — Federated Graph Learning REST API Endpoints.

Provides privacy-preserving multi-bank federated graph learning endpoints:
    - Bank participant registration & authentication
    - Federated training round orchestration (FedAvg)
    - Differential privacy weight uploading and global model distribution
    - Private Set Intersection (PSI) cross-bank alert correlation
"""

from __future__ import annotations


from typing import Optional, Any
from fastapi import APIRouter, Header, HTTPException, Query, status

from app.engines.federated.alert_correlator import alert_correlator
from app.engines.federated.coordinator import coordinator
from app.engines.federated.local_trainer import local_trainer
from app.engines.federated.privacy import dp_engine
from app.engines.federated.schemas import (
    BankRegistrationRequest,
    BankRegistrationResponse,
    CrossBankAlert,
    CrossBankAlertSeverity,
    CrossBankQueryRequest,
    CrossBankQueryResponse,
    FederatedPlatformStatus,
    GlobalModelResponse,
    InitiateRoundRequest,
    InitiateRoundResponse,
    ModelWeightUpload,
    RegisteredBankInfo,
    TrainingRoundInfo,
)

router = APIRouter(prefix="/federated", tags=["Federated Graph Learning"])


# ---------------------------------------------------------------------------
# Platform Status & Registration
# ---------------------------------------------------------------------------

@router.get("/status", response_model=FederatedPlatformStatus, summary="Get federated platform status")
async def get_platform_status() -> FederatedPlatformStatus:
    """Get overall health, registered banks, active round, and DP budget metrics."""
    return coordinator.get_platform_status()


@router.post(
    "/register",
    response_model=BankRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a participating bank",
)
async def register_bank(payload: BankRegistrationRequest) -> BankRegistrationResponse:
    """Register a new bank as a federated graph learning participant."""
    return coordinator.register_bank(payload)


@router.get("/banks", response_model=list[RegisteredBankInfo], summary="List all registered banks")
async def list_banks() -> list[RegisteredBankInfo]:
    """List all registered participating banks and their training statistics."""
    return coordinator.get_registered_banks()


# ---------------------------------------------------------------------------
# Training Round Orchestration (FedAvg)
# ---------------------------------------------------------------------------

@router.post("/rounds/initiate", response_model=InitiateRoundResponse, summary="Initiate a federated training round")
async def initiate_round(payload: InitiateRoundRequest) -> InitiateRoundResponse:
    """Initiate a new federated training round for cross-bank GNN model updates."""
    return coordinator.initiate_round(payload)


@router.get("/rounds/current", response_model=Optional[TrainingRoundInfo], summary="Get active training round")
async def get_current_round() -> Optional[TrainingRoundInfo]:
    """Get information about the currently active training round."""
    return coordinator.get_current_round()


@router.get("/rounds", response_model=list[TrainingRoundInfo], summary="Get all training rounds history")
async def list_rounds() -> list[TrainingRoundInfo]:
    """Get complete history of all federated training rounds."""
    return coordinator.get_round_history()


# ---------------------------------------------------------------------------
# Weight Exchange & Model Aggregation
# ---------------------------------------------------------------------------

@router.post("/weights/upload", summary="Upload noisy model weights")
async def upload_weights(payload: ModelWeightUpload) -> dict[str, Any]:
    """Upload DP-noised local model weight deltas from a participating bank."""
    result = coordinator.receive_weight_update(payload)
    if not result.get("accepted"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))
    return result


@router.post("/weights/aggregate", response_model=Optional[GlobalModelResponse], summary="Execute FedAvg aggregation")
async def aggregate_weights() -> Optional[GlobalModelResponse]:
    """Execute Federated Averaging (FedAvg) on current round uploaded weights."""
    result = coordinator.aggregate_weights()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot aggregate — no active round or no weight updates received.",
        )
    return result


@router.get("/global-model", response_model=Optional[GlobalModelResponse], summary="Download latest global model")
async def get_global_model() -> Optional[GlobalModelResponse]:
    """Download the latest aggregated global GNN model weights."""
    model = coordinator.get_global_model()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No global model weights available yet.")
    return model


# ---------------------------------------------------------------------------
# Local GNN Trainer Trigger
# ---------------------------------------------------------------------------

@router.post("/train-local", summary="Run local GNN training on Neo4j graph")
async def train_local_gnn(epochs: int = Query(default=5, ge=1, le=50)) -> dict[str, Any]:
    """Trigger a local GraphSAGE GNN training run on the local Neo4j subgraph.

    Extracts graph topology, trains 2-layer GraphSAGE, and returns weight deltas.
    """
    # Fetch global model weights if available
    global_model = coordinator.get_global_model()
    g_weights = global_model.layer_weights if global_model else None
    g_biases = global_model.layer_biases if global_model else None

    # Run local trainer
    train_res = await local_trainer.train(
        epochs=epochs,
        learning_rate=0.01,
        global_weights=g_weights,
        global_biases=g_biases,
    )

    # Apply Differential Privacy noise before returning weights
    noisy_weights, noise_scale = dp_engine.add_gaussian_noise(
        weights=train_res.layer_weights,
        epsilon=1.0,
        delta=1e-5,
    )
    noisy_biases = dp_engine.add_noise_to_biases(
        biases=train_res.layer_biases,
        epsilon=1.0,
        delta=1e-5,
    )

    return {
        "status": "SUCCESS",
        "epochs_completed": train_res.epochs_completed,
        "local_loss": train_res.local_loss,
        "local_accuracy": train_res.local_accuracy,
        "num_samples": train_res.num_samples,
        "dp_epsilon_spent": 1.0,
        "dp_noise_scale": noise_scale,
        "noisy_layer_weights": noisy_weights,
        "noisy_layer_biases": noisy_biases,
    }


# ---------------------------------------------------------------------------
# Privacy-Preserving Cross-Bank Queries (PSI) & Alerts
# ---------------------------------------------------------------------------

@router.post("/query-psi", response_model=CrossBankQueryResponse, summary="Query cross-bank account hashes (PSI)")
async def query_cross_bank_hashes(payload: CrossBankQueryRequest) -> CrossBankQueryResponse:
    """Execute a Private Set Intersection (PSI) query using salted account hashes."""
    return alert_correlator.process_query(payload)


@router.post("/report-hashes", response_model=list[CrossBankAlert], summary="Report flagged account hashes")
async def report_flagged_hashes(
    bank_id: str = Query(...),
    account_hashes: list[str] = Query(...),
    pattern_type: str = Query(default="Mule Chain"),
    risk_score: float = Query(default=85.0, ge=0.0, le=100.0),
) -> list[CrossBankAlert]:
    """Report a batch of flagged account hashes. Triggers cross-bank alert correlation."""
    new_alerts = alert_correlator.report_flagged_accounts(
        bank_id=bank_id,
        account_hashes=account_hashes,
        pattern_type=pattern_type,
        risk_score=risk_score,
    )
    coordinator.increment_cross_bank_alerts(len(new_alerts))
    return new_alerts


@router.get("/alerts", response_model=list[CrossBankAlert], summary="Get cross-bank mule network alerts")
async def get_cross_bank_alerts(
    min_severity: Optional[CrossBankAlertSeverity] = Query(default=None),
) -> list[CrossBankAlert]:
    """Get all privacy-preserving cross-bank mule network alerts."""
    return alert_correlator.get_all_alerts(min_severity=min_severity)


@router.post("/alerts/{alert_id}/acknowledge", summary="Acknowledge a cross-bank alert")
async def acknowledge_cross_bank_alert(alert_id: str) -> dict[str, Any]:
    """Mark a cross-bank alert as acknowledged by an investigator."""
    success = alert_correlator.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found.")
    return {"alert_id": alert_id, "acknowledged": True}
