# backend/api/services.py
from datetime import date
from django.db.models import Sum
from .models import Loan, Customer

def calculate_credit_score(customer: Customer):
    """
    Calculates a credit score for a given customer based on historical loan data.
    """
    # Rule: If sum of current loans > approved limit, credit score = 0
    current_loans_sum = Loan.objects.filter(
        customer=customer, 
        end_date__gte=date.today()
    ).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    
    if current_loans_sum > customer.approved_limit:
        return 0
    
    # Start with a base score
    score = 50
    
    # --- Component i: Past Loans paid on time ---
    loans = Loan.objects.filter(customer=customer)
    total_emis_paid_on_time = loans.aggregate(Sum('emis_paid_on_time'))['emis_paid_on_time__sum'] or 0
    score += total_emis_paid_on_time / 10  # Simple scoring: 1 point for every 10 EMIs paid on time

    # --- Component ii: No of loans taken in past ---
    score -= loans.count() * 5 # Penalty for too many loans

    # --- Component iii: Loan activity in current year ---
    current_year_loans = loans.filter(start_date__year=date.today().year).count()
    score -= current_year_loans * 3 # Small penalty for recent loan activity

    # Ensure score is within a 0-100 range
    return max(0, min(100, int(score)))

def calculate_monthly_installment(loan_amount, interest_rate, tenure_months):
    """
    Calculates the monthly installment (EMI) for a loan using the compound interest formula.
    """
    # Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    # where P = Principal loan amount, r = monthly interest rate, n = tenure in months.
    
    if tenure_months == 0:
        return 0
        
    monthly_interest_rate = (interest_rate / 100) / 12
    
    if monthly_interest_rate == 0:
        return loan_amount / tenure_months

    emi = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**tenure_months) / ((1 + monthly_interest_rate)**tenure_months - 1)
    return round(emi, 2)