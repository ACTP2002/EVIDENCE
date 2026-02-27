import json
import joblib
import pandas as pd
import numpy as np
from scipy.stats import median_abs_deviation

def anomaly_prediction(model_path: str, input_csv: str):
  artifact = joblib.load(model_path)
  model = artifact["model"]
  threshold = artifact["threshold"]

  test_df = pd.read_csv(input_csv)
  test_df["event_time"] = pd.to_datetime(test_df["event_time"])

  test_df["amount_abs"] = test_df["amount"].abs()

  grp = test_df.groupby("user_id", sort=False)

  # Rolling windows (15 transactions minimum, 7 transactions at least to compute)
  test_df["amt_roll_med_15"] = grp["amount_abs"].transform(lambda s: s.rolling(15, min_periods=7).median())

  # Rolling MAD
  test_df["amt_roll_mad_15"] = grp["amount_abs"].transform(lambda s: s.rolling(15, min_periods=7).apply(
      lambda x: median_abs_deviation(x, scale="normal"), raw=False
  ))

  test_df["amt_dev_from_med"] = test_df["amount_abs"] - test_df["amt_roll_med_15"]
  test_df["amt_robust_z"] = test_df["amt_dev_from_med"] / (test_df["amt_roll_mad_15"] + 1e-9)

  test_df["prev_event_time"] = grp["event_time"].shift(1)
  # Gap between consecutive transactions (in seconds)
  test_df["gap_seconds"] = (test_df["event_time"] - test_df["prev_event_time"]).dt.total_seconds()

  # Fill first-transaction gaps
  test_df["gap_seconds"] = test_df["gap_seconds"].fillna(test_df["gap_seconds"].median())

  # Log-scaled time gap
  test_df["gap_log"] = np.log1p(test_df["gap_seconds"])

  test_df["deposit_to_income_ratio"] = (test_df["account_deposit"] / (test_df["declared_income"] + 1e-9))

  test_df["amount_to_income_ratio"] = (test_df["amount_abs"] / (test_df["declared_income"] + 1e-9))

  test_df["net_flow_1d"] = test_df["amount_in_1d"] - test_df["amount_out_1d"]

  test_df["failed_login_ratio_1h"] = (test_df["failed_login_1h"] / (test_df["login_count_1h"] + 1e-9))
  test_df["new_ip_1d"] = test_df["new_ip_1d"].fillna(0)
  test_df["geo_change_1d"] = test_df["geo_change_1d"].fillna(0)

  test_df["is_cross_border"] = (test_df["residence_country"] != test_df["transaction_country"]).astype(int)

  raw = model.decision_function(test_df)
  test_df["anomaly_score"] = -raw
  test_df["is_anomaly"] = (test_df["anomaly_score"] >= threshold).astype(int)

  output = test_df[
        ["user_id", "txn_id", "event_time", "anomaly_score", "is_anomaly"]
    ].copy()

  output["event_time"] = output["event_time"].astype(str)

  return output.to_dict(orient="records")

if __name__ == "__main__":
  results = anomaly_prediction(
      model_path="behavior_iforest.pkl",
      input_csv="test_transactions 2.csv"
  )

  print(json.dumps(results, indent=2))
