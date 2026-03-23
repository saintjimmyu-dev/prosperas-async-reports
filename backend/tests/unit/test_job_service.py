from datetime import UTC, datetime

import pytest

from app.core.exceptions import NotFoundError
from app.core.config import get_settings
from app.models.job import Job, JobStatus
from app.schemas.job import DateRange, JobCreateRequest
from app.services.job_service import JobService


class FakeDynamoDBService:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}

    def put_job(self, job: Job) -> None:
        self.jobs[job.job_id] = job

    def get_job(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def list_jobs_by_user(self, user_id: str, page_size: int, cursor: str | None) -> tuple[list[Job], str | None]:
        jobs = [job for job in self.jobs.values() if job.user_id == user_id][:page_size]
        return jobs, cursor


class FakeSQSService:
    def __init__(self) -> None:
        self.sent_messages: list[tuple[dict, bool]] = []

    def send_job_message(self, payload: dict, priority: bool = False) -> None:
        self.sent_messages.append((payload, priority))


def test_create_job_routes_priority_message() -> None:
    settings = get_settings()
    settings.sqs_priority_report_keywords = "priority,urgent"
    dynamodb = FakeDynamoDBService()
    sqs = FakeSQSService()
    service = JobService(dynamodb_service=dynamodb, sqs_service=sqs, settings=settings)

    response = service.create_job(
        user_id="demo",
        payload=JobCreateRequest(
            report_type="reporte priority mensual",
            date_range=DateRange(start_date=datetime(2026, 3, 1, tzinfo=UTC).date(), end_date=datetime(2026, 3, 22, tzinfo=UTC).date()),
            format="pdf",
        ),
    )

    assert response.status == JobStatus.PENDING
    assert response.job_id in dynamodb.jobs
    assert sqs.sent_messages[0][1] is True
    assert sqs.sent_messages[0][0]["report_type"] == "reporte priority mensual"


def test_get_job_for_user_raises_not_found_for_other_owner() -> None:
    settings = get_settings()
    dynamodb = FakeDynamoDBService()
    sqs = FakeSQSService()
    service = JobService(dynamodb_service=dynamodb, sqs_service=sqs, settings=settings)

    job = Job(
        job_id="job-1",
        user_id="owner-a",
        status=JobStatus.PENDING,
        report_type="ventas",
        date_range={"start_date": "2026-03-01", "end_date": "2026-03-22"},
        format="pdf",
    )
    dynamodb.put_job(job)

    with pytest.raises(NotFoundError):
        service.get_job_for_user(job_id="job-1", user_id="owner-b")


def test_list_jobs_for_user_returns_items_and_cursor() -> None:
    settings = get_settings()
    dynamodb = FakeDynamoDBService()
    sqs = FakeSQSService()
    service = JobService(dynamodb_service=dynamodb, sqs_service=sqs, settings=settings)

    for index in range(2):
        dynamodb.put_job(
            Job(
                job_id=f"job-{index}",
                user_id="demo",
                status=JobStatus.COMPLETED,
                report_type="ventas",
                date_range={"start_date": "2026-03-01", "end_date": "2026-03-22"},
                format="pdf",
                result_url=f"s3://prosperas-reports/job-{index}.pdf",
            )
        )

    response = service.list_jobs_for_user(user_id="demo", page_size=20, cursor="cursor-1")

    assert len(response.items) == 2
    assert response.next_cursor == "cursor-1"