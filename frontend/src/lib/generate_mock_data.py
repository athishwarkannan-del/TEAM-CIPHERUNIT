import csv
import json

csv_path = "data_set/transactions_data_set.csv"

records = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append(row)

nodes_dict = {}
edges_list = []

for i, r in enumerate(records):
    # Sender Node
    acc = r["account_number"]
    if acc not in nodes_dict:
        nodes_dict[acc] = {
            "id": f"acc-{acc}",
            "label": f"{acc} — {r['name']}",
            "type": "account",
            "risk_score": round(float(r["risk_score"])),
            "account_number": acc,
            "customer_name": r["name"],
            "bank": r["bank_name"],
            "phone": f"+91 {r['mobile_number']}",
            "device": r["device"],
            "ip": r["ip_address"],
            "location": f"Pincode {r['pincode']}",
            "last_transaction": f"₹{float(r['amount']):,.2f} via {r['trans_type']}",
            "total_received": round(float(r["amount"]) * 1.2),
            "total_sent": round(float(r["amount"])),
            "is_mule": r["is_fraud"] == "1",
            "community_id": "COMMUNITY-A12" if r["is_fraud"] == "1" else "COMMUNITY-B04",
        }

    # Receiver Node
    r_acc = r["receiver_account"]
    if r_acc not in nodes_dict:
        nodes_dict[r_acc] = {
            "id": f"acc-{r_acc}",
            "label": f"{r_acc} — {r['receiver_name']}",
            "type": "victim" if r["fraud_type"] == "Phishing Fraud" else "account",
            "risk_score": round(float(r["risk_score"]) * 0.8) if r["is_fraud"] == "1" else round(float(r["risk_score"])),
            "account_number": r_acc,
            "customer_name": r["receiver_name"],
            "bank": r["receiver_bank"],
            "location": f"Pincode {r['receiver_pincode']}",
            "is_mule": False,
            "community_id": "COMMUNITY-A12" if r["is_fraud"] == "1" else "COMMUNITY-B04",
        }

    # Device Node
    dev = r["device"]
    dev_id = f"dev-{hash(dev) % 10000}"
    if dev_id not in nodes_dict:
        nodes_dict[dev_id] = {
            "id": dev_id,
            "label": dev,
            "type": "device",
            "risk_score": round(float(r["device_risk_score"])),
            "device": dev,
            "community_id": "COMMUNITY-A12",
        }

    # IP Node
    ip = r["ip_address"]
    ip_id = f"ip-{ip.replace('.', '_')}"
    if ip_id not in nodes_dict:
        nodes_dict[ip_id] = {
            "id": ip_id,
            "label": f"{ip} (Network)",
            "type": "ip",
            "risk_score": round(float(r["network_risk_score"])),
            "ip": ip,
            "community_id": "COMMUNITY-A12",
        }

    # Edges
    edges_list.append({
        "source": f"acc-{acc}",
        "target": f"acc-{r_acc}",
        "relationship": "TRANSFERRED_FUNDS",
        "amount": round(float(r["amount"])),
        "channel": r["trans_type"],
        "timestamp": r["timestamp"],
    })

    if r["is_rooted_or_emulator"] == "1" or r["fraud_type"] == "Shared Device":
        edges_list.append({
            "source": f"acc-{acc}",
            "target": dev_id,
            "relationship": "SHARED_DEVICE",
        })

    if r["is_vpn_or_proxy"] == "1":
        edges_list.append({
            "source": f"acc-{acc}",
            "target": ip_id,
            "relationship": "SHARED_IP",
        })

# Format mockGraph TS object
nodes_json = json.dumps(list(nodes_dict.values())[:45], indent=2)
edges_json = json.dumps(edges_list[:60], indent=2)

print(f"Generated {len(nodes_dict)} nodes and {len(edges_list)} edges!")

# Update mock-data.ts header
with open("frontend/src/lib/mock-data.ts", "r", encoding="utf-8") as f:
    content = f.read()

# Replace mockGraph nodes & edges
graph_start = content.find("export const mockGraph: GraphResponse = {")
if graph_start != -1:
    graph_end = content.find("export const mockGeo: GeoIntelligenceResponse", graph_start)
    new_graph = f"export const mockGraph: GraphResponse = {{\n  nodes: {nodes_json},\n  edges: {edges_json},\n  community_id: \"COMMUNITY-A12\",\n}};\n\n"
    new_content = content[:graph_start] + new_graph + content[graph_end:]
    with open("frontend/src/lib/mock-data.ts", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Updated frontend/src/lib/mock-data.ts with data_set transactions!")
