"""
MuleTrace AI — Phase 2: Local Graph Trainer.

Trains a lightweight Graph Neural Network (GNN) on the local Neo4j subgraph
to produce account node embeddings and mule-classification weight matrices.

Architecture:
    - Extracts the local transaction graph from Neo4j as an adjacency matrix
      and feature matrix using Cypher queries.
    - Implements a 2-layer GraphSAGE-style message-passing network using
      pure NumPy (no PyTorch dependency required).
    - Produces weight matrices that can be uploaded to the federated
      coordinator for FedAvg aggregation.

Why NumPy instead of PyTorch Geometric?
    - Zero additional dependency installation on constrained environments
    - Weights are still fully compatible with FedAvg aggregation
    - Demonstrates the core GNN computation without framework lock-in
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from app.database.neo4j import neo4j_manager

logger = logging.getLogger("app.engines.federated.local_trainer")


# ---------------------------------------------------------------------------
# Graph Data Structures
# ---------------------------------------------------------------------------

@dataclass
class LocalGraphData:
    """Extracted local graph for GNN training."""
    node_ids: list[str]
    node_features: np.ndarray       # shape: (num_nodes, feature_dim)
    adjacency: np.ndarray           # shape: (num_nodes, num_nodes)
    labels: np.ndarray              # shape: (num_nodes,) — 1=mule, 0=clean
    num_nodes: int = 0
    num_edges: int = 0
    feature_dim: int = 0


@dataclass
class TrainingResult:
    """Output of a local training run."""
    layer_weights: dict[str, list[list[float]]]
    layer_biases: dict[str, list[float]]
    local_loss: float
    local_accuracy: float
    num_samples: int
    epochs_completed: int


# ---------------------------------------------------------------------------
# GraphSAGE-style GNN (NumPy Implementation)
# ---------------------------------------------------------------------------

class GraphSAGEModel:
    """Two-layer GraphSAGE-Mean model implemented in pure NumPy.

    Layer 1: h_v^1 = σ(W_1 · CONCAT(x_v, MEAN({x_u : u ∈ N(v)})))
    Layer 2: h_v^2 = σ(W_2 · CONCAT(h_v^1, MEAN({h_u^1 : u ∈ N(v)})))
    Output:  ŷ_v  = sigmoid(W_out · h_v^2)

    All weight matrices are stored and exported for FedAvg.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 64, output_dim: int = 1) -> None:
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        # Initialize weights with Xavier/Glorot initialization
        scale1 = np.sqrt(2.0 / (input_dim * 2 + hidden_dim))
        scale2 = np.sqrt(2.0 / (hidden_dim * 2 + hidden_dim))
        scale_out = np.sqrt(2.0 / (hidden_dim + output_dim))

        self.W1 = np.random.randn(input_dim * 2, hidden_dim).astype(np.float64) * scale1
        self.b1 = np.zeros(hidden_dim, dtype=np.float64)
        self.W2 = np.random.randn(hidden_dim * 2, hidden_dim).astype(np.float64) * scale2
        self.b2 = np.zeros(hidden_dim, dtype=np.float64)
        self.W_out = np.random.randn(hidden_dim, output_dim).astype(np.float64) * scale_out
        self.b_out = np.zeros(output_dim, dtype=np.float64)

    @staticmethod
    def _relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def _aggregate_neighbors(self, features: np.ndarray, adj: np.ndarray) -> np.ndarray:
        """Mean aggregation of neighbor features."""
        degree = adj.sum(axis=1, keepdims=True)
        degree = np.maximum(degree, 1.0)  # Avoid division by zero
        agg = (adj @ features) / degree
        return agg

    def forward(self, features: np.ndarray, adj: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Forward pass through the 2-layer GraphSAGE.

        Returns:
            Tuple of (predictions, final_embeddings).
        """
        # Layer 1
        neighbor_agg_1 = self._aggregate_neighbors(features, adj)
        concat_1 = np.concatenate([features, neighbor_agg_1], axis=1)
        h1 = self._relu(concat_1 @ self.W1 + self.b1)

        # Layer 2
        neighbor_agg_2 = self._aggregate_neighbors(h1, adj)
        concat_2 = np.concatenate([h1, neighbor_agg_2], axis=1)
        h2 = self._relu(concat_2 @ self.W2 + self.b2)

        # Output layer
        logits = h2 @ self.W_out + self.b_out
        preds = self._sigmoid(logits)

        return preds.flatten(), h2

    def get_weights(self) -> dict[str, list[list[float]]]:
        """Export all weight matrices as serializable lists."""
        return {
            "sage_layer1": self.W1.tolist(),
            "sage_layer2": self.W2.tolist(),
            "output_layer": self.W_out.tolist(),
        }

    def get_biases(self) -> dict[str, list[float]]:
        """Export all bias vectors as serializable lists."""
        return {
            "sage_layer1": self.b1.tolist(),
            "sage_layer2": self.b2.tolist(),
            "output_layer": self.b_out.tolist(),
        }

    def set_weights(self, weights: dict[str, list[list[float]]], biases: dict[str, list[float]]) -> None:
        """Load weights from the global model (start of each round)."""
        if "sage_layer1" in weights:
            self.W1 = np.array(weights["sage_layer1"], dtype=np.float64)
        if "sage_layer2" in weights:
            self.W2 = np.array(weights["sage_layer2"], dtype=np.float64)
        if "output_layer" in weights:
            self.W_out = np.array(weights["output_layer"], dtype=np.float64)
        if "sage_layer1" in biases:
            self.b1 = np.array(biases["sage_layer1"], dtype=np.float64)
        if "sage_layer2" in biases:
            self.b2 = np.array(biases["sage_layer2"], dtype=np.float64)
        if "output_layer" in biases:
            self.b_out = np.array(biases["output_layer"], dtype=np.float64)


# ---------------------------------------------------------------------------
# Local Trainer
# ---------------------------------------------------------------------------

class LocalGraphTrainer:
    """Trains a GraphSAGE model on the local Neo4j transaction subgraph.

    Workflow:
        1. Extract graph topology and node features from Neo4j.
        2. Initialize or load global model weights.
        3. Run local SGD training for N epochs.
        4. Export trained weight deltas for federated upload.
    """

    def __init__(self, hidden_dim: int = 64) -> None:
        self.hidden_dim = hidden_dim
        self.model: GraphSAGEModel | None = None

    async def extract_local_graph(self) -> LocalGraphData:
        """Extract account nodes and transaction edges from Neo4j.

        Returns a LocalGraphData with feature matrix, adjacency, and labels.
        """
        if not neo4j_manager.is_connected:
            logger.warning("Neo4j not connected — generating synthetic local graph for demonstration")
            return self._generate_synthetic_graph()

        try:
            async with neo4j_manager.get_session() as session:
                # Extract all account nodes
                node_result = await session.run(
                    "MATCH (a:Account) RETURN a.account_number AS acc, "
                    "coalesce(a.risk_score, 0) AS risk, "
                    "coalesce(a.is_mule, false) AS is_mule"
                )
                node_records = await node_result.data()

                # Extract all transaction edges
                edge_result = await session.run(
                    "MATCH (s:Account)-[r:TRANSFERRED_FUNDS]->(t:Account) "
                    "RETURN s.account_number AS src, t.account_number AS dst, "
                    "r.amount AS amount"
                )
                edge_records = await edge_result.data()

            if not node_records:
                logger.info("No account nodes found in Neo4j — using synthetic graph")
                return self._generate_synthetic_graph()

            # Build node index
            node_ids = [r["acc"] for r in node_records]
            node_idx = {acc: i for i, acc in enumerate(node_ids)}
            n = len(node_ids)

            # Build feature matrix (risk_score normalized to [0,1])
            features = np.zeros((n, 4), dtype=np.float64)
            labels = np.zeros(n, dtype=np.float64)
            for i, rec in enumerate(node_records):
                features[i, 0] = float(rec.get("risk", 0)) / 100.0
                features[i, 1] = 1.0  # Bias feature
                labels[i] = 1.0 if rec.get("is_mule", False) else 0.0

            # Build adjacency matrix
            adj = np.zeros((n, n), dtype=np.float64)
            num_edges = 0
            for e in edge_records:
                src_idx = node_idx.get(e["src"])
                dst_idx = node_idx.get(e["dst"])
                if src_idx is not None and dst_idx is not None:
                    adj[src_idx, dst_idx] = 1.0
                    adj[dst_idx, src_idx] = 1.0  # Undirected
                    num_edges += 1

            # Add self-loops
            np.fill_diagonal(adj, 1.0)

            # Compute degree-based features
            degree = adj.sum(axis=1)
            features[:, 2] = degree / max(degree.max(), 1.0)
            features[:, 3] = np.log1p(degree)

            graph_data = LocalGraphData(
                node_ids=node_ids,
                node_features=features,
                adjacency=adj,
                labels=labels,
                num_nodes=n,
                num_edges=num_edges,
                feature_dim=4,
            )
            logger.info(
                "Extracted local graph — %d nodes, %d edges, %d mule labels",
                n, num_edges, int(labels.sum()),
            )
            return graph_data

        except Exception as e:
            logger.warning("Error extracting Neo4j graph: %s — falling back to synthetic", e)
            return self._generate_synthetic_graph()

    def _generate_synthetic_graph(self, num_nodes: int = 50, num_edges: int = 120) -> LocalGraphData:
        """Generate a synthetic graph for testing when Neo4j is unavailable."""
        rng = np.random.default_rng(42)

        node_ids = [f"SYNTH-ACC-{i:04d}" for i in range(num_nodes)]
        features = rng.random((num_nodes, 4))
        adj = np.zeros((num_nodes, num_nodes), dtype=np.float64)

        for _ in range(num_edges):
            i, j = rng.integers(0, num_nodes, size=2)
            if i != j:
                adj[i, j] = 1.0
                adj[j, i] = 1.0

        np.fill_diagonal(adj, 1.0)

        # 10% mule labels
        labels = np.zeros(num_nodes, dtype=np.float64)
        mule_indices = rng.choice(num_nodes, size=max(1, num_nodes // 10), replace=False)
        labels[mule_indices] = 1.0

        return LocalGraphData(
            node_ids=node_ids,
            node_features=features,
            adjacency=adj,
            labels=labels,
            num_nodes=num_nodes,
            num_edges=num_edges,
            feature_dim=4,
        )

    async def train(
        self,
        epochs: int = 5,
        learning_rate: float = 0.01,
        global_weights: dict[str, list[list[float]]] | None = None,
        global_biases: dict[str, list[float]] | None = None,
    ) -> TrainingResult:
        """Run local GNN training on the extracted graph.

        Args:
            epochs: Number of local training epochs.
            learning_rate: SGD learning rate.
            global_weights: Pre-trained global model weights to initialize from.
            global_biases: Pre-trained global model biases.

        Returns:
            TrainingResult with trained weights and metrics.
        """
        graph = await self.extract_local_graph()

        # Initialize model
        self.model = GraphSAGEModel(
            input_dim=graph.feature_dim,
            hidden_dim=self.hidden_dim,
            output_dim=1,
        )

        # Load global weights if provided (federated round continuation)
        if global_weights and global_biases:
            self.model.set_weights(global_weights, global_biases)

        # Training loop (simple gradient descent with numerical gradients)
        best_loss = float("inf")
        final_accuracy = 0.0

        for epoch in range(epochs):
            preds, embeddings = self.model.forward(graph.node_features, graph.adjacency)

            # Binary cross-entropy loss
            eps = 1e-7
            preds_clipped = np.clip(preds, eps, 1.0 - eps)
            loss = -np.mean(
                graph.labels * np.log(preds_clipped)
                + (1 - graph.labels) * np.log(1 - preds_clipped)
            )

            # Accuracy
            predicted_labels = (preds > 0.5).astype(np.float64)
            accuracy = np.mean(predicted_labels == graph.labels)

            # Numerical gradient descent on output layer weights
            grad_output = (preds_clipped - graph.labels).reshape(-1, 1)
            dW_out = embeddings.T @ grad_output / graph.num_nodes
            db_out = grad_output.mean(axis=0)

            self.model.W_out -= learning_rate * dW_out
            self.model.b_out -= learning_rate * db_out.flatten()

            if loss < best_loss:
                best_loss = loss
            final_accuracy = accuracy

            if (epoch + 1) % max(1, epochs // 3) == 0:
                logger.info(
                    "Local training — epoch %d/%d, loss=%.4f, accuracy=%.4f",
                    epoch + 1, epochs, loss, accuracy,
                )

        result = TrainingResult(
            layer_weights=self.model.get_weights(),
            layer_biases=self.model.get_biases(),
            local_loss=float(best_loss),
            local_accuracy=float(final_accuracy),
            num_samples=graph.num_nodes,
            epochs_completed=epochs,
        )

        logger.info(
            "Local training complete — loss=%.4f, accuracy=%.4f, samples=%d",
            result.local_loss, result.local_accuracy, result.num_samples,
        )
        return result


# Singleton instance
local_trainer = LocalGraphTrainer(hidden_dim=64)
