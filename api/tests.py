from django.test import TestCase
from .models import Customer, Loan
from .services import calculate_credit_score, get_eligibility_status

class ServiceLogicTest(TestCase):
    def setUp(self):
        """Set up a standard customer for testing"""
        self.customer = Customer.objects.create(
            first_name="Test", 
            last_name="User", 
            age=30, 
            phone_number="9999999999", 
            monthly_salary=50000, 
            approved_limit=1800000
        )

    def test_new_customer_score(self):
        """A new customer should start with a perfect score"""
        score = calculate_credit_score(self.customer)
        self.assertEqual(score, 100)

    def test_rejected_due_to_dti(self):
        """Loan should be rejected if current EMIs exceed 50% of salary"""
        # Create a massive existing loan that takes up all their salary
        Loan.objects.create(
            customer=self.customer,
            loan_amount=500000,
            interest_rate=10,
            tenure=12,
            monthly_repayment=30000, # Salary is 50k, so 30k is > 50%
            emis_paid_on_time=0,
            start_date="2025-01-01",
            end_date="2026-01-01"
        )
        
        # Try to get a new loan
        approved, corrected_rate = get_eligibility_status(
            self.customer, 10000, 10, 12
        )
        
        # It should be False because they are already in too much debt
        self.assertFalse(approved)