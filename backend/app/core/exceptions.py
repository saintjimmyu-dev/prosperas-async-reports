from typing import Any


class AppError(Exception):
    """Excepcion de dominio para mapear errores a respuestas HTTP consistentes."""

    def __init__(
        self,
        *,
        message: str,
        code: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    def __init__(self, message: str = "Recurso no encontrado.", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="NOT_FOUND", status_code=404, details=details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "No autorizado.", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401, details=details)


class InfrastructureError(AppError):
    def __init__(
        self,
        message: str = "Error de infraestructura.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code="INFRASTRUCTURE_ERROR", status_code=500, details=details)
