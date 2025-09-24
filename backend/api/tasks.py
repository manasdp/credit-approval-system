# backend/api/tasks.py
import pandas as pd
from celery import shared_task
from .models import Customer, Loan

@shared_task
def ingest_customer_data():
    # The path '/app/data/...' is used because that's where we mounted the folder in docker-compose.yml
    try:
        df = pd.read_excel('/app/data/customer_data.xlsx')
        for _, row in df.iterrows():
            Customer.objects.update_or_create(
                customer_id=row['Customer ID'],
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'phone_number': row['Phone Number'],
                    'monthly_salary': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit'],
                    # The 'Age' column seems to be missing from the provided customer_data file,
                    # so it's omitted here. The /register endpoint will add it for new customers.
                }
            )
        return "Customer data ingestion successful."
    except Exception as e:
        return f"Error ingesting customer data: {e}"


@shared_task
def ingest_loan_data():
    try:
        df = pd.read_excel('/app/data/loan_data.xlsx')
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])
                Loan.objects.update_or_create(
                    loan_id=row['Loan ID'],
                    defaults={
                        'customer': customer,
                        'loan_amount': row['Loan Amount'],
                        'tenure': row['Tenure'],
                        'interest_rate': row['Interest Rate'],
                        'monthly_repayment': row['Monthly payment'],
                         # The assignment PDF has a typo, so we map from the correct column name
                        'emis_paid_on_time': row['EMIs paid on Time'],
                        'start_date': row['Date of Approval'],
                        'end_date': row['End Date'],
                    }
                )
            except Customer.DoesNotExist:
                print(f"Customer with ID {row['Customer ID']} not found for loan {row['Loan ID']}.")
        return "Loan data ingestion successful."
    except Exception as e:
        return f"Error ingesting loan data: {e}"