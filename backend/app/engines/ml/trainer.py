"""
MuleTrace AI — ML Model Trainer.

Trains RandomForest and XGBoost models on ml/transactions.csv dataset and
exports model artifacts (.pkl / .json) to app/engines/ml/artifacts/.
"""

from __future__ import annotations


import logging
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import xgboost as xgb

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("ml_trainer")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
CSV_PATH = BASE_DIR / "ml" / "transactions.csv"
ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


def train_and_export_models() -> None:
    """Train ML models on transactions.csv and save serialized artifacts."""
    if not CSV_PATH.exists():
        logger.error("Dataset not found at %s", CSV_PATH)
        return

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Loading dataset from %s...", CSV_PATH)
    df = pd.read_csv(CSV_PATH)
    logger.info("Dataset shape: %s", df.shape)

    # ── 1. Feature Engineering & Encodings ──────────────────────────────────
    drop_cols = ["txn_id", "name", "account_number", "mobile_number", "receiver_account", "receiver_name", "timestamp"]
    high_card_cols = ["ip_address", "pincode", "receiver_pincode"]

    freq_encodings = {}
    for col in high_card_cols:
        if col in df.columns:
            freq_encodings[col] = df[col].value_counts(normalize=True).to_dict()
            df[f"{col}_freq"] = df[col].map(freq_encodings[col]).fillna(0)
            df = df.drop(columns=[col])

    # Task 1 Data (Regression on risk_score)
    X1 = df.drop(columns=drop_cols + ["risk_score", "is_fraud", "fraud_type"], errors="ignore")
    y1 = df["risk_score"]

    # Task 2 Data (Classification on is_fraud)
    X2 = df.drop(columns=drop_cols + ["risk_score", "is_fraud", "fraud_type"], errors="ignore")
    y2 = df["is_fraud"]

    cat_cols = X2.select_dtypes(include=["object"]).columns.tolist()
    num_cols = X2.select_dtypes(include=["int64", "float64"]).columns.tolist()

    logger.info("Features identified — Categorical: %s, Numerical: %s", cat_cols, num_cols)

    # ── 2. Task 1: Risk Regressor ───────────────────────────────────────────
    logger.info("Training Task 1: RandomForestRegressor...")
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )
    reg_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)),
    ])
    reg_pipeline.fit(X1, y1)

    # ── 3. Task 2: Fraud Classifier ─────────────────────────────────────────
    logger.info("Training Task 2: XGBClassifier...")
    clf_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, class_weight="balanced", n_jobs=-1)),
    ])
    clf_pipeline.fit(X2, y2)

    # ── 4. Save Artifacts ───────────────────────────────────────────────────
    joblib.dump(reg_pipeline, ARTIFACTS_DIR / "rf_regressor_pipeline.pkl")
    joblib.dump(clf_pipeline, ARTIFACTS_DIR / "rf_classifier_pipeline.pkl")
    joblib.dump(freq_encodings, ARTIFACTS_DIR / "freq_encodings.pkl")

    logger.info("Successfully exported all ML model artifacts to %s", ARTIFACTS_DIR)


if __name__ == "__main__":
    train_and_export_models()
