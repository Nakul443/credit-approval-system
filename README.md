# Credit Approval System

A Django REST backend that automates customer onboarding, credit eligibility checks, and loan creation using a weighted credit score and a debt-to-income cap. The project also supports batch ingestion from Excel files via Celery and Redis.

## Demo Video (Loom)

Loom link: https://www.loom.com/share/8ce3c0c5a5f74c97a31cb087d708083d

## Features

- Customer registration with approved limit computed from monthly income.
- Eligibility checks with credit score calculation and interest rate correction.
- Loan creation with EMI estimation and DTI validation.
- Loan lookup by loan ID or by customer.
- Background ingestion of customer and loan data from Excel files.
- Dockerized local environment with PostgreSQL, Redis, and Celery worker.

## Tech Stack

- Python 3.12
- Django 4.2, Django REST Framework
- PostgreSQL
- Celery + Redis
- Pandas + OpenPyXL for Excel ingestion
- Docker and Docker Compose

## Getting Started

### Option A: Docker (recommended)

Prerequisites:
- Docker and Docker Compose

Start everything:

```bash
docker-compose up --build
```

This runs migrations and starts:
- API server on `http://localhost:8000`
- PostgreSQL on port `5432`
- Redis on port `6379`
- Celery worker for background tasks

### Option B: Local (without Docker)

Prerequisites:
- Python 3.12
- PostgreSQL and Redis running locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Update database settings in `core/settings.py` to point to your local PostgreSQL instance, then run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

In a separate terminal, start the Celery worker:

```bash
celery -A core worker --loglevel=info
```

### Makefile Shortcuts (local)

These are convenience commands and assume a local `./venv` exists.

```bash
make migrate
make dev
make stop
make ingest
```

## Data Ingestion (Excel)

The project includes `customer_data.xlsx` and `loan_data.xlsx` at the repo root. With the worker running, trigger ingestion:

Local:
```bash
make ingest
```

Docker:
```bash
docker-compose exec web python manage.py shell -c "from api.tasks import ingest_customer_data, ingest_loan_data; ingest_customer_data.delay('customer_data.xlsx'); ingest_loan_data.delay('loan_data.xlsx')"
```

## API Reference

Base URL: `http://localhost:8000/api/`

### POST `/register/`

Creates a new customer profile. Approved limit uses:

```
round((36 * monthly_income) / 100000) * 100000
```

Request body:
```json
{
  "first_name": "Ava",
  "last_name": "Singh",
  "age": 28,
  "phone_number": "9999999999",
  "monthly_income": 75000
}
```

Response `201`:
```json
{
  "customer_id": 1,
  "name": "Ava Singh",
  "age": 28,
  "monthly_income": 75000,
  "approved_limit": 2700000,
  "phone_number": "9999999999"
}
```

### POST `/check-eligibility/`

Checks loan eligibility without creating a loan.

Request body:
```json
{
  "customer_id": 1,
  "loan_amount": 300000,
  "interest_rate": 12,
  "tenure": 12
}
```

Response `200`:
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 12,
  "corrected_interest_rate": 12.0,
  "tenure": 12,
  "monthly_installment": 25000,
  "credit_rating": 100,
  "debug_info": {
    "monthly_salary": 75000,
    "existing_emis": 0,
    "emi_limit": 37500
  }
}
```

### POST `/create-loan/`

Creates a new loan if eligible.

Request body:
```json
{
  "customer_id": 1,
  "loan_amount": 300000,
  "interest_rate": 12,
  "tenure": 12
}
```

Response `201` (approved):
```json
{
  "loan_id": 101,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan successfully sanctioned",
  "monthly_installment": 25000
}
```

Response `200` (rejected):
```json
{
  "loan_id": null,
  "customer_id": 1,
  "loan_approved": false,
  "message": "Loan rejected: Eligibility criteria not met",
  "monthly_installment": 0
}
```

### GET `/view-loan/<loan_id>/`

Fetches a single loan with customer details.

Response `200`:
```json
{
  "loan_id": 101,
  "customer": {
    "id": 1,
    "first_name": "Ava",
    "last_name": "Singh",
    "phone_number": "9999999999",
    "age": 28
  },
  "loan_amount": 300000,
  "interest_rate": 12.0,
  "monthly_installment": 25000,
  "tenure": 12
}
```

### GET `/view-loans-customer/<customer_id>/`

Lists all loans for a customer.

Response `200`:
```json
[
  {
    "loan_id": 101,
    "loan_amount": 300000,
    "interest_rate": 12.0,
    "monthly_installment": 25000,
    "repayments_left": 12
  }
]
```

## Credit Scoring and Approval Rules

- Payment history score based on on-time EMIs.
- Loan count penalty: each loan reduces score by 5 (minimum 0).
- Recent activity penalty for loans started in 2026 (hard-coded in `api/services.py`).
- Weighted score: 50% payment history, 20% loan count, 30% current-year activity.
- Interest rate corrections:
  - Score > 50: approve at requested rate.
  - 30 < score <= 50: approve, minimum 12% rate.
  - 10 < score <= 30: approve, minimum 16% rate.
  - Score <= 10: reject.
- DTI cap: reject if existing EMIs plus new EMI exceed 50% of monthly salary.

## Folder Structure

```
credit-approval-system/
  api/
    migrations/
    models.py
    serializers.py
    services.py
    tasks.py
    tests.py
    urls.py
    views.py
  core/
    settings.py
    urls.py
    celery.py
    wsgi.py
    asgi.py
  customer_data.xlsx
  loan_data.xlsx
  docker-compose.yml
  Dockerfile
  Makefile
  manage.py
  requirements.txt
  README.md
```

## Running Tests

```bash
python manage.py test
```
