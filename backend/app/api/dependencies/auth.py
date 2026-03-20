from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models.auth import UserContext


_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UserContext:
    """Valida el JWT y devuelve el contexto del usuario autenticado.

    Esta dependencia centraliza la autenticacion en un solo punto para evitar
    repetir logica en cada endpoint protegido. Si el token no existe o no es
    valido, se lanza un error 401 uniforme para toda la API.
    """
    if credentials is None:
        raise UnauthorizedError(message="Token de acceso requerido.")

    payload = decode_access_token(credentials.credentials)
    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError(message="El token no contiene un sujeto valido.")

    return UserContext(user_id=subject)
