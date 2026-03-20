from datetime import UTC, datetime, timedelta
from secrets import compare_digest

from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Genera un JWT con fecha de expiracion.

    El token incluye `sub` para identificar al usuario en rutas protegidas.
    El manejo de expiracion evita tokens indefinidos que comprometan seguridad.
    """
    settings = get_settings()
    expires_in = expires_minutes if expires_minutes is not None else settings.jwt_expire_minutes
    now = datetime.now(UTC)

    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_in)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decodifica y valida un JWT.

    Cualquier error de firma, formato o expiracion retorna un 401 uniforme para
    no exponer detalles internos de autenticacion al cliente.
    """
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedError(message="Token invalido o expirado.") from exc


def verify_demo_password(plain_password: str, expected_password: str) -> bool:
    """Compara password en tiempo constante para credenciales demo."""
    return compare_digest(plain_password, expected_password)
