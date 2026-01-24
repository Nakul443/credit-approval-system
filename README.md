# Credit Approval System

A robust Django-based backend system that automates credit eligibility and loan management using weighted scoring models.

## 🚀 Key Features

- **Customer Management**: Automated credit limit calculation ($36 \times$ monthly income).
- **Service-Oriented Architecture**: Business logic is decoupled from views for high maintainability.
- **Weighted Credit Scoring**: Real-time assessment based on:
  - Past payment history.
  - Number of active loans.
  - Recent credit activity (current year).
  - Debt-to-Income (DTI) ratio (50% salary cap).
- **Background Processing**: Integrated with Celery and Redis for scalable task management.
- **Fully Dockerized**: One-command setup for App, DB, Redis, and Worker.

---

## 🛠 Tech Stack

- **Framework:** Django, Django Rest Framework
- **Database:** PostgreSQL
- **Task Queue:** Celery / Redis
- **Containerization:** Docker & Docker Compose
- **Date Handling:** python-dateutil

---

## 🏃 Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine.

### Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone <your-repo-link>
   cd credit-approval-system