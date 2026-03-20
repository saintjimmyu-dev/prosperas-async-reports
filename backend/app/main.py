from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

allowed_origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
