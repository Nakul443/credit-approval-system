# decision maker file
# takes input -> performs calculations -> talks to the db -> decides what final response will look like

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer
from datetime import date
from dateutil.relativedelta import relativedelta
# Added import for the service layer logic
from .services import calculate_credit_score, get_eligibility_status


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
        
        # --- REFACTORED LOGIC ---
        # Using service layer to get approval, corrected rate, and current credit score
        approval, corrected_interest_rate = get_eligibility_status(
            customer, loan_amount, interest_rate, tenure
        )
        credit_score = calculate_credit_score(customer)
        
        # Calculate current EMIs for the debug info
        current_loans = Loan.objects.filter(customer=customer)
        total_current_emis = sum(l.monthly_repayment for l in current_loans)
        
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

@api_view(['POST'])
def create_loan(request):
    # This endpoint checks eligibility AND saves the loan if approved
    data = request.data
    customer_id = data.get('customer_id')
    loan_amount = data.get('loan_amount')
    interest_rate = data.get('interest_rate')
    tenure = data.get('tenure')
    start_date = date.today()
    end_date = start_date + relativedelta(months=tenure)

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        
        # --- REFACTORED LOGIC ---
        # 1. Determine Approval and Corrected Interest Rate using Service Layer
        approval, corrected_interest_rate = get_eligibility_status(
            customer, loan_amount, interest_rate, tenure
        )

        # 2. Final Decision
        if approval:
            # Calculate installment
            monthly_installment = round(loan_amount / tenure, 2)

            # CREATE THE RECORD
            new_loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                interest_rate=corrected_interest_rate,
                tenure=tenure,
                monthly_repayment=monthly_installment,
                emis_paid_on_time=0,
                start_date=start_date,
                end_date=end_date
            )

            return Response({
                "loan_id": new_loan.loan_id,
                "customer_id": customer_id,
                "loan_approved": True,
                "message": "Loan successfully sanctioned",
                "monthly_installment": monthly_installment
            }, status=status.HTTP_201_CREATED)
        else:
            # Match PDF requirement for rejected loans
            return Response({
                "loan_id": None, # Should be null in JSON
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Loan rejected: Eligibility criteria not met",
                "monthly_installment": 0
            }, status=status.HTTP_200_OK)

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

@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    # PDF structure: Returns a list of all current loans for a customer
    loans = Loan.objects.filter(customer__customer_id=customer_id)
    loan_data = []
    for l in loans:
        loan_data.append({
            "loan_id": l.loan_id,
            "loan_amount": l.loan_amount,
            "interest_rate": l.interest_rate,
            "monthly_installment": l.monthly_repayment,
            "repayments_left": l.tenure - l.emis_paid_on_time
        })
    return Response(loan_data, status=status.HTTP_200_OK)