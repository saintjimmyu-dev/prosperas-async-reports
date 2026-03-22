from datetime import UTC, datetime, timedelta

from app.services.circuit_breaker import ReportTypeCircuitBreaker


def test_circuit_breaker_opens_after_threshold_failures() -> None:
    breaker = ReportTypeCircuitBreaker(failure_threshold=2, cooldown_seconds=30)
    now = datetime(2026, 3, 22, 12, 0, tzinfo=UTC)

    allowed, retry_after = breaker.allow_processing("ventas", now=now)
    assert allowed is True
    assert retry_after == 0

    breaker.record_failure("ventas", error=RuntimeError("boom-1"), now=now)
    breaker.record_failure("ventas", error=RuntimeError("boom-2"), now=now)

    allowed, retry_after = breaker.allow_processing("ventas", now=now + timedelta(seconds=5))
    snapshot = breaker.snapshot("ventas")

    assert allowed is False
    assert retry_after == 25
    assert snapshot["state"] == "OPEN"
    assert snapshot["consecutive_failures"] == 2


def test_circuit_breaker_half_open_then_closes_on_success() -> None:
    breaker = ReportTypeCircuitBreaker(failure_threshold=2, cooldown_seconds=10)
    now = datetime(2026, 3, 22, 12, 0, tzinfo=UTC)

    breaker.record_failure("ventas", error=RuntimeError("boom-1"), now=now)
    breaker.record_failure("ventas", error=RuntimeError("boom-2"), now=now)

    allowed, retry_after = breaker.allow_processing("ventas", now=now + timedelta(seconds=11))
    assert allowed is True
    assert retry_after == 0
    assert breaker.snapshot("ventas")["state"] == "HALF_OPEN"

    breaker.record_success("ventas")
    snapshot = breaker.snapshot("ventas")

    assert snapshot["state"] == "CLOSED"
    assert snapshot["consecutive_failures"] == 0
    assert snapshot["opened_at"] is None


def test_circuit_breaker_half_open_reopens_on_failure() -> None:
    breaker = ReportTypeCircuitBreaker(failure_threshold=2, cooldown_seconds=10)
    now = datetime(2026, 3, 22, 12, 0, tzinfo=UTC)

    breaker.record_failure("ventas", error=RuntimeError("boom-1"), now=now)
    breaker.record_failure("ventas", error=RuntimeError("boom-2"), now=now)
    allowed, _ = breaker.allow_processing("ventas", now=now + timedelta(seconds=12))

    assert allowed is True

    breaker.record_failure("ventas", error=RuntimeError("boom-3"), now=now + timedelta(seconds=12))
    snapshot = breaker.snapshot("ventas")

    assert snapshot["state"] == "OPEN"
    assert snapshot["consecutive_failures"] == 2


def test_circuit_breaker_normalizes_report_type() -> None:
    breaker = ReportTypeCircuitBreaker(failure_threshold=1, cooldown_seconds=15)
    breaker.record_failure("  VENTAS  ", error=RuntimeError("boom"))

    assert breaker.snapshot("ventas")["state"] == "OPEN"