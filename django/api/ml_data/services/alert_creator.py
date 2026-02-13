"""
Alert Creator Service

Creates alert records from ML predictions.

Input:
    - DataFrame with predictions (from Predictor)

Output:
    - List of alert dictionaries
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any


class AlertCreator:
    """
    Creates alerts from ML predictions.

    Only transactions flagged as anomalies become alerts.
    Fraud type is inferred from transaction features.
    """

    def create_alerts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create alerts from predictions.

        Args:
            df: DataFrame with anomaly_score and is_anomaly columns

        Returns:
            List of alert dictionaries
        """
        # Filter to only anomalies
        anomalies = df[df["is_anomaly"] == True]

        alerts = []
        for _, row in anomalies.iterrows():
            alert = self._create_single_alert(row)
            alerts.append(alert)

        return alerts

    def _create_single_alert(self, row: pd.Series) -> Dict[str, Any]:
        """Create a single alert from a transaction row."""

        fraud_type, detector_type, signal = self._infer_fraud_type(row)
        severity = self._calculate_severity(row["anomaly_score"])

        alert = {
            "alert_id": f"ALT-{row['txn_id']:06d}",
            "event_time": row["event_time"].isoformat() + "Z" if hasattr(row["event_time"], "isoformat") else str(row["event_time"]),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "detector_type": detector_type,
            "detector_source": "ml_isolation_forest",
            "signal": signal,
            "severity": severity,
            "confidence": round(float(row["anomaly_score"]), 3),
            "fraud_type_inferred": fraud_type,
            "user_id": row["user_id"],
            "account_id": row["account_id"],
            "txn_id": int(row["txn_id"]),
            "evidence": self._build_evidence(row)
        }

        return alert

    def _infer_fraud_type(self, row: pd.Series) -> Tuple[str, str, str]:
        """
        Infer fraud type from transaction features.

        Returns: (fraud_type, detector_type, signal)
        """
        # Check for fraud ring indicators
        if "RING" in str(row.get("user_id", "")).upper():
            return "fraud_ring", "NETWORK", "COORDINATED_ACTIVITY"

        # Check for multi-account fraud
        if "MULTI" in str(row.get("user_id", "")).upper():
            return "multi_account_fraud", "TRANSACTION", "MULTI_ACCOUNT_LAYERING"

        # Account takeover indicators
        failed_logins = row.get("failed_login_1h", 0)
        geo_change = row.get("geo_change_1d", 0)
        new_ip = row.get("new_ip_1d", 0)

        if failed_logins >= 3 or (geo_change == 1 and new_ip == 1):
            return "account_takeover", "ATO", "SUSPICIOUS_LOGIN_PATTERN"

        # Income anomaly
        amount = row.get("amount", 0)
        income = row.get("declared_income", 1)
        if income > 0 and (amount / income) > 0.5:
            return "income_anomaly", "BEHAVIOR", "INCOME_EXCEEDS_DECLARATION"

        # Geo anomaly
        is_cross_border = row.get("is_cross_border", 0)
        if is_cross_border == 1 and geo_change == 1:
            return "geo_anomaly", "BEHAVIOR", "IMPOSSIBLE_TRAVEL"

        # Money mule indicators
        amount_in = row.get("amount_in_1d", 0)
        amount_out = row.get("amount_out_1d", 0)

        if amount_in > 5000 and amount_out > 5000:
            return "money_mule", "TRANSACTION", "RAPID_FUND_MOVEMENT"

        # Structuring
        if 8000 <= amount <= 9999:
            return "money_mule", "TRANSACTION", "STRUCTURING_PATTERN"

        # Default
        return "behavioral_anomaly", "BEHAVIOR", "ML_ANOMALY_DETECTED"

    def _calculate_severity(self, score: float) -> str:
        """Calculate alert severity from anomaly score."""
        if score > 0.7:
            return "CRITICAL"
        elif score > 0.5:
            return "HIGH"
        elif score > 0.3:
            return "MEDIUM"
        else:
            return "LOW"

    def _build_evidence(self, row: pd.Series) -> Dict[str, Any]:
        """Build evidence dictionary for alert."""
        evidence = {
            "anomaly_score": round(float(row.get("anomaly_score", 0)), 4),
            "amount": round(float(row.get("amount", 0)), 2),
            "currency": str(row.get("currency", "USD")).upper(),
            "channel": str(row.get("channel", "unknown")),
            "transaction_country": str(row.get("transaction_country", "")).upper(),
            "residence_country": str(row.get("residence_country", "")).upper(),
            "is_cross_border": bool(row.get("is_cross_border", False)),
            "device_id": str(row.get("device_id", "unknown")),
            "ip_address": str(row.get("ip_address", "unknown")),
            "failed_login_1h": int(row.get("failed_login_1h", 0)),
            "new_ip_1d": int(row.get("new_ip_1d", 0)),
            "geo_change_1d": int(row.get("geo_change_1d", 0))
        }

        # Add computed ratios if available
        if "amount_to_income_ratio" in row:
            evidence["amount_to_income_ratio"] = round(float(row["amount_to_income_ratio"]), 3)

        if "mod_z_score_abs" in row:
            evidence["mod_z_score"] = round(float(row["mod_z_score_abs"]), 3)

        return evidence
