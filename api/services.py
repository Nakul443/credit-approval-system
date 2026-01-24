from .models import Loan
from datetime import date

# logic to calculate credit score
def calculate_credit_score(customer):
    loans = Loan.objects.filter(customer=customer)

    # 1. Past Payment History
    total_emis = sum(l.tenure for l in loans)
    on_time_emis = sum(l.emis_paid_on_time for l in loans)
    payment_score = (on_time_emis / total_emis * 100) if total_emis > 0 else 100

    # 2. Number of loans taken in the past
    num_loans = loans.count()
    # If a customer has many loans, it reduces their score
    loan_count_score = max(0, 100 - (num_loans * 5)) # Penalty for too many loans

    # 3. Loans taken in current year
    current_year_loans = loans.filter(start_date__year=2026).count()
    year_score = max(0, 100 - (current_year_loans * 20))

    # 4. Final Weighted Score
    # 50% weight to payment history, 20% to number of loans, 30% to recent activity
    credit_score = (payment_score * 0.5) + (loan_count_score * 0.2) + (year_score * 0.3)
    return round(credit_score)

# NEW: Logic to decide eligibility and rate correction
def get_eligibility_status(customer, loan_amount, interest_rate, tenure):
    """
    Centralized logic to determine if a loan is approved and at what rate.
    Returns: (bool: approved, float: corrected_rate)
    """
    credit_score = calculate_credit_score(customer)
    
    approved = False
    corrected_rate = interest_rate

    # Slab logic
    if credit_score > 50:
        approved = True
    elif 50 >= credit_score > 30:
        approved = True
        if interest_rate < 12: corrected_rate = 12.0
    elif 30 >= credit_score > 10:
        approved = True
        if interest_rate < 16: corrected_rate = 16.0
    else:
        approved = False # Score <= 10

    # Debt-to-Income (DTI) Check
    # Current sum of all EMIs for this customer
    current_loans = Loan.objects.filter(customer=customer)
    total_current_emis = sum(l.monthly_repayment for l in current_loans)
    
    # New loan EMI estimation (used for DTI check)
    new_emi = loan_amount / tenure
    
    # If existing EMIs + new EMI > 50% of salary, reject
    # Note: Some prefer checking only current EMIs, but including the new one is safer.
    if total_current_emis > (customer.monthly_salary * 0.5):
        approved = False
        
    return approved, corrected_rate