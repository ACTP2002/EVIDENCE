from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from pathlib import Path

class BaseDataView(APIView):
    """Base class for loading JSON data files"""
    data_file = None
    _cache = {}
    
    @classmethod
    def get_data(cls):
        if cls.data_file not in cls._cache:
            file_path = Path(__file__).parent / 'dummy_data' / cls.data_file
            with open(file_path, 'r') as f:
                cls._cache[cls.data_file] = json.load(f)
        return cls._cache[cls.data_file]

# ============ CASES ============
class CaseListView(BaseDataView):
    data_file = 'cases.json'
    
    def get(self, request):
        return Response(self.get_data())

class CaseDetailView(BaseDataView):
    data_file = 'cases.json'
    
    def get(self, request, case_id):
        cases = self.get_data()
        case = next((c for c in cases if c["case_id"] == case_id), None)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        return Response(case)

class CaseCustomerView(BaseDataView):
    """Get customer data for a specific case"""
    
    def get(self, request, case_id):
        # Load case
        cases_path = Path(__file__).parent / 'dummy_data/cases.json'
        with open(cases_path) as f:
            cases = json.load(f)
        case = next((c for c in cases if c["case_id"] == case_id), None)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        # Load customer
        customers_path = Path(__file__).parent / 'dummy_data/customers.json'
        with open(customers_path) as f:
            customers = json.load(f)
        customer = next((c for c in customers if c["customer_id"] == case["customer_id"]), None)
        if not customer:
            return Response({"error": "Customer not found"}, status=404)
        
        return Response(customer)

class CaseAccountView(BaseDataView):
    """Get account data for a specific case"""
    
    def get(self, request, case_id):
        cases_path = Path(__file__).parent / 'dummy_data/cases.json'
        with open(cases_path) as f:
            cases = json.load(f)
        case = next((c for c in cases if c["case_id"] == case_id), None)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        accounts_path = Path(__file__).parent / 'dummy_data/accounts.json'
        with open(accounts_path) as f:
            accounts = json.load(f)
        account = next((a for a in accounts if a["account_id"] == case["account_id"]), None)
        if not account:
            return Response({"error": "Account not found"}, status=404)
        
        return Response(account)

class CaseTransactionsView(BaseDataView):
    """Get all transactions for a specific case"""
    
    def get(self, request, case_id):
        cases_path = Path(__file__).parent / 'dummy_data/cases.json'
        with open(cases_path) as f:
            cases = json.load(f)
        case = next((c for c in cases if c["case_id"] == case_id), None)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        transactions_path = Path(__file__).parent / 'dummy_data/transactions.json'
        with open(transactions_path) as f:
            transactions = json.load(f)
        
        case_transactions = [t for t in transactions if t["account_id"] == case["account_id"]]
        return Response(case_transactions)

class CaseLoginsView(BaseDataView):
    """Get all login events for a specific case"""
    
    def get(self, request, case_id):
        cases_path = Path(__file__).parent / 'dummy_data/cases.json'
        with open(cases_path) as f:
            cases = json.load(f)
        case = next((c for c in cases if c["case_id"] == case_id), None)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        logins_path = Path(__file__).parent / 'dummy_data/logins.json'
        with open(logins_path) as f:
            logins = json.load(f)
        
        case_logins = [l for l in logins if l["account_id"] == case["account_id"]]
        return Response(case_logins)

class CaseDevicesView(BaseDataView):
    """Get all devices for a specific case"""
    
    def get(self, request, case_id):
        cases_path = Path(__file__).parent / 'dummy_data/cases.json'
        with open(cases_path) as f:
            cases = json.load(f)
        case = next((c for c in cases if c["case_id"] == case_id), None)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        devices_path = Path(__file__).parent / 'dummy_data/devices.json'
        with open(devices_path) as f:
            devices = json.load(f)
        
        # Get devices linked to the case's account
        case_devices = [d for d in devices if case["account_id"] in d["linked_accounts"]]
        return Response(case_devices)

class CaseNetworkView(BaseDataView):
    """Get network connections for a specific case"""
    
    def get(self, request, case_id):
        cases_path = Path(__file__).parent / 'dummy_data/cases.json'
        with open(cases_path) as f:
            cases = json.load(f)
        case = next((c for c in cases if c["case_id"] == case_id), None)
        if not case:
            return Response({"error": "Case not found"}, status=404)
        
        network_path = Path(__file__).parent / 'dummy_data/network_connections.json'
        with open(network_path) as f:
            connections = json.load(f)
        
        case_network = [n for n in connections if n["entity_id"] == case["account_id"]]
        return Response(case_network)

class CaseTimelineView(BaseDataView):
    """Get timeline events for a specific case"""
    
    def get(self, request, case_id):
        timeline_path = Path(__file__).parent / 'dummy_data/timeline_events.json'
        with open(timeline_path) as f:
            events = json.load(f)
        
        case_timeline = [e for e in events if e["case_id"] == case_id]
        return Response(case_timeline)

# ============ CUSTOMERS (Raw) ============
class CustomerListView(BaseDataView):
    data_file = 'customers.json'
    
    def get(self, request):
        return Response(self.get_data())

class CustomerDetailView(BaseDataView):
    data_file = 'customers.json'
    
    def get(self, request, customer_id):
        customers = self.get_data()
        customer = next((c for c in customers if c["customer_id"] == customer_id), None)
        if not customer:
            return Response({"error": "Customer not found"}, status=404)
        return Response(customer)

class CustomerAccountsView(BaseDataView):
    
    def get(self, request, customer_id):
        accounts_path = Path(__file__).parent / 'dummy_data/accounts.json'
        with open(accounts_path) as f:
            accounts = json.load(f)
        
        customer_accounts = [a for a in accounts if a["customer_id"] == customer_id]
        return Response(customer_accounts)

class CustomerCasesView(BaseDataView):
    
    def get(self, request, customer_id):
        cases_path = Path(__file__).parent / 'dummy_data/cases.json'
        with open(cases_path) as f:
            cases = json.load(f)
        
        customer_cases = [c for c in cases if c["customer_id"] == customer_id]
        return Response(customer_cases)

class CustomerTransactionsView(BaseDataView):
    
    def get(self, request, customer_id):
        transactions_path = Path(__file__).parent / 'dummy_data/transactions.json'
        with open(transactions_path) as f:
            transactions = json.load(f)
        
        customer_transactions = [t for t in transactions if t["customer_id"] == customer_id]
        return Response(customer_transactions)

class CustomerLoginsView(BaseDataView):
    
    def get(self, request, customer_id):
        logins_path = Path(__file__).parent / 'dummy_data/logins.json'
        with open(logins_path) as f:
            logins = json.load(f)
        
        customer_logins = [l for l in logins if l["customer_id"] == customer_id]
        return Response(customer_logins)

# ============ ACCOUNTS (Raw) ============
class AccountListView(BaseDataView):
    data_file = 'accounts.json'
    
    def get(self, request):
        return Response(self.get_data())

class AccountDetailView(BaseDataView):
    data_file = 'accounts.json'
    
    def get(self, request, account_id):
        accounts = self.get_data()
        account = next((a for a in accounts if a["account_id"] == account_id), None)
        if not account:
            return Response({"error": "Account not found"}, status=404)
        return Response(account)

class AccountCustomerView(BaseDataView):
    
    def get(self, request, account_id):
        accounts_path = Path(__file__).parent / 'dummy_data/accounts.json'
        with open(accounts_path) as f:
            accounts = json.load(f)
        account = next((a for a in accounts if a["account_id"] == account_id), None)
        if not account:
            return Response({"error": "Account not found"}, status=404)
        
        customers_path = Path(__file__).parent / 'dummy_data/customers.json'
        with open(customers_path) as f:
            customers = json.load(f)
        customer = next((c for c in customers if c["customer_id"] == account["customer_id"]), None)
        
        return Response(customer)

class AccountTransactionsView(BaseDataView):
    
    def get(self, request, account_id):
        transactions_path = Path(__file__).parent / 'dummy_data/transactions.json'
        with open(transactions_path) as f:
            transactions = json.load(f)
        
        account_transactions = [t for t in transactions if t["account_id"] == account_id]
        return Response(account_transactions)

class AccountCasesView(BaseDataView):
    
    def get(self, request, account_id):
        cases_path = Path(__file__).parent / 'dummy_data/cases.json'
        with open(cases_path) as f:
            cases = json.load(f)
        
        account_cases = [c for c in cases if c["account_id"] == account_id]
        return Response(account_cases)

# ============ TRANSACTIONS (Raw) ============
class TransactionListView(BaseDataView):
    data_file = 'transactions.json'
    
    def get(self, request):
        transactions = self.get_data()
        
        # Filter support
        customer_id = request.query_params.get('customer_id')
        account_id = request.query_params.get('account_id')
        txn_type = request.query_params.get('type')
        min_amount = request.query_params.get('min_amount')
        
        if customer_id:
            transactions = [t for t in transactions if t["customer_id"] == customer_id]
        if account_id:
            transactions = [t for t in transactions if t["account_id"] == account_id]
        if txn_type:
            transactions = [t for t in transactions if t["type"] == txn_type]
        if min_amount:
            transactions = [t for t in transactions if t["amount"] >= float(min_amount)]
        
        return Response(transactions)

class TransactionDetailView(BaseDataView):
    data_file = 'transactions.json'
    
    def get(self, request, transaction_id):
        transactions = self.get_data()
        transaction = next((t for t in transactions if t["transaction_id"] == transaction_id), None)
        if not transaction:
            return Response({"error": "Transaction not found"}, status=404)
        return Response(transaction)

# ============ DEVICES (Raw) ============
class DeviceListView(BaseDataView):
    data_file = 'devices.json'
    
    def get(self, request):
        return Response(self.get_data())

class DeviceDetailView(BaseDataView):
    data_file = 'devices.json'
    
    def get(self, request, device_id):
        devices = self.get_data()
        device = next((d for d in devices if d["device_id"] == device_id), None)
        if not device:
            return Response({"error": "Device not found"}, status=404)
        return Response(device)

class DeviceAccountsView(BaseDataView):
    
    def get(self, request, device_id):
        devices_path = Path(__file__).parent / 'dummy_data/devices.json'
        with open(devices_path) as f:
            devices = json.load(f)
        device = next((d for d in devices if d["device_id"] == device_id), None)
        if not device:
            return Response({"error": "Device not found"}, status=404)
        
        accounts_path = Path(__file__).parent / 'dummy_data/accounts.json'
        with open(accounts_path) as f:
            accounts = json.load(f)
        
        linked_accounts = [a for a in accounts if a["account_id"] in device["linked_accounts"]]
        return Response(linked_accounts)

class DeviceLoginsView(BaseDataView):
    
    def get(self, request, device_id):
        logins_path = Path(__file__).parent / 'dummy_data/logins.json'
        with open(logins_path) as f:
            logins = json.load(f)
        
        device_logins = [l for l in logins if l["device_id"] == device_id]
        return Response(device_logins)

# ============ ALERTS (Raw) ============
class AlertListView(BaseDataView):
    data_file = 'alerts.json'
    
    def get(self, request):
        alerts = self.get_data()
        
        severity = request.query_params.get('severity')
        alert_type = request.query_params.get('alert_type')
        
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        if alert_type:
            alerts = [a for a in alerts if a["alert_type"] == alert_type]
        
        return Response(alerts)

class AlertDetailView(BaseDataView):
    data_file = 'alerts.json'
    
    def get(self, request, alert_id):
        alerts = self.get_data()
        alert = next((a for a in alerts if a["alert_id"] == alert_id), None)
        if not alert:
            return Response({"error": "Alert not found"}, status=404)
        return Response(alert)

# ============ NETWORK (Raw) ============
class NetworkConnectionsView(BaseDataView):
    data_file = 'network_connections.json'
    
    def get(self, request, entity_id):
        connections = self.get_data()
        entity_connections = [c for c in connections if c["entity_id"] == entity_id]
        return Response(entity_connections)

# ============ INVESTIGATION NOTES ============
class InvestigationNotesView(BaseDataView):
    data_file = 'investigation_notes.json'
    
    def get(self, request, case_id):
        notes = self.get_data()
        case_notes = [n for n in notes if n["case_id"] == case_id]
        return Response(case_notes)