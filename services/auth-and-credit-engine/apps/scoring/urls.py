# routing table
# when a request comes in from the internet,
# urls.py looks at it and send it to the correct path
# defines the endpoints (specific actions)
# differs from core/urls.py

from django.urls import path
from . import views # import views.py from current directory

urlpatterns = [
    # /api/scoring/register/
    path('register/', views.register, name='register'),
    
    # /api/scoring/check-eligibility/
    path('check-eligibility/', views.check_eligibility, name='check_eligibility'),
    
    # /api/scoring/view-loan/:load_id/
    path('view-loan/<int:loan_id>/', views.view_loan, name='view_loan'),
    
    # /api/scoring/view-loans/:customer_id/
    path('view-loans-customer/<int:customer_id>/', views.view_loans_by_customer, name='view_loans_by_customer'),
    
    # /api/scoring/create-loan/
    path('create-loan/', views.create_loan, name='create_loan'),
]