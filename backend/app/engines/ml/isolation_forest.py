"""
MuleTrace AI — Isolation Forest Anomaly Detection.

Unsupervised anomaly detector for statistical outlier detection in transaction streams.
"""

import logging
from typing import Any
import numpy as np
from sklearn.ensemble import IsolationForest

logger = logging.getLogger("app.engines.ml.isolation_forest")


class IsolationForestDetector:
    """Isolation Forest anomaly detector for transaction outlier identification."""

    def __init__(self) -> None:
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,  # Expect 5% anomalies
            random_state=42,
        )
        self.is_fitted = False
        self._fit_default_baseline()

    def _fit_default_baseline(self) -> None:
        """Fit model on synthetic normal transaction distributions."""
        amounts = np.random.normal(loc=5000, scale=3000, size=500)
        amounts = np.clip(amounts, 100, 100000).reshape(-1, 1)
        self.model.fit(amounts)
        self.is_fitted = True

    def detect_anomaly(self, amount: float) -> tuple[bool, float]:
        """Detect whether a transaction amount is an anomaly.

        Args:
            amount: Transaction amount.

        Returns:
            Tuple of (is_anomaly: bool, anomaly_score: float)
        """
        X = np.array([[amount]])
        prediction = self.model.predict(X)[0]
        # decision_function gives anomaly score (negative for anomalies)
        score = float(self.model.decision_function(X)[0])
        is_anomaly = bool(prediction == -1)
        return is_anomaly, round(score, 4)


# Singleton instance
isolation_forest_detector = IsolationForestDetector()
