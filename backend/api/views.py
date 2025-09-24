# backend/api/views.py
from rest_framework import generics, status, views
from rest_framework.response import Response
from django.db.models import Sum
from datetime import date
import pandas as pd
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer, LoanViewSerializer
from .services import calculate_credit_score, calculate_monthly_installment

# --- Endpoint: /register ---
class RegisterCustomer(views.APIView):
    def post(self, request):
        data = request.data
        monthly_salary = data.get('monthly_income', 0)
        # approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        approved_limit = round(36 * monthly_salary / 100000) * 100000

        customer = Customer.objects.create(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            monthly_salary=monthly_salary,
            approved_limit=approved_limit,
            phone_number=data.get('phone_number')
        )
        
        response_data = {
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": customer.monthly_salary,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

# --- Endpoint: /check-eligibility ---
class CheckEligibility(views.APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount'))
        interest_rate = float(request.data.get('interest_rate'))
        tenure = int(request.data.get('tenure'))

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        credit_score = calculate_credit_score(customer)
        
        # Rule: If sum of all current EMIs > 50% of monthly salary, don't approve
        current_emis_sum = Loan.objects.filter(customer=customer, end_date__gte=date.today()).aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0
        if current_emis_sum > customer.monthly_salary / 2:
            return Response({
                "approval": False, "message": "High debt to income ratio."
            }, status=status.HTTP_200_OK)

        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            approval = True
            if interest_rate <= 12: corrected_interest_rate = 12.0
        elif 10 < credit_score <= 30:
            approval = True
            if interest_rate <= 16: corrected_interest_rate = 16.0
        else: # credit_score <= 10
            approval = False

        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        
        return Response({
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": monthly_installment,
        }, status=status.HTTP_200_OK)

# --- Endpoint: /create-loan ---
class CreateLoan(views.APIView):
    def post(self, request):
        # We re-use the logic from CheckEligibility to make a decision
        eligibility_checker = CheckEligibility()
        eligibility_response = eligibility_checker.post(request)
        
        data = eligibility_response.data
        if not data['approval']:
            return Response({
                "loan_id": None, "customer_id": data['customer_id'], "loan_approved": False,
                "message": "Loan not approved based on eligibility criteria.", "monthly_installment": None
            }, status=status.HTTP_200_OK)

        customer = Customer.objects.get(pk=data['customer_id'])
        new_loan = Loan.objects.create(
            customer=customer,
            loan_amount=request.data.get('loan_amount'),
            tenure=data['tenure'],
            interest_rate=data['corrected_interest_rate'],
            monthly_repayment=data['monthly_installment'],
            start_date=date.today(),
            end_date=date.today() + pd.DateOffset(months=data['tenure'])
        )
        
        return Response({
            "loan_id": new_loan.loan_id, "customer_id": customer.customer_id, "loan_approved": True,
            "message": "Loan approved successfully!", "monthly_installment": new_loan.monthly_repayment
        }, status=status.HTTP_201_CREATED)

# --- Endpoint: /view-loan/<loan_id> ---
class ViewLoan(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    lookup_field = 'loan_id'

# --- Endpoint: /view-loans/<customer_id> ---
class ViewCustomerLoans(generics.ListAPIView):
    serializer_class = LoanViewSerializer
    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Loan.objects.filter(customer__customer_id=customer_id)