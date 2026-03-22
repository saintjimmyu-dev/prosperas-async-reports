import json
import logging
import math
import signal
import threading
import time
from dataclasses import dataclass

from app.core.config import get_settings
from app.models.job import JobStatus
from app.services.circuit_breaker import ReportTypeCircuitBreaker
from app.services.dynamodb_service import DynamoDBService
from app.services.sqs_service import SQSService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s",
)
logger = logging.getLogger("prosperas-worker")


@dataclass
class WorkerConfig:
    consumer_count: int = 2
    wait_time_seconds: int = 20
    visibility_timeout: int = 30
    simulated_processing_seconds: int = 3


class JobWorker:
    """Worker concurrente para procesar mensajes SQS y actualizar estados en DynamoDB."""

    def __init__(
        self,
        config: WorkerConfig | None = None,
        dynamodb_service: DynamoDBService | None = None,
        sqs_service: SQSService | None = None,
        breaker: ReportTypeCircuitBreaker | None = None,
    ) -> None:
        self._settings = get_settings()
        self._config = config or WorkerConfig()
        self._dynamodb = dynamodb_service or DynamoDBService(settings=self._settings)
        self._sqs = sqs_service or SQSService(settings=self._settings)
        self._breaker = breaker or ReportTypeCircuitBreaker(
            failure_threshold=self._settings.worker_circuit_breaker_failure_threshold,
            cooldown_seconds=self._settings.worker_circuit_breaker_cooldown_seconds,
        )
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

    def run_forever(self) -> None:
        logger.info("Iniciando worker con %s consumidores.", self._config.consumer_count)
        self._install_signal_handlers()

        for index in range(self._config.consumer_count):
            thread = threading.Thread(
                target=self._consumer_loop,
                args=(index + 1,),
                daemon=True,
                name=f"consumer-{index + 1}",
            )
            thread.start()
            self._threads.append(thread)

        while not self._stop_event.is_set():
            time.sleep(0.5)

        for thread in self._threads:
            thread.join(timeout=10)

        logger.info("Worker detenido correctamente.")

    def _install_signal_handlers(self) -> None:
        def _handle_shutdown(signum, _frame) -> None:  # type: ignore[no-untyped-def]
            logger.info("Senal %s recibida. Deteniendo worker...", signum)
            self._stop_event.set()

        signal.signal(signal.SIGINT, _handle_shutdown)
        signal.signal(signal.SIGTERM, _handle_shutdown)

    def _consumer_loop(self, consumer_id: int) -> None:
        logger.info("Consumidor %s listo.", consumer_id)

        while not self._stop_event.is_set():
            handled_priority = self._poll_queue(
                queue_url=self._settings.sqs_priority_queue_url,
                consumer_id=consumer_id,
                queue_label="priority",
            )
            if handled_priority:
                continue

            self._poll_queue(
                queue_url=self._settings.sqs_queue_url,
                consumer_id=consumer_id,
                queue_label="main",
            )

    def _poll_queue(self, *, queue_url: str, consumer_id: int, queue_label: str) -> bool:
        try:
            messages = self._sqs.receive_messages(
                queue_url,
                max_messages=1,
                wait_time_seconds=self._config.wait_time_seconds,
                visibility_timeout=self._config.visibility_timeout,
            )
        except Exception as exc:
            logger.warning(
                "Consumidor %s no pudo leer cola=%s (%s). Reintentando...",
                consumer_id,
                queue_label,
                exc,
            )
            time.sleep(2)
            return False

        if not messages:
            return False

        for message in messages:
            self._process_message(
                queue_url=queue_url,
                queue_label=queue_label,
                consumer_id=consumer_id,
                message=message,
            )

        return True

    def _process_message(self, *, queue_url: str, queue_label: str, consumer_id: int, message: dict) -> None:
        message_id = message.get("MessageId", "unknown")
        receipt_handle = message.get("ReceiptHandle")
        job_id: str | None = None
        report_type = "unknown"

        try:
            payload = json.loads(message.get("Body", "{}"))
            job_id = payload["job_id"]
            report_type = str(payload.get("report_type", ""))
            output_format = str(payload.get("format", "pdf"))

            allowed, retry_after_seconds = self._breaker.allow_processing(report_type)
            if not allowed:
                self._handle_open_circuit(
                    queue_url=queue_url,
                    queue_label=queue_label,
                    consumer_id=consumer_id,
                    message_id=message_id,
                    job_id=job_id,
                    report_type=report_type,
                    receipt_handle=receipt_handle,
                    retry_after_seconds=retry_after_seconds,
                )
                return

            self._dynamodb.update_job_status(job_id=job_id, status=JobStatus.PROCESSING)

            # Permite probar ruta de fallo sin dependencias externas.
            if report_type.lower().startswith("fail"):
                raise RuntimeError("Fallo simulado de procesamiento por report_type.")

            time.sleep(self._config.simulated_processing_seconds)
            result_url = f"s3://prosperas-reports/{job_id}.{output_format}"

            self._dynamodb.update_job_status(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                result_url=result_url,
            )
            self._breaker.record_success(report_type)

            if receipt_handle:
                self._sqs.delete_message(queue_url=queue_url, receipt_handle=receipt_handle)

            logger.info(
                "Consumidor %s proceso job=%s desde cola=%s y marco COMPLETED.",
                consumer_id,
                job_id,
                queue_label,
            )
        except Exception as exc:
            receive_count = self._extract_receive_count(message)
            self._handle_failure(
                queue_url=queue_url,
                queue_label=queue_label,
                consumer_id=consumer_id,
                message_id=message_id,
                job_id=job_id,
                report_type=report_type,
                receipt_handle=receipt_handle,
                receive_count=receive_count,
                error=exc,
            )

    def _handle_open_circuit(
        self,
        *,
        queue_url: str,
        queue_label: str,
        consumer_id: int,
        message_id: str,
        job_id: str | None,
        report_type: str,
        receipt_handle: str | None,
        retry_after_seconds: int,
    ) -> None:
        if receipt_handle:
            try:
                self._sqs.change_message_visibility(
                    queue_url=queue_url,
                    receipt_handle=receipt_handle,
                    timeout_seconds=max(1, retry_after_seconds),
                )
            except Exception:
                logger.exception(
                    "No se pudo aplicar enfriamiento del circuit breaker para message_id=%s",
                    message_id,
                )

        logger.warning(
            "Consumidor %s difirio job_id=%s report_type=%s cola=%s por circuit breaker OPEN; retry_after=%ss message_id=%s",
            consumer_id,
            job_id,
            report_type,
            queue_label,
            max(1, retry_after_seconds),
            message_id,
        )

    def _handle_failure(
        self,
        *,
        queue_url: str,
        queue_label: str,
        consumer_id: int,
        message_id: str,
        job_id: str | None,
        report_type: str,
        receipt_handle: str | None,
        receive_count: int,
        error: Exception,
    ) -> None:
        self._breaker.record_failure(report_type, error=error)

        if receive_count >= self._settings.worker_max_attempts:
            if job_id:
                try:
                    self._dynamodb.update_job_status(job_id=job_id, status=JobStatus.FAILED)
                except Exception:
                    logger.exception("No se pudo actualizar estado FAILED para job=%s", job_id)

            logger.warning(
                "Consumidor %s agoto reintentos para message_id=%s job_id=%s cola=%s intento=%s error=%s",
                consumer_id,
                message_id,
                job_id,
                queue_label,
                receive_count,
                error,
            )
            # No se elimina el mensaje para que SQS aplique RedrivePolicy hacia la DLQ.
            return

        backoff_seconds = min(
            self._settings.worker_retry_base_seconds * int(math.pow(2, max(receive_count - 1, 0))),
            self._settings.worker_retry_max_seconds,
        )

        if job_id:
            try:
                self._dynamodb.update_job_status(job_id=job_id, status=JobStatus.PENDING)
            except Exception:
                logger.exception("No se pudo revertir estado a PENDING para job=%s", job_id)

        if receipt_handle:
            try:
                self._sqs.change_message_visibility(
                    queue_url=queue_url,
                    receipt_handle=receipt_handle,
                    timeout_seconds=backoff_seconds,
                )
            except Exception:
                logger.exception(
                    "No se pudo ajustar visibilidad para backoff en message_id=%s",
                    message_id,
                )

        logger.warning(
            "Consumidor %s fallo procesando message_id=%s job_id=%s cola=%s intento=%s backoff=%ss error=%s",
            consumer_id,
            message_id,
            job_id,
            queue_label,
            receive_count,
            backoff_seconds,
            error,
        )

    @staticmethod
    def _extract_receive_count(message: dict) -> int:
        raw_value = message.get("Attributes", {}).get("ApproximateReceiveCount", "1")
        try:
            return max(1, int(raw_value))
        except Exception:
            return 1


def main() -> None:
    worker = JobWorker(config=WorkerConfig())
    worker.run_forever()


if __name__ == "__main__":
    main()
