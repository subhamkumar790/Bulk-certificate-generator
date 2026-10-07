from datetime import datetime

from app.database import SessionLocal
from app.models.certificate import Job, Certificate
from app.services.generator import generate_certificate


def process_job(job_id: str):

    db = SessionLocal()

    try:

        job = db.query(Job).filter(
            Job.id == job_id
        ).first()

        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        certificates = db.query(Certificate).filter(
            Certificate.job_id == job_id,
            Certificate.status == "PENDING"
        ).all()

        for certificate in certificates:

            try:

                file_path = generate_certificate(
                    recipient_name=certificate.recipient_name,
                    event_name=job.event_name,
                    course_name=job.course_name,
                    certificate_id=certificate.id
                )

                certificate.status = "COMPLETED"
                certificate.file_path = file_path

                job.successful += 1

            except Exception as e:

                certificate.status = "FAILED"
                certificate.error_message = str(e)

                job.failed += 1

            db.commit()

        if job.failed == 0:
            job.status = "COMPLETED"
        else:
            job.status = "COMPLETED_WITH_ERRORS"

        job.completed_at = datetime.utcnow()

        db.commit()

    finally:
        db.close()