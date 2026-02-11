from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from pathlib import Path
from functools import lru_cache

import json
import joblib
import pandas as pd
import numpy as np
from scipy.stats import median_abs_deviation

# ============ AI LOGIC FUNCTION ============
def anomaly_prediction(model_path: str, input_csv: str):
    # Load model
    artifact = joblib.load(model_path)
    model = artifact["model"]
    threshold = artifact["threshold"]

    # Load and process data
    test_df = pd.read_csv(input_csv)
    test_df["event_time"] = pd.to_datetime(test_df["event_time"])
    test_df["amount_abs"] = test_df["amount"].abs()

    grp = test_df.groupby("user_id", sort=False)

    # Rolling calculations
    test_df["amt_roll_med_15"] = grp["amount_abs"].transform(lambda s: s.rolling(15, min_periods=7).median())
    test_df["amt_roll_mad_15"] = grp["amount_abs"].transform(lambda s: s.rolling(15, min_periods=7).apply(
        lambda x: median_abs_deviation(x, scale="normal"), raw=False
    ))

    # Features
    test_df["amt_dev_from_med"] = test_df["amount_abs"] - test_df["amt_roll_med_15"]
    test_df["amt_robust_z"] = test_df["amt_dev_from_med"] / (test_df["amt_roll_mad_15"] + 1e-9)
    test_df["prev_event_time"] = grp["event_time"].shift(1)
    test_df["gap_seconds"] = (test_df["event_time"] - test_df["prev_event_time"]).dt.total_seconds()
    test_df["gap_seconds"] = test_df["gap_seconds"].fillna(test_df["gap_seconds"].median())
    test_df["gap_log"] = np.log1p(test_df["gap_seconds"])
    test_df["deposit_to_income_ratio"] = (test_df["account_deposit"] / (test_df["declared_income"] + 1e-9))
    test_df["amount_to_income_ratio"] = (test_df["amount_abs"] / (test_df["declared_income"] + 1e-9))
    test_df["net_flow_1d"] = test_df["amount_in_1d"] - test_df["amount_out_1d"]
    test_df["failed_login_ratio_1h"] = (test_df["failed_login_1h"] / (test_df["login_count_1h"] + 1e-9))
    
    test_df["new_ip_1d"] = test_df["new_ip_1d"].fillna(0)
    test_df["geo_change_1d"] = test_df["geo_change_1d"].fillna(0)
    test_df["is_cross_border"] = (test_df["residence_country"] != test_df["transaction_country"]).astype(int)

    # Model Inference
    raw = model.decision_function(test_df)
    test_df["anomaly_score"] = -raw
    test_df["is_anomaly"] = (test_df["anomaly_score"] >= threshold).astype(int)

    # Format Output
    output = test_df[["user_id", "txn_id", "event_time", "anomaly_score", "is_anomaly"]].copy()
    output["event_time"] = output["event_time"].astype(str)
    
    return output.to_dict(orient="records")

class AIAnomalyDetectionView(APIView):
    """
    Endpoint that triggers the AI model and returns anomaly results
    """
    def get(self, request):
        try:
            # Resolve file paths (Assumes files are in the same folder as views.py)
            base_path = Path(__file__).resolve().parent.parent.parent
            model_path = base_path / "behavior_iforest.pkl"
            csv_path = base_path / "test_transactions 2.csv"

            # Check if files exist before running
            if not model_path.exists() or not csv_path.exists():
                return Response(
                    {"error": f"Required files not found at {base_path}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Run AI prediction
            results = anomaly_prediction(str(model_path), str(csv_path))
            print (results)

            return Response({
                "count": len(results),
                "results": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ============ DATA LOADER ============
class DataLoader:
    """Centralized data loading with caching"""
    _cache = {}
    
    @classmethod
    @lru_cache(maxsize=None)
    def load(cls, filename):
        """Load and cache JSON data"""
        file_path = Path(__file__).parent / 'dummy_data' / filename
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @classmethod
    def get_by_id(cls, filename, id_field, id_value):
        """Get single item by ID"""
        data = cls.load(filename)
        return next((item for item in data if item.get(id_field) == id_value), None)
    
    @classmethod
    def filter_by(cls, filename, **filters):
        """Filter data by multiple fields"""
        data = cls.load(filename)
        result = data
        
        for key, value in filters.items():
            if value is not None:
                result = [item for item in result if item.get(key) == value]
        
        return result

# ============ BASE VIEWS ============
class BaseListView(APIView):
    """Generic list view"""
    filename = None
    
    def get(self, request):
        data = DataLoader.load(self.filename)
        return Response(data)

class BaseDetailView(APIView):
    """Generic detail view"""
    filename = None
    id_field = None
    
    def get(self, request, **kwargs):
        id_value = kwargs.get(self.id_field)
        item = DataLoader.get_by_id(self.filename, self.id_field, id_value)
        
        if not item:
            return Response({"error": f"{self.id_field} not found"}, status=404)
        
        return Response(item)

class BaseRelatedView(APIView):
    """Generic view for related data"""
    parent_filename = None
    parent_id_field = None
    child_filename = None
    child_filter_field = None
    
    def get(self, request, **kwargs):
        parent_id = kwargs.get(self.parent_id_field)
        
        # Verify parent exists
        parent = DataLoader.get_by_id(self.parent_filename, self.parent_id_field, parent_id)
        if not parent:
            return Response({"error": f"{self.parent_id_field} not found"}, status=404)
        
        # Get child data
        if self.child_filter_field:
            children = DataLoader.filter_by(
                self.child_filename, 
                **{self.child_filter_field: parent.get(self.child_filter_field, parent_id)}
            )
        else:
            children = DataLoader.load(self.child_filename)
        
        return Response(children)

# ============ Input Data ============================ #
# ============ CASES ============
class CaseListView(BaseListView):
    filename = 'cases.json'

class CaseDetailView(BaseDetailView):
    filename = 'cases.json'
    id_field = 'case_id'

class CaseCustomerView(APIView):
    def get(self, request, case_id):
        case = DataLoader.get_by_id('cases.json', 'case_id', case_id)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        customer = DataLoader.get_by_id('customers.json', 'customer_id', case['customer_id'])
        if not customer:
            return Response({"error": "Customer not found"}, status=404)
        
        return Response(customer)

class CaseAccountView(APIView):
    def get(self, request, case_id):
        case = DataLoader.get_by_id('cases.json', 'case_id', case_id)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        account = DataLoader.get_by_id('accounts.json', 'account_id', case['account_id'])
        if not account:
            return Response({"error": "Account not found"}, status=404)
        
        return Response(account)

class CaseTransactionsView(APIView):
    def get(self, request, case_id):
        case = DataLoader.get_by_id('cases.json', 'case_id', case_id)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        transactions = DataLoader.filter_by('transactions.json', account_id=case['account_id'])
        return Response(transactions)

class CaseLoginsView(APIView):
    def get(self, request, case_id):
        case = DataLoader.get_by_id('cases.json', 'case_id', case_id)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        logins = DataLoader.filter_by('logins.json', account_id=case['account_id'])
        return Response(logins)

class CaseDevicesView(APIView):
    def get(self, request, case_id):
        case = DataLoader.get_by_id('cases.json', 'case_id', case_id)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        devices = DataLoader.load('devices.json')
        case_devices = [d for d in devices if case['account_id'] in d['linked_accounts']]
        return Response(case_devices)

class CaseNetworkView(APIView):
    def get(self, request, case_id):
        case = DataLoader.get_by_id('cases.json', 'case_id', case_id)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        connections = DataLoader.filter_by('network_connections.json', entity_id=case['account_id'])
        return Response(connections)

class CaseTimelineView(APIView):
    def get(self, request, case_id):
        events = DataLoader.filter_by('timeline_events.json', case_id=case_id)
        return Response(events)

class CaseNotesView(APIView):
    def get(self, request, case_id):
        notes = DataLoader.filter_by('investigation_notes.json', case_id=case_id)
        return Response(notes)

# ============ CUSTOMERS ============
class CustomerListView(BaseListView):
    filename = 'customers.json'

class CustomerDetailView(BaseDetailView):
    filename = 'customers.json'
    id_field = 'customer_id'

class CustomerAccountsView(APIView):
    def get(self, request, customer_id):
        accounts = DataLoader.filter_by('accounts.json', customer_id=customer_id)
        return Response(accounts)

class CustomerCasesView(APIView):
    def get(self, request, customer_id):
        cases = DataLoader.filter_by('cases.json', customer_id=customer_id)
        return Response(cases)

class CustomerTransactionsView(APIView):
    def get(self, request, customer_id):
        transactions = DataLoader.filter_by('transactions.json', customer_id=customer_id)
        return Response(transactions)

class CustomerLoginsView(APIView):
    def get(self, request, customer_id):
        logins = DataLoader.filter_by('logins.json', customer_id=customer_id)
        return Response(logins)

# ============ ACCOUNTS ============
class AccountListView(BaseListView):
    filename = 'accounts.json'

class AccountDetailView(BaseDetailView):
    filename = 'accounts.json'
    id_field = 'account_id'

class AccountCustomerView(APIView):
    def get(self, request, account_id):
        account = DataLoader.get_by_id('accounts.json', 'account_id', account_id)
        if not account:
            return Response({"error": "Account not found"}, status=404)
        
        customer = DataLoader.get_by_id('customers.json', 'customer_id', account['customer_id'])
        return Response(customer)

class AccountTransactionsView(APIView):
    def get(self, request, account_id):
        transactions = DataLoader.filter_by('transactions.json', account_id=account_id)
        return Response(transactions)

class AccountCasesView(APIView):
    def get(self, request, account_id):
        cases = DataLoader.filter_by('cases.json', account_id=account_id)
        return Response(cases)

# ============ TRANSACTIONS ============
class TransactionListView(APIView):
    def get(self, request):
        transactions = DataLoader.load('transactions.json')
        
        # Apply filters
        customer_id = request.query_params.get('customer_id')
        account_id = request.query_params.get('account_id')
        txn_type = request.query_params.get('type')
        min_amount = request.query_params.get('min_amount')
        
        if customer_id:
            transactions = [t for t in transactions if t['customer_id'] == customer_id]
        if account_id:
            transactions = [t for t in transactions if t['account_id'] == account_id]
        if txn_type:
            transactions = [t for t in transactions if t['type'] == txn_type]
        if min_amount:
            transactions = [t for t in transactions if t['amount'] >= float(min_amount)]
        
        return Response(transactions)

class TransactionDetailView(BaseDetailView):
    filename = 'transactions.json'
    id_field = 'transaction_id'

# ============ DEVICES ============
class DeviceListView(BaseListView):
    filename = 'devices.json'

class DeviceDetailView(BaseDetailView):
    filename = 'devices.json'
    id_field = 'device_id'

class DeviceAccountsView(APIView):
    def get(self, request, device_id):
        device = DataLoader.get_by_id('devices.json', 'device_id', device_id)
        if not device:
            return Response({"error": "Device not found"}, status=404)
        
        accounts = DataLoader.load('accounts.json')
        linked = [a for a in accounts if a['account_id'] in device['linked_accounts']]
        return Response(linked)

class DeviceLoginsView(APIView):
    def get(self, request, device_id):
        logins = DataLoader.filter_by('logins.json', device_id=device_id)
        return Response(logins)

# ============ ALERTS ============
class AlertListView(APIView):
    def get(self, request):
        alerts = DataLoader.load('alerts.json')
        
        severity = request.query_params.get('severity')
        alert_type = request.query_params.get('alert_type')
        
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        if alert_type:
            alerts = [a for a in alerts if a['alert_type'] == alert_type]
        
        return Response(alerts)

class AlertDetailView(BaseDetailView):
    filename = 'alerts.json'
    id_field = 'alert_id'

# ============ NETWORK ============
class NetworkConnectionsView(APIView):
    def get(self, request, entity_id):
        connections = DataLoader.filter_by('network_connections.json', entity_id=entity_id)
        return Response(connections)
    

# ============ Output Data ============================ #

# ============ AI AGENT INVESTIGATION ============
class CaseInvestigateView(APIView):
    """
    AI Agent Investigation Endpoint

    POST /api/cases/{case_id}/investigate/
    """

    def post(self, request, case_id):
        """Run AI investigation on a case."""
        try:
            from ai_agent.orchestrator import InvestigationOrchestrator

            # Get optional parameters from request
            include_report = request.data.get('include_report', True)
            include_regulatory = request.data.get('include_regulatory', False)
            skills = request.data.get('skills', None)

            # Create orchestrator and run investigation
            orchestrator = InvestigationOrchestrator()
            result = orchestrator.investigate(
                case_id=case_id,
                skills=skills,
                include_report=include_report,
                include_regulatory=include_regulatory
            )

            return Response(result.to_dict())

        except ValueError as e:
            # Case not found
            return Response(
                {"error": str(e), "case_id": case_id},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Other errors
            return Response(
                {"error": f"Investigation failed: {str(e)}", "case_id": case_id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, case_id):
        """
        GET method returns investigation metadata and available skills.
        Use POST to actually run the investigation.
        """
        # Verify case exists
        case = DataLoader.get_by_id('cases.json', 'case_id', case_id)
        if not case:
            return Response(
                {"error": "Case not found", "case_id": case_id},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "case_id": case_id,
            "message": "Use POST to run investigation",
            "available_skills": {
                "case_context_assembler": {
                    "name": "Case Context Assembler",
                    "description": "Gathers all relevant data (customer, account, transactions, logins, devices, network)",
                    "skill_number": 1,
                    "required": True
                },
                "explainability_generator": {
                    "name": "Explainability Generator",
                    "description": "Explains why alerts fired with human-readable justifications",
                    "skill_number": 2,
                    "required": False
                },
                "risk_decomposer": {
                    "name": "Risk Decomposer",
                    "description": "Breaks down risk scores into identity, behavioral, transaction, network, and historical components",
                    "skill_number": 3,
                    "required": False
                },
                "pattern_matching": {
                    "name": "Pattern Matcher",
                    "description": "Compares case to historical fraud patterns and predicts likely outcome",
                    "skill_number": 4,
                    "required": False
                },
                "timeline_reconstruction": {
                    "name": "Timeline Reconstructor",
                    "description": "Builds chronological event sequence and detects escalation patterns",
                    "skill_number": 5,
                    "required": False
                },
                "recommendation_engine": {
                    "name": "Recommendation Engine",
                    "description": "Suggests prioritized investigation steps and actions",
                    "skill_number": 6,
                    "required": False
                },
                "network_intelligence": {
                    "name": "Network Intelligence",
                    "description": "Analyzes connections between accounts, devices, IPs to detect fraud rings",
                    "skill_number": 7,
                    "required": False
                },
                "report_generator": {
                    "name": "Report Generator",
                    "description": "Creates audit-ready investigation documentation",
                    "skill_number": 9,
                    "required": False
                },
                "regulatory_explainer": {
                    "name": "Regulatory Explainer",
                    "description": "Tailors findings for different audiences (investigators, compliance, regulators)",
                    "skill_number": 10,
                    "required": False
                },
                "learning_engine": {
                    "name": "Learning Engine",
                    "description": "Records outcomes to improve future detection (used via /feedback endpoint)",
                    "skill_number": 11,
                    "required": False
                }
            },
            "options": {
                "include_report": "boolean - Generate full report (default: true)",
                "include_regulatory": "boolean - Include regulatory explanations (default: false)",
                "skills": "array - Specific skill keys to run, e.g. ['case_context_assembler', 'network_intelligence'] (default: all)"
            },
            "example_requests": {
                "run_all_skills": {
                    "method": "POST",
                    "body": {}
                },
                "run_specific_skills": {
                    "method": "POST",
                    "body": {
                        "skills": ["case_context_assembler", "explainability_generator", "recommendation_engine"]
                    }
                },
                "with_regulatory": {
                    "method": "POST",
                    "body": {
                        "include_regulatory": True
                    }
                }
            }
        })


class InvestigationFeedbackView(APIView):
    """
    Record investigation outcome for learning.

    POST /api/cases/{case_id}/feedback/

    Records the investigation outcome to improve future detection:
    - confirmed_fraud: Case was actual fraud
    - false_positive: Case was not fraud
    - inconclusive: Unable to determine
    """

    def post(self, request, case_id):
        """Record investigation outcome."""
        try:
            from ai_agent.orchestrator import InvestigationOrchestrator

            outcome = request.data.get('outcome')
            notes = request.data.get('notes', None)

            if outcome not in ['confirmed_fraud', 'false_positive', 'inconclusive']:
                return Response(
                    {
                        "error": "Invalid outcome. Must be one of: confirmed_fraud, false_positive, inconclusive",
                        "provided": outcome
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            orchestrator = InvestigationOrchestrator()
            result = orchestrator.record_outcome(case_id, outcome, notes)

            return Response({
                "message": "Feedback recorded successfully",
                "case_id": case_id,
                "outcome": outcome,
                "learning_result": result
            })

        except ValueError as e:
            return Response(
                {"error": str(e), "case_id": case_id},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to record feedback: {str(e)}", "case_id": case_id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============ SENTINEL CHAT AGENT ============
class CaseChatView(APIView):
    """
    SENTINEL Conversational Chat Endpoint

    POST /api/cases/{case_id}/chat/

    Enables natural language conversation with the SENTINEL AI agent
    for fraud investigation assistance.
    """

    def post(self, request, case_id):
        """
        Process chat message and return AI response.

        Request body:
        {
            "message": "Why was this flagged?",
            "history": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }

        Response:
        {
            "response": "This case was flagged due to...",
            "suggested_questions": [
                "What are the risk factors?",
                "Show connected accounts",
                ...
            ]
        }
        """
        try:
            from ai_agent.chat_agent import chat_with_sentinel

            message = request.data.get('message', '').strip()
            history = request.data.get('history', [])

            if not message:
                return Response(
                    {"error": "Message is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate history format
            if not isinstance(history, list):
                history = []

            # Call the SENTINEL agent
            result = chat_with_sentinel(case_id, message, history)

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            # Case not found or invalid input
            return Response(
                {"error": str(e), "case_id": case_id},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Log error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Chat error for case {case_id}: {str(e)}", exc_info=True)

            return Response(
                {"error": "Failed to process message", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
