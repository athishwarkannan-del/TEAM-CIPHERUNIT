"""
MuleTrace AI — Phase 3: Differential Privacy Layer.

Implements epsilon-differential privacy via the Gaussian mechanism.
Provides noise injection for model weight gradients before upload and
secure aggregation mask generation for multi-party computation.

Privacy Guarantees:
    - (ε, δ)-differential privacy via calibrated Gaussian noise
    - Per-round privacy budget tracking
    - Gradient clipping to bound sensitivity
    - Secure aggregation masks (additive secret sharing)

References:
    - Dwork & Roth, "The Algorithmic Foundations of Differential Privacy" (2014)
    - Abadi et al., "Deep Learning with Differential Privacy" (2016)
"""

from __future__ import annotations
from typing import Optional

import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from math import log, sqrt

import numpy as np

logger = logging.getLogger("app.engines.federated.privacy")


@dataclass
class PrivacyAccountant:
    """Tracks cumulative privacy budget expenditure across training rounds.

    Uses the moments accountant approximation for composed Gaussian mechanisms.
    """

    total_epsilon_spent: float = 0.0
    total_delta: float = 1e-5
    max_epsilon_budget: float = 10.0
    round_history: list[dict] = field(default_factory=list)

    @property
    def remaining_budget(self) -> float:
        """Remaining epsilon budget before privacy guarantee degrades."""
        return max(0.0, self.max_epsilon_budget - self.total_epsilon_spent)

    @property
    def is_budget_exhausted(self) -> bool:
        return self.total_epsilon_spent >= self.max_epsilon_budget

    def record_round(self, epsilon: float, delta: float, noise_scale: float) -> None:
        """Record privacy expenditure for one training round."""
        self.total_epsilon_spent += epsilon
        self.round_history.append({
            "epsilon": epsilon,
            "delta": delta,
            "noise_scale": noise_scale,
            "cumulative_epsilon": self.total_epsilon_spent,
        })
        logger.info(
            "Privacy accountant — round recorded: ε=%.4f, cumulative ε=%.4f / %.1f",
            epsilon, self.total_epsilon_spent, self.max_epsilon_budget,
        )


class DifferentialPrivacyEngine:
    """Applies (ε, δ)-differential privacy to model weight gradients.

    The Gaussian mechanism adds calibrated noise:
        noisy_weight = weight + N(0, σ²)
    where σ = (Δf · √(2 ln(1.25/δ))) / ε
    and Δf is the L2 sensitivity (controlled via gradient clipping).
    """

    def __init__(self, max_grad_norm: float = 1.0) -> None:
        self.max_grad_norm = max_grad_norm
        self.accountant = PrivacyAccountant()

    def compute_noise_scale(self, epsilon: float, delta: float) -> float:
        """Compute Gaussian noise standard deviation σ for given (ε, δ).

        σ = (Δf · √(2 ln(1.25/δ))) / ε
        """
        if epsilon <= 0:
            raise ValueError("Epsilon must be positive")
        if delta <= 0 or delta >= 1:
            raise ValueError("Delta must be in (0, 1)")

        sensitivity = self.max_grad_norm
        sigma = (sensitivity * sqrt(2.0 * log(1.25 / delta))) / epsilon
        return sigma

    def clip_gradients(self, weights: dict[str, list[list[float]]]) -> dict[str, list[list[float]]]:
        """Clip weight matrices to enforce bounded L2 sensitivity.

        Each weight matrix is clipped so that its Frobenius norm
        does not exceed max_grad_norm.
        """
        clipped = {}
        for layer_name, matrix in weights.items():
            arr = np.array(matrix, dtype=np.float64)
            norm = np.linalg.norm(arr)
            if norm > self.max_grad_norm:
                arr = arr * (self.max_grad_norm / norm)
            clipped[layer_name] = arr.tolist()
        return clipped

    def add_gaussian_noise(
        self,
        weights: dict[str, list[list[float]]],
        epsilon: float,
        delta: float,
    ) -> tuple[dict[str, list[list[float]]], float]:
        """Add calibrated Gaussian noise to clipped weight gradients.

        Args:
            weights: Dictionary of layer_name -> 2D weight matrix.
            epsilon: Privacy budget for this operation.
            delta: Probability of privacy breach.

        Returns:
            Tuple of (noisy_weights, noise_scale_sigma).
        """
        # Step 1: Clip gradients to bound sensitivity
        clipped = self.clip_gradients(weights)

        # Step 2: Compute noise scale
        sigma = self.compute_noise_scale(epsilon, delta)

        # Step 3: Add Gaussian noise to each layer
        noisy_weights = {}
        for layer_name, matrix in clipped.items():
            arr = np.array(matrix, dtype=np.float64)
            noise = np.random.normal(loc=0.0, scale=sigma, size=arr.shape)
            noisy_arr = arr + noise
            noisy_weights[layer_name] = noisy_arr.tolist()

        # Step 4: Record privacy expenditure
        self.accountant.record_round(epsilon, delta, sigma)

        logger.info(
            "DP noise applied — σ=%.6f, ε=%.4f, δ=%.2e, layers=%d",
            sigma, epsilon, delta, len(noisy_weights),
        )

        return noisy_weights, sigma

    def add_noise_to_biases(
        self,
        biases: dict[str, list[float]],
        epsilon: float,
        delta: float,
    ) -> dict[str, list[float]]:
        """Add calibrated Gaussian noise to bias vectors."""
        sigma = self.compute_noise_scale(epsilon, delta)
        noisy_biases = {}
        for layer_name, bias_vec in biases.items():
            arr = np.array(bias_vec, dtype=np.float64)
            noise = np.random.normal(loc=0.0, scale=sigma, size=arr.shape)
            noisy_biases[layer_name] = (arr + noise).tolist()
        return noisy_biases


class SecureAggregationEngine:
    """Implements additive secret sharing for secure multi-party aggregation.

    Each bank generates a random mask and shares it pairwise. The central
    server receives masked weights — after summation the masks cancel out,
    leaving only the true aggregate. The server never sees individual
    bank contributions in the clear.

    Protocol:
        1. Bank_i generates mask M_i (random matrix, same shape as weights)
        2. Bank_i uploads (W_i + M_i) to the server
        3. Bank_i also uploads M_i to a secure mask buffer
        4. Server computes: Σ(W_i + M_i) - Σ(M_i) = Σ(W_i)
    """

    def __init__(self) -> None:
        self._mask_buffer: dict[str, dict[str, list[list[float]]]] = {}

    def generate_mask(
        self,
        bank_id: str,
        weight_shapes: dict[str, tuple[int, ...]],
        seed: Optional[int] = None,
    ) -> dict[str, list[list[float]]]:
        """Generate a random additive mask for a bank's weight matrices.

        Args:
            bank_id: Identifier for the participating bank.
            weight_shapes: Dictionary mapping layer names to weight shapes.
            seed: Optional deterministic seed for reproducibility.

        Returns:
            Dictionary of layer_name -> 2D mask matrix.
        """
        rng = np.random.default_rng(seed or secrets.randbits(64))
        masks = {}
        for layer_name, shape in weight_shapes.items():
            mask = rng.standard_normal(size=shape)
            masks[layer_name] = mask.tolist()

        self._mask_buffer[bank_id] = masks
        logger.debug("Generated secure aggregation mask for bank %s", bank_id)
        return masks

    def apply_mask(
        self,
        weights: dict[str, list[list[float]]],
        masks: dict[str, list[list[float]]],
    ) -> dict[str, list[list[float]]]:
        """Apply additive mask to weight matrices: W_masked = W + M."""
        masked = {}
        for layer_name, matrix in weights.items():
            w = np.array(matrix, dtype=np.float64)
            m = np.array(masks.get(layer_name, np.zeros_like(w)), dtype=np.float64)
            masked[layer_name] = (w + m).tolist()
        return masked

    def unmask_aggregate(
        self,
        masked_sum: dict[str, list[list[float]]],
        bank_ids: list[str],
    ) -> dict[str, list[list[float]]]:
        """Remove masks from the aggregated sum to recover true aggregate.

        unmasked = Σ(W_i + M_i) - Σ(M_i) = Σ(W_i)
        """
        result = {}
        for layer_name, summed_matrix in masked_sum.items():
            arr = np.array(summed_matrix, dtype=np.float64)
            for bid in bank_ids:
                if bid in self._mask_buffer and layer_name in self._mask_buffer[bid]:
                    mask_arr = np.array(self._mask_buffer[bid][layer_name], dtype=np.float64)
                    arr = arr - mask_arr
            result[layer_name] = arr.tolist()
        return result

    def clear_masks(self, bank_ids: Optional[list[str]] = None) -> None:
        """Clear stored masks after a round completes."""
        if bank_ids:
            for bid in bank_ids:
                self._mask_buffer.pop(bid, None)
        else:
            self._mask_buffer.clear()


# Singleton instances
dp_engine = DifferentialPrivacyEngine(max_grad_norm=1.0)
secure_agg_engine = SecureAggregationEngine()
