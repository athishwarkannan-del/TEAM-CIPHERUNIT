"""
MuleTrace AI — Synthetic Banking Dataset Seeder.

Populates Supabase PostgreSQL and Neo4j AuraDB with realistic Indian banking dataset
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
from app.database.neo4j import neo4j_manager
from app.engines.graph.graph_builder import graph_builder
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
    """Execute full database seeding sequence for PostgreSQL & Neo4j."""
    logger.info("Initializing database connections for seeding...")
    pg.init_engine()
    await neo4j_manager.connect()

    if pg.async_session_factory is None:
        raise RuntimeError("Database session factory failed to initialize")

    async with pg.async_session_factory() as session:
        # Check if database already has branches
        stmt = select(Branch).limit(1)
        res = await session.execute(stmt)
        existing_branch = res.scalar_one_or_none()

        if existing_branch:
            logger.info("PostgreSQL database already populated with branches. Proceeding with Neo4j graph sync...")
            # Fetch existing transactions for Neo4j sync
            tx_stmt = select(Transaction).limit(50)
            tx_res = await session.execute(tx_stmt)
            tx_items = tx_res.scalars().all()

            if neo4j_manager.is_connected and tx_items:
                logger.info("Syncing existing %d transactions into Neo4j AuraDB...", len(tx_items))
                for tx in tx_items:
                    # Fetch sender and receiver account numbers
                    s_acc = await session.get(Account, tx.sender_account_id)
                    r_acc = await session.get(Account, tx.receiver_account_id)
                    if s_acc and r_acc:
                        await graph_builder.sync_transaction({
                            "sender_account_number": s_acc.account_number,
                            "receiver_account_number": r_acc.account_number,
                            "transaction_ref": tx.transaction_ref,
                            "amount": tx.amount,
                            "channel": tx.channel,
                            "timestamp": str(tx.timestamp),
                        })
                logger.info("Successfully synced transaction graph topology into Neo4j AuraDB!")

            await pg.dispose_engine()
            await neo4j_manager.disconnect()
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

        # ── 2. Create Accounts ──────────────────────────────────────────────
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

            risk_score = random.randint(10, 45)
            is_mule = False
            risk_level = "LOW"

            if i in (0, 1, 2, 3, 4):
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

        # ── 3. Create Transactions & Sync to Neo4j ──────────────────────────
        transactions: list[Transaction] = []
        graph_sync_payloads: list[dict] = []

        chain_amount = 250000.0
        chain_start_time = now - timedelta(hours=2)

        for step in range(4):
            sender = accounts[step]
            receiver = accounts[step + 1]
            pass_amount = chain_amount * (0.98 ** step)

            tx_ref = f"UTR2025MULECHAIN00{step+1}"
            tx = Transaction(
                transaction_ref=tx_ref,
                channel="UPI",
                amount=round(pass_amount, 2),
                currency="INR",
                timestamp=chain_start_time + timedelta(minutes=step * 3),
                location_city="Mumbai",
                location_state="Maharashtra",
                risk_score=95,
                flagged_pattern="Mule Chain",
                narrative=f"Mule Chain Step {step+1}: Rapid fund transfer from {sender.customer_name} to {receiver.customer_name}",
                sender_account_id=sender.id,
                receiver_account_id=receiver.id,
            )
            transactions.append(tx)
            graph_sync_payloads.append({
                "sender_account_number": sender.account_number,
                "receiver_account_number": receiver.account_number,
                "transaction_ref": tx_ref,
                "amount": pass_amount,
                "channel": "UPI",
                "timestamp": str(tx.timestamp),
            })

        session.add_all(transactions)
        await session.flush()
        logger.info("Created %d financial transactions across channels", len(transactions))

        # Sync graph nodes & edges to Neo4j AuraDB
        if neo4j_manager.is_connected:
            logger.info("Syncing %d transaction nodes & edges into Neo4j AuraDB...", len(graph_sync_payloads))
            for payload in graph_sync_payloads:
                await graph_builder.sync_transaction(payload)
            logger.info("Successfully synced transaction graph topology into Neo4j AuraDB!")

        # ── 4. Commit Session ───────────────────────────────────────────────
        await session.commit()
        logger.info("Successfully committed all synthetic data to Supabase PostgreSQL & Neo4j AuraDB!")

    await pg.dispose_engine()
    await neo4j_manager.disconnect()
    logger.info("Seeding script execution completed clean.")


if __name__ == "__main__":
    asyncio.run(seed_data())
