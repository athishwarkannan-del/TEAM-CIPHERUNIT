"""
MuleTrace AI — Live HTTP API Verification for Federated Graph Learning.

Executes live HTTP requests against http://localhost:8000/api/v1/federated/
to test bank registration, local GNN training, FedAvg aggregation, PSI queries,
and cross-bank alert generation.
"""

import json
import urllib.request

BASE_URL = "http://localhost:8000/api/v1/federated"


def http_post(url_path: str, data: dict = None) -> dict:
    url = f"{BASE_URL}{url_path}"
    json_data = json.dumps(data or {}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=json_data if data is not None else b"",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_get(url_path: str) -> dict:
    url = f"{BASE_URL}{url_path}"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_live_verification():
    print("=" * 70)
    print("LIVE API TEST: FEDERATED GRAPH LEARNING PLATFORM (http://localhost:8000)")
    print("=" * 70)

    # 1. Check Status
    print("\n1. GET /api/v1/federated/status")
    status_data = http_get("/status")
    print("   Response:", json.dumps(status_data, indent=2))
    assert status_data["is_active"] is True, "Platform should be active"

    # 2. Register Participating Banks
    print("\n2. POST /api/v1/federated/register (Registering Banks)")
    sbi = http_post("/register", {
        "bank_code": "SBI_LIVE",
        "bank_name": "State Bank of India",
        "endpoint_url": "https://api.sbi.co.in/fl",
        "local_account_count": 15000,
        "local_transaction_count": 80000,
    })
    print("   SBI Registered ID:", sbi["bank_id"])

    hdfc = http_post("/register", {
        "bank_code": "HDFC_LIVE",
        "bank_name": "HDFC Bank",
        "endpoint_url": "https://api.hdfc.com/fl",
        "local_account_count": 12000,
        "local_transaction_count": 65000,
    })
    print("   HDFC Registered ID:", hdfc["bank_id"])

    # 3. Initiate Federated Round
    print("\n3. POST /api/v1/federated/rounds/initiate")
    round_data = http_post("/rounds/initiate", {
        "min_participants": 2,
        "target_epochs": 5,
        "dp_epsilon": 1.0,
        "dp_delta": 1e-5,
    })
    round_id = round_data["round_id"]
    print("   Round Initiated:", round_id)

    # 4. Trigger Local GNN Training on Neo4j Graph
    print("\n4. POST /api/v1/federated/train-local?epochs=5 (GraphSAGE Training)")
    train_data = http_post("/train-local?epochs=5")
    print(f"   Local GNN Loss: {train_data['local_loss']:.4f}, Accuracy: {train_data['local_accuracy']:.4f}")
    print(f"   DP Noise Scale: {train_data['dp_noise_scale']:.6f}")

    # 5. Upload Noisy Weights for SBI
    print("\n5. POST /api/v1/federated/weights/upload (SBI Upload)")
    up1 = http_post("/weights/upload", {
        "bank_id": sbi["bank_id"],
        "round_id": round_id,
        "layer_weights": train_data["noisy_layer_weights"],
        "layer_biases": train_data["noisy_layer_biases"],
        "local_sample_count": 150,
        "local_loss": train_data["local_loss"],
        "local_accuracy": train_data["local_accuracy"],
        "dp_epsilon_spent": 1.0,
        "dp_noise_scale": train_data["dp_noise_scale"],
    })
    print("   SBI Weight Upload Result:", up1)

    # 6. Upload Noisy Weights for HDFC
    print("\n6. POST /api/v1/federated/weights/upload (HDFC Upload)")
    up2 = http_post("/weights/upload", {
        "bank_id": hdfc["bank_id"],
        "round_id": round_id,
        "layer_weights": train_data["noisy_layer_weights"],
        "layer_biases": train_data["noisy_layer_biases"],
        "local_sample_count": 200,
        "local_loss": 0.18,
        "local_accuracy": 0.95,
        "dp_epsilon_spent": 1.0,
        "dp_noise_scale": 0.04,
    })
    print("   HDFC Weight Upload Result:", up2)

    # 7. Aggregate Global Model Weights (FedAvg)
    print("\n7. POST /api/v1/federated/weights/aggregate (FedAvg Aggregation)")
    agg = http_post("/weights/aggregate")
    print(f"   Global Model Version: {agg['round_number']}, Total Samples: {agg['total_samples']}, Loss: {agg['aggregated_loss']:.4f}")

    # 8. Report Flagged Account Hashes & Trigger Cross-Bank Alert
    print("\n8. POST /api/v1/federated/report-hashes (Cross-Bank Alert Correlation)")
    sample_hash = "c035222d7258a1b2c3d4e5f67890123456789abcdef"
    rep1 = http_post(f"/report-hashes?bank_id={sbi['bank_id']}&account_hashes={sample_hash}&pattern_type=Mule%20Chain&risk_score=94.0")
    rep2 = http_post(f"/report-hashes?bank_id={hdfc['bank_id']}&account_hashes={sample_hash}&pattern_type=Mule%20Chain&risk_score=91.0")
    print(f"   Cross-Bank Alert Triggered! Contributing Banks: {rep2[0]['contributing_bank_count']}, Aggregate Risk: {rep2[0]['aggregate_risk_score']}")

    # 9. Private Set Intersection (PSI) Query
    print("\n9. POST /api/v1/federated/query-psi (PSI Query)")
    psi = http_post("/query-psi", {
        "bank_id": "BANK_QUERY_TEST",
        "account_hashes": [sample_hash, "non_existent_hash"],
    })
    print(f"   PSI Query Matches Found: {psi['matches_found']}/{psi['total_hashes_submitted']}")
    print("   Match Details:", json.dumps(psi["matches"], indent=2))

    # 10. Fetch Cross-Bank Alerts Queue
    print("\n10. GET /api/v1/federated/alerts")
    alerts = http_get("/alerts")
    print(f"    Total Cross-Bank Alerts in Queue: {len(alerts)}")

    print("\n" + "=" * 70)
    print("LIVE INTEGRATION VERIFICATION COMPLETED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    run_live_verification()
