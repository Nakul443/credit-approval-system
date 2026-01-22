# logic to read excel files and save them in the postgres db

import pandas as pd
from celery import shared_task
from .models import Customer, Loan

@shared_task # tells celery that this function is a "background_task"
def ingest_customer_data(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['customer_id'],
            defaults={
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'age': row['age'],
                'phone_number': str(row['phone_number']),
                'monthly_salary': row['monthly_salary'],
                'approved_limit': row['approved_limit'],
            }
        )

@shared_task
def ingest_loan_data(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        customer = Customer.objects.get(customer_id=row['customer_id'])
        Loan.objects.update_or_create(
            loan_id=row['loan_id'],
            defaults={
                'customer': customer,
                'loan_amount': row['loan_amount'],
                'tenure': row['tenure'],
                'interest_rate': row['interest_rate'],
                'monthly_repayment': row['monthly_repayment'],
                'emis_paid_on_time': row['emis_paid_on_time'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
            }
        )