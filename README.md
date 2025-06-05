# 🏦 Credit Approval System

This project is a backend-only Credit Approval System built using **Django 4+, Django REST Framework**, **PostgreSQL**, **Docker**, and **Celery** for background tasks. It handles customer registrations, eligibility checks, loan approvals, and data ingestion from Excel files.

---

## 🚀 Features

- ✅ Customer Registration with credit limit calculation
- ✅ Loan Eligibility Check with custom credit scoring
- ✅ Loan Creation with EMI calculation
- ✅ View Loan details
- ✅ View all loans for a customer
- ✅ Background task to ingest Excel data (`customer_data.xlsx`, `loan_data.xlsx`)
- ✅ Fully Dockerized setup

---

## 🛠️ Tech Stack

- Python 3.11+
- Django 4+
- Django REST Framework
- PostgreSQL
- Celery + Redis
- Docker + Docker Compose

---

---

## 🐳 Run with Docker


### Prerequisites:
- Docker & Docker Compose installed

### 1. Build and run:
```bash
docker-compose up --build
---
Run migrations:
docker-compose exec web python manage.py migrate
