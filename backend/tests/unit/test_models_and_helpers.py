import pytest

from app.core.exceptions import InfrastructureError
from app.models.job import Job, JobStatus
from app.services.dynamodb_service import DynamoDBService


def test_job_to_item_and_from_item_round_trip() -> None:
    job = Job(
        job_id="job-1",
        user_id="demo",
        status=JobStatus.COMPLETED,
        report_type="ventas",
        date_range={"start_date": "2026-03-01", "end_date": "2026-03-22"},
        format="pdf",
        result_url="s3://prosperas-reports/job-1.pdf",
    )

    restored = Job.from_item(job.to_item())

    assert restored.job_id == job.job_id
    assert restored.status == JobStatus.COMPLETED
    assert restored.result_url == "s3://prosperas-reports/job-1.pdf"


def test_dynamodb_cursor_round_trip() -> None:
    cursor = DynamoDBService._encode_cursor({"job_id": "job-1", "user_id": "demo"})

    assert cursor is not None
    assert DynamoDBService._decode_cursor(cursor) == {"job_id": "job-1", "user_id": "demo"}


def test_dynamodb_invalid_cursor_raises_infrastructure_error() -> None:
    with pytest.raises(InfrastructureError):
        DynamoDBService._decode_cursor("not-base64")