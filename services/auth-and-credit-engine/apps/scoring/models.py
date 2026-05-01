# file to define the database structure (tables, fields, relationships)
# contains the ORM models that represent the database tables for customers and loans.
# Django's ORM allows us to interact with the database using Python code instead of raw SQL queries

from django.db import models
from django.conf import settings # Import settings to reference the Custom User

class Customer(models.Model):
    # Link this profile to the central Auth User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='customer_profile',
        null=True, # Optional: allows existing data to exist without a user initially
        blank=True
    )
    customer_id = models.AutoField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Loan(models.Model):
    customer = models.ForeignKey(Customer, related_name='customer_loans', on_delete=models.CASCADE)
    loan_id = models.AutoField(unique=True, primary_key=True)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    # formatted string, allows to put variables directly inside a sentence
    # displays a record in plain english instead of ("Customer Object 1")
    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer.first_name}"