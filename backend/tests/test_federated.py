"""
MuleTrace AI — Federated Graph Learning Unit Tests.

Tests bank registration, GNN local training, differential privacy noise injection,
FedAvg weight aggregation, Private Set Intersection (PSI), and cross-bank alerts.
"""

import pytest
from fastapi.testclient import TestClient

from app.engines.federated.alert_correlator import alert_correlator
from app.engines.federated.coordinator import coordinator
from app.engines.federated.local_trainer import local_trainer
from app.engines.federated.privacy import dp_engine, secure_agg_engine
from app.main import app

client = TestClient(app)


def test_federated_platform_status():
    """Test GET /api/v1/federated/status endpoint."""
    response = client.get("/api/v1/federated/status")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True
    assert "registered_banks" in data
    assert "global_model_version" in data


def test_bank_registration():
    """Test POST /api/v1/federated/register endpoint."""
    payload = {
        "bank_code": "SBI",
        "bank_name": "State Bank of India",
        "endpoint_url": "https://api.sbi.co.in/fl",
        "local_account_count": 10000,
        "local_transaction_count": 50000,
    }
    response = client.post("/api/v1/federated/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["bank_code"] == "SBI"
    assert data["status"] == "ACTIVE"
    assert "api_token" in data


def test_list_banks():
    """Test GET /api/v1/federated/banks endpoint."""
    response = client.get("/api/v1/federated/banks")
    assert response.status_code == 200
    banks = response.json()
    assert isinstance(banks, list)
    assert len(banks) >= 1


def test_initiate_round_and_upload():
    """Test full federated round lifecycle: initiate -> train-local -> upload -> aggregate."""
    # 1. Register two banks
    r1 = client.post("/api/v1/federated/register", json={
        "bank_code": "HDFC", "bank_name": "HDFC Bank", "endpoint_url": "https://api.hdfc.com/fl",
    })
    b1_id = r1.json()["bank_id"]

    r2 = client.post("/api/v1/federated/register", json={
        "bank_code": "ICICI", "bank_name": "ICICI Bank", "endpoint_url": "https://api.icici.com/fl",
    })
    b2_id = r2.json()["bank_id"]

    # 2. Initiate round
    init_res = client.post("/api/v1/federated/rounds/initiate", json={
        "min_participants": 2, "target_epochs": 3, "learning_rate": 0.01, "dp_epsilon": 1.0, "dp_delta": 1e-5,
    })
    assert init_res.status_code == 200
    round_id = init_res.json()["round_id"]

    # 3. Train local GNN & Upload weights for Bank 1
    t1 = client.post("/api/v1/federated/train-local?epochs=3")
    assert t1.status_code == 200
    train1_data = t1.json()

    u1 = client.post("/api/v1/federated/weights/upload", json={
        "bank_id": b1_id,
        "round_id": round_id,
        "layer_weights": train1_data["noisy_layer_weights"],
        "layer_biases": train1_data["noisy_layer_biases"],
        "local_sample_count": 50,
        "local_loss": train1_data["local_loss"],
        "local_accuracy": train1_data["local_accuracy"],
        "dp_epsilon_spent": 1.0,
        "dp_noise_scale": train1_data["dp_noise_scale"],
    })
    assert u1.status_code == 200

    # Upload weights for Bank 2
    u2 = client.post("/api/v1/federated/weights/upload", json={
        "bank_id": b2_id,
        "round_id": round_id,
        "layer_weights": train1_data["noisy_layer_weights"],
        "layer_biases": train1_data["noisy_layer_biases"],
        "local_sample_count": 75,
        "local_loss": 0.25,
        "local_accuracy": 0.92,
        "dp_epsilon_spent": 1.0,
        "dp_noise_scale": 0.05,
    })
    assert u2.status_code == 200

    # 4. Aggregate weights
    agg_res = client.post("/api/v1/federated/weights/aggregate")
    assert agg_res.status_code == 200
    agg_data = agg_res.json()
    assert agg_data["total_participants"] == 2
    assert agg_data["total_samples"] == 125


def test_psi_and_cross_bank_alerts():
    """Test Private Set Intersection (PSI) query and cross-bank alert generation."""
    # Hash an account number
    acc = "409900100100"
    acc_hash = alert_correlator.hash_account_number(acc)

    # Bank 1 reports hash
    client.post(f"/api/v1/federated/report-hashes?bank_id=BANK-SBI&account_hashes={acc_hash}&pattern_type=Mule%20Chain&risk_score=92.0")

    # Bank 2 reports same hash -> triggers cross-bank alert
    rep_res = client.post(f"/api/v1/federated/report-hashes?bank_id=BANK-HDFC&account_hashes={acc_hash}&pattern_type=Mule%20Chain&risk_score=88.0")
    assert rep_res.status_code == 200
    alerts = rep_res.json()
    assert len(alerts) >= 1
    assert alerts[0]["contributing_bank_count"] == 2

    # Query PSI
    psi_res = client.post("/api/v1/federated/query-psi", json={
        "bank_id": "BANK-ICICI",
        "account_hashes": [acc_hash, "non_existent_hash_12345"],
    })
    assert psi_res.status_code == 200
    psi_data = psi_res.json()
    assert psi_data["matches_found"] == 1
    assert psi_data["matches"][0]["matched_bank_count"] == 2


def test_get_cross_bank_alerts_list():
    """Test GET /api/v1/federated/alerts endpoint."""
    response = client.get("/api/v1/federated/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
