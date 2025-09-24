# backend/api/serializers.py
from rest_framework import serializers
from .models import Customer, Loan
from datetime import date

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_salary', 'approved_limit', 'phone_number']
        read_only_fields = ['customer_id', 'approved_limit']

class LoanSerializer(serializers.ModelSerializer):
    # This nests the customer's details inside the loan response
    customer = CustomerSerializer(read_only=True)
    class Meta:
        model = Loan
        fields = '__all__'

class LoanViewSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_repayment', 'repayments_left']

    def get_repayments_left(self, obj):
        # This method calculates the value for the 'repayments_left' field
        today = date.today()
        end_date = obj.end_date
        
        # Calculate the number of months remaining until the end date
        repayments = (end_date.year - today.year) * 12 + (end_date.month - today.month)
        return max(0, repayments)
    