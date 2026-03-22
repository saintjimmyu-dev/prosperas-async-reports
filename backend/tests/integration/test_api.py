import app.main as main_module

from fastapi.testclient import TestClient

from app.core.exceptions import NotFoundError
from app.models.job import JobStatus
from app.schemas.job import JobCreateResponse, JobDetailResponse, JobsListResponse
from app.services.job_service import get_job_service


class FakeJobService:
    def __init__(self) -> None:
        self.created_payloads: list[dict] = []

    def create_job(self, user_id: str, payload) -> JobCreateResponse:  # type: ignore[no-untyped-def]
        self.created_payloads.append({"user_id": user_id, "payload": payload})
        return JobCreateResponse(job_id="job-api-1", status=JobStatus.PENDING)

    def get_job_for_user(self, job_id: str, user_id: str) -> JobDetailResponse:
        if job_id == "missing":
            raise NotFoundError(message="No encontrado")
        return JobDetailResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            report_type="ventas",
            format="pdf",
            date_range={"start_date": "2026-03-01", "end_date": "2026-03-22"},
            result_url=f"s3://prosperas-reports/{job_id}.pdf",
            created_at="2026-03-22T00:00:00+00:00",
            updated_at="2026-03-22T00:00:03+00:00",
        )

    def list_jobs_for_user(self, user_id: str, page_size: int, cursor: str | None) -> JobsListResponse:
        return JobsListResponse(items=[self.get_job_for_user("job-api-1", user_id)], next_cursor=cursor)


def _client_with_fake_job_service(fake_service: FakeJobService) -> TestClient:
    main_module.app.dependency_overrides[get_job_service] = lambda: fake_service
    return TestClient(main_module.app)


def test_login_returns_access_token() -> None:
    client = TestClient(main_module.app)
    response = client.post("/auth/login", json={"username": "demo", "password": "demo123"})

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_create_job_requires_authentication() -> None:
    client = TestClient(main_module.app)
    response = client.post(
        "/jobs",
        json={
            "report_type": "ventas",
            "date_range": {"start_date": "2026-03-01", "end_date": "2026-03-22"},
            "format": "pdf",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_create_job_success_with_dependency_override() -> None:
    fake_service = FakeJobService()
    client = _client_with_fake_job_service(fake_service)
    token = client.post("/auth/login", json={"username": "demo", "password": "demo123"}).json()["access_token"]

    response = client.post(
        "/jobs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "report_type": "ventas",
            "date_range": {"start_date": "2026-03-01", "end_date": "2026-03-22"},
            "format": "pdf",
        },
    )

    assert response.status_code == 201
    assert response.json()["job_id"] == "job-api-1"
    assert fake_service.created_payloads[0]["user_id"] == "demo"
    main_module.app.dependency_overrides.clear()


def test_create_job_validation_error_uses_standard_envelope() -> None:
    fake_service = FakeJobService()
    client = _client_with_fake_job_service(fake_service)
    token = client.post("/auth/login", json={"username": "demo", "password": "demo123"}).json()["access_token"]

    response = client.post(
        "/jobs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "report_type": "ventas",
            "date_range": {"start_date": "2026-03-01", "end_date": "2026-03-22"},
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    main_module.app.dependency_overrides.clear()


def test_health_reports_dependency_statuses(monkeypatch) -> None:
    class FakeDynamoClient:
        def describe_table(self, TableName: str) -> None:  # noqa: N803
            assert TableName

    class FakeSQSClient:
        def get_queue_attributes(self, QueueUrl: str, AttributeNames: list[str]) -> None:  # noqa: N803
            assert QueueUrl
            assert AttributeNames == ["ApproximateNumberOfMessages"]

    def fake_boto3_client(service_name: str, **kwargs):  # type: ignore[no-untyped-def]
        assert kwargs["region_name"]
        if service_name == "dynamodb":
            return FakeDynamoClient()
        if service_name == "sqs":
            return FakeSQSClient()
        raise AssertionError(f"Servicio inesperado: {service_name}")

    monkeypatch.setattr(main_module.boto3, "client", fake_boto3_client)
    client = TestClient(main_module.app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["dependencies"] == {"dynamodb": "ok", "sqs": "ok"}