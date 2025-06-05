from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class CustomerAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_customer(self):  # This method is indented inside the class
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "1234567890",
            "age": 30,
            "monthly_income": 50000  # Changed from monthly_salary to monthly_income
        }
        response = self.client.post('/api/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
