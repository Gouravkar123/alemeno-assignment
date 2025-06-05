# credit_approval/tasks.py
import pandas as pd
from celery import shared_task
from .models import Customer, Loan
from django.utils.dateparse import parse_date

@shared_task
def load_customer_data_task():
    df = pd.read_excel("data/customer_data.xlsx")
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            id=row["Customer ID"],
            defaults={
                "first_name": row["First Name"],
                "last_name": row["Last Name"],
                "phone_number": str(row["Phone Number"]),
                "age": row["Age"],
                "monthly_salary": row["Monthly Salary"],
                "approved_limit": row["Approved Limit"],
                "current_debt": 0,
            }
        )
    return "Customer data loaded successfully"

@shared_task
def load_loan_data_task():
    df = pd.read_excel("data/loan_data.xlsx")
    for _, row in df.iterrows():
        try:
            customer = Customer.objects.get(id=row["Customer ID"])
            Loan.objects.update_or_create(
                loan_id=row["Loan ID"],
                defaults={
                    "customer": customer,
                    "loan_amount": row["Loan Amount"],
                    "tenure": row["Tenure"],
                    "interest_rate": row["Interest Rate"],
                    "monthly_payment": row["Monthly payment"],
                    "emis_paid_on_time": row["EMIs paid on Time"],
                    "date_of_approval": parse_date(str(row["Date of Approval"])),
                    "end_date": parse_date(str(row["End Date"])),
                }
            )
        except Customer.DoesNotExist:
            continue
    return "Loan data loaded successfully"
