"""
Transaction Fraud Detection and Risk Scoring Models
===================================================
This script builds two separate models using RandomForest and XGBoost:
1. Regression on risk_score (continuous target)
2. Classification on is_fraud (0/1 target)

Author: Data Science Team
Date: 2026-07-24
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    r2_score, mean_absolute_error, mean_squared_error,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import xgboost as xgb
import joblib
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# =============================================================================
# DATA LOADING AND PREPROCESSING
# =============================================================================

def load_and_explore_data(filepath):
    """Load the dataset and print basic information."""
    df = pd.read_csv(filepath)
    print("="*80)
    print("DATA EXPLORATION")
    print("="*80)
    print(f"Dataset shape: {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFraud distribution:\n{df['is_fraud'].value_counts()}")
    fraud_percentage = (df['is_fraud'].sum() / len(df)) * 100
    print(f"Fraud percentage: {fraud_percentage:.2f}%")
    print(f"\nRisk Score stats:\n{df['risk_score'].describe()}")
    print(f"\nMissing values:\n{df.isnull().sum()}")
    return df

def prep_data_task1(df):
    """Prepare data for Task 1 - Regression on risk_score."""
    # Drop identifier/leakage columns
    drop_cols = ['txn_id', 'name', 'account_number', 'mobile_number', 
                 'receiver_account', 'receiver_name', 'timestamp']
    
    # Drop outcome-adjacent columns
    target_cols = ['risk_score']
    outcome_adjacent = ['is_fraud', 'fraud_type']
    
    X = df.drop(columns=drop_cols + target_cols + outcome_adjacent, errors='ignore')
    y = df['risk_score']
    
    return X, y

def prep_data_task2(df):
    """Prepare data for Task 2 - Classification on is_fraud."""
    # Drop identifier/leakage columns
    drop_cols = ['txn_id', 'name', 'account_number', 'mobile_number', 
                 'receiver_account', 'receiver_name', 'timestamp']
    
    # Drop leakage columns (risk_score is derived from fraud)
    leakage_cols = ['risk_score', 'fraud_type']
    
    X = df.drop(columns=drop_cols + leakage_cols, errors='ignore')
    y = df['is_fraud']
    
    return X, y

def apply_frequency_encoding(X, high_card_cols):
    """
    Apply frequency encoding to high-cardinality columns.
    Returns encoded DataFrame and the encodings dictionary.
    """
    X_encoded = X.copy()
    freq_encodings = {}
    
    for col in high_card_cols:
        if col in X_encoded.columns:
            # Create frequency encoding
            freq_encodings[col] = X_encoded[col].value_counts(normalize=True).to_dict()
            X_encoded[f'{col}_freq'] = X_encoded[col].map(freq_encodings[col]).fillna(0)
            X_encoded = X_encoded.drop(columns=[col])
    
    return X_encoded, freq_encodings

def get_column_types(X):
    """Identify categorical and numerical columns."""
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    return categorical_cols, numerical_cols

# =============================================================================
# OPTIMIZED MODEL TRAINING FUNCTIONS
# =============================================================================

def train_randomforest_regressor(X_train, X_test, y_train, y_test, 
                                 categorical_cols, numerical_cols):
    """Train and evaluate RandomForestRegressor with hyperparameter tuning."""
    print("\n" + "="*60)
    print("TASK 1: RandomForestRegressor")
    print("="*60)
    
    # Create preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ],
        remainder='drop'
    )
    
    # RandomForestRegressor with hyperparameter tuning
    rf_reg = RandomForestRegressor(random_state=42, n_jobs=-1)
    
    rf_reg_params = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    
    print("Running GridSearchCV (this may take 2-3 minutes)...")
    rf_reg_grid = GridSearchCV(
        rf_reg, rf_reg_params, cv=3, scoring='r2', n_jobs=-1, verbose=0
    )
    
    rf_reg_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', rf_reg_grid)
    ])
    
    # Fit the model
    rf_reg_pipeline.fit(X_train, y_train)
    
    # Predictions and metrics
    y_pred = rf_reg_pipeline.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\nBest parameters: {rf_reg_pipeline.named_steps['model'].best_params_}")
    print(f"\nResults:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  MAE: {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    
    # Get feature importances
    best_model = rf_reg_pipeline.named_steps['model'].best_estimator_
    importance = best_model.feature_importances_
    
    return rf_reg_pipeline, r2, mae, rmse, importance

def train_xgboost_regressor(X_train, X_test, y_train, y_test, 
                           categorical_cols, numerical_cols):
    """Train and evaluate XGBRegressor with hyperparameter tuning."""
    print("\n" + "="*60)
    print("TASK 1: XGBRegressor")
    print("="*60)
    
    # Preprocessor for XGBoost (no scaling needed)
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ],
        remainder='passthrough'
    )
    
    # Transform features
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)
    
    # XGBoost Regressor
    xgb_reg = xgb.XGBRegressor(random_state=42, n_jobs=-1)
    
    xgb_reg_params = {
        'n_estimators': [100, 200],
        'max_depth': [3, 6],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }
    
    print("Running GridSearchCV (this may take 2-3 minutes)...")
    xgb_reg_grid = GridSearchCV(
        xgb_reg, xgb_reg_params, cv=3, scoring='r2', n_jobs=-1, verbose=0
    )
    
    xgb_reg_grid.fit(X_train_transformed, y_train)
    
    # Predictions and metrics
    y_pred = xgb_reg_grid.predict(X_test_transformed)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\nBest parameters: {xgb_reg_grid.best_params_}")
    print(f"\nResults:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  MAE: {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    
    # Get feature importances
    importance = xgb_reg_grid.best_estimator_.feature_importances_
    
    return xgb_reg_grid, preprocessor, r2, mae, rmse, importance

def train_randomforest_classifier(X_train, X_test, y_train, y_test,
                                  categorical_cols, numerical_cols):
    """Train and evaluate RandomForestClassifier with hyperparameter tuning."""
    print("\n" + "="*60)
    print("TASK 2: RandomForestClassifier")
    print("="*60)
    
    # Create preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ],
        remainder='drop'
    )
    
    rf_clf = RandomForestClassifier(random_state=42, n_jobs=-1, class_weight='balanced')
    
    rf_clf_params = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    
    print("Running GridSearchCV (this may take 2-3 minutes)...")
    rf_clf_grid = GridSearchCV(
        rf_clf, rf_clf_params, cv=3, scoring='f1', n_jobs=-1, verbose=0
    )
    
    rf_clf_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', rf_clf_grid)
    ])
    
    rf_clf_pipeline.fit(X_train, y_train)
    
    # Predictions and metrics
    y_pred = rf_clf_pipeline.predict(X_test)
    y_proba = rf_clf_pipeline.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"\nBest parameters: {rf_clf_pipeline.named_steps['model'].best_params_}")
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]:,}, FP: {cm[0,1]:,}")
    print(f"  FN: {cm[1,0]:,}, TP: {cm[1,1]:,}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Get feature importances
    best_model = rf_clf_pipeline.named_steps['model'].best_estimator_
    importance = best_model.feature_importances_
    
    return rf_clf_pipeline, accuracy, precision, recall, f1, cm, importance

def train_xgboost_classifier(X_train, X_test, y_train, y_test,
                             categorical_cols, numerical_cols):
    """Train and evaluate XGBClassifier with hyperparameter tuning."""
    print("\n" + "="*60)
    print("TASK 2: XGBClassifier")
    print("="*60)
    
    # Preprocessor for XGBoost
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ],
        remainder='passthrough'
    )
    
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)
    
    # Calculate scale_pos_weight for imbalance
    scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
    
    xgb_clf = xgb.XGBClassifier(
        random_state=42, 
        n_jobs=-1,
        scale_pos_weight=scale_pos_weight,
        eval_metric='logloss'
    )
    
    xgb_clf_params = {
        'n_estimators': [100, 200],
        'max_depth': [3, 6],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }
    
    print("Running GridSearchCV (this may take 2-3 minutes)...")
    xgb_clf_grid = GridSearchCV(
        xgb_clf, xgb_clf_params, cv=3, scoring='f1', n_jobs=-1, verbose=0
    )
    
    xgb_clf_grid.fit(X_train_transformed, y_train)
    
    # Predictions and metrics
    y_pred = xgb_clf_grid.predict(X_test_transformed)
    y_proba = xgb_clf_grid.predict_proba(X_test_transformed)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"\nBest parameters: {xgb_clf_grid.best_params_}")
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]:,}, FP: {cm[0,1]:,}")
    print(f"  FN: {cm[1,0]:,}, TP: {cm[1,1]:,}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Get feature importances
    importance = xgb_clf_grid.best_estimator_.feature_importances_
    
    return xgb_clf_grid, preprocessor, accuracy, precision, recall, f1, cm, importance

# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def plot_feature_importance(importance_1, title_1, importance_2, title_2, 
                            task_name, top_k=20):
    """
    Plot feature importance for two models side by side.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Sort and take top k
    imp1_sorted = np.sort(importance_1)[::-1][:top_k]
    imp2_sorted = np.sort(importance_2)[::-1][:top_k]
    
    # RandomForest plot
    axes[0].bar(range(top_k), imp1_sorted, color='#2E86C1', alpha=0.8)
    axes[0].set_title(f'{title_1} - Top {top_k} Feature Importance', fontsize=12)
    axes[0].set_xlabel('Feature Index', fontsize=10)
    axes[0].set_ylabel('Importance', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # XGBoost plot
    axes[1].bar(range(top_k), imp2_sorted, color='#E74C3C', alpha=0.8)
    axes[1].set_title(f'{title_2} - Top {top_k} Feature Importance', fontsize=12)
    axes[1].set_xlabel('Feature Index', fontsize=10)
    axes[1].set_ylabel('Importance', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    plt.suptitle(f'Feature Importance Comparison - {task_name}', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(f'{task_name.replace(" ", "_").lower()}_feature_importance.png', dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()

def plot_confusion_matrices(cm_rf, cm_xgb, task_name):
    """
    Plot confusion matrices for both models side by side.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # RandomForest confusion matrix
    sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Blues', ax=axes[0],
                xticklabels=['Non-Fraud', 'Fraud'],
                yticklabels=['Non-Fraud', 'Fraud'])
    axes[0].set_title('RandomForestClassifier')
    axes[0].set_xlabel('Predicted')
    axes[0].set_ylabel('Actual')
    
    # XGBoost confusion matrix
    sns.heatmap(cm_xgb, annot=True, fmt='d', cmap='Reds', ax=axes[1],
                xticklabels=['Non-Fraud', 'Fraud'],
                yticklabels=['Non-Fraud', 'Fraud'])
    axes[1].set_title('XGBClassifier')
    axes[1].set_xlabel('Predicted')
    axes[1].set_ylabel('Actual')
    
    plt.suptitle(f'Confusion Matrices - {task_name}', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(f'{task_name.replace(" ", "_").lower()}_confusion_matrices.png', dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()

def plot_actual_vs_predicted(y_test, y_pred_rf, y_pred_xgb, task_name):
    """
    Plot actual vs predicted values for regression.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # RandomForest
    axes[0].scatter(y_test, y_pred_rf, alpha=0.5, color='#2E86C1')
    axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[0].set_xlabel('Actual Risk Score')
    axes[0].set_ylabel('Predicted Risk Score')
    axes[0].set_title('RandomForestRegressor')
    axes[0].grid(True, alpha=0.3)
    
    # XGBoost
    axes[1].scatter(y_test, y_pred_xgb, alpha=0.5, color='#E74C3C')
    axes[1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[1].set_xlabel('Actual Risk Score')
    axes[1].set_ylabel('Predicted Risk Score')
    axes[1].set_title('XGBRegressor')
    axes[1].grid(True, alpha=0.3)
    
    plt.suptitle(f'Actual vs Predicted - {task_name}', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(f'{task_name.replace(" ", "_").lower()}_actual_vs_predicted.png', dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function."""
    
    # Load data
    df = load_and_explore_data('transactions.csv')
    
    # ========================================================================
    # TASK 1: REGRESSION ON RISK_SCORE
    # ========================================================================
    
    print("\n" + "="*80)
    print("TASK 1: REGRESSION ON RISK_SCORE")
    print("="*80)
    
    # Prepare data
    X1, y1 = prep_data_task1(df)
    categorical_cols1, numerical_cols1 = get_column_types(X1)
    
    print(f"\nCategorical columns: {categorical_cols1}")
    print(f"Numerical columns: {numerical_cols1}")
    
    # Apply frequency encoding to high-cardinality columns
    high_card_cols = ['ip_address', 'pincode', 'receiver_pincode']
    X1_encoded, freq_encodings1 = apply_frequency_encoding(X1, high_card_cols)
    
    # Update column types after encoding
    categorical_cols1_updated = [col for col in categorical_cols1 
                                 if col not in high_card_cols and col in X1_encoded.columns]
    numerical_cols1_updated = [col for col in numerical_cols1 if col in X1_encoded.columns]
    freq_cols1 = [f'{col}_freq' for col in high_card_cols if f'{col}_freq' in X1_encoded.columns]
    numerical_cols1_updated = numerical_cols1_updated + freq_cols1
    
    print(f"\nUpdated categorical columns: {categorical_cols1_updated}")
    print(f"Updated numerical columns: {numerical_cols1_updated}")
    
    # Train/test split
    X1_train, X1_test, y1_train, y1_test = train_test_split(
        X1_encoded, y1, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set size: {X1_train.shape[0]}")
    print(f"Test set size: {X1_test.shape[0]}")
    print(f"Target range: {y1.min():.2f} to {y1.max():.2f}")
    
    # Train RandomForest Regressor
    rf_reg_pipeline, r2_rf, mae_rf, rmse_rf, rf_reg_importance = train_randomforest_regressor(
        X1_train, X1_test, y1_train, y1_test,
        categorical_cols1_updated, numerical_cols1_updated
    )
    
    # Train XGBoost Regressor
    xgb_reg_grid, xgb_reg_preprocessor, r2_xgb, mae_xgb, rmse_xgb, xgb_reg_importance = train_xgboost_regressor(
        X1_train, X1_test, y1_train, y1_test,
        categorical_cols1_updated, numerical_cols1_updated
    )
    
    # Get predictions for scatter plot
    y1_pred_rf = rf_reg_pipeline.predict(X1_test)
    y1_pred_xgb = xgb_reg_grid.predict(xgb_reg_preprocessor.transform(X1_test))
    
    # Plot actual vs predicted
    plot_actual_vs_predicted(y1_test, y1_pred_rf, y1_pred_xgb, 'Task_1_Regression')
    
    # Plot feature importance for Task 1
    plot_feature_importance(
        rf_reg_importance, 'RandomForestRegressor',
        xgb_reg_importance, 'XGBRegressor',
        'Task_1_Regression'
    )
    
    # ========================================================================
    # TASK 2: CLASSIFICATION ON IS_FRAUD
    # ========================================================================
    
    print("\n" + "="*80)
    print("TASK 2: CLASSIFICATION ON IS_FRAUD")
    print("="*80)
    
    # Prepare data
    X2, y2 = prep_data_task2(df)
    categorical_cols2, numerical_cols2 = get_column_types(X2)
    
    print(f"\nCategorical columns: {categorical_cols2}")
    print(f"Numerical columns: {numerical_cols2}")
    
    # Apply frequency encoding to high-cardinality columns
    X2_encoded, freq_encodings2 = apply_frequency_encoding(X2, high_card_cols)
    
    # Update column types after encoding
    categorical_cols2_updated = [col for col in categorical_cols2 
                                 if col not in high_card_cols and col in X2_encoded.columns]
    numerical_cols2_updated = [col for col in numerical_cols2 if col in X2_encoded.columns]
    freq_cols2 = [f'{col}_freq' for col in high_card_cols if f'{col}_freq' in X2_encoded.columns]
    numerical_cols2_updated = numerical_cols2_updated + freq_cols2
    
    print(f"\nUpdated categorical columns: {categorical_cols2_updated}")
    print(f"Updated numerical columns: {numerical_cols2_updated}")
    
    # Train/test split with stratification
    X2_train, X2_test, y2_train, y2_test = train_test_split(
        X2_encoded, y2, test_size=0.2, random_state=42, stratify=y2
    )
    
    print(f"\nTraining set size: {X2_train.shape[0]}")
    print(f"Test set size: {X2_test.shape[0]}")
    print(f"Fraud distribution in training:\n{y2_train.value_counts()}")
    print(f"Fraud distribution in test:\n{y2_test.value_counts()}")
    
    # Train RandomForest Classifier
    rf_clf_pipeline, accuracy_rf, precision_rf, recall_rf, f1_rf, cm_rf, rf_clf_importance = train_randomforest_classifier(
        X2_train, X2_test, y2_train, y2_test,
        categorical_cols2_updated, numerical_cols2_updated
    )
    
    # Train XGBoost Classifier
    xgb_clf_grid, xgb_clf_preprocessor, accuracy_xgb, precision_xgb, recall_xgb, f1_xgb, cm_xgb, xgb_clf_importance = train_xgboost_classifier(
        X2_train, X2_test, y2_train, y2_test,
        categorical_cols2_updated, numerical_cols2_updated
    )
    
    # Plot feature importance for Task 2
    plot_feature_importance(
        rf_clf_importance, 'RandomForestClassifier',
        xgb_clf_importance, 'XGBClassifier',
        'Task_2_Classification'
    )
    
    # Plot confusion matrices
    plot_confusion_matrices(cm_rf, cm_xgb, 'Task_2_Classification')
    
    # ========================================================================
    # FINAL COMPARISON TABLES
    # ========================================================================
    
    print("\n" + "="*80)
    print("FINAL RESULTS SUMMARY")
    print("="*80)
    
    # Task 1 Comparison
    print("\nTASK 1: Regression on risk_score")
    print("-"*50)
    comparison_df1 = pd.DataFrame({
        'Metric': ['R² Score', 'MAE', 'RMSE'],
        'RandomForest': [r2_rf, mae_rf, rmse_rf],
        'XGBoost': [r2_xgb, mae_xgb, rmse_xgb]
    })
    print(comparison_df1.to_string(index=False))
    
    # Determine which model performed better for Task 1
    if r2_rf > r2_xgb:
        best_regressor = "RandomForest"
        best_regressor_score = r2_rf
    else:
        best_regressor = "XGBoost"
        best_regressor_score = r2_xgb
    print(f"\n✓ Best Regressor: {best_regressor} (R² = {best_regressor_score:.4f})")
    
    # Task 2 Comparison
    print("\nTASK 2: Classification on is_fraud")
    print("-"*60)
    comparison_df2 = pd.DataFrame({
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
        'RandomForest': [accuracy_rf, precision_rf, recall_rf, f1_rf],
        'XGBoost': [accuracy_xgb, precision_xgb, recall_xgb, f1_xgb]
    })
    print(comparison_df2.to_string(index=False))
    
    # Determine which model performed better for Task 2
    if f1_rf > f1_xgb:
        best_classifier = "RandomForest"
        best_classifier_score = f1_rf
    else:
        best_classifier = "XGBoost"
        best_classifier_score = f1_xgb
    print(f"\n✓ Best Classifier: {best_classifier} (F1 = {best_classifier_score:.4f})")
    
    print("\nConfusion Matrices (Task 2):")
    print("-"*60)
    print("RandomForest:")
    print(f"  TN: {cm_rf[0,0]:,}, FP: {cm_rf[0,1]:,}")
    print(f"  FN: {cm_rf[1,0]:,}, TP: {cm_rf[1,1]:,}")
    fraud_detection_rate_rf = cm_rf[1,1] / (cm_rf[1,0] + cm_rf[1,1]) * 100
    print(f"  Fraud Detection Rate: {fraud_detection_rate_rf:.2f}%")
    
    print("\nXGBoost:")
    print(f"  TN: {cm_xgb[0,0]:,}, FP: {cm_xgb[0,1]:,}")
    print(f"  FN: {cm_xgb[1,0]:,}, TP: {cm_xgb[1,1]:,}")
    fraud_detection_rate_xgb = cm_xgb[1,1] / (cm_xgb[1,0] + cm_xgb[1,1]) * 100
    print(f"  Fraud Detection Rate: {fraud_detection_rate_xgb:.2f}%")
    
    # ========================================================================
    # SAVE MODELS
    # ========================================================================
    
    print("\n" + "="*80)
    print("SAVING MODELS")
    print("="*80)
    
    # Save Task 1 models
    joblib.dump(rf_reg_pipeline, 'rf_regressor_pipeline.pkl')
    print("✓ Saved: rf_regressor_pipeline.pkl")
    xgb_reg_grid.best_estimator_.save_model('xgb_regressor.json')
    print("✓ Saved: xgb_regressor.json")
    joblib.dump(xgb_reg_preprocessor, 'xgb_regressor_preprocessor.pkl')
    print("✓ Saved: xgb_regressor_preprocessor.pkl")
    
    # Save Task 2 models
    joblib.dump(rf_clf_pipeline, 'rf_classifier_pipeline.pkl')
    print("✓ Saved: rf_classifier_pipeline.pkl")
    xgb_clf_grid.best_estimator_.save_model('xgb_classifier.json')
    print("✓ Saved: xgb_classifier.json")
    joblib.dump(xgb_clf_preprocessor, 'xgb_classifier_preprocessor.pkl')
    print("✓ Saved: xgb_classifier_preprocessor.pkl")
    
    # Save frequency encodings
    joblib.dump(freq_encodings1, 'freq_encodings_regressor.pkl')
    print("✓ Saved: freq_encodings_regressor.pkl")
    joblib.dump(freq_encodings2, 'freq_encodings_classifier.pkl')
    print("✓ Saved: freq_encodings_classifier.pkl")
    
    # Save results
    results = {
        'task1': {
            'randomforest': {'r2': r2_rf, 'mae': mae_rf, 'rmse': rmse_rf},
            'xgboost': {'r2': r2_xgb, 'mae': mae_xgb, 'rmse': rmse_xgb}
        },
        'task2': {
            'randomforest': {
                'accuracy': accuracy_rf, 
                'precision': precision_rf, 
                'recall': recall_rf, 
                'f1': f1_rf, 
                'confusion_matrix': cm_rf.tolist()
            },
            'xgboost': {
                'accuracy': accuracy_xgb, 
                'precision': precision_xgb,
                'recall': recall_xgb, 
                'f1': f1_xgb, 
                'confusion_matrix': cm_xgb.tolist()
            }
        }
    }
    joblib.dump(results, 'model_results.pkl')
    print("✓ Saved: model_results.pkl")
    
    print("\n" + "="*80)
    print("✓ ALL MODELS AND RESULTS GENERATED SUCCESSFULLY!")
    print("="*80)
    
    # ========================================================================
    # MODEL SUMMARY
    # ========================================================================
    
    print("\n" + "="*80)
    print("MODEL SUMMARY")
    print("="*80)
    
    print("\nTask 1 - Regression (risk_score prediction):")
    print("-"*50)
    print(f"  Best Model: {best_regressor}")
    print(f"  R² Score: {best_regressor_score:.4f}")
    print(f"  MAE: {mae_xgb if best_regressor == 'XGBoost' else mae_rf:.4f}")
    print(f"  RMSE: {rmse_xgb if best_regressor == 'XGBoost' else rmse_rf:.4f}")
    
    print("\nTask 2 - Classification (fraud detection):")
    print("-"*50)
    print(f"  Best Model: {best_classifier}")
    print(f"  F1-Score: {best_classifier_score:.4f}")
    print(f"  Fraud Detection Rate: {fraud_detection_rate_xgb if best_classifier == 'XGBoost' else fraud_detection_rate_rf:.2f}%")
    print(f"  Precision: {precision_xgb if best_classifier == 'XGBoost' else precision_rf:.4f}")
    print(f"  Recall: {recall_xgb if best_classifier == 'XGBoost' else recall_rf:.4f}")
    
    print("\n" + "="*80)

# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

if __name__ == "__main__":
    main()