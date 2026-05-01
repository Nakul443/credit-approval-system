# serializer is the translator
# acts as the bridge between the database models and JSON data types that can be sent over the internet
# converts database rows into JSON format

from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    # custom field
    # allows to combine first name and last name
    name = serializers.SerializerMethodField()

    # source tells DRF to look at monthly_salary column to fill this field
    monthly_income = serializers.IntegerField(source='monthly_salary')

    # tell the serializer to use which database model and what specific fields to turn into JSON
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']

    # defines what the 'name' field above should contain
    # 'obj' is the Customer record from the database
    # grabs two separate columns from DB and merges them into one string for JSON response
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"