from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json
import os
from pathlib import Path

class FraudCaseDetailView(APIView):
    _mock_db = None
    
    @classmethod
    def get_mock_db(cls):
        if cls._mock_db is None:
            # Option 1: Same directory as views.py
            file_path = Path(__file__).parent / 'fraud_cases.txt'
            
            
            with open(file_path, 'r') as f:
                cls._mock_db = json.load(f)
        return cls._mock_db

    def get(self, request, case_id=None):
        db = self.get_mock_db()
        
        if case_id:
            case = next((item for item in db if item["case_metadata"]["case_id"] == case_id), None)
            if case:
                return Response(case)
            return Response({"error": "Not found"}, status=404)
        return Response(db)
    
class CaseSummaryView(APIView):
    def get(self, request):
        data = {
            "case_id": "CASE-2025-88412",
            "created_at": "2025-05-14T09:15:00Z",
            "assembled_at": "2025-05-14T09:15:22Z",
            "alerts": [
                {
                    "alert_id": "ALT-9901",
                    "alert_type": "money_laundering",
                    "triggered_at": "2025-05-14T08:00:00Z",
                    "severity": "critical",
                    "risk_score": 92,
                    "description": "Total deposits ($35,000) exceed declared monthly income ($2,500) by 1400%.",
                    "detector_source": "ml_anomaly"
                }
            ],
            "customer": {
                "customer_id": "CUST-7721",
                "full_name": "James Terrence Miller",
                "email": "j.miller882@gmail.com",
                "phone": "+1-555-0199",
                "date_of_birth": "1985-11-12",
                "country": "USA",
                "address": "123 Maple St, Springfield, IL",
                "verification_status": "verified",
                "verification_method": "biometric",
                "verification_date": "2025-01-10",
                "declared_income": 2500.00,
                "income_currency": "USD",
                "employment_status": "Self-employed",
                "risk_rating": "high",
                "pep_status": False,
                "sanctions_hit": False,
                "adverse_media": True,
                "document_type": "passport",
                "document_country": "USA",
                "document_verified": True,
                "document_flags": ["ai_generated_face_risk", "unusual_font_spacing"]
            },
            "account": {
                "account_id": "ACC-882193",
                "account_type": "trading",
                "account_status": "under_review",
                "created_at": "2025-01-10T14:22:10Z",
                "total_deposits_30d": 35000.00,
                "total_withdrawals_30d": 32000.00,
                "total_trades_30d": 145,
                "average_transaction_amount": 241.37,
                "deposit_to_income_ratio": 14.0,
                "account_age_days": 124,
                "is_dormant_reactivated": True
            },
            "transactions": [
                {
                    "transaction_id": "TXN-44102",
                    "timestamp": "2025-05-13T14:20:00Z",
                    "type": "deposit",
                    "amount": 15000.00,
                    "currency": "USD",
                    "status": "completed",
                    "channel": "crypto",
                    "counterparty": "External Wallet (0x71C...a4f)",
                    "risk_flags": ["high_amount", "obfuscated_source"]
                },
                {
                    "transaction_id": "TXN-44105",
                    "timestamp": "2025-05-13T16:05:00Z",
                    "type": "withdrawal",
                    "amount": 14500.00,
                    "currency": "USD",
                    "status": "completed",
                    "channel": "bank_transfer",
                    "counterparty": "Offshore Bank Ltd",
                    "risk_flags": ["rapid_outflow", "high_risk_destination"]
                }
            ],
            "logins": [
                {
                    "event_id": "EVT-1029",
                    "timestamp": "2025-05-14T07:45:00Z",
                    "ip_address": "192.168.1.1",
                    "device_id": "DEV-IPHONE-99",
                    "device_type": "mobile",
                    "browser": "Mobile Safari",
                    "location_country": "Nigeria",
                    "location_city": "Lagos",
                    "is_vpn": True,
                    "is_proxy": False,
                    "login_success": True,
                    "failure_reason": None,
                    "risk_flags": ["new_location", "impossible_travel", "vpn_detected"]
                }
            ],
            "devices": [
                {
                    "device_id": "DEV-IPHONE-99",
                    "device_type": "mobile",
                    "os": "iOS 17.4",
                    "first_seen": "2025-05-10T10:00:00Z",
                    "last_seen": "2025-05-14T07:45:00Z",
                    "is_trusted": False,
                    "linked_accounts": ["ACC-0012", "ACC-4491", "ACC-7721"]
                }
            ],
            "network_connections": [
                {
                    "connection_type": "shared_device",
                    "connected_entity_id": "ACC-0012",
                    "connection_strength": "strong",
                    "first_observed": "2025-05-10T10:00:00Z",
                    "details": "Device DEV-IPHONE-99 used by both accounts within 10 minutes."
                }
            ],
            "prior_cases": [
                {
                    "case_id": "CASE-2025-1102",
                    "case_date": "2025-02-15T11:00:00Z",
                    "case_type": "identity_fraud",
                    "outcome": "false_positive",
                    "resolution_notes": "Customer provided valid secondary ID verification after initial flag."
                }
            ],
            "data_completeness": {
                "kyc": "complete",
                "transactions": "complete",
                "device_fingerprint": "available",
                "external_sanctions": "checked"
            }
        }
        return Response(data)