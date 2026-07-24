"""
MuleTrace AI — Graph Relationship Engine.

Maps multi-entity relationships (Account -> Device, Account -> IP, Account -> Beneficiary).
"""

import logging
from app.database.neo4j import neo4j_manager

logger = logging.getLogger("app.engines.graph.relationship_engine")


class RelationshipEngine:
    """Relationship mapping engine for cross-entity link analysis."""

    async def link_account_device(self, account_number: str, device_fingerprint: str) -> None:
        """Create USED_DEVICE relationship between Account and Device node."""
        if not neo4j_manager.is_connected:
            return

        cypher = """
        MERGE (a:Account {account_number: $acc})
        MERGE (d:Device {fingerprint: $fp})
        MERGE (a)-[r:USED_DEVICE]->(d)
        """
        try:
            async with neo4j_manager.get_session() as session:
                await session.run(cypher, {"acc": account_number, "fp": device_fingerprint})
        except Exception as e:
            logger.warning("Failed to link device in Neo4j: %s", e)


# Singleton instance
relationship_engine = RelationshipEngine()
