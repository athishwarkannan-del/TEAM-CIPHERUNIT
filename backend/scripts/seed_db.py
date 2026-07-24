"""
MuleTrace AI — Synthetic Banking Dataset Seeder.

Populates Supabase PostgreSQL database with realistic Indian banking dataset
embedded with synthetic fraud scenarios:
    - Mule Chain (5-step rapid fund pass-through)
    - Fan-In Collector (20 senders -> 1 collector)
    - Fan-Out Distributor (1 distributor -> 15 receivers)
    - Smurfing / Structuring (Multiple transfers under ₹50,000)
    - Shared Device & Shared IP patterns

Usage:
    cd backend
    python scripts/seed_db.py
"""

import asyncio
import logging
import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent path to allow imports when running script directly
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config.settings import settings
import app.database.postgres as pg
from app.models.account import Account
from app.models.alert import Alert
from app.models.atm import ATM
from app.models.beneficiary import Beneficiary
from app.models.branch import Branch
from app.models.case import Case
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.report import Report
from app.models.rule import Rule
from app.models.transaction import Transaction

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("seed_db")


async def seed_data() -> None:
    """Execute full database seeding sequence."""
    logger.info("Initializing database connection for seeding...")
    pg.init_engine()

    if pg.async_session_factory is None:
        raise RuntimeError("Database session factory failed to initialize")

    async with pg.async_session_factory() as session:
        # Check if database already has accounts
        stmt = select(Account).limit(1)
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            logger.warning("Database already contains account records! Skipping seed to avoid duplicate data.")
            await pg.dispose_engine()
            return

        logger.info("Starting database seeding...")

        # ── 1. Create Bank Branches ─────────────────────────────────────────
        branches_data = [
            {"branch_code": "BR-MUM-01", "branch_name": "Nariman Point Main", "bank_name": "State Bank of India", "ifsc_code": "SBIN0000300", "city": "Mumbai", "state": "Maharashtra", "latitude": 18.9256, "longitude": 72.8242},
            {"branch_code": "BR-MUM-02", "branch_name": "Bandra Kurla Complex", "bank_name": "HDFC Bank", "ifsc_code": "HDFC0000123", "city": "Mumbai", "state": "Maharashtra", "latitude": 19.0674, "longitude": 72.8687},
            {"branch_code": "BR-DEL-01", "branch_name": "Connaught Place Branch", "bank_name": "ICICI Bank", "ifsc_code": "ICIC0000007", "city": "Delhi", "state": "Delhi", "latitude": 28.6315, "longitude": 77.2167},
            {"branch_code": "BR-BLR-01", "branch_name": "MG Road Digital Hub", "bank_name": "Axis Bank", "ifsc_code": "UTIB0000010", "city": "Bengaluru", "state": "Karnataka", "latitude": 12.9756, "longitude": 77.6083},
            {"branch_code": "BR-HYD-01", "branch_name": "HITEC City Branch", "bank_name": "State Bank of India", "ifsc_code": "SBIN0011564", "city": "Hyderabad", "state": "Telangana", "latitude": 17.4435, "longitude": 78.3772},
        ]
        branches = [Branch(**b) for b in branches_data]
        session.add_all(branches)
        await session.flush()
        logger.info("Created %d bank branches", len(branches))

        # ── 2. Create Detection Rules ───────────────────────────────────────
        rules_data = [
            {"rule_code": "R001", "rule_name": "High Velocity Transactions", "pattern_name": "High Velocity", "description": ">20 transactions within 1 hour", "risk_score_contribution": 25, "threshold_value": 20.0, "time_window_minutes": 60},
            {"rule_code": "R002", "rule_name": "Fan-In Aggregation", "pattern_name": "Fan In", "description": ">10 unique senders to 1 collector in 24h", "risk_score_contribution": 30, "threshold_value": 10.0, "time_window_minutes": 1440},
            {"rule_code": "R003", "rule_name": "Fan-Out Dispersion", "pattern_name": "Fan Out", "description": ">10 unique receivers from 1 distributor in 24h", "risk_score_contribution": 30, "threshold_value": 10.0, "time_window_minutes": 1440},
            {"rule_code": "R004", "rule_name": "Mule Chain Rapid Pass-Through", "pattern_name": "Mule Chain", "description": ">90% pass-through within 15 minutes", "risk_score_contribution": 40, "threshold_value": 0.90, "time_window_minutes": 15},
            {"rule_code": "R005", "rule_name": "Smurfing / Structuring", "pattern_name": "Smurfing", "description": "Multiple transfers between ₹48,000 and ₹49,999", "risk_score_contribution": 35, "threshold_value": 49000.0, "time_window_minutes": 1440},
            {"rule_code": "R006", "rule_name": "Shared Hardware Device", "pattern_name": "Shared Device", "description": ">3 accounts accessed from same device fingerprint", "risk_score_contribution": 35, "threshold_value": 3.0, "time_window_minutes": 10080},
            {"rule_code": "R007", "rule_name": "Impossible Travel Velocity", "pattern_name": "Impossible Travel", "description": "Consecutive transactions >500 km apart within 1 hour", "risk_score_contribution": 45, "threshold_value": 500.0, "time_window_minutes": 60},
        ]
        rules = [Rule(**r) for r in rules_data]
        session.add_all(rules)
        await session.flush()
        logger.info("Created %d detection rules", len(rules))

        # ── 3. Create Accounts ──────────────────────────────────────────────
        names = [
            "Aarav Sharma", "Priya Patel", "Rohan Mehta", "Ananya Iyer", "Vikram Singh",
            "Kavya Reddy", "Aditya Nair", "Sneha Kulkarni", "Rahul Verma", "Neha Gupta",
            "Siddharth Rao", "Pooja Joshi", "Manish Kumar", "Divya Agarwal", "Karan Malhotra",
            "Ritu Deshmukh", "Amit Trivedi", "Meera Saxena", "Suresh Pillai", "Deepika Roy",
        ]

        now = datetime.now(timezone.utc)
        accounts: list[Account] = []

        for i, name in enumerate(names):
            acc_num = f"409900100{i+100:03d}"
            cif_id = f"CIF99{i+1000:04d}"
            branch = branches[i % len(branches)]

            # Determine risk level for demonstration
            risk_score = random.randint(10, 45)
            is_mule = False
            risk_level = "LOW"

            if i in (0, 1, 2, 3, 4):  # High risk mule accounts
                risk_score = random.randint(85, 98)
                is_mule = True
                risk_level = "CRITICAL" if risk_score >= 90 else "HIGH"
            elif i in (5, 6, 7):
                risk_score = random.randint(65, 80)
                risk_level = "HIGH"

            acc = Account(
                account_number=acc_num,
                customer_id=cif_id,
                customer_name=name,
                account_type="savings" if i % 2 == 0 else "current",
                currency="INR",
                balance=round(random.uniform(5000.0, 450000.0), 2),
                risk_score=risk_score,
                risk_level=risk_level,
                is_flagged_mule=is_mule,
                opened_at=now - timedelta(days=random.randint(10, 365)),
                branch_id=branch.id,
            )
            accounts.append(acc)

        session.add_all(accounts)
        await session.flush()
        logger.info("Created %d bank accounts", len(accounts))

        # ── 4. Create Devices & IP Addresses ────────────────────────────────
        shared_device_fp = "DEV-HW-SHARED-MULE-8899"
        shared_ip_str = "103.110.170.45"

        devices: list[Device] = []
        ip_addresses: list[IPAddress] = []

        for idx, acc in enumerate(accounts):
            # Shared device linked to first 5 mule accounts
            fp = shared_device_fp if idx < 5 else f"DEV-HW-{uuid.uuid4().hex[:8].upper()}"
            dev = Device(
                device_fingerprint=fp,
                device_model="Samsung Galaxy S23" if idx < 5 else "Redmi Note 12",
                os_version="Android 14",
                app_version="v4.2.1",
                last_seen_at=now - timedelta(minutes=random.randint(5, 300)),
                shared_account_count=5 if idx < 5 else 1,
                account_id=acc.id,
            )
            devices.append(dev)

            # Shared VPN IP for suspect accounts
            ip_str = shared_ip_str if idx < 5 else f"49.36.{random.randint(10, 200)}.{random.randint(1, 250)}"
            ip_obj = IPAddress(
                ip_str=ip_str,
                isp="Jio Broadband" if idx % 2 == 0 else "Airtel Fiber",
                city="Mumbai" if idx < 5 else "Delhi",
                country="India",
                latitude=19.0760 if idx < 5 else 28.7041,
                longitude=72.8777 if idx < 5 else 77.1025,
                is_vpn_or_proxy=(idx < 5),  # First 5 use VPN
                last_used_at=now - timedelta(minutes=random.randint(5, 200)),
                associated_accounts_count=5 if idx < 5 else 1,
                account_id=acc.id,
            )
            ip_addresses.append(ip_obj)

        session.add_all(devices)
        session.add_all(ip_addresses)
        await session.flush()
        logger.info("Created %d devices and %d IP addresses", len(devices), len(ip_addresses))

        # ── 5. Create Synthetic Transactions & Fraud Patterns ───────────────
        transactions: list[Transaction] = []

        # Pattern 1: Mule Chain Rapid Pass-Through (Acc 0 -> Acc 1 -> Acc 2 -> Acc 3 -> Acc 4)
        chain_amount = 250000.0
        chain_start_time = now - timedelta(hours=2)

        for step in range(4):
            sender = accounts[step]
            receiver = accounts[step + 1]
            pass_amount = chain_amount * (0.98 ** step)  # 2% retention per hop

            tx = Transaction(
                transaction_ref=f"UTR2025MULECHAIN00{step+1}",
                channel="UPI",
                amount=round(pass_amount, 2),
                currency="INR",
                timestamp=chain_start_time + timedelta(minutes=step * 3),  # 3 minutes between hops
                location_city="Mumbai",
                location_state="Maharashtra",
                ip_address_str=shared_ip_str,
                device_fingerprint=shared_device_fp,
                risk_score=95,
                flagged_pattern="Mule Chain",
                narrative=f"Mule Chain Step {step+1}: Rapid fund transfer from {sender.customer_name} to {receiver.customer_name}",
                sender_account_id=sender.id,
                receiver_account_id=receiver.id,
            )
            transactions.append(tx)

        # Pattern 2: Fan-In Aggregation (Accounts 5-14 send ₹49,000 each to Acc 0)
        collector = accounts[0]
        fan_in_start = now - timedelta(hours=6)

        for i in range(5, 15):
            sender = accounts[i]
            amt = 49000.0 + random.randint(100, 800)  # Smurfing under 50K
            tx = Transaction(
                transaction_ref=f"UTRFANIN202500{i:02d}",
                channel="IMPS" if i % 2 == 0 else "UPI",
                amount=amt,
                currency="INR",
                timestamp=fan_in_start + timedelta(minutes=(i - 5) * 12),
                location_city="Delhi",
                location_state="Delhi",
                risk_score=88,
                flagged_pattern="Fan In",
                narrative=f"Fan-In Transfer: {sender.customer_name} transferred ₹{amt} to Collector Account",
                sender_account_id=sender.id,
                receiver_account_id=collector.id,
            )
            transactions.append(tx)

        # General Background Transactions (50 random normal transactions)
        for i in range(40):
            s_idx = random.randint(5, len(accounts) - 1)
            r_idx = random.randint(5, len(accounts) - 1)
            while r_idx == s_idx:
                r_idx = random.randint(5, len(accounts) - 1)

            sender = accounts[s_idx]
            receiver = accounts[r_idx]
            amt = round(random.uniform(500.0, 15000.0), 2)
            channel = random.choice(["UPI", "NEFT", "IMPS", "RTGS"])

            tx = Transaction(
                transaction_ref=f"UTRGEN2025{i+100:04d}",
                channel=channel,
                amount=amt,
                currency="INR",
                timestamp=now - timedelta(days=random.randint(1, 15), hours=random.randint(1, 23)),
                location_city=sender.branch.city if sender.branch else "Mumbai",
                risk_score=random.randint(5, 30),
                flagged_pattern=None,
                narrative=f"Regular payment via {channel}",
                sender_account_id=sender.id,
                receiver_account_id=receiver.id,
            )
            transactions.append(tx)

        session.add_all(transactions)
        await session.flush()
        logger.info("Created %d financial transactions across channels", len(transactions))

        # ── 6. Create Investigation Cases & Alerts ──────────────────────────
        case_1 = Case(
            case_number="CAS-2025-00101",
            title="Cross-Bank Mule Chain & Fan-In Network",
            priority="CRITICAL",
            case_status="IN_PROGRESS",
            assigned_investigator_id="INV-ANALYST-07",
            opened_at=now - timedelta(hours=4),
            summary_notes="Identified active 5-node mule chain with ₹2.5L rapid pass-through. Shared device and IP confirmed across accounts.",
        )
        case_2 = Case(
            case_number="CAS-2025-00102",
            title="Smurfing & Structuring Investigation",
            priority="HIGH",
            case_status="OPEN",
            assigned_investigator_id="INV-ANALYST-12",
            opened_at=now - timedelta(hours=12),
            summary_notes="Multiple transfers under ₹50,000 threshold detected targeting collector account 409900100100.",
        )
        session.add_all([case_1, case_2])
        await session.flush()

        alerts_data = [
            {
                "alert_number": "ALT-2025-0001",
                "title": "Mule Chain Rapid Pass-Through Detected",
                "pattern_type": "Mule Chain",
                "severity": "CRITICAL",
                "risk_score": 95,
                "alert_status": "ESCALATED",
                "triggered_at": now - timedelta(hours=2),
                "description": "Account 409900100100 initiated 5-step rapid fund pass-through totaling ₹2.5L within 12 minutes.",
                "account_id": accounts[0].id,
                "case_id": case_1.id,
            },
            {
                "alert_number": "ALT-2025-0002",
                "title": "High-Volume Fan-In Collector Account",
                "pattern_type": "Fan In",
                "severity": "HIGH",
                "risk_score": 88,
                "alert_status": "UNDER_INVESTIGATION",
                "triggered_at": now - timedelta(hours=5),
                "description": "10 unique senders transferred ₹4.9L in 4 hours to single account.",
                "account_id": accounts[0].id,
                "case_id": case_1.id,
            },
            {
                "alert_number": "ALT-2025-0003",
                "title": "Multiple Accounts from Single Device Fingerprint",
                "pattern_type": "Shared Device",
                "severity": "HIGH",
                "risk_score": 85,
                "alert_status": "NEW",
                "triggered_at": now - timedelta(hours=8),
                "description": "Device DEV-HW-SHARED-MULE-8899 accessed 5 distinct customer accounts within 24 hours.",
                "account_id": accounts[1].id,
                "case_id": case_2.id,
            },
            {
                "alert_number": "ALT-2025-0004",
                "title": "Smurfing / Structuring Pattern Flagged",
                "pattern_type": "Smurfing",
                "severity": "MEDIUM",
                "risk_score": 78,
                "alert_status": "NEW",
                "triggered_at": now - timedelta(hours=14),
                "description": "Repeated transfers of ₹49,200 avoiding ₹50,000 regulatory reporting threshold.",
                "account_id": accounts[2].id,
                "case_id": None,
            },
        ]

        alerts = [Alert(**a) for a in alerts_data]
        session.add_all(alerts)
        await session.flush()
        logger.info("Created %d investigation cases and %d alerts", 2, len(alerts))

        # ── 7. Create Regulatory Reports (STR / CTR) ────────────────────────
        report_1 = Report(
            report_number="STR-2025-MUM-0012",
            report_type="STR",
            title="Suspicious Transaction Report — Mule Chain Network",
            generated_at=now - timedelta(hours=1),
            file_path="/exports/reports/STR-2025-MUM-0012.pdf",
            summary_text="Suspicious Transaction Report generated for FIU-IND. Case CAS-2025-00101 involving 5 mule accounts and ₹2.5L layered transfers.",
            case_id=case_1.id,
        )
        session.add_all([report_1])

        # ── 8. Commit Session ───────────────────────────────────────────────
        await session.commit()
        logger.info("Successfully committed all synthetic data to Supabase database!")

    await pg.dispose_engine()
    logger.info("Seeding script execution completed clean.")


if __name__ == "__main__":
    asyncio.run(seed_data())
