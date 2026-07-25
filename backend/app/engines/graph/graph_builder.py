"""
MuleTrace AI — Graph Builder.

Constructs Neo4j Cypher statements to sync transaction graph nodes and edges.
"""

from __future__ import annotations


import logging
from typing import Any
from app.database.neo4j import neo4j_manager

logger = logging.getLogger("app.engines.graph.graph_builder")


class GraphBuilder:
    """Graph builder constructing Neo4j account nodes and transaction relationships."""

    async def sync_transaction(self, transaction: dict[str, Any]) -> None:
        """Create or update transaction nodes and TRANSFERRED_FUNDS edge in Neo4j.

        Args:
            transaction: Transaction dictionary (sender_acc, receiver_acc, amount, channel, timestamp)
        """
        if not neo4j_manager.is_connected:
            logger.debug("Neo4j driver not connected — skipping graph node sync.")
            return

        cypher = """
        MERGE (s:Account {account_number: $sender_acc})
        SET s.bank_name = $sender_bank, s.customer_name = $sender_name
        MERGE (r:Account {account_number: $receiver_acc})
        SET r.bank_name = $receiver_bank, r.customer_name = $receiver_name
        CREATE (s)-[t:TRANSFERRED_FUNDS {
            ref: $tx_ref,
            amount: $amount,
            channel: $channel,
            timestamp: $timestamp
        }]->(r)
        """

        params = {
            "sender_acc": str(transaction.get("sender_account_number", "UNKNOWN")),
            "sender_bank": str(transaction.get("sender_bank", transaction.get("bank_name", "State Bank of India"))),
            "sender_name": str(transaction.get("sender_name", transaction.get("name", "Account Holder"))),
            "receiver_acc": str(transaction.get("receiver_account_number", transaction.get("receiver_account", "UNKNOWN"))),
            "receiver_bank": str(transaction.get("receiver_bank", "HDFC Bank")),
            "receiver_name": str(transaction.get("receiver_name", "Beneficiary Holder")),
            "tx_ref": str(transaction.get("transaction_ref", transaction.get("txn_id", ""))),
            "amount": float(transaction.get("amount", 0.0)),
            "channel": str(transaction.get("channel", transaction.get("trans_type", "UPI"))),
            "timestamp": str(transaction.get("timestamp", "")),
        }

        try:
            async with neo4j_manager.get_session() as session:
                await session.run(cypher, params)
                logger.info("Synced transaction %s to Neo4j graph", params["tx_ref"])
        except Exception as e:
            logger.warning("Failed to sync transaction to Neo4j: %s", e)


# Singleton instance
graph_builder = GraphBuilder()
