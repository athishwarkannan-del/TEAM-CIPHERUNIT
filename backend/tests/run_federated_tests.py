"""
MuleTrace AI — Federated Learning Direct Test Runner.

Executes test suite assertions directly without relying on external pytest CLI.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.engines.federated.alert_correlator import alert_correlator
from app.main import app


def run_all_tests():
    print("=" * 60)
    print("RUNNING FEDERATED GRAPH LEARNING TEST SUITE")
    print("=" * 60)

    client = TestClient(app)

    # Test 1: Platform status
    print("[1/5] Testing GET /api/v1/federated/status...")
    res = client.get("/api/v1/federated/status")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert data["is_active"] is True
    print("  [OK] Platform status verified: active=True, banks=%d" % data["registered_banks"])

    # Test 2: Bank Registration
    print("[2/5] Testing Bank Registration & List...")
    r_sbi = client.post("/api/v1/federated/register", json={
        "bank_code": "SBI", "bank_name": "State Bank of India", "endpoint_url": "https://api.sbi.co.in/fl",
    })
    assert r_sbi.status_code == 201
    sbi_id = r_sbi.json()["bank_id"]

    r_hdfc = client.post("/api/v1/federated/register", json={
        "bank_code": "HDFC", "bank_name": "HDFC Bank", "endpoint_url": "https://api.hdfc.com/fl",
    })
    assert r_hdfc.status_code == 201
    hdfc_id = r_hdfc.json()["bank_id"]

    r_icici = client.post("/api/v1/federated/register", json={
        "bank_code": "ICICI", "bank_name": "ICICI Bank", "endpoint_url": "https://api.icici.com/fl",
    })
    assert r_icici.status_code == 201
    icici_id = r_icici.json()["bank_id"]
    print("  [OK] Registered 3 banks successfully: %s, %s, %s" % (sbi_id, hdfc_id, icici_id))

    # Test 3: Federated Round & Local GNN Training & FedAvg
    print("[3/5] Testing Federated Round & FedAvg Aggregation...")
    init_res = client.post("/api/v1/federated/rounds/initiate", json={
        "min_participants": 2, "target_epochs": 3, "dp_epsilon": 1.0, "dp_delta": 1e-5,
    })
    assert init_res.status_code == 200
    round_id = init_res.json()["round_id"]

    # Local training & upload for Bank 1
    t1 = client.post("/api/v1/federated/train-local?epochs=3")
    assert t1.status_code == 200
    t1_data = t1.json()

    u1 = client.post("/api/v1/federated/weights/upload", json={
        "bank_id": sbi_id,
        "round_id": round_id,
        "layer_weights": t1_data["noisy_layer_weights"],
        "layer_biases": t1_data["noisy_layer_biases"],
        "local_sample_count": 50,
        "local_loss": t1_data["local_loss"],
        "local_accuracy": t1_data["local_accuracy"],
        "dp_epsilon_spent": 1.0,
        "dp_noise_scale": t1_data["dp_noise_scale"],
    })
    assert u1.status_code == 200

    # Upload for Bank 2
    u2 = client.post("/api/v1/federated/weights/upload", json={
        "bank_id": hdfc_id,
        "round_id": round_id,
        "layer_weights": t1_data["noisy_layer_weights"],
        "layer_biases": t1_data["noisy_layer_biases"],
        "local_sample_count": 75,
        "local_loss": 0.22,
        "local_accuracy": 0.94,
        "dp_epsilon_spent": 1.0,
        "dp_noise_scale": 0.05,
    })
    assert u2.status_code == 200

    # FedAvg aggregation
    agg_res = client.post("/api/v1/federated/weights/aggregate")
    assert agg_res.status_code == 200
    agg_data = agg_res.json()
    assert agg_data["total_participants"] == 2
    assert agg_data["total_samples"] == 125
    print("  [OK] FedAvg aggregation complete: total_samples=125, model_version=%s" % agg_data["round_number"])

    # Test 4: PSI & Cross-Bank Alert Correlation
    print("[4/5] Testing PSI Query & Cross-Bank Alert Correlation...")
    acc_hash = alert_correlator.hash_account_number("409900100100")

    # SBI reports hash
    client.post(f"/api/v1/federated/report-hashes?bank_id={sbi_id}&account_hashes={acc_hash}&pattern_type=Mule%20Chain&risk_score=95.0")

    # HDFC reports same hash -> triggers cross-bank alert
    rep2 = client.post(f"/api/v1/federated/report-hashes?bank_id={hdfc_id}&account_hashes={acc_hash}&pattern_type=Mule%20Chain&risk_score=89.0")
    assert rep2.status_code == 200
    alerts = rep2.json()
    assert len(alerts) >= 1
    assert alerts[0]["contributing_bank_count"] == 2
    print("  [OK] Cross-bank alert triggered across 2 banks for hash %s..." % acc_hash[:12])

    # PSI query
    psi_res = client.post("/api/v1/federated/query-psi", json={
        "bank_id": icici_id,
        "account_hashes": [acc_hash, "unknown_hash_999"],
    })
    assert psi_res.status_code == 200
    psi_data = psi_res.json()
    assert psi_data["matches_found"] == 1
    print("  [OK] PSI query matched hash successfully without revealing raw account numbers!")

    # Test 5: Fetch Cross-Bank Alerts List
    print("[5/5] Testing GET /api/v1/federated/alerts...")
    alerts_res = client.get("/api/v1/federated/alerts")
    assert alerts_res.status_code == 200
    all_alerts = alerts_res.json()
    assert len(all_alerts) >= 1
    print("  [OK] Retrieved %d cross-bank alerts from platform queue." % len(all_alerts))

    print("\n" + "=" * 60)
    print("ALL 5 FEDERATED GRAPH LEARNING TESTS PASSED 100% CLEANLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
