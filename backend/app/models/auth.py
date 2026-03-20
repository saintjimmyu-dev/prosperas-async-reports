from pydantic import BaseModel


class UserContext(BaseModel):
    """Contexto minimo del usuario autenticado disponible en dependencias."""

    user_id: str
