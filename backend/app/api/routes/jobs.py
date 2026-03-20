from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import get_current_user
from app.models.auth import UserContext
from app.schemas.job import JobCreateRequest, JobCreateResponse, JobDetailResponse, JobsListResponse
from app.services.job_service import JobService, get_job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> JobCreateResponse:
    """Crea un job, lo persiste en DynamoDB y lo publica en SQS.

    La respuesta es inmediata para cumplir el requerimiento asincrono del reto:
    el usuario obtiene job_id y estado PENDING sin esperar el procesamiento.
    """
    return job_service.create_job(user_id=current_user.user_id, payload=payload)


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: str,
    current_user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> JobDetailResponse:
    """Consulta el estado actual de un job del usuario autenticado."""
    return job_service.get_job_for_user(job_id=job_id, user_id=current_user.user_id)


@router.get("", response_model=JobsListResponse)
def list_jobs(
    page_size: int = Query(default=20, ge=20, le=100),
    cursor: str | None = Query(default=None),
    current_user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> JobsListResponse:
    """Lista jobs del usuario autenticado con paginacion basada en cursor."""
    return job_service.list_jobs_for_user(
        user_id=current_user.user_id,
        page_size=page_size,
        cursor=cursor,
    )
