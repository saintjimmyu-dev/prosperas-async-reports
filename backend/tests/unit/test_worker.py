import json

from app.core.config import get_settings
from app.models.job import JobStatus
from app.services.circuit_breaker import ReportTypeCircuitBreaker
from app.worker.consumer import JobWorker, WorkerConfig


class FakeDynamoDBService:
    def __init__(self) -> None:
        self.status_updates: list[dict[str, str | None]] = []

    def update_job_status(self, job_id: str, status: JobStatus, result_url: str | None = None) -> None:
        self.status_updates.append(
            {
                "job_id": job_id,
                "status": status.value,
                "result_url": result_url,
            }
        )


class FakeSQSService:
    def __init__(self) -> None:
        self.deleted_messages: list[dict[str, str]] = []
        self.visibility_changes: list[dict[str, str | int]] = []

    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        self.deleted_messages.append({"queue_url": queue_url, "receipt_handle": receipt_handle})

    def change_message_visibility(self, queue_url: str, receipt_handle: str, timeout_seconds: int) -> None:
        self.visibility_changes.append(
            {
                "queue_url": queue_url,
                "receipt_handle": receipt_handle,
                "timeout_seconds": timeout_seconds,
            }
        )


def _message(job_id: str, report_type: str, receive_count: int, receipt_handle: str) -> dict:
    return {
        "MessageId": f"message-{job_id}-{receive_count}",
        "ReceiptHandle": receipt_handle,
        "Body": json.dumps({"job_id": job_id, "report_type": report_type, "format": "pdf"}),
        "Attributes": {"ApproximateReceiveCount": str(receive_count)},
    }


def test_worker_completes_successful_job() -> None:
    dynamodb = FakeDynamoDBService()
    sqs = FakeSQSService()
    breaker = ReportTypeCircuitBreaker(failure_threshold=2, cooldown_seconds=30)
    worker = JobWorker(
        config=WorkerConfig(simulated_processing_seconds=0),
        dynamodb_service=dynamodb,
        sqs_service=sqs,
        breaker=breaker,
    )

    worker._process_message(
        queue_url="queue-main",
        queue_label="main",
        consumer_id=1,
        message=_message("job-1", "ventas", 1, "rh-1"),
    )

    assert [entry["status"] for entry in dynamodb.status_updates] == ["PROCESSING", "COMPLETED"]
    assert sqs.deleted_messages == [{"queue_url": "queue-main", "receipt_handle": "rh-1"}]
    assert breaker.snapshot("ventas")["state"] == "CLOSED"


def test_worker_opens_circuit_breaker_after_repeated_failures() -> None:
    dynamodb = FakeDynamoDBService()
    sqs = FakeSQSService()
    settings = get_settings()
    breaker = ReportTypeCircuitBreaker(failure_threshold=2, cooldown_seconds=30)
    worker = JobWorker(
        config=WorkerConfig(simulated_processing_seconds=0),
        dynamodb_service=dynamodb,
        sqs_service=sqs,
        breaker=breaker,
    )
    worker._settings.worker_max_attempts = 3
    worker._settings.worker_retry_base_seconds = 2
    worker._settings.worker_retry_max_seconds = 60

    worker._process_message(
        queue_url=settings.sqs_queue_url,
        queue_label="main",
        consumer_id=1,
        message=_message("job-2", "fail-ventas", 1, "rh-2a"),
    )
    worker._process_message(
        queue_url=settings.sqs_queue_url,
        queue_label="main",
        consumer_id=1,
        message=_message("job-2", "fail-ventas", 2, "rh-2b"),
    )
    previous_updates = len(dynamodb.status_updates)

    worker._process_message(
        queue_url=settings.sqs_queue_url,
        queue_label="main",
        consumer_id=1,
        message=_message("job-3", "fail-ventas", 1, "rh-3"),
    )

    assert breaker.snapshot("fail-ventas")["state"] == "OPEN"
    assert len(dynamodb.status_updates) == previous_updates
    assert [entry["status"] for entry in dynamodb.status_updates] == [
        "PROCESSING",
        "PENDING",
        "PROCESSING",
        "PENDING",
    ]
    assert sqs.visibility_changes[0]["timeout_seconds"] == 2
    assert sqs.visibility_changes[1]["timeout_seconds"] == 4
    assert sqs.visibility_changes[2]["timeout_seconds"] >= 1