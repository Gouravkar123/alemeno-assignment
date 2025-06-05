from django.db import models

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    age = models.PositiveIntegerField()
    monthly_salary = models.PositiveIntegerField()
    approved_limit = models.PositiveIntegerField()
    current_debt = models.FloatField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_id = models.AutoField(primary_key=True)  # <-- Use AutoField for unique, auto-increment ID
    loan_amount = models.FloatField()
    tenure = models.PositiveIntegerField(help_text="Loan tenure in months")
    interest_rate = models.FloatField(help_text="Annual interest rate in percentage")
    monthly_payment = models.FloatField()
    emis_paid_on_time = models.PositiveIntegerField(default=0)
    date_of_approval = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer.first_name}"
