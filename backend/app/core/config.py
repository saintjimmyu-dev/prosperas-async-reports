from functools import lru_cache

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
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_endpoint_url: str | None = "http://localstack:4566"

    dynamodb_table_name: str = "prosperas-jobs"
    dynamodb_user_index_name: str = "user_id-index"

    sqs_queue_url: str = "http://localstack:4566/000000000000/prosperas-jobs-queue"
    sqs_priority_queue_url: str = "http://localstack:4566/000000000000/prosperas-jobs-priority-queue"
    sqs_dlq_url: str = "http://localstack:4566/000000000000/prosperas-jobs-dlq"

    demo_user_username: str = "demo"
    demo_user_password: str = "demo123"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Retorna la configuracion cacheada para evitar lecturas repetidas de entorno."""
    return Settings()
