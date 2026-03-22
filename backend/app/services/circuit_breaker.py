from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock


@dataclass
class CircuitBreakerEntry:
    state: str = "CLOSED"
    consecutive_failures: int = 0
    opened_at: datetime | None = None
    half_open_in_flight: bool = False
    last_error: str | None = None


class ReportTypeCircuitBreaker:
    """Circuit breaker en memoria por tipo de reporte.

    El objetivo es frenar rapidamente tipos de reporte que estan fallando de
    forma repetida para evitar desperdiciar capacidad del worker. La memoria en
    proceso es suficiente para la topologia actual de una sola instancia EC2.
    """

    def __init__(self, *, failure_threshold: int, cooldown_seconds: int) -> None:
        self._failure_threshold = max(1, int(failure_threshold))
        self._cooldown_seconds = max(1, int(cooldown_seconds))
        self._entries: dict[str, CircuitBreakerEntry] = {}
        self._lock = Lock()

    def allow_processing(self, report_type: str, now: datetime | None = None) -> tuple[bool, int]:
        current_time = now or datetime.now(UTC)
        normalized = self._normalize_report_type(report_type)

        with self._lock:
            entry = self._entries.setdefault(normalized, CircuitBreakerEntry())

            if entry.state == "OPEN":
                if entry.opened_at and current_time - entry.opened_at >= timedelta(seconds=self._cooldown_seconds):
                    entry.state = "HALF_OPEN"
                    entry.half_open_in_flight = True
                    return True, 0
                return False, self._remaining_cooldown_seconds(entry, current_time)

            if entry.state == "HALF_OPEN":
                if entry.half_open_in_flight:
                    return False, 1
                entry.half_open_in_flight = True
                return True, 0

            return True, 0

    def record_success(self, report_type: str) -> None:
        normalized = self._normalize_report_type(report_type)
        with self._lock:
            entry = self._entries.setdefault(normalized, CircuitBreakerEntry())
            entry.state = "CLOSED"
            entry.consecutive_failures = 0
            entry.opened_at = None
            entry.half_open_in_flight = False
            entry.last_error = None

    def record_failure(self, report_type: str, *, error: Exception | None = None, now: datetime | None = None) -> None:
        current_time = now or datetime.now(UTC)
        normalized = self._normalize_report_type(report_type)

        with self._lock:
            entry = self._entries.setdefault(normalized, CircuitBreakerEntry())
            entry.last_error = str(error) if error is not None else None

            if entry.state == "HALF_OPEN":
                self._open(entry, current_time)
                return

            entry.consecutive_failures += 1
            entry.half_open_in_flight = False
            if entry.consecutive_failures >= self._failure_threshold:
                self._open(entry, current_time)

    def snapshot(self, report_type: str) -> dict[str, int | str | None | bool]:
        normalized = self._normalize_report_type(report_type)
        with self._lock:
            entry = self._entries.setdefault(normalized, CircuitBreakerEntry())
            return {
                "state": entry.state,
                "consecutive_failures": entry.consecutive_failures,
                "opened_at": entry.opened_at.isoformat() if entry.opened_at else None,
                "half_open_in_flight": entry.half_open_in_flight,
                "last_error": entry.last_error,
            }

    def _open(self, entry: CircuitBreakerEntry, current_time: datetime) -> None:
        entry.state = "OPEN"
        entry.opened_at = current_time
        entry.half_open_in_flight = False
        entry.consecutive_failures = max(entry.consecutive_failures, self._failure_threshold)

    def _remaining_cooldown_seconds(self, entry: CircuitBreakerEntry, current_time: datetime) -> int:
        if entry.opened_at is None:
            return self._cooldown_seconds
        elapsed = current_time - entry.opened_at
        remaining = self._cooldown_seconds - int(elapsed.total_seconds())
        return max(1, remaining)

    @staticmethod
    def _normalize_report_type(report_type: str) -> str:
        normalized = report_type.strip().lower()
        return normalized or "unknown"