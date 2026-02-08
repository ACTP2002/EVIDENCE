from django.urls import path
from . import views

urlpatterns = [
    path('ai-detect/', views.AIAnomalyDetectionView.as_view(), name='ai-detect'),

    # Cases
    path('cases/', views.CaseListView.as_view(), name='case-list'),
    path('cases/<str:case_id>/', views.CaseDetailView.as_view(), name='case-detail'),
    path('cases/<str:case_id>/customer/', views.CaseCustomerView.as_view(), name='case-customer'),
    path('cases/<str:case_id>/account/', views.CaseAccountView.as_view(), name='case-account'),
    path('cases/<str:case_id>/transactions/', views.CaseTransactionsView.as_view(), name='case-transactions'),
    path('cases/<str:case_id>/logins/', views.CaseLoginsView.as_view(), name='case-logins'),
    path('cases/<str:case_id>/devices/', views.CaseDevicesView.as_view(), name='case-devices'),
    path('cases/<str:case_id>/network/', views.CaseNetworkView.as_view(), name='case-network'),
    path('cases/<str:case_id>/timeline/', views.CaseTimelineView.as_view(), name='case-timeline'),
    path('cases/<str:case_id>/notes/', views.CaseNotesView.as_view(), name='case-notes'),

    # AI Agent Investigation
    path('cases/<str:case_id>/investigate/', views.CaseInvestigateView.as_view(), name='case-investigate'),
    path('cases/<str:case_id>/feedback/', views.InvestigationFeedbackView.as_view(), name='case-feedback'),
    
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/<str:customer_id>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<str:customer_id>/accounts/', views.CustomerAccountsView.as_view(), name='customer-accounts'),
    path('customers/<str:customer_id>/cases/', views.CustomerCasesView.as_view(), name='customer-cases'),
    path('customers/<str:customer_id>/transactions/', views.CustomerTransactionsView.as_view(), name='customer-transactions'),
    path('customers/<str:customer_id>/logins/', views.CustomerLoginsView.as_view(), name='customer-logins'),
    
    # Accounts
    path('accounts/', views.AccountListView.as_view(), name='account-list'),
    path('accounts/<str:account_id>/', views.AccountDetailView.as_view(), name='account-detail'),
    path('accounts/<str:account_id>/customer/', views.AccountCustomerView.as_view(), name='account-customer'),
    path('accounts/<str:account_id>/transactions/', views.AccountTransactionsView.as_view(), name='account-transactions'),
    path('accounts/<str:account_id>/cases/', views.AccountCasesView.as_view(), name='account-cases'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<str:transaction_id>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    
    # Devices
    path('devices/', views.DeviceListView.as_view(), name='device-list'),
    path('devices/<str:device_id>/', views.DeviceDetailView.as_view(), name='device-detail'),
    path('devices/<str:device_id>/accounts/', views.DeviceAccountsView.as_view(), name='device-accounts'),
    path('devices/<str:device_id>/logins/', views.DeviceLoginsView.as_view(), name='device-logins'),
    
    # Alerts
    path('alerts/', views.AlertListView.as_view(), name='alert-list'),
    path('alerts/<str:alert_id>/', views.AlertDetailView.as_view(), name='alert-detail'),
    
    # Network
    path('network/connections/<str:entity_id>/', views.NetworkConnectionsView.as_view(), name='network-connections'),

    path('cases/<str:case_id>/investigate/', views.CaseInvestigateView.as_view(), name='case-investigate'),
    path('cases/<str:case_id>/feedback/', views.InvestigationFeedbackView.as_view(), name='case-feedback'),
]