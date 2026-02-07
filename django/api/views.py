from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from pathlib import Path
from functools import lru_cache

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