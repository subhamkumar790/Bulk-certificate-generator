from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_job():

    response = client.post(
        "/api/jobs/",
        json={
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
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["total"] == 2
    assert data["status"] == "PENDING"


def test_invalid_recipient():

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "course_name": "Python Programming",
            "date": "2026-10-08",
            "recipients": [
                {
                    "name": "A",
                    "email": "invalid-email"
                }
            ]
        }
    )

    assert response.status_code == 422


def test_job_status():

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "course_name": "Python Programming",
            "date": "2026-10-08",
            "recipients": [
                {
                    "name": "Rahul Kumar",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    job_id = response.json()["job_id"]

    response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 1


def test_job_not_found():

    response = client.get(
        "/api/jobs/non-existing-job"
    )

    assert response.status_code == 404


def test_get_job_certificates():

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "course_name": "Python Programming",
            "date": "2026-10-08",
            "recipients": [
                {
                    "name": "Rahul Kumar",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 1
    assert len(data["certificates"]) == 1


def test_certificate_not_found():

    response = client.get(
        "/api/jobs/certificates/non-existing-certificate"
    )

    assert response.status_code == 404


def test_download_certificate():

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "course_name": "Python Programming",
            "date": "2026-10-08",
            "recipients": [
                {
                    "name": "Rahul Kumar",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )

    assert response.status_code == 200

    data = response.json()

    certificate_id = data["certificates"][0]["certificate_id"]

    response = client.get(
        f"/api/jobs/certificates/{certificate_id}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert len(response.content) > 0


@patch("app.services.job_processor.generate_certificate")
def test_one_certificate_failure(mock_generate):

    def generate_side_effect(
        recipient_name,
        event_name,
        course_name,
        certificate_id
    ):

        if recipient_name == "Bad User":
            raise Exception("Certificate generation failed")

        return "generated_certificates/test-success.pdf"

    mock_generate.side_effect = generate_side_effect

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "course_name": "Python Programming",
            "date": "2026-10-08",
            "recipients": [
                {
                    "name": "Rahul Kumar",
                    "email": "rahul@example.com"
                },
                {
                    "name": "Bad User",
                    "email": "bad@example.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "COMPLETED_WITH_ERRORS"
    assert data["total"] == 2
    assert data["successful"] == 1
    assert data["failed"] == 1
    assert data["progress"] == 100