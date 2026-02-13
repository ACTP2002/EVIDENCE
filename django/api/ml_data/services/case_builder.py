"""
Case Builder Service

Groups related alerts into investigation cases.

Input:
    - List of alerts (from AlertCreator)

Output:
    - List of case dictionaries
"""

from datetime import datetime
from typing import Dict, List, Any, Set
from collections import defaultdict


class CaseBuilder:
    """
    Groups related alerts into cases for investigation.

    Grouping logic:
    1. Fraud rings: Group by shared device_id
    2. Multi-account fraud: Group by user with multiple accounts
    3. Other fraud: Group by user_id
    """

    def build_cases(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build cases from alerts.

        Args:
            alerts: List of alert dictionaries

        Returns:
            List of case dictionaries
        """
        if not alerts:
            return []

        cases = []
        processed_alert_ids: Set[str] = set()

        # First pass: Find fraud rings (shared device)
        cases_from_rings, processed_alert_ids = self._build_fraud_ring_cases(
            alerts, processed_alert_ids
        )
        cases.extend(cases_from_rings)

        # Second pass: Group remaining alerts by user
        cases_from_users = self._build_user_cases(alerts, processed_alert_ids)
        cases.extend(cases_from_users)

        return cases

    def _build_fraud_ring_cases(
        self,
        alerts: List[Dict[str, Any]],
        processed_ids: Set[str]
    ) -> tuple:
        """
        Build cases for fraud rings (multiple users, same device).

        Returns:
            (cases, updated_processed_ids)
        """
        cases = []

        # Group by device_id
        device_groups: Dict[str, List[Dict]] = defaultdict(list)
        for alert in alerts:
            device_id = alert.get("evidence", {}).get("device_id", "unknown")
            if device_id != "unknown":
                device_groups[device_id].append(alert)

        # Create cases for rings (multiple users on same device)
        for device_id, device_alerts in device_groups.items():
            unique_users = set(a["user_id"] for a in device_alerts)

            if len(unique_users) > 1:
                # This is a fraud ring
                case = self._build_single_case(
                    alerts=device_alerts,
                    fraud_type="fraud_ring",
                    case_suffix=f"RING-{device_id[-8:]}"
                )
                case["ring_members"] = list(unique_users)
                case["shared_device"] = device_id
                case["shared_ip"] = device_alerts[0].get("evidence", {}).get("ip_address")
                cases.append(case)

                # Mark alerts as processed
                for alert in device_alerts:
                    processed_ids.add(alert["alert_id"])

        return cases, processed_ids

    def _build_user_cases(
        self,
        alerts: List[Dict[str, Any]],
        processed_ids: Set[str]
    ) -> List[Dict[str, Any]]:
        """
        Build cases grouped by user.

        Returns:
            List of cases
        """
        cases = []

        # Group remaining alerts by user
        user_groups: Dict[str, List[Dict]] = defaultdict(list)
        for alert in alerts:
            if alert["alert_id"] not in processed_ids:
                user_groups[alert["user_id"]].append(alert)

        # Create user-level cases
        for user_id, user_alerts in user_groups.items():
            if not user_alerts:
                continue

            # Determine primary fraud type
            fraud_types = [a.get("fraud_type_inferred", "unknown") for a in user_alerts]
            primary_type = max(set(fraud_types), key=fraud_types.count)

            # Check for multi-account
            unique_accounts = set(a["account_id"] for a in user_alerts)
            if len(unique_accounts) > 1:
                primary_type = "multi_account_fraud"

            case = self._build_single_case(
                alerts=user_alerts,
                fraud_type=primary_type,
                case_suffix=user_id
            )

            if primary_type == "multi_account_fraud":
                case["accounts_involved"] = list(unique_accounts)

            cases.append(case)

        return cases

    def _build_single_case(
        self,
        alerts: List[Dict[str, Any]],
        fraud_type: str,
        case_suffix: str
    ) -> Dict[str, Any]:
        """Build a single case from a group of alerts."""

        # Calculate case score
        scores = [a.get("confidence", 0) for a in alerts]
        max_score = max(scores) if scores else 0
        avg_score = sum(scores) / len(scores) if scores else 0

        # Higher score for more alerts
        alert_factor = min(len(alerts) * 0.05, 0.2)
        case_score = int(min(95, (avg_score + max_score) / 2 * 100 + alert_factor * 100))

        # Determine risk level
        if case_score >= 80:
            risk_level = "CRITICAL"
        elif case_score >= 60:
            risk_level = "HIGH"
        elif case_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Get time range
        times = [a["event_time"] for a in alerts]

        # Calculate total amount
        total_amount = sum(
            a.get("evidence", {}).get("amount", 0) for a in alerts
        )

        # Get first alert's user_id (or list for fraud rings)
        if fraud_type == "fraud_ring":
            user_id = list(set(a["user_id"] for a in alerts))
        else:
            user_id = alerts[0]["user_id"]

        case = {
            "case_id": f"CASE-{datetime.now().strftime('%Y%m%d')}-{case_suffix[:12].upper()}",
            "created_by": "ml_pipeline",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "OPEN",
            "priority": risk_level,
            "case_score": case_score,
            "risk_level": risk_level,
            "fraud_type": fraud_type,
            "user_id": user_id,
            "account_id": alerts[0]["account_id"],
            "alert_ids": [a["alert_id"] for a in alerts],
            "alert_count": len(alerts),
            "summary": {
                "total_alerts": len(alerts),
                "total_amount": round(total_amount, 2),
                "unique_users": len(set(a["user_id"] for a in alerts)),
                "unique_accounts": len(set(a["account_id"] for a in alerts)),
                "max_anomaly_score": round(max_score, 3),
                "avg_anomaly_score": round(avg_score, 3),
                "time_range": {
                    "first": min(times),
                    "last": max(times)
                }
            },
            "investigation": {
                "status": "pending",
                "assigned_to": None,
                "ai_summary": None,
                "recommendations": []
            }
        }

        return case
