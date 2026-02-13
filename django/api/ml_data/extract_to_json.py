"""
Extract raw data from demo_data.csv into input JSON files.

This simulates what the input data would look like BEFORE ML processing.
Used for Option B1 verification - we can verify that feature_engineer.py
produces output matching demo_data.csv.

Usage:
    python extract_to_json.py
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime


def extract_transactions(df: pd.DataFrame) -> list:
    """
    Extract transaction events from CSV.

    These represent raw transaction events that would come from
    an event stream in production.
    """
    transactions = []

    for _, row in df.iterrows():
        txn = {
            "txn_id": int(row["txn_id"]),
            "event_time": row["event_time"],
            "user_id": row["user_id"],
            "account_id": row["account_id"],
            "event_type": row["event_type"],
            "amount": float(row["amount"]),
            "currency": row["currency"],
            "channel": row["channel"],
            "transaction_country": row["transaction_country"],
            "device_id": row["device_id"],
            "ip_address": row["ip_address"],
            # account_deposit varies per transaction (running balance)
            "account_deposit": float(row["account_deposit"]),
            # Aggregated fields (pre-computed for B1 simulation)
            # In production, these would be computed from event streams
            "amount_in_1d": float(row["amount_in_1d"]),
            "amount_out_1d": float(row["amount_out_1d"]),
            "login_count_1h": int(row["login_count_1h"]),
            "failed_login_1h": int(row["failed_login_1h"]),
            "new_ip_1d": int(row["new_ip_1d"]),
            "geo_change_1d": int(row["geo_change_1d"])
        }
        transactions.append(txn)

    return transactions


def extract_profiles(df: pd.DataFrame) -> list:
    """
    Extract user profiles from CSV.

    These represent user KYC/profile data.
    One profile per unique user.
    """
    profiles = []

    # Get unique users with their profile data
    user_data = df.groupby("user_id").first().reset_index()

    for _, row in user_data.iterrows():
        # Get all accounts for this user
        user_accounts = df[df["user_id"] == row["user_id"]]["account_id"].unique().tolist()

        profile = {
            "user_id": row["user_id"],
            "declared_income": int(row["declared_income"]),
            "account_deposit": float(row["account_deposit"]),
            "residence_country": row["residence_country"],
            "accounts": user_accounts
        }
        profiles.append(profile)

    return profiles


def main():
    script_dir = Path(__file__).parent
    input_dir = script_dir / "input"
    input_dir.mkdir(exist_ok=True)

    # Load CSV
    csv_path = script_dir / "demo_data.csv"
    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} transactions")

    # Extract transactions
    print("\nExtracting transactions...")
    transactions = extract_transactions(df)
    txn_path = input_dir / "transactions.json"
    with open(txn_path, "w") as f:
        json.dump(transactions, f, indent=2)
    print(f"  Saved {len(transactions)} transactions to {txn_path.name}")

    # Extract profiles
    print("\nExtracting profiles...")
    profiles = extract_profiles(df)
    profile_path = input_dir / "profiles.json"
    with open(profile_path, "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"  Saved {len(profiles)} profiles to {profile_path.name}")

    # Summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"\nInput files created in: {input_dir}")
    print(f"  - transactions.json: {len(transactions)} records")
    print(f"  - profiles.json: {len(profiles)} records")
    print("\nThese files represent INPUT to the ML pipeline.")
    print("Run feature_engineer.py next to compute ML features.")


if __name__ == "__main__":
    main()
