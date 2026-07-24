"""
MuleTrace AI — Graph Builder.

Constructs Neo4j Cypher statements to sync transaction graph nodes and edges.
"""

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
        MERGE (r:Account {account_number: $receiver_acc})
        CREATE (s)-[t:TRANSFERRED_FUNDS {
            ref: $tx_ref,
            amount: $amount,
            channel: $channel,
            timestamp: $timestamp
        }]->(r)
        """

        params = {
            "sender_acc": str(transaction.get("sender_account_number", "UNKNOWN")),
            "receiver_acc": str(transaction.get("receiver_account_number", "UNKNOWN")),
            "tx_ref": str(transaction.get("transaction_ref", "")),
            "amount": float(transaction.get("amount", 0.0)),
            "channel": str(transaction.get("channel", "UPI")),
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
