from django.urls import path
from .views import *

urlpatterns = [
    # Cases
    path('cases/', CaseListView.as_view()),
    path('cases/<str:case_id>/', CaseDetailView.as_view()),
    path('cases/<str:case_id>/customer/', CaseCustomerView.as_view()),
    path('cases/<str:case_id>/account/', CaseAccountView.as_view()),
    path('cases/<str:case_id>/transactions/', CaseTransactionsView.as_view()),
    path('cases/<str:case_id>/logins/', CaseLoginsView.as_view()),
    path('cases/<str:case_id>/devices/', CaseDevicesView.as_view()),
    path('cases/<str:case_id>/network/', CaseNetworkView.as_view()),
    path('cases/<str:case_id>/timeline/', CaseTimelineView.as_view()),
    path('cases/<str:case_id>/notes/', InvestigationNotesView.as_view()),
    
    # Customers
    path('customers/', CustomerListView.as_view()),
    path('customers/<str:customer_id>/', CustomerDetailView.as_view()),
    path('customers/<str:customer_id>/accounts/', CustomerAccountsView.as_view()),
    path('customers/<str:customer_id>/cases/', CustomerCasesView.as_view()),
    path('customers/<str:customer_id>/transactions/', CustomerTransactionsView.as_view()),
    path('customers/<str:customer_id>/logins/', CustomerLoginsView.as_view()),
    
    # Accounts
    path('accounts/', AccountListView.as_view()),
    path('accounts/<str:account_id>/', AccountDetailView.as_view()),
    path('accounts/<str:account_id>/customer/', AccountCustomerView.as_view()),
    path('accounts/<str:account_id>/transactions/', AccountTransactionsView.as_view()),
    path('accounts/<str:account_id>/cases/', AccountCasesView.as_view()),
    
    # Transactions
    path('transactions/', TransactionListView.as_view()),
    path('transactions/<str:transaction_id>/', TransactionDetailView.as_view()),
    
    # Devices
    path('devices/', DeviceListView.as_view()),
    path('devices/<str:device_id>/', DeviceDetailView.as_view()),
    path('devices/<str:device_id>/accounts/', DeviceAccountsView.as_view()),
    path('devices/<str:device_id>/logins/', DeviceLoginsView.as_view()),
    
    # Alerts
    path('alerts/', AlertListView.as_view()),
    path('alerts/<str:alert_id>/', AlertDetailView.as_view()),
    
    # Network
    path('network/connections/<str:entity_id>/', NetworkConnectionsView.as_view()),
]