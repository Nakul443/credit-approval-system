# logic to read excel files and save them in the postgres db

import pandas as pd # used to read Excel file
from celery import shared_task
from .models import Customer, Loan

@shared_task # tells celery that this function is a "background_task", celery doesn't run this on the main server
def ingest_customer_data(file_path):
    df = pd.read_excel(file_path) # tells panda to open the .xlsx file
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['Customer ID'],
            # outside defaults : tells django which record to look for
            defaults={
                # everything inside defaults tells django what to fill in / change
                # will only run if a match of 'customer_id' is found
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'age': row['Age'],
                'phone_number': str(row['Phone Number']),
                'monthly_salary': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
            }
        )
    return "Ingestion Successful"

@shared_task
def ingest_loan_data(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows(): # loop through excel sheet row by row
        # Updated headers to match your Excel output:
        # ['Customer ID', 'Loan ID', 'Loan Amount', 'Tenure', 'Interest Rate', 'Monthly payment', 'EMIs paid on Time', 'Date of Approval', 'End Date']
        
        customer, _ = Customer.objects.get_or_create(customer_id=row['Customer ID'])
        
        Loan.objects.update_or_create(
            loan_id=row['Loan ID'],
            defaults={
                'customer': customer,
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_repayment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'start_date': row['Date of Approval'],
                'end_date': row['End Date'],
            }
        )
    return "Loan Ingestion Successful"