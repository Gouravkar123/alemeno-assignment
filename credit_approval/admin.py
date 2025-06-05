print("💡 Django is loading admin.py from credit_approval")
from django.contrib import admin
from .models import Customer, Loan

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "phone_number", "age", "monthly_salary", "approved_limit", "current_debt")
    search_fields = ("first_name", "last_name", "phone_number")
    list_filter = ("age", "monthly_salary")

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "loan_id", "customer", "loan_amount", "tenure",
        "interest_rate", "monthly_payment", "emis_paid_on_time",
        "date_of_approval", "end_date"
    )
    search_fields = ("loan_id", "customer__first_name", "customer__last_name")
    list_filter = ("tenure", "interest_rate", "date_of_approval")
