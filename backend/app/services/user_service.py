from app.core.config import get_settings
from app.core.security import verify_demo_password


def validate_demo_credentials(username: str, password: str) -> bool:
    """Valida credenciales demo configuradas por entorno.

    Esta funcion desacopla la ruta de auth de la fuente de usuarios para facilitar
    una migracion posterior a tabla real de usuarios sin tocar el router.
    """
    settings = get_settings()
    return username == settings.demo_user_username and verify_demo_password(
        password,
        settings.demo_user_password,
    )
