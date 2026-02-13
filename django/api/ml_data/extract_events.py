"""
Extract raw events from demo_data.csv into separate event JSON files.

This implements Option B2: Full Event Stream Simulation.

Unlike B1 (extract_to_json.py), this creates TRULY RAW events:
- transactions_raw.json: NO pre-computed aggregations
- auth_events.json: Individual login attempts (generated from login_count_1h, failed_login_1h)
- network_events.json: Device/IP events with geo info

The feature_engineer.py will then compute all aggregations from these raw events.

Usage:
    python extract_events.py
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
import hashlib


def generate_auth_events(df: pd.DataFrame) -> list:
    """
    Generate individual auth/login events from aggregated columns.

    For each transaction, if login_count_1h=5 and failed_login_1h=2,
    we generate:
    - 3 successful login events in the hour before the transaction
    - 2 failed login events in the hour before the transaction

    Events are deterministically generated using transaction ID as seed.
    """
    auth_events = []
    event_id = 1

    for _, row in df.iterrows():
        txn_time = pd.to_datetime(row["event_time"])
        user_id = row["user_id"]
        device_id = row["device_id"]
        ip_address = row["ip_address"]
        txn_country = row["transaction_country"]
        txn_id = int(row["txn_id"])

        total_logins = int(row["login_count_1h"])
        failed_logins = int(row["failed_login_1h"])
        successful_logins = total_logins - failed_logins

        # Generate login events spread across the hour before transaction
        # Use deterministic seeding based on txn_id
        np.random.seed(txn_id)

        # Generate timestamps for all logins in the hour before transaction
        # Spread them somewhat evenly with some randomness
        all_login_count = total_logins
        if all_login_count > 0:
            # Create time slots
            minutes_per_login = 60 / all_login_count

            login_times = []
            for i in range(all_login_count):
                # Base time: spread evenly
                base_minutes = (i + 0.5) * minutes_per_login
                # Add some jitter
                jitter = np.random.uniform(-minutes_per_login/3, minutes_per_login/3)
                minutes_before = max(1, min(59, base_minutes + jitter))
                login_time = txn_time - timedelta(minutes=minutes_before)
                login_times.append(login_time)

            # Sort chronologically
            login_times.sort()

            # Assign success/failure
            # Failed logins typically come before successful ones (user trying to get in)
            for i, login_time in enumerate(login_times):
                is_failed = i < failed_logins

                auth_event = {
                    "event_id": f"auth_{event_id:06d}",
                    "event_time": login_time.isoformat(),
                    "event_type": "login_failed" if is_failed else "login_success",
                    "user_id": user_id,
                    "device_id": device_id,
                    "ip_address": ip_address,
                    "geo_country": txn_country,
                    "session_id": f"sess_{txn_id}_{i}",
                    "related_txn_id": txn_id  # For verification
                }
                auth_events.append(auth_event)
                event_id += 1

    return auth_events


def generate_network_events(df: pd.DataFrame) -> list:
    """
    Generate network/device events from transaction data.

    Each transaction generates a network event capturing the device/IP context.
    The new_ip_1d and geo_change_1d flags indicate if this was a new IP or
    geo location change for the user.
    """
    network_events = []

    for _, row in df.iterrows():
        txn_time = pd.to_datetime(row["event_time"])

        network_event = {
            "event_id": f"net_{int(row['txn_id']):06d}",
            "event_time": txn_time.isoformat(),
            "user_id": row["user_id"],
            "account_id": row["account_id"],
            "device_id": row["device_id"],
            "ip_address": row["ip_address"],
            "geo_country": row["transaction_country"],
            "channel": row["channel"],
            "is_new_ip": int(row["new_ip_1d"]),
            "is_geo_change": int(row["geo_change_1d"]),
            "related_txn_id": int(row["txn_id"])  # For verification
        }
        network_events.append(network_event)

    return network_events


def extract_transactions_raw(df: pd.DataFrame) -> list:
    """
    Extract RAW transaction events - NO aggregations.

    Unlike B1 extract_to_json.py, this EXCLUDES:
    - amount_in_1d, amount_out_1d
    - login_count_1h, failed_login_1h
    - new_ip_1d, geo_change_1d

    These will be computed by feature_engineer from auth_events and network_events.
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
            "account_deposit": float(row["account_deposit"])
            # NOTE: NO aggregations here!
            # amount_in_1d, amount_out_1d, login_count_1h, etc. are EXCLUDED
        }
        transactions.append(txn)

    return transactions


def extract_profiles(df: pd.DataFrame) -> list:
    """
    Extract user profiles from CSV.

    Same as B1 - profiles don't change.
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

    # 1. Extract RAW transactions (no aggregations)
    print("\n[1/4] Extracting raw transactions (NO aggregations)...")
    transactions = extract_transactions_raw(df)
    txn_path = input_dir / "transactions_raw.json"
    with open(txn_path, "w") as f:
        json.dump(transactions, f, indent=2)
    print(f"  Saved {len(transactions)} transactions to {txn_path.name}")

    # 2. Generate auth events
    print("\n[2/4] Generating auth events from login columns...")
    auth_events = generate_auth_events(df)
    auth_path = input_dir / "auth_events.json"
    with open(auth_path, "w") as f:
        json.dump(auth_events, f, indent=2)
    print(f"  Saved {len(auth_events)} auth events to {auth_path.name}")

    # Count success/fail
    success_count = sum(1 for e in auth_events if e["event_type"] == "login_success")
    fail_count = sum(1 for e in auth_events if e["event_type"] == "login_failed")
    print(f"    - Successful logins: {success_count}")
    print(f"    - Failed logins: {fail_count}")

    # 3. Generate network events
    print("\n[3/4] Generating network events...")
    network_events = generate_network_events(df)
    net_path = input_dir / "network_events.json"
    with open(net_path, "w") as f:
        json.dump(network_events, f, indent=2)
    print(f"  Saved {len(network_events)} network events to {net_path.name}")

    # Count flags
    new_ip_count = sum(1 for e in network_events if e["is_new_ip"])
    geo_change_count = sum(1 for e in network_events if e["is_geo_change"])
    print(f"    - New IP events: {new_ip_count}")
    print(f"    - Geo change events: {geo_change_count}")

    # 4. Extract profiles (same as B1)
    print("\n[4/4] Extracting profiles...")
    profiles = extract_profiles(df)
    profile_path = input_dir / "profiles.json"
    with open(profile_path, "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"  Saved {len(profiles)} profiles to {profile_path.name}")

    # Summary
    print("\n" + "="*70)
    print("B2 EXTRACTION COMPLETE - Raw Event Stream Simulation")
    print("="*70)
    print(f"\nInput files created in: {input_dir}")
    print(f"  - transactions_raw.json: {len(transactions)} records (NO aggregations)")
    print(f"  - auth_events.json: {len(auth_events)} records")
    print(f"  - network_events.json: {len(network_events)} records")
    print(f"  - profiles.json: {len(profiles)} records")
    print("\nNext step: Run feature_engineer.py to compute aggregations from raw events")
    print("           Output should match demo_data.csv exactly!")

    # Verification hint
    print("\n" + "-"*70)
    print("VERIFICATION:")
    print("-"*70)
    print("Expected aggregations to compute:")
    total_logins = int(df["login_count_1h"].sum())
    total_failed = int(df["failed_login_1h"].sum())
    print(f"  - Total login_count_1h across all txns: {total_logins}")
    print(f"  - Total failed_login_1h across all txns: {total_failed}")
    print(f"  - Auth events generated: {len(auth_events)} (should equal {total_logins})")


if __name__ == "__main__":
    main()
