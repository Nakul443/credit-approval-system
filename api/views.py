# decision maker file
# takes input -> performs calculations -> talks to the db -> decides what final response will look like

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer
from datetime import date

# logic to calculate credit score
def calculate_credit_score(customer):
    loans = Loan.objects.filter(customer=customer)

    # Past Payment History
    total_emis = sum(l.tenure for l in loans)
    on_time_emis = sum(l.emis_paid_on_time for l in loans)
    payment_score = (on_time_emis / total_emis * 100) if total_emis > 0 else 100

    # Number of loans taken in the past
    num_loans = loans.count()
    # If a customer has many loans, it reduces their score
    loan_count_score = max(0, 100 - (num_loans * 5)) # Penalty for too many loans

    # Loans taken in current year
    current_year_loans = loans.filter(start_date__year=2026).count()
    year_score = max(0, 100 - (current_year_loans * 20))

    # Final Weighted Score
    # 50% weight to payment history, 20% to number of loans, 30% to recent activity
    credit_score = (payment_score * 0.5) + (loan_count_score * 0.2) + (year_score * 0.3)
    return round(credit_score)

@api_view(['POST'])
def register(request):
    try:
        data = request.data # JSON the user sent
        
        income = data.get('monthly_income')

        approved_limit = round((36*income) / 100000) * 100000

        # create a new record in Customer table
        customer = Customer.objects.create(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            phone_number=data.get('phone_number'),
            monthly_salary=income,
            approved_limit=approved_limit
        )

        # turn the 'customer' object into JSON
        serializer = CustomerSerializer(customer)

        # return the JSON
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_eligibility(request):
    data = request.data
    customer_id = data.get('customer_id')
    loan_amount = data.get('loan_amount')
    interest_rate = data.get('interest_rate')
    tenure = data.get('tenure')

    try:
        # get the customer from the db
        customer = Customer.objects.get(customer_id=customer_id)
        
        # call our helper function to get the score (0-100)
        credit_score = calculate_credit_score(customer)

        # LOGIC for approval and interest rate correction
        approval = False
        corrected_interest_rate = interest_rate

        # check slabs according to the credit rating
        # Added >= to handle exact scores like 50, 30, and 10
        if credit_score > 50:
            approval = True
            # No changes to interest_rate if score is high
        elif 50 >= credit_score > 30:
            approval = True
            # if rating is mid-range, interest must be at least 12%
            if interest_rate < 12:
                corrected_interest_rate = 12.0
        elif 30 >= credit_score > 10:
            approval = True
            # if rating is low, interest must be at least 16%
            if interest_rate < 16:
                corrected_interest_rate = 16.0
        else:
            approval = False # reject score below 10 or exactly 10

        # SUM OF ALL CURRENT EMIs check
        # We need to see if they are already paying too much in other loans
        current_loans = Loan.objects.filter(customer=customer)
        total_current_emis = sum(l.monthly_repayment for l in current_loans)
        
        # if existing EMIs are more than 50% of salary, we must reject the new loan
        # This is why your output was 'False' even with a score of 80!
        if total_current_emis > (customer.monthly_salary * 0.5):
            approval = False
        
        # return response with corrected values and debug info
        return Response({
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(loan_amount / tenure, 2),
            "credit_rating": credit_score,
            "debug_info": {
                "monthly_salary": customer.monthly_salary,
                "existing_emis": total_current_emis,
                "emi_limit": customer.monthly_salary * 0.5
            }
        })

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        customer = loan.customer
        return Response({
            "loan_id": loan.loan_id,
            "customer": {
                "id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_repayment,
            "tenure": loan.tenure
        })

    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)