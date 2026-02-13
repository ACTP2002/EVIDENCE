"""
SENTINEL Fraud Detection Predictor
===================================
Run predictions using the trained SENTINEL model.

Usage:
    python predict.py --model sentinel_model.pkl --input test_data.csv
    python predict.py --model sentinel_model.pkl --input test_data.csv --output results.json
"""

import pandas as pd
import numpy as np
from scipy.stats import median_abs_deviation
import joblib
import json
import argparse


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering pipeline (same as training).
    """
    df = df.copy()

    df["event_time"] = pd.to_datetime(df["event_time"])
    df = df.sort_values(["user_id", "event_time"]).reset_index(drop=True)

    cat_cols = ["currency", "channel", "residence_country", "transaction_country", "event_type"]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    df["amount_abs"] = df["amount"].abs()
    df["amount_to_income_ratio"] = df["amount_abs"] / (df["declared_income"] + 1e-9)
    df["deposit_to_income_ratio"] = df["account_deposit"] / (df["declared_income"] + 1e-9)
    df["net_flow_1d"] = df["amount_in_1d"] - df["amount_out_1d"]

    grp = df.groupby("user_id", sort=False)

    GLOBAL_MEDIAN = df["amount_abs"].median()
    GLOBAL_MAD = median_abs_deviation(df["amount_abs"], scale="normal") + 1e-9

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

    df["baseline_median"] = df["user_median_15"].fillna(GLOBAL_MEDIAN)
    df["baseline_mad"] = df["user_mad_15"].fillna(GLOBAL_MAD)

    df["mod_z_score"] = 0.6745 * (df["amount_abs"] - df["baseline_median"]) / (df["baseline_mad"] + 1e-9)
    df["mod_z_score_abs"] = df["mod_z_score"].abs()

    df["ewma"] = grp["amount_abs"].transform(lambda s: s.ewm(span=8, adjust=False).mean())
    df["ewma_resid"] = (df["amount_abs"] - df["ewma"]).abs()

    df["prev_event_time"] = grp["event_time"].shift(1)
    df["gap_seconds"] = (df["event_time"] - df["prev_event_time"]).dt.total_seconds()
    df["gap_seconds"] = df["gap_seconds"].fillna(df["gap_seconds"].median())
    df["gap_log"] = np.log1p(df["gap_seconds"])

    df["failed_login_ratio_1h"] = df["failed_login_1h"] / (df["login_count_1h"] + 1e-9)
    df["new_ip_1d"] = df["new_ip_1d"].fillna(0).astype(int)
    df["geo_change_1d"] = df["geo_change_1d"].fillna(0).astype(int)

    df["is_cross_border"] = (df["residence_country"] != df["transaction_country"]).astype(int)

    return df


def predict(model_path: str, input_csv: str) -> list:
    """
    Run predictions on input data.

    Args:
        model_path: Path to trained model pickle
        input_csv: Path to input CSV

    Returns:
        List of prediction results
    """
    # Load model
    artifact = joblib.load(model_path)
    model = artifact["model"]
    scaler = artifact["scaler"]
    imputer = artifact["imputer"]
    threshold = artifact["threshold"]
    features = artifact["features"]

    # Load and process data
    df = pd.read_csv(input_csv)
    df = engineer_features(df)

    # Prepare features
    X = df[features].copy()
    X_imputed = imputer.transform(X)
    X_scaled = scaler.transform(X_imputed)

    # Predict
    raw_scores = model.decision_function(X_scaled)
    df["anomaly_score"] = -raw_scores
    df["is_anomaly"] = (df["anomaly_score"] >= threshold).astype(int)

    # Build output
    output_cols = ["user_id", "account_id", "txn_id", "event_time", "amount",
                   "anomaly_score", "is_anomaly"]

    # Add device_id and ip_address if available (for network analysis)
    for col in ["device_id", "ip_address", "transaction_country"]:
        if col in df.columns:
            output_cols.append(col)

    output = df[output_cols].copy()
    output["event_time"] = output["event_time"].astype(str)

    return output.to_dict(orient="records")


def main():
    parser = argparse.ArgumentParser(description="Run SENTINEL predictions")
    parser.add_argument("--model", "-m", required=True, help="Model pickle file")
    parser.add_argument("--input", "-i", required=True, help="Input CSV file")
    parser.add_argument("--output", "-o", help="Output JSON file (optional)")
    parser.add_argument("--anomalies-only", action="store_true",
                        help="Only output anomalies")

    args = parser.parse_args()

    print(f"Loading model from {args.model}...")
    print(f"Running predictions on {args.input}...")

    results = predict(args.model, args.input)

    if args.anomalies_only:
        results = [r for r in results if r["is_anomaly"] == 1]

    print(f"\nTotal transactions: {len(results) if not args.anomalies_only else 'N/A'}")
    anomaly_count = len([r for r in results if r["is_anomaly"] == 1])
    print(f"Anomalies detected: {anomaly_count}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print("\nAnomalies found:")
        print(json.dumps([r for r in results if r["is_anomaly"] == 1], indent=2))


if __name__ == "__main__":
    main()
