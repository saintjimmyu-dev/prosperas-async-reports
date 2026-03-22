import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.realtime import router as realtime_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API para procesamiento asincrono de reportes en Prosperas.",
)

allowed_origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(realtime_router)


@app.get("/")
def root() -> dict:
    return {
        "message": "Prosperas Async Reports API",
        "environment": settings.app_env,
    }


@app.get("/health")
def health() -> dict:
    """Healthcheck extendido: verifica que la API esta viva y que puede alcanzar
    DynamoDB y SQS. Satisface el bonus B5 de observabilidad.

    Devuelve HTTP 200 incluso cuando una dependencia falla, pero incluye el
    detalle en la respuesta para que sea visible sin romper reverse proxies o
    load balancers que usen este endpoint como liveness probe.
    """
    checks: dict[str, str] = {}

    # Verificar DynamoDB describiendo la tabla (operacion ligera, no consume RCU)
    try:
        boto3_kwargs: dict = {"region_name": settings.aws_region}
        if settings.aws_endpoint_url:
            boto3_kwargs["endpoint_url"] = settings.aws_endpoint_url
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            boto3_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            boto3_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        dynamodb = boto3.client("dynamodb", **boto3_kwargs)
        dynamodb.describe_table(TableName=settings.dynamodb_table_name)
        checks["dynamodb"] = "ok"
    except (BotoCoreError, ClientError) as exc:
        checks["dynamodb"] = f"error: {exc}"

    # Verificar SQS obteniendo atributos de la cola (operacion ligera y gratuita)
    try:
        sqs = boto3.client("sqs", **boto3_kwargs)
        sqs.get_queue_attributes(
            QueueUrl=settings.sqs_queue_url,
            AttributeNames=["ApproximateNumberOfMessages"],
        )
        checks["sqs"] = "ok"
    except (BotoCoreError, ClientError) as exc:
        checks["sqs"] = f"error: {exc}"

    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "service": "backend",
        "environment": settings.app_env,
        "dependencies": checks,
    }
