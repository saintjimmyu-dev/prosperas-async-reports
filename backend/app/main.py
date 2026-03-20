from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.jobs import router as jobs_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API para procesamiento asincrono de reportes en Prosperas.",
)

register_error_handlers(app)

app.include_router(auth_router)
app.include_router(jobs_router)


@app.get("/")
def root() -> dict:
    return {
        "message": "Prosperas Async Reports API",
        "environment": settings.app_env,
    }


@app.get("/health")
def health() -> dict:
    """Endpoint simple de salud para validar que la API esta viva."""
    return {"status": "ok", "service": "backend"}
