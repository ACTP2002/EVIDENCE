from django.urls import path
from .views import FraudCaseDetailView, CaseSummaryView 
urlpatterns = [
     # Get ALL cases
    path('fraud-case/', FraudCaseDetailView.as_view(), name='fraud-case-list'),
    path('fraud-case/<str:case_id>/', FraudCaseDetailView.as_view(), name='fraud-case-detail'),
    path('case-summary/', CaseSummaryView.as_view(), name='case-summary'), 
]