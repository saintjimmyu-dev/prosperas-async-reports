import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.services.service_factory import get_dynamodb_service, get_sqs_service


@pytest.fixture(autouse=True)
def clear_cached_dependencies() -> None:
    get_settings.cache_clear()
    get_dynamodb_service.cache_clear()
    get_sqs_service.cache_clear()
    yield
    get_settings.cache_clear()
    get_dynamodb_service.cache_clear()
    get_sqs_service.cache_clear()