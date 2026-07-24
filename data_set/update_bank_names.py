import csv
import hashlib

csv_path = "data_set/transactions_data_set.csv"

bank_prefix_map = {
    "SB": "State Bank of India",
    "YS": "YES Bank",
    "AX": "Axis Bank",
    "ID": "IDFC FIRST Bank",
    "CN": "Canara Bank",
    "PN": "Punjab National Bank",
    "HD": "HDFC Bank",
    "IC": "ICICI Bank",
    "KT": "Kotak Mahindra Bank",
    "UB": "Union Bank of India",
}

default_banks = [
    "State Bank of India",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Kotak Mahindra Bank",
    "YES Bank",
    "Punjab National Bank",
    "Canara Bank",
    "Bank of Baroda",
    "IDFC FIRST Bank",
]

def map_bank(acc_str):
    acc = str(acc_str).strip()
    prefix = acc[:2].upper()
    if prefix in bank_prefix_map:
        return bank_prefix_map[prefix]
    h = int(hashlib.md5(acc.encode("utf-8")).hexdigest(), 16)
    return default_banks[h % len(default_banks)]

rows = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    
    if "bank_name" not in fieldnames:
        fieldnames.append("bank_name")
    if "receiver_bank" not in fieldnames:
        fieldnames.append("receiver_bank")

    for row in reader:
        row["bank_name"] = map_bank(row["account_number"])
        row["receiver_bank"] = map_bank(row["receiver_account"])
        rows.append(row)

# Save to data_set and ml directories
for out_path in ["data_set/transactions_data_set.csv", "ml/transactions.csv"]:
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

print(f"Successfully synthesized and added bank_name & receiver_bank to {len(rows)} records!")
