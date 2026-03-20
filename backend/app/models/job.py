from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(BaseModel):
    """Representa el estado persistido de un job de reporte."""

    job_id: str
    user_id: str
    status: JobStatus = JobStatus.PENDING
    report_type: str
    date_range: dict[str, str]
    format: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    result_url: str | None = None

    def to_item(self) -> dict:
        """Convierte el modelo a un item serializable para DynamoDB."""
        payload = self.model_dump()
        payload["created_at"] = self.created_at.isoformat()
        payload["updated_at"] = self.updated_at.isoformat()
        payload["status"] = self.status.value
        return payload

    @classmethod
    def from_item(cls, item: dict) -> "Job":
        """Reconstruye el modelo Job desde un item de DynamoDB."""
        return cls(
            job_id=item["job_id"],
            user_id=item["user_id"],
            status=JobStatus(item["status"]),
            report_type=item["report_type"],
            date_range=item["date_range"],
            format=item["format"],
            created_at=datetime.fromisoformat(item["created_at"]),
            updated_at=datetime.fromisoformat(item["updated_at"]),
            result_url=item.get("result_url"),
        )
