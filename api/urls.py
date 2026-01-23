# routing table
# when a request comes in from the internet,
# urls.py looks at it and send it to the correct path
# defines the endpoints (specific actions)
# differs from core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # /api/register
    path('register', views.register, name='register'),
    
    # /api/check-eligibility
    path('check-eligibility', views.check_eligibility, name='check_eligibility'),
    
    # /api/view-loan/:load_id
    path('view-loan/<int:loan_id>/', views.view_loan, name='view_loan'),
]