"""
MuleTrace AI — Graph Path Analysis Engine.

Performs Cypher-based path tracing, community detection, and centrality analysis on Neo4j.
"""

import logging
from typing import Any
from app.database.neo4j import neo4j_manager

logger = logging.getLogger("app.engines.graph.path_analysis")


class PathAnalysisEngine:
    """Path analysis engine for tracing mule chains and money laundering routes."""

    async def trace_money_path(self, start_account: str, max_depth: int = 5) -> list[dict[str, Any]]:
        """Trace downstream money flow path from a source account up to max_depth hops.

        Args:
            start_account: Origin account number.
            max_depth: Maximum hops to trace.

        Returns:
            List of path step dictionaries.
        """
        if not neo4j_manager.is_connected:
            return []

        cypher = f"""
        MATCH path = (s:Account {{account_number: $start_acc}})-[r:TRANSFERRED_FUNDS*1..{max_depth}]->(target:Account)
        RETURN path
        LIMIT 25
        """

        try:
            async with neo4j_manager.get_session() as session:
                result = await session.run(cypher, {"start_acc": start_account})
                records = await result.data()
                return records
        except Exception as e:
            logger.warning("Error running Neo4j path tracing query: %s", e)
            return []


# Singleton instance
path_analysis_engine = PathAnalysisEngine()
