import random
import string
import json
from datetime import datetime, UTC


class CaseBuilder:
    def __init__(self):
        pass

    # ---------- Private Helpers ----------

    def _generate_case_id(self):
        date_str = datetime.now(UTC).strftime("%Y%m%d")
        random_part = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        return f"CASE-{date_str}-{random_part}"

    def _generate_alert_id(self, index: int) -> str:
        return f"A-{index:03d}"

    def _to_iso_z(self, dt_string: str) -> str:
        dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---------- Public API ----------

    def build_cases(self, alert_list: list) -> list:
        """
        Groups alerts automatically by user_id and builds case objects.
        """

        cases = {}

        for alert in alert_list:
            user_id = alert["user_id"]

            if user_id not in cases:
                cases[user_id] = {
                    "case_id": self._generate_case_id(),
                    "user_id": user_id,
                    "status": "OPEN",
                    "alerts": []
                }

            alert_index = len(cases[user_id]["alerts"]) + 1

            formatted_alert = {
                "alert_id": self._generate_alert_id(alert_index),
                "event_time": self._to_iso_z(alert["event_time"]),
                "detector_type": alert["detector_type"],
                "signal": alert["signal"],
                "severity": alert["severity"],
                "confidence": float(alert["confidence"]),
                "evidence": alert.get("evidence", [])
            }

            cases[user_id]["alerts"].append(formatted_alert)

        return list(cases.values())

    def to_json(self, cases: list, indent: int = 4) -> str:
        """
        Converts case list to formatted JSON string.
        """
        return json.dumps(cases, indent=indent)


# ---------- Example Usage ----------

if __name__ == "__main__":
    ### SAMPLE ALERT LIST ####
    # alert_list = [

    #   # ---------- U9001 ----------
    #   {
    #       "event_time": "2026-03-03 01:10:00",
    #       "txn_id": "8",
    #       "user_id": "U9001",
    #       "is_anomaly": 0,
    #       "detector_type": "BEHAVIOR",
    #       "signal": "Liquidity Shift",
    #       "severity": "LOW",
    #       "confidence": "0.9934347970563214",
    #       "evidence": [
    #           {
    #               "risk_category": "Liquidity Shift",
    #               "feature": "net_flow_1d",
    #               "impact": "reduced",
    #               "contribution": -0.0098327295854687,
    #               "explanation": "Daily net cash flow shift detected (net_flow_1d=1000.00). This reduced anomaly risk."
    #           },
    #           {
    #               "risk_category": "Monetary Deviation",
    #               "feature": "ewma_resid",
    #               "impact": "reduced",
    #               "contribution": -0.0090753240510821,
    #               "explanation": "Recent transaction amount differs from short-term trend (EWMA residual=0.00). This reduced anomaly risk."
    #           }
    #       ]
    #   },
    #   {
    #       "event_time": "2026-03-03 01:12:00",
    #       "txn_id": "9",
    #       "user_id": "U9001",
    #       "is_anomaly": 1,
    #       "detector_type": "BEHAVIOR",
    #       "signal": "Monetary Deviation",
    #       "severity": "HIGH",
    #       "confidence": "0.9987824745707596",
    #       "evidence": [
    #           {
    #               "risk_category": "Monetary Deviation",
    #               "feature": "ewma_resid",
    #               "impact": "increased",
    #               "contribution": 0.0736454203724861,
    #               "explanation": "Recent transaction amount differs from short-term trend (EWMA residual=10500.00). This increased anomaly risk."
    #           },
    #           {
    #               "risk_category": "Liquidity Shift",
    #               "feature": "net_flow_1d",
    #               "impact": "increased",
    #               "contribution": 0.0728737562894821,
    #               "explanation": "Daily net cash flow shift detected (net_flow_1d=-24000.00). This increased anomaly risk."
    #           }
    #       ]
    #   },
    #   {
    #       "event_time": "2026-03-03 01:13:00",
    #       "txn_id": "10",
    #       "user_id": "U9001",
    #       "is_anomaly": 1,
    #       "detector_type": "BEHAVIOR",
    #       "signal": "Liquidity Shift",
    #       "severity": "HIGH",
    #       "confidence": "0.9958792943956113",
    #       "evidence": [
    #           {
    #               "risk_category": "Liquidity Shift",
    #               "feature": "net_flow_1d",
    #               "impact": "increased",
    #               "contribution": 0.1100607514381408,
    #               "explanation": "Daily net cash flow shift detected (net_flow_1d=-42000.00). This increased anomaly risk."
    #           },
    #           {
    #               "risk_category": "Temporal Anomaly",
    #               "feature": "gap_log",
    #               "impact": "increased",
    #               "contribution": 0.022754643112421,
    #               "explanation": "Transaction timing gap is unusual compared to prior activity (gap_log=4.11). This increased anomaly risk."
    #           }
    #       ]
    #   },

    #   # ---------- U1001 ----------
    #   {
    #       "event_time": "2026-03-01 09:00:00",
    #       "txn_id": "1",
    #       "user_id": "U1001",
    #       "is_anomaly": 0,
    #       "detector_type": "BEHAVIOR",
    #       "signal": "Liquidity Shift",
    #       "severity": "LOW",
    #       "confidence": "0.9939026409883166",
    #       "evidence": [
    #           {
    #               "risk_category": "Liquidity Shift",
    #               "feature": "net_flow_1d",
    #               "impact": "reduced",
    #               "contribution": -0.0096564134582877,
    #               "explanation": "Daily net cash flow shift detected (net_flow_1d=500.00). This reduced anomaly risk."
    #           },
    #           {
    #               "risk_category": "Monetary Deviation",
    #               "feature": "ewma_resid",
    #               "impact": "reduced",
    #               "contribution": -0.0090642059221863,
    #               "explanation": "Recent transaction amount differs from short-term trend (EWMA residual=0.00). This reduced anomaly risk."
    #           }
    #       ]
    #   },
    #   {
    #       "event_time": "2026-03-01 12:00:00",
    #       "txn_id": "2",
    #       "user_id": "U1001",
    #       "is_anomaly": 0,
    #       "detector_type": "BEHAVIOR",
    #       "signal": "Monetary Deviation",
    #       "severity": "LOW",
    #       "confidence": "0.9879828125993106",
    #       "evidence": [
    #           {
    #               "risk_category": "Monetary Deviation",
    #               "feature": "ewma_resid",
    #               "impact": "reduced",
    #               "contribution": -0.0108003849163651,
    #               "explanation": "Recent transaction amount differs from short-term trend (EWMA residual=131.25). This reduced anomaly risk."
    #           },
    #           {
    #               "risk_category": "Temporal Anomaly",
    #               "feature": "gap_log",
    #               "impact": "increased",
    #               "contribution": 0.0100764408707618,
    #               "explanation": "Transaction timing gap is unusual compared to prior activity (gap_log=9.29). This increased anomaly risk."
    #           }
    #       ]
    #   }
    # ]

    builder = CaseBuilder()

    cases = builder.build_cases(alert_list)

    print(builder.to_json(cases))
