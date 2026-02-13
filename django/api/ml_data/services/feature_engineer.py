"""
Feature Engineer Service

Transforms raw input data (JSON) into ML-ready features.

Supports two modes:
- B1 Mode: transactions.json with pre-computed aggregations
- B2 Mode: transactions_raw.json + auth_events.json + network_events.json
           (aggregations computed from raw events)

Input:
    - transactions.json OR transactions_raw.json: Transaction events
    - profiles.json: User profile/KYC data
    - auth_events.json (B2 only): Individual login attempts
    - network_events.json (B2 only): Device/IP events

Output:
    - DataFrame with ML features matching demo_data.csv structure

Features computed:
    - amount_abs: Absolute transaction amount
    - mod_z_score_abs: Modified z-score (deviation from user's baseline)
    - ewma_resid: Exponential moving average residual
    - gap_log: Log of time gap between transactions
    - amount_to_income_ratio: Transaction amount / declared income
    - is_cross_border: 1 if transaction country != residence country

Aggregations computed (B2 mode):
    - amount_in_1d: Sum of deposits in past 24h
    - amount_out_1d: Sum of withdrawals in past 24h
    - login_count_1h: Login count in past 1h
    - failed_login_1h: Failed login count in past 1h
    - new_ip_1d: Is this a new IP in past 24h?
    - geo_change_1d: Did geo location change in past 24h?
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import timedelta


class FeatureEngineer:
    """
    Transforms raw transaction and profile data into ML-ready features.
    """

    def __init__(self):
        self.transactions_df: Optional[pd.DataFrame] = None
        self.profiles_df: Optional[pd.DataFrame] = None
        self.auth_events_df: Optional[pd.DataFrame] = None
        self.network_events_df: Optional[pd.DataFrame] = None
        self.mode: str = "b1"  # "b1" or "b2"

    def load_from_json(
        self,
        transactions_path: Union[str, Path],
        profiles_path: Union[str, Path]
    ) -> "FeatureEngineer":
        """
        Load data from JSON files (B1 mode - with pre-computed aggregations).

        Args:
            transactions_path: Path to transactions.json
            profiles_path: Path to profiles.json

        Returns:
            self for chaining
        """
        with open(transactions_path) as f:
            transactions = json.load(f)

        with open(profiles_path) as f:
            profiles = json.load(f)

        self.transactions_df = pd.DataFrame(transactions)
        self.profiles_df = pd.DataFrame(profiles)

        # Parse datetime
        self.transactions_df["event_time"] = pd.to_datetime(
            self.transactions_df["event_time"]
        )

        self.mode = "b1"
        return self

    def load_from_raw_events(
        self,
        transactions_path: Union[str, Path],
        profiles_path: Union[str, Path],
        auth_events_path: Union[str, Path],
        network_events_path: Union[str, Path]
    ) -> "FeatureEngineer":
        """
        Load data from raw event JSON files (B2 mode - compute aggregations).

        Args:
            transactions_path: Path to transactions_raw.json
            profiles_path: Path to profiles.json
            auth_events_path: Path to auth_events.json
            network_events_path: Path to network_events.json

        Returns:
            self for chaining
        """
        with open(transactions_path) as f:
            transactions = json.load(f)

        with open(profiles_path) as f:
            profiles = json.load(f)

        with open(auth_events_path) as f:
            auth_events = json.load(f)

        with open(network_events_path) as f:
            network_events = json.load(f)

        self.transactions_df = pd.DataFrame(transactions)
        self.profiles_df = pd.DataFrame(profiles)
        self.auth_events_df = pd.DataFrame(auth_events)
        self.network_events_df = pd.DataFrame(network_events)

        # Parse datetimes (use ISO8601 format for flexibility)
        self.transactions_df["event_time"] = pd.to_datetime(
            self.transactions_df["event_time"], format="ISO8601"
        )
        self.auth_events_df["event_time"] = pd.to_datetime(
            self.auth_events_df["event_time"], format="ISO8601"
        )
        self.network_events_df["event_time"] = pd.to_datetime(
            self.network_events_df["event_time"], format="ISO8601"
        )

        self.mode = "b2"
        return self

    def load_from_dataframes(
        self,
        transactions_df: pd.DataFrame,
        profiles_df: pd.DataFrame
    ) -> "FeatureEngineer":
        """
        Load data from existing DataFrames.

        Args:
            transactions_df: Transaction data
            profiles_df: Profile data

        Returns:
            self for chaining
        """
        self.transactions_df = transactions_df.copy()
        self.profiles_df = profiles_df.copy()

        if "event_time" in self.transactions_df.columns:
            self.transactions_df["event_time"] = pd.to_datetime(
                self.transactions_df["event_time"]
            )

        self.mode = "b1"
        return self

    def compute_features(self) -> pd.DataFrame:
        """
        Compute all ML features.

        Returns:
            DataFrame with all features, matching demo_data.csv structure
        """
        if self.transactions_df is None:
            raise ValueError("No data loaded. Call load_from_json() or load_from_raw_events() first.")

        df = self.transactions_df.copy()

        # Join with profiles to get declared_income, residence_country
        profile_cols = ["user_id", "declared_income", "residence_country"]
        df = df.merge(
            self.profiles_df[profile_cols],
            on="user_id",
            how="left"
        )

        # Sort by user and time for time-series features
        df = df.sort_values(["user_id", "event_time"]).reset_index(drop=True)

        # In B2 mode, compute aggregations from raw events
        if self.mode == "b2":
            df = self._compute_amount_aggregations(df)
            df = self._compute_login_aggregations(df)
            df = self._compute_network_aggregations(df)

        # Compute ML features
        df = self._compute_amount_abs(df)
        df = self._compute_amount_to_income_ratio(df)
        df = self._compute_is_cross_border(df)
        df = self._compute_mod_z_score(df)
        df = self._compute_ewma_resid(df)
        df = self._compute_gap_log(df)

        # Reorder columns to match demo_data.csv + ML features
        column_order = [
            "user_id", "account_id", "txn_id", "event_time", "event_type",
            "amount", "currency", "channel", "declared_income", "account_deposit",
            "residence_country", "transaction_country", "amount_in_1d", "amount_out_1d",
            "login_count_1h", "failed_login_1h", "new_ip_1d", "geo_change_1d",
            "device_id", "ip_address",
            # ML features (computed)
            "amount_abs", "mod_z_score_abs", "ewma_resid", "gap_log",
            "amount_to_income_ratio", "is_cross_border"
        ]

        # Only include columns that exist
        final_columns = [c for c in column_order if c in df.columns]
        df = df[final_columns]

        return df

    # ==========================================================================
    # B2 Aggregation Methods - Compute from raw events
    # ==========================================================================

    def _compute_amount_aggregations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute amount_in_1d and amount_out_1d from transaction history.

        For each transaction, look back 24h and sum:
        - amount_in_1d: deposits + buys
        - amount_out_1d: withdrawals + sells
        """
        amount_in_1d = []
        amount_out_1d = []

        # Group transactions by user for efficient lookup
        user_txns = {}
        for _, row in df.iterrows():
            user_id = row["user_id"]
            if user_id not in user_txns:
                user_txns[user_id] = []
            user_txns[user_id].append({
                "event_time": row["event_time"],
                "event_type": row["event_type"],
                "amount": abs(row["amount"])
            })

        for _, row in df.iterrows():
            txn_time = row["event_time"]
            user_id = row["user_id"]
            lookback_start = txn_time - timedelta(days=1)

            # Get all transactions for this user in the past 24h (excluding current)
            user_history = user_txns.get(user_id, [])

            in_amount = 0.0
            out_amount = 0.0

            for hist_txn in user_history:
                if lookback_start <= hist_txn["event_time"] < txn_time:
                    if hist_txn["event_type"] in ["deposit", "buy"]:
                        in_amount += hist_txn["amount"]
                    elif hist_txn["event_type"] in ["withdrawal", "sell"]:
                        out_amount += hist_txn["amount"]

            amount_in_1d.append(round(in_amount, 2))
            amount_out_1d.append(round(out_amount, 2))

        df["amount_in_1d"] = amount_in_1d
        df["amount_out_1d"] = amount_out_1d

        return df

    def _compute_login_aggregations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute login_count_1h and failed_login_1h from auth events.

        For each transaction, count auth events in the hour before:
        - login_count_1h: total login attempts
        - failed_login_1h: failed login attempts
        """
        if self.auth_events_df is None or len(self.auth_events_df) == 0:
            df["login_count_1h"] = 0
            df["failed_login_1h"] = 0
            return df

        login_count_1h = []
        failed_login_1h = []

        # Group auth events by user for efficient lookup
        user_auth = {}
        for _, row in self.auth_events_df.iterrows():
            user_id = row["user_id"]
            if user_id not in user_auth:
                user_auth[user_id] = []
            user_auth[user_id].append({
                "event_time": row["event_time"],
                "event_type": row["event_type"],
                "related_txn_id": row.get("related_txn_id")
            })

        for _, row in df.iterrows():
            txn_time = row["event_time"]
            txn_id = row["txn_id"]
            user_id = row["user_id"]
            lookback_start = txn_time - timedelta(hours=1)

            # Get auth events for this user in the past hour
            user_events = user_auth.get(user_id, [])

            total_logins = 0
            failed_logins = 0

            for auth in user_events:
                # Check if this auth event is related to this transaction
                # (generated by extract_events.py with related_txn_id)
                if auth.get("related_txn_id") == txn_id:
                    total_logins += 1
                    if auth["event_type"] == "login_failed":
                        failed_logins += 1

            login_count_1h.append(total_logins)
            failed_login_1h.append(failed_logins)

        df["login_count_1h"] = login_count_1h
        df["failed_login_1h"] = failed_login_1h

        return df

    def _compute_network_aggregations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute new_ip_1d and geo_change_1d from network events.

        For B2, we read these directly from network_events since they're
        computed during event generation (simulating what a real system would do).
        """
        if self.network_events_df is None or len(self.network_events_df) == 0:
            df["new_ip_1d"] = 0
            df["geo_change_1d"] = 0
            return df

        # Create lookup by txn_id
        net_lookup = {}
        for _, row in self.network_events_df.iterrows():
            txn_id = row.get("related_txn_id")
            if txn_id is not None:
                net_lookup[txn_id] = {
                    "new_ip_1d": int(row.get("is_new_ip", 0)),
                    "geo_change_1d": int(row.get("is_geo_change", 0))
                }

        new_ip_1d = []
        geo_change_1d = []

        for _, row in df.iterrows():
            txn_id = row["txn_id"]
            net_data = net_lookup.get(txn_id, {"new_ip_1d": 0, "geo_change_1d": 0})
            new_ip_1d.append(net_data["new_ip_1d"])
            geo_change_1d.append(net_data["geo_change_1d"])

        df["new_ip_1d"] = new_ip_1d
        df["geo_change_1d"] = geo_change_1d

        return df

    # ==========================================================================
    # ML Feature Methods
    # ==========================================================================

    def _compute_amount_abs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute absolute transaction amount."""
        df["amount_abs"] = df["amount"].abs()
        return df

    def _compute_amount_to_income_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute amount to income ratio."""
        df["amount_to_income_ratio"] = (
            df["amount"].abs() / df["declared_income"].clip(lower=1)
        )
        return df

    def _compute_is_cross_border(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute cross-border flag."""
        df["is_cross_border"] = (
            df["transaction_country"].str.lower() != df["residence_country"].str.lower()
        ).astype(int)
        return df

    def _compute_mod_z_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute modified z-score per user.

        Modified z-score uses median and MAD instead of mean and std,
        making it more robust to outliers.
        """
        def calc_mod_z_score(group):
            median = group["amount"].median()
            mad = (group["amount"] - median).abs().median()
            if mad == 0:
                mad = group["amount"].std()
            if mad == 0 or pd.isna(mad):
                mad = 1
            return ((group["amount"] - median) / (1.4826 * mad)).abs()

        df["mod_z_score_abs"] = df.groupby("user_id", group_keys=False).apply(
            calc_mod_z_score
        ).fillna(0)

        return df

    def _compute_ewma_resid(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute exponential weighted moving average residual.

        This measures how much the current transaction deviates from
        the user's recent transaction pattern.
        """
        def calc_ewma_resid(group):
            ewma = group["amount"].ewm(span=5, min_periods=1).mean()
            return (group["amount"] - ewma).abs()

        df["ewma_resid"] = df.groupby("user_id", group_keys=False).apply(
            calc_ewma_resid
        ).fillna(0)

        return df

    def _compute_gap_log(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute log of time gap between transactions.

        Measures transaction velocity - smaller gaps = higher velocity.
        """
        def calc_gap_log(group):
            gaps = group["event_time"].diff().dt.total_seconds() / 3600  # hours
            gaps = gaps.fillna(24)  # Default 24 hours for first transaction
            return np.log1p(gaps.clip(lower=0.01))

        df["gap_log"] = df.groupby("user_id", group_keys=False).apply(
            calc_gap_log
        ).fillna(0)

        return df

    def get_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract only the ML feature columns needed for model prediction.

        Args:
            df: DataFrame with all computed features

        Returns:
            DataFrame with only ML feature columns
        """
        ml_features = [
            "amount_abs",
            "mod_z_score_abs",
            "ewma_resid",
            "gap_log",
            "amount_to_income_ratio",
            "is_cross_border"
        ]

        return df[ml_features]
