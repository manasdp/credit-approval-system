# Credit Approval System Backend

This is a backend system for a credit approval service, built with Django and Django Rest Framework. The application is fully containerized using Docker and uses Celery for handling asynchronous tasks like data ingestion from Excel files.

---

## Tech Stack

- **Backend**: Python, Django, Django Rest Framework
- **Database**: PostgreSQL
- **Asynchronous Tasks**: Celery, Redis
- **Containerization**: Docker, Docker Compose

---

## Setup and Installation

To run this project locally, you need to have Docker and Docker Compose installed.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/manasdp/credit-approval-system](https://github.com/manasdp/credit-approval-system)
    cd credit-approval-system
    ```

2.  **Place Data Files:**
    Ensure `customer_data.xlsx` and `loan_data.xlsx` are placed inside the `data/` directory.

3.  **Build and Run the Containers:**
    ```bash
    docker compose up --build -d
    ```

4.  **Apply Database Migrations:**
    ```bash
    docker compose exec backend python manage.py migrate
    ```

5.  **Ingest Initial Data:**
    This command queues the background tasks to populate the database. It is recommended to run this command a second time to ensure all loan data is linked correctly after customer data is fully loaded.
    ```bash
    docker compose exec backend python manage.py ingest_data
    ```

---

## API Endpoints

The API is available at `http://localhost:8000/api/`.

### 1. Register a New Customer

- **Endpoint**: `/api/register/`
- **Method**: `POST`
- **Body**:
  ```json
  {
      "first_name": "Manas",
      "last_name": "Patil",
      "age": 21,
      "monthly_income": 50000,
      "phone_number": "9922468220"
  }
  ```
- **Example `curl` (Windows CMD):**
  ```bash
  curl -X POST http://localhost:8000/api/register/ -H "Content-Type: application/json" -d "{\"first_name\": \"Manas\", \"last_name\": \"Patil\", \"age\": 21, \"monthly_income\": 50000, \"phone_number\": \"9922468220\"}"
  ```

### 2. Check Loan Eligibility

- **Endpoint**: `/api/check-eligibility/`
- **Method**: `POST`
- **Body**:
  ```json
  {
      "customer_id": 1,
      "loan_amount": 100000,
      "interest_rate": 10,
      "tenure": 12
  }
  ```
- **Example `curl` (Windows CMD):**
  ```bash
  curl -X POST http://localhost:8000/api/check-eligibility/ -H "Content-Type: application/json" -d "{\"customer_id\": 1, \"loan_amount\": 100000, \"interest_rate\": 10, \"tenure\": 12}"
  ```

### 3. Create a New Loan

- **Endpoint**: `/api/create-loan/`
- **Method**: `POST`
- **Body**:
  ```json
  {
      "customer_id": 1,
      "loan_amount": 100000,
      "interest_rate": 10,
      "tenure": 12
  }
  ```
- **Example `curl` (Windows CMD):**
  ```bash
  curl -X POST http://localhost:8000/api/create-loan/ -H "Content-Type: application/json" -d "{\"customer_id\": 1, \"loan_amount\": 100000, \"interest_rate\": 10, \"tenure\": 12}"
  ```

### 4. View a Specific Loan

- **Endpoint**: `/api/view-loan/<loan_id>/`
- **Method**: `GET`
- **Example `curl`:**
  ```bash
  curl -X GET http://localhost:8000/api/view-loan/7798/
  ```

### 5. View All Loans for a Customer

- **Endpoint**: `/api/view-loans/<customer_id>/`
- **Method**: `GET`
- **Example `curl`:**
  ```bash
  curl -X GET http://localhost:8000/api/view-loans/1/
  ```
