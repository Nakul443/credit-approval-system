# decision maker file
# takes input -> performs calculations -> talks to the db -> decides what final response will look like

from django.shortcuts import render

# Create your views here
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer

@api_view(['POST'])
def register(request):
    try:
        data = request.data # JSON the user sent
        salary = data.get('monthly_income')
        
        # 36 * salary rounded to nearest lakh
        raw_limit = 36 * salary
        approved_limit = round(raw_limit / 100000) * 100000

        # create a new record in Customer table
        customer = Customer.objects.create(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            phone_number=data.get('phone_number'),
            monthly_salary=salary,
            approved_limit=approved_limit
        )

        # turn the 'customer' object into JSON
        serializer = CustomerSerializer(customer)

        # return the JSON
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)