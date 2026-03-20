from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Depends

from app.core.exceptions import InfrastructureError, NotFoundError
from app.models.job import Job, JobStatus
from app.schemas.job import DateRange, JobCreateRequest, JobCreateResponse, JobDetailResponse, JobsListResponse
from app.services.service_factory import get_dynamodb_service, get_sqs_service
from app.services.dynamodb_service import DynamoDBService
from app.services.sqs_service import SQSService


class JobService:
    """Orquesta casos de uso de jobs entre persistencia y mensajeria."""

    def __init__(self, dynamodb_service: DynamoDBService, sqs_service: SQSService) -> None:
        self._dynamodb_service = dynamodb_service
        self._sqs_service = sqs_service

    def create_job(self, user_id: str, payload: JobCreateRequest) -> JobCreateResponse:
        now = datetime.now(UTC)
        job = Job(
            job_id=str(uuid4()),
            user_id=user_id,
            status=JobStatus.PENDING,
            report_type=payload.report_type,
            date_range={
                "start_date": payload.date_range.start_date.isoformat(),
                "end_date": payload.date_range.end_date.isoformat(),
            },
            format=payload.format,
            created_at=now,
            updated_at=now,
        )

        self._dynamodb_service.put_job(job)

        try:
            self._sqs_service.send_job_message(
                {
                    "job_id": job.job_id,
                    "user_id": job.user_id,
                    "report_type": job.report_type,
                    "format": job.format,
                    "date_range": job.date_range,
                    "status": job.status.value,
                }
            )
        except Exception as exc:
            raise InfrastructureError(
                message="No se pudo publicar el job en SQS.",
                details={"job_id": job.job_id},
            ) from exc

        return JobCreateResponse(job_id=job.job_id, status=job.status)

    def get_job_for_user(self, job_id: str, user_id: str) -> JobDetailResponse:
        job = self._dynamodb_service.get_job(job_id)
        if not job or job.user_id != user_id:
            raise NotFoundError(message="No se encontro el job solicitado.", details={"job_id": job_id})
        return self._to_response(job)

    def list_jobs_for_user(self, user_id: str, page_size: int, cursor: str | None) -> JobsListResponse:
        jobs, next_cursor = self._dynamodb_service.list_jobs_by_user(
            user_id=user_id,
            page_size=page_size,
            cursor=cursor,
        )
        return JobsListResponse(items=[self._to_response(job) for job in jobs], next_cursor=next_cursor)

    @staticmethod
    def _to_response(job: Job) -> JobDetailResponse:
        return JobDetailResponse(
            job_id=job.job_id,
            status=job.status,
            report_type=job.report_type,
            format=job.format,
            date_range=DateRange(
                start_date=datetime.fromisoformat(job.date_range["start_date"]).date(),
                end_date=datetime.fromisoformat(job.date_range["end_date"]).date(),
            ),
            result_url=job.result_url,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )


def get_job_service(
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service),
    sqs_service: SQSService = Depends(get_sqs_service),
) -> JobService:
    """Proveedor de dependencia para reutilizar servicios en rutas."""
    return JobService(dynamodb_service=dynamodb_service, sqs_service=sqs_service)
