from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from django.shortcuts import get_object_or_404
import math, datetime
from .tasks import load_customer_data_task, load_loan_data_task
from .utils import calculate_emi


class RegisterCustomer(APIView):
    def post(self, request):
        data = request.data
        approved_limit = round(36 * data['monthly_income'] / 100000) * 100000
        customer = Customer.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            monthly_salary=data['monthly_income'],
            phone_number=data['phone_number'],
            approved_limit=approved_limit
        )
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)

class CheckEligibility(APIView):
    def post(self, request):
        data = request.data
        customer = get_object_or_404(Customer, id=data['customer_id'])
        loans = Loan.objects.filter(customer=customer)
        
        current_year = datetime.date.today().year
        score = 100

        # If current debt exceeds approved limit, score is zero
        if customer.current_debt > customer.approved_limit:
            score = 0
        else:
            if loans.exists():
                on_time = sum(l.emis_paid_on_time for l in loans)
                total_loan_volume = sum(l.loan_amount for l in loans)
                loans_this_year = len([l for l in loans if l.date_of_approval.year == current_year])
                
                # Subtract points for number of loans
                score -= (len(loans) * 5)
                # Subtract points proportional to loan volume ratio
                score -= (total_loan_volume / customer.approved_limit) * 20
                # Add points proportional to on-time payments
                score += (on_time / (len(loans) * 10)) * 20
                # Subtract points for recent loan activity
                score -= loans_this_year * 5
        
        # Clamp score between 0 and 100
        score = max(0, min(100, int(score)))

        # Calculate EMI for requested loan
        requested_emi = calculate_emi(data['loan_amount'], data['interest_rate'], data['tenure'])

        # Calculate total EMI of existing active loans
        total_existing_emi = sum(l.monthly_payment for l in loans)

        # Initialize approval and corrected_interest_rate
        approval = True
        corrected_rate = data['interest_rate']

        # Check if total EMI (existing + requested) > 50% monthly salary
        if (total_existing_emi + requested_emi) > 0.5 * customer.monthly_salary:
            approval = False
        
        # Check if current debt > approved limit disqualifies
        if customer.current_debt > customer.approved_limit:
            approval = False
        
        # Approval logic based on credit score and interest slabs
        if score > 50:
            # Approve any loan, interest rate unchanged
            corrected_rate = data['interest_rate']
        elif 30 < score <= 50:
            # Approve only if interest rate >= 12%
            if data['interest_rate'] < 12:
                approval = False
                corrected_rate = 12
        elif 10 < score <= 30:
            # Approve only if interest rate >= 16%
            if data['interest_rate'] < 16:
                approval = False
                corrected_rate = 16
        else:
            # Score <= 10, no loans approved
            approval = False

        monthly_installment = calculate_emi(data['loan_amount'], corrected_rate, data['tenure'])

        return Response({
            "customer_id": customer.id,
            "approval": approval,
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": corrected_rate,
            "tenure": data['tenure'],
            "monthly_installment": monthly_installment
        }, status=status.HTTP_200_OK)


class CreateLoan(APIView):
    def post(self, request):
        data = request.data
        customer = get_object_or_404(Customer, id=data['customer_id'])
        eligibility = CheckEligibility().post(request).data

        if not eligibility['approval']:
            return Response({
                "loan_id": None,
                "customer_id": customer.id,
                "loan_approved": False,
                "message": "Loan not approved",
                "monthly_installment": eligibility['monthly_installment']
            }, status=200)

        loan = Loan.objects.create(
            customer=customer,
            loan_id=Loan.objects.count() + 1000,
            loan_amount=data['loan_amount'],
            tenure=data['tenure'],
            interest_rate=eligibility['corrected_interest_rate'],
            monthly_payment=eligibility['monthly_installment'],
            emis_paid_on_time=0,
            date_of_approval=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=30*data['tenure'])
        )

        customer.current_debt += data['loan_amount']
        customer.save()

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer.id,
            "loan_approved": True,
            "message": "Loan approved",
            "monthly_installment": loan.monthly_payment
        }, status=201)

class ViewLoan(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        return Response({
            "loan_id": loan.loan_id,
            "customer": CustomerSerializer(loan.customer).data,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_payment,
            "tenure": loan.tenure
        })

class ViewCustomerLoans(APIView):
    def get(self, request, customer_id):
        loans = Loan.objects.filter(customer_id=customer_id)
        return Response([
            {
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_payment,
                "repayments_left": loan.tenure - loan.emis_paid_on_time
            } for loan in loans
        ])

class TriggerDataLoad(APIView):
    def post(self, request):
        load_customer_data_task.delay()
        load_loan_data_task.delay()
        return Response({"message": "Data ingestion started"}, status=202)