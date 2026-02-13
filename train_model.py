"""
SENTINEL Fraud Detection Model Trainer
=======================================
Trains an Isolation Forest model for behavioral anomaly detection.

Architecture matches the original Behavior_Model.ipynb:
- Isolation Forest (600 estimators)
- Feature engineering with rolling statistics
- Threshold calibration

Usage:
    python train_model.py --input training_data.csv --output sentinel_model.pkl
"""

import pandas as pd
import numpy as np
from scipy.stats import median_abs_deviation
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer
import joblib
import argparse
from pathlib import Path


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering pipeline.
    Creates behavioral features for anomaly detection.
    """
    df = df.copy()

    # Ensure datetime
    df["event_time"] = pd.to_datetime(df["event_time"])

    # Sort by user and time
    df = df.sort_values(["user_id", "event_time"]).reset_index(drop=True)

    # Normalize categorical columns
    cat_cols = ["currency", "channel", "residence_country", "transaction_country", "event_type"]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    # ========== TRANSACTION AMOUNT FEATURES ==========

    # Absolute amount
    df["amount_abs"] = df["amount"].abs()

    # Amount ratios
    df["amount_to_income_ratio"] = df["amount_abs"] / (df["declared_income"] + 1e-9)
    df["deposit_to_income_ratio"] = df["account_deposit"] / (df["declared_income"] + 1e-9)

    # Net flow
    df["net_flow_1d"] = df["amount_in_1d"] - df["amount_out_1d"]

    # ========== ROLLING STATISTICS (Per User) ==========

    grp = df.groupby("user_id", sort=False)

    # Global fallbacks
    GLOBAL_MEDIAN = df["amount_abs"].median()
    GLOBAL_MAD = median_abs_deviation(df["amount_abs"], scale="normal") + 1e-9

    # Rolling median and MAD (15-transaction window)
    ROLL_WINDOW = 15
    ROLL_MIN = 2

    df["user_median_15"] = grp["amount_abs"].transform(
        lambda s: s.rolling(ROLL_WINDOW, min_periods=ROLL_MIN).median()
    )

    df["user_mad_15"] = grp["amount_abs"].transform(
        lambda s: s.rolling(ROLL_WINDOW, min_periods=ROLL_MIN).apply(
            lambda x: median_abs_deviation(x, scale="normal"), raw=False
        )
    )

    # Fallback to global stats for users with few transactions
    df["baseline_median"] = df["user_median_15"].fillna(GLOBAL_MEDIAN)
    df["baseline_mad"] = df["user_mad_15"].fillna(GLOBAL_MAD)

    # Modified Z-score (robust outlier detection)
    df["mod_z_score"] = 0.6745 * (df["amount_abs"] - df["baseline_median"]) / (df["baseline_mad"] + 1e-9)
    df["mod_z_score_abs"] = df["mod_z_score"].abs()

    # EWMA (Exponentially Weighted Moving Average) for drift detection
    df["ewma"] = grp["amount_abs"].transform(lambda s: s.ewm(span=8, adjust=False).mean())
    df["ewma_resid"] = (df["amount_abs"] - df["ewma"]).abs()

    # ========== TIME GAP FEATURES ==========

    df["prev_event_time"] = grp["event_time"].shift(1)
    df["gap_seconds"] = (df["event_time"] - df["prev_event_time"]).dt.total_seconds()
    df["gap_seconds"] = df["gap_seconds"].fillna(df["gap_seconds"].median())
    df["gap_log"] = np.log1p(df["gap_seconds"])

    # ========== ACCESS RISK FEATURES ==========

    df["failed_login_ratio_1h"] = df["failed_login_1h"] / (df["login_count_1h"] + 1e-9)
    df["new_ip_1d"] = df["new_ip_1d"].fillna(0).astype(int)
    df["geo_change_1d"] = df["geo_change_1d"].fillna(0).astype(int)

    # ========== LOCATION FEATURES ==========

    df["is_cross_border"] = (df["residence_country"] != df["transaction_country"]).astype(int)

    return df


def train_isolation_forest(df: pd.DataFrame,
                            contamination: float = 0.02,
                            n_estimators: int = 600) -> dict:
    """
    Train Isolation Forest model.

    Args:
        df: DataFrame with engineered features
        contamination: Expected proportion of anomalies (default 2%)
        n_estimators: Number of trees

    Returns:
        Dictionary with model, scaler, imputer, threshold, and feature names
    """

    # Features for Isolation Forest
    features = [
        "amount_abs",
        "mod_z_score_abs",
        "ewma_resid",
        "gap_log",
        "amount_to_income_ratio",
        "is_cross_border"
    ]

    # Ensure all features exist
    features = [f for f in features if f in df.columns]

    print(f"Training with features: {features}")

    # Prepare data
    X = df[features].copy()

    # Impute missing values
    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X)

    # Scale features (RobustScaler handles outliers better)
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # Train Isolation Forest
    print(f"Training Isolation Forest with {n_estimators} estimators...")
    model = IsolationForest(
        n_estimators=n_estimators,
        max_samples="auto",
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_scaled)

    # Calculate threshold
    # Isolation Forest: decision_function returns negative for anomalies
    # We negate to make higher = more anomalous
    raw_scores = model.decision_function(X_scaled)
    anomaly_scores = -raw_scores

    # Set threshold at specified percentile
    threshold = np.percentile(anomaly_scores, (1 - contamination) * 100)

    print(f"Threshold set at: {threshold:.6f}")
    print(f"Score range: [{anomaly_scores.min():.4f}, {anomaly_scores.max():.4f}]")

    # Count anomalies
    anomalies = (anomaly_scores >= threshold).sum()
    print(f"Training anomalies: {anomalies} ({anomalies/len(df)*100:.2f}%)")

    return {
        "model": model,
        "scaler": scaler,
        "imputer": imputer,
        "threshold": threshold,
        "features": features,
        "training_stats": {
            "n_samples": len(df),
            "n_features": len(features),
            "contamination": contamination,
            "threshold": threshold,
            "anomalies_found": int(anomalies)
        }
    }


def save_model(artifact: dict, output_path: str):
    """Save model artifact to pickle file."""
    joblib.dump(artifact, output_path)
    print(f"Model saved to {output_path}")


def evaluate_model(df: pd.DataFrame, artifact: dict) -> dict:
    """
    Evaluate model performance if labels are available.
    """
    if "is_fraud" not in df.columns:
        print("No labels available for evaluation")
        return {}

    features = artifact["features"]
    model = artifact["model"]
    scaler = artifact["scaler"]
    imputer = artifact["imputer"]
    threshold = artifact["threshold"]

    X = df[features].copy()
    X_imputed = imputer.transform(X)
    X_scaled = scaler.transform(X_imputed)

    raw_scores = model.decision_function(X_scaled)
    anomaly_scores = -raw_scores
    predictions = (anomaly_scores >= threshold).astype(int)

    # True labels
    y_true = df["is_fraud"].values

    # Metrics
    tp = ((predictions == 1) & (y_true == 1)).sum()
    fp = ((predictions == 1) & (y_true == 0)).sum()
    tn = ((predictions == 0) & (y_true == 0)).sum()
    fn = ((predictions == 0) & (y_true == 1)).sum()

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    results = {
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4)
    }

    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    print(f"True Positives:  {tp} (fraud correctly caught)")
    print(f"False Positives: {fp} (normal flagged as fraud)")
    print(f"True Negatives:  {tn} (normal correctly cleared)")
    print(f"False Negatives: {fn} (fraud missed)")
    print(f"\nPrecision: {precision:.2%} (of flagged, how many are real fraud)")
    print(f"Recall:    {recall:.2%} (of real fraud, how many did we catch)")
    print(f"F1 Score:  {f1:.2%}")
    print("="*50)

    return results


def main():
    parser = argparse.ArgumentParser(description="Train SENTINEL fraud detection model")
    parser.add_argument("--input", "-i", required=True, help="Input training data CSV")
    parser.add_argument("--output", "-o", default="sentinel_model.pkl", help="Output model file")
    parser.add_argument("--contamination", "-c", type=float, default=0.02,
                        help="Expected anomaly rate (default: 0.02)")
    parser.add_argument("--estimators", "-e", type=int, default=600,
                        help="Number of trees (default: 600)")
    parser.add_argument("--evaluate", action="store_true",
                        help="Evaluate if labeled data available")

    args = parser.parse_args()

    # Load data
    print(f"Loading data from {args.input}...")
    df = pd.read_csv(args.input)
    print(f"Loaded {len(df)} transactions")

    # Check for labels
    labeled_file = args.input.replace('.csv', '_labeled.csv')
    if Path(labeled_file).exists() and args.evaluate:
        print(f"Found labeled data: {labeled_file}")
        df = pd.read_csv(labeled_file)

    # Engineer features
    print("\nEngineering features...")
    df = engineer_features(df)

    # Train model
    print("\nTraining model...")
    artifact = train_isolation_forest(
        df,
        contamination=args.contamination,
        n_estimators=args.estimators
    )

    # Evaluate if labels available
    if "is_fraud" in df.columns:
        artifact["evaluation"] = evaluate_model(df, artifact)

    # Save model
    save_model(artifact, args.output)

    print("\nDone! Model ready for use.")
    print(f"To use: artifact = joblib.load('{args.output}')")


if __name__ == "__main__":
    main()
