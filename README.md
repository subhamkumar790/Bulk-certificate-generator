# Bulk Certificate Generator API

A FastAPI-based backend application for generating certificates in bulk from a single API request.

The application accepts event details and a list of recipients, creates a background job, generates one PDF certificate for each recipient, tracks job progress, handles individual certificate failures, and provides APIs to retrieve generated certificates.

## Features

* Bulk certificate generation
* Single API request for multiple recipients
* PDF certificate generation using ReportLab
* Background job processing
* Job status tracking
* Progress tracking
* Individual certificate status
* Failure handling without stopping the complete job
* Certificate listing
* Individual PDF download
* Request validation using Pydantic
* SQLite relational database
* Automated tests using Pytest

## Technology Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* ReportLab
* Pytest
* HTTPX

## Project Structure

```text
Bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── certificate.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── certificate.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── jobs.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── generator.py
│       └── job_processor.py
│
├── tests/
│   ├── __init__.py
│   └── test_jobs.py
│
├── generated_certificates/
├── certificates.db
├── README.md
└── venv/
```

## Setup

### 1. Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install fastapi uvicorn sqlalchemy reportlab pydantic[email] pytest httpx
```

### 3. Run the application

```powershell
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available through FastAPI Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Create a Job

```http
POST /api/jobs/
```

Example request:

```json
{
    "event_name": "Python Workshop",
    "course_name": "Python Programming",
    "date": "2026-10-08",
    "recipients": [
        {
            "name": "Rahul Kumar",
            "email": "rahul@example.com"
        },
        {
            "name": "Amit Kumar",
            "email": "amit@example.com"
        }
    ]
}
```

Example response:

```json
{
    "job_id": "job-uuid",
    "status": "PENDING",
    "total": 2
}
```

## Check Job Status

```http
GET /api/jobs/{job_id}
```

Example response:

```json
{
    "job_id": "job-uuid",
    "event_name": "Python Workshop",
    "course_name": "Python Programming",
    "status": "COMPLETED",
    "total": 2,
    "successful": 2,
    "failed": 0,
    "progress": 100
}
```

Possible job statuses include:

* `PENDING`
* `PROCESSING`
* `COMPLETED`
* `COMPLETED_WITH_ERRORS`

## Get Certificates for a Job

```http
GET /api/jobs/{job_id}/certificates
```

This endpoint returns the certificates associated with a job along with their individual status.

Example:

```json
{
    "job_id": "job-uuid",
    "total": 2,
    "certificates": [
        {
            "certificate_id": "certificate-uuid",
            "recipient_name": "Rahul Kumar",
            "recipient_email": "rahul@example.com",
            "status": "COMPLETED",
            "file_path": "generated_certificates/certificate-uuid.pdf",
            "error_message": null
        }
    ]
}
```

## Download a Certificate

```http
GET /api/jobs/certificates/{certificate_id}
```

The endpoint returns the generated certificate as a PDF file.

## Validation

The API validates:

* Recipient name length
* Email format
* Event name length
* Course name length
* Date format
* Minimum number of recipients
* Maximum number of recipients

The current API accepts up to 1000 recipients in one request.

## Failure Handling

Certificate generation is handled independently for each recipient.

If one certificate fails:

1. The failed certificate is marked as `FAILED`.
2. The error message is stored.
3. The failed count is increased.
4. Other recipients continue to be processed.
5. The final job status becomes `COMPLETED_WITH_ERRORS`.

This prevents a single certificate failure from stopping the entire bulk generation process.

## Testing

Run all automated tests using:

```powershell
pytest -v
```

The project currently contains tests for:

* Job creation
* Invalid recipient validation
* Job status
* Job not found
* Certificate listing
* Certificate not found
* Certificate PDF download
* Individual certificate failure handling

Current result:

```text
8 passed
```

## Design Decisions

### FastAPI

FastAPI was selected because it provides:

* Simple API development
* Automatic request validation
* Interactive Swagger documentation
* Good support for background tasks
* Easy testing with TestClient

### SQLite

SQLite is used as the relational database because it is lightweight and requires no separate database server.

For production deployment, PostgreSQL or another production-grade relational database can be used.

### SQLAlchemy

SQLAlchemy provides database models and database interaction while keeping the application independent from a specific database engine.

### Background Processing

FastAPI BackgroundTasks are used so certificate generation can be handled after the job request is created.

For a production system with very large workloads, a distributed task queue such as Celery with Redis could be used instead.

### Individual Failure Handling

Each certificate is processed inside its own `try/except` block. This ensures that one failed certificate does not stop the processing of other recipients.

## Workflow

```text
Client
   |
   | POST /api/jobs/
   v
FastAPI
   |
   | Validate request
   v
Create Job + Certificates
   |
   | Background processing
   v
Process each recipient
   |
   +----> Generate PDF ----> COMPLETED
   |
   +----> Generation error -> FAILED
   |
   v
Update Job Progress
   |
   v
GET /api/jobs/{job_id}
   |
   v
GET /api/jobs/{job_id}/certificates
   |
   v
Download individual PDF
```

## Future Improvements

Possible production improvements include:

* Celery + Redis for distributed background processing
* PostgreSQL database
* Authentication and authorization
* Configurable certificate templates
* Email delivery of certificates
* Cloud storage such as AWS S3
* Job cancellation
* Retry mechanism for failed certificates
* Rate limiting
* Docker deployment
* Production logging and monitoring

## Conclusion

The Bulk Certificate Generator provides a complete backend workflow for submitting a bulk certificate generation job, processing recipients independently, tracking progress, handling failures, and retrieving generated PDF certificates through REST APIs.
