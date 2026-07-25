"""
MuleTrace AI — ML Inference Engine.

Loads pre-trained RandomForest & XGBoost model pipelines from app/engines/ml/artifacts/
to compute real-time risk scores and fraud probabilities for incoming transactions.
"""

from __future__ import annotations


import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import joblib
import pandas as pd

logger = logging.getLogger("app.engines.ml.xgboost_model")
ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


@dataclass
class MLPredictionResult:
    """Prediction result from ML Engine inference."""

    predicted_risk_score: int
    fraud_probability: float
    is_fraud_predicted: bool
    model_version: str = "rf_xgboost_v1.0"


class MLEngine:
    """Inference service for ML-based risk scoring and fraud classification."""

    def __init__(self) -> None:
        self.reg_pipeline = None
        self.clf_pipeline = None
        self.freq_encodings = {}
        self.is_loaded = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load serialized model pipelines and frequency encodings."""
        try:
            reg_path = ARTIFACTS_DIR / "rf_regressor_pipeline.pkl"
            clf_path = ARTIFACTS_DIR / "rf_classifier_pipeline.pkl"
            freq_path = ARTIFACTS_DIR / "freq_encodings.pkl"

            if reg_path.exists() and clf_path.exists():
                self.reg_pipeline = joblib.load(reg_path)
                self.clf_pipeline = joblib.load(clf_path)
                if freq_path.exists():
                    self.freq_encodings = joblib.load(freq_path)
                self.is_loaded = True
                logger.info("ML Engine successfully loaded trained model pipelines from %s", ARTIFACTS_DIR)
            else:
                logger.warning("ML Engine model artifacts not found at %s. Running in baseline fallback mode.", ARTIFACTS_DIR)
        except Exception as e:
            logger.warning("Failed to load ML artifacts: %s. Using heuristic fallback.", e)

    def predict_transaction_risk(self, tx_dict: dict[str, Any]) -> MLPredictionResult:
        """Compute predicted risk score and fraud probability for a transaction.

        Args:
            tx_dict: Transaction attribute dictionary.

        Returns:
            MLPredictionResult with risk score (0-100) and fraud probability.
        """
        if not self.is_loaded:
            # Heuristic fallback if model artifacts are not present
            amount = float(tx_dict.get("amount", 0.0))
            score = min(99, int(amount / 500.0)) if amount > 50000 else int(amount / 2000.0)
            return MLPredictionResult(
                predicted_risk_score=score,
                fraud_probability=round(score / 100.0, 4),
                is_fraud_predicted=score >= 70,
                model_version="heuristic_fallback",
            )

        try:
            # Build input DataFrame
            input_df = pd.DataFrame([{
                "amount": float(tx_dict.get("amount", 0.0)),
                "account_type": str(tx_dict.get("account_type", "savings")),
                "narration": str(tx_dict.get("channel", "UPI")),
                "trans_type": "debit",
                "device": "Android",
                "account_age_days": 180,
                "velocity_l6h": 2,
                "churn_rate": 0.01,
                "ip_account_density": 1,
                "amount_deviation_ratio": 1.2,
                "daily_limit_fraction": 0.3,
                "user_risk_score": float(tx_dict.get("user_risk_score", 15.0)),
                "device_trust_score": 85.0,
                "is_rooted_or_emulator": 0,
                "device_risk_score": 10.0,
                "merchant_chargeback_rate": 0.0,
                "merchant_risk_score": 5.0,
                "is_vpn_or_proxy": 1 if tx_dict.get("is_vpn_or_proxy") else 0,
                "network_risk_score": 20.0,
                "ip_address_freq": self.freq_encodings.get("ip_address", {}).get(tx_dict.get("ip_address_str"), 0.0),
                "pincode_freq": 0.01,
                "receiver_pincode_freq": 0.01,
            }])

            # Regression prediction (risk_score 0-100)
            predicted_score = float(self.reg_pipeline.predict(input_df)[0])
            predicted_score = max(0, min(100, int(round(predicted_score))))

            # Classification prediction (fraud probability)
            proba = float(self.clf_pipeline.predict_proba(input_df)[0, 1])
            is_fraud = bool(self.clf_pipeline.predict(input_df)[0] == 1)

            return MLPredictionResult(
                predicted_risk_score=predicted_score,
                fraud_probability=round(proba, 4),
                is_fraud_predicted=is_fraud,
                model_version="rf_xgboost_v1.0",
            )
        except Exception as e:
            logger.warning("Error during ML inference execution: %s. Reverting to heuristic fallback.", e)
            amount = float(tx_dict.get("amount", 0.0))
            score = min(99, int(amount / 1000.0))
            return MLPredictionResult(
                predicted_risk_score=score,
                fraud_probability=0.2,
                is_fraud_predicted=False,
                model_version="fallback_on_error",
            )


# Singleton instance
ml_engine = MLEngine()
