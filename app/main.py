from fastapi import FastAPI

from app.database import Base, engine
from app.models.certificate import Job, Certificate
from app.api.jobs import router as jobs_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for bulk certificate generation",
    version="1.0.0"
)


app.include_router(jobs_router)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }