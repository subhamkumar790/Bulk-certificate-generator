from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.certificate import Job, Certificate
from app.schemas.certificate import GenerationRequest
from app.services.job_processor import process_job


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


@router.post("/")
def create_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    job = Job(
        event_name=request.event_name,
        course_name=request.course_name,
        date=str(request.date),
        total=len(request.recipients),
        status="PENDING"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    for recipient in request.recipients:

        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="PENDING"
        )

        db.add(certificate)

    db.commit()

    background_tasks.add_task(
        process_job,
        job.id
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total
    }


@router.get("/{job_id}")
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    completed = job.successful + job.failed

    progress = (
        round((completed / job.total) * 100, 2)
        if job.total > 0
        else 0
    )

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "course_name": job.course_name,
        "status": job.status,
        "total": job.total,
        "successful": job.successful,
        "failed": job.failed,
        "progress": progress,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }


@router.get("/{job_id}/certificates")
def get_job_certificates(
    job_id: str,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    certificates = db.query(Certificate).filter(
        Certificate.job_id == job_id
    ).all()

    return {
        "job_id": job_id,
        "total": len(certificates),
        "certificates": [
            {
                "certificate_id": certificate.id,
                "recipient_name": certificate.recipient_name,
                "recipient_email": certificate.recipient_email,
                "status": certificate.status,
                "file_path": certificate.file_path,
                "error_message": certificate.error_message
            }
            for certificate in certificates
        ]
    }


@router.get("/certificates/{certificate_id}")
def get_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):

    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Certificate is not ready"
        )

    if not certificate.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    return FileResponse(
        certificate.file_path,
        media_type="application/pdf",
        filename=f"{certificate.recipient_name}.pdf"
    )