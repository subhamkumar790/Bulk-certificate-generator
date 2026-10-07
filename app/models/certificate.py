import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    event_name = Column(
        String,
        nullable=False
    )

    course_name = Column(
        String,
        nullable=False
    )

    date = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="PENDING"
    )

    total = Column(
        Integer,
        default=0
    )

    successful = Column(
        Integer,
        default=0
    )

    failed = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    certificates = relationship(
        "Certificate",
        back_populates="job"
    )


class Certificate(Base):

    __tablename__ = "certificates"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    job_id = Column(
        String,
        ForeignKey("jobs.id"),
        nullable=False
    )

    recipient_name = Column(
        String,
        nullable=False
    )

    recipient_email = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="PENDING"
    )

    file_path = Column(
        String,
        nullable=True
    )

    error_message = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    job = relationship(
        "Job",
        back_populates="certificates"
    )