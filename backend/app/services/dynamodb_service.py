import base64
import json

import boto3
from boto3.dynamodb.conditions import Key

from app.core.config import Settings
from app.core.exceptions import InfrastructureError
from app.models.job import Job


class DynamoDBService:
    """Abstraccion de acceso a DynamoDB para jobs.

    Esta clase encapsula serializacion, paginacion por cursor y consultas por
    indice secundario, manteniendo la logica AWS fuera de los routers.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._resource = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        self._table = self._resource.Table(settings.dynamodb_table_name)

    def put_job(self, job: Job) -> None:
        try:
            self._table.put_item(Item=job.to_item())
        except Exception as exc:
            raise InfrastructureError(
                message="No se pudo persistir el job en DynamoDB.",
                details={"table": self._settings.dynamodb_table_name},
            ) from exc

    def get_job(self, job_id: str) -> Job | None:
        try:
            response = self._table.get_item(Key={"job_id": job_id})
        except Exception as exc:
            raise InfrastructureError(
                message="No se pudo consultar el job en DynamoDB.",
                details={"job_id": job_id},
            ) from exc

        item = response.get("Item")
        if not item:
            return None
        return Job.from_item(item)

    def list_jobs_by_user(self, user_id: str, page_size: int, cursor: str | None) -> tuple[list[Job], str | None]:
        exclusive_start_key = self._decode_cursor(cursor)

        query_params: dict = {
            "IndexName": self._settings.dynamodb_user_index_name,
            "KeyConditionExpression": Key("user_id").eq(user_id),
            "Limit": page_size,
            "ScanIndexForward": False,
        }
        if exclusive_start_key:
            query_params["ExclusiveStartKey"] = exclusive_start_key

        try:
            response = self._table.query(**query_params)
        except Exception as exc:
            raise InfrastructureError(
                message="No se pudo listar jobs por usuario en DynamoDB.",
                details={"user_id": user_id},
            ) from exc

        items = [Job.from_item(item) for item in response.get("Items", [])]
        next_cursor = self._encode_cursor(response.get("LastEvaluatedKey"))
        return items, next_cursor

    @staticmethod
    def _encode_cursor(last_evaluated_key: dict | None) -> str | None:
        if not last_evaluated_key:
            return None
        raw = json.dumps(last_evaluated_key).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("utf-8")

    @staticmethod
    def _decode_cursor(cursor: str | None) -> dict | None:
        if not cursor:
            return None
        try:
            raw = base64.urlsafe_b64decode(cursor.encode("utf-8"))
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise InfrastructureError(
                message="El cursor de paginacion es invalido.",
                details={"cursor": cursor},
            ) from exc
