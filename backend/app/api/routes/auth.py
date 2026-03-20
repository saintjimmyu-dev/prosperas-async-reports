from fastapi import APIRouter

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import validate_demo_credentials

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    """Genera un JWT para el usuario demo configurado.

    Esta implementacion permite arrancar el proyecto sin bloquear Fase 1 por la
    definicion final de registro de usuarios. Si luego se confirma registro/login
    real, esta ruta puede evolucionar sin romper los endpoints de jobs.
    """
    if not validate_demo_credentials(payload.username, payload.password):
        raise UnauthorizedError(message="Credenciales invalidas.")

    token = create_access_token(subject=payload.username)
    return TokenResponse(access_token=token)
