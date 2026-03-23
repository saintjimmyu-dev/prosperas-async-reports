from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion centralizada de la aplicacion.

    Se usa BaseSettings para leer variables de entorno sin hardcodear secretos.
    Esto permite que el mismo codigo funcione en local con LocalStack y luego en
    AWS real con cambios solo de configuracion.
    """

    app_name: str = "Prosperas Async Reports API"
    app_env: str = "local"
    app_port: int = 8000

    jwt_secret_key: str = "cambia-esto-en-produccion"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_endpoint_url: str | None = None

    dynamodb_table_name: str = "prosperas-jobs"
    dynamodb_user_index_name: str = "user_id-index"

    sqs_queue_url: str = "http://localstack:4566/000000000000/prosperas-jobs-queue"
    sqs_priority_queue_url: str = "http://localstack:4566/000000000000/prosperas-jobs-priority-queue"
    sqs_dlq_url: str = "http://localstack:4566/000000000000/prosperas-jobs-dlq"
    sqs_priority_report_keywords: str = "priority,urgent,critico,critica"

    worker_max_attempts: int = 3
    worker_retry_base_seconds: int = 2
    worker_retry_max_seconds: int = 60
    worker_circuit_breaker_failure_threshold: int = 2
    worker_circuit_breaker_cooldown_seconds: int = 30
    realtime_stream_interval_seconds: int = 2

    cors_allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    demo_user_username: str = "demo"
    demo_user_password: str = "demo123"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("aws_access_key_id", "aws_secret_access_key", "aws_endpoint_url", mode="before")
    @classmethod
    def _empty_string_to_none(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    """Retorna la configuracion cacheada para evitar lecturas repetidas de entorno."""
    return Settings()
