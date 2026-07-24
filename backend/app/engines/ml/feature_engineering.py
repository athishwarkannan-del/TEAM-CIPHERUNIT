"""
MuleTrace AI — ML Feature Engineering Pipeline.

Provides feature extraction, frequency encoding, one-hot encoding, and scaling
transformations for ML inference and model training.
"""

from typing import Any
import numpy as np
import pandas as pd


class FeatureEngineer:
    """Feature engineering pipeline for fraud classification and risk regression."""

    HIGH_CARDINALITY_COLS = ["ip_address", "pincode", "receiver_pincode"]
    DROP_COLS = [
        "txn_id", "name", "account_number", "mobile_number",
        "receiver_account", "receiver_name", "timestamp",
    ]

    def __init__(self, freq_encodings: dict[str, dict[str, float]] | None = None) -> None:
        self.freq_encodings = freq_encodings or {}

    def fit_frequency_encodings(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        """Compute frequency dictionaries for high-cardinality columns."""
        self.freq_encodings = {}
        for col in self.HIGH_CARDINALITY_COLS:
            if col in df.columns:
                self.freq_encodings[col] = df[col].value_counts(normalize=True).to_dict()
        return self.freq_encodings

    def transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply frequency encoding and drop identifier columns."""
        df_encoded = df.copy()

        # Apply frequency encodings
        for col in self.HIGH_CARDINALITY_COLS:
            if col in df_encoded.columns:
                freq_map = self.freq_encodings.get(col, {})
                df_encoded[f"{col}_freq"] = df_encoded[col].map(freq_map).fillna(0)
                df_encoded = df_encoded.drop(columns=[col])

        # Drop identifier columns
        df_encoded = df_encoded.drop(columns=self.DROP_COLS, errors="ignore")
        return df_encoded

    def extract_features_single(self, tx_dict: dict[str, Any]) -> pd.DataFrame:
        """Extract ML feature vector from a single transaction dictionary."""
        amount = float(tx_dict.get("amount", 0.0))
        channel = str(tx_dict.get("channel", "UPI"))
        ip_str = str(tx_dict.get("ip_address_str", ""))

        ip_freq = self.freq_encodings.get("ip_address", {}).get(ip_str, 0.0)

        # Build feature dict matching training schema
        feat_dict = {
            "amount": amount,
            "channel": channel,
            "ip_address_freq": ip_freq,
            "risk_score": float(tx_dict.get("risk_score", 0.0)),
        }
        return pd.DataFrame([feat_dict])
