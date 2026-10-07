from datetime import date

from pydantic import BaseModel, EmailStr, Field


class Recipient(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr


class GenerationRequest(BaseModel):

    event_name: str = Field(
        min_length=2,
        max_length=200
    )

    course_name: str = Field(
        min_length=2,
        max_length=200
    )

    date: date

    recipients: list[Recipient] = Field(
        min_length=1,
        max_length=1000
    )