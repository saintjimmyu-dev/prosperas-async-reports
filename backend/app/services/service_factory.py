from functools import lru_cache

from app.core.config import get_settings
from app.services.dynamodb_service import DynamoDBService
from app.services.sqs_service import SQSService


@lru_cache
def get_dynamodb_service() -> DynamoDBService:
    return DynamoDBService(settings=get_settings())


@lru_cache
def get_sqs_service() -> SQSService:
    return SQSService(settings=get_settings())
