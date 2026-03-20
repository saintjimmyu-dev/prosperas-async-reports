import json

import boto3

from app.core.config import Settings
from app.core.exceptions import InfrastructureError


class SQSService:
    """Cliente simple de SQS para publicar trabajos asincronos."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def send_job_message(self, payload: dict, priority: bool = False) -> None:
        """Publica un mensaje en la cola principal o de prioridad.

        El enrutamiento de prioridad queda listo para Fase 2, permitiendo activar
        B1 sin refactor profundo del backend.
        """
        queue_url = self._settings.sqs_queue_url
        if priority and self._settings.sqs_priority_queue_url:
            queue_url = self._settings.sqs_priority_queue_url

        try:
            self._client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(payload),
                MessageAttributes={
                    "report_type": {
                        "DataType": "String",
                        "StringValue": str(payload.get("report_type", "unknown")),
                    }
                },
            )
        except Exception as exc:
            raise InfrastructureError(
                message="No se pudo publicar el mensaje en SQS.",
                details={"queue_url": queue_url},
            ) from exc

    def receive_messages(
        self,
        queue_url: str,
        *,
        max_messages: int = 1,
        wait_time_seconds: int = 20,
        visibility_timeout: int = 30,
    ) -> list[dict]:
        """Recibe mensajes desde SQS usando long polling para reducir consumo ocioso."""
        try:
            response = self._client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,
                VisibilityTimeout=visibility_timeout,
                AttributeNames=["All"],
                MessageAttributeNames=["All"],
            )
        except Exception as exc:
            raise InfrastructureError(
                message="No se pudieron recibir mensajes desde SQS.",
                details={"queue_url": queue_url},
            ) from exc

        return response.get("Messages", [])

    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        """Confirma procesamiento exitoso eliminando el mensaje de la cola."""
        try:
            self._client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        except Exception as exc:
            raise InfrastructureError(
                message="No se pudo eliminar el mensaje de SQS.",
                details={"queue_url": queue_url},
            ) from exc
