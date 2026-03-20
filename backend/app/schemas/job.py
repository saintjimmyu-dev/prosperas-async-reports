from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.models.job import JobStatus


class DateRange(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_range(self) -> "DateRange":
        if self.end_date < self.start_date:
            raise ValueError("end_date no puede ser menor que start_date")
        return self


class JobCreateRequest(BaseModel):
    report_type: str = Field(min_length=2, max_length=80)
    date_range: DateRange
    format: Literal["pdf", "csv", "xlsx"]


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobDetailResponse(BaseModel):
    job_id: str
    status: JobStatus
    report_type: str
    format: str
    date_range: DateRange
    result_url: str | None = None
    created_at: str
    updated_at: str


class JobsListResponse(BaseModel):
    items: list[JobDetailResponse]
    next_cursor: str | None = None
