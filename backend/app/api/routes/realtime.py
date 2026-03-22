import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.models.job import Job
from app.services.dynamodb_service import DynamoDBService

router = APIRouter(prefix="/ws", tags=["realtime"])


def _serialize_job(job: Job) -> dict:
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "report_type": job.report_type,
        "format": job.format,
        "date_range": {
            "start_date": job.date_range["start_date"],
            "end_date": job.date_range["end_date"],
        },
        "result_url": job.result_url,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


@router.websocket("/jobs")
async def jobs_stream(websocket: WebSocket) -> None:
    """Emite snapshots de jobs del usuario autenticado mediante WebSocket.

    El token JWT se envia como query param `token` para mantener el cliente web
    simple. Si el socket se interrumpe, el frontend debe volver al polling.
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return

    try:
        payload = decode_access_token(token)
        user_id = str(payload.get("sub", "")).strip()
        if not user_id:
            await websocket.close(code=4401)
            return
    except Exception:
        await websocket.close(code=4401)
        return

    settings = get_settings()
    dynamodb = DynamoDBService(settings=settings)
    await websocket.accept()

    interval_seconds = max(1, settings.realtime_stream_interval_seconds)
    previous_fingerprint: str | None = None

    try:
        while True:
            jobs, _ = dynamodb.list_jobs_by_user(user_id=user_id, page_size=20, cursor=None)
            payload = {
                "type": "jobs.snapshot",
                "sent_at": datetime.utcnow().isoformat(),
                "items": [_serialize_job(job) for job in jobs],
            }
            fingerprint = json.dumps(payload["items"], sort_keys=True)

            if fingerprint != previous_fingerprint:
                await websocket.send_json(payload)
                previous_fingerprint = fingerprint

            await asyncio.sleep(interval_seconds)
    except WebSocketDisconnect:
        return
    except Exception:
        try:
            await websocket.send_json(
                {
                    "type": "jobs.error",
                    "message": "No fue posible mantener el stream en tiempo real.",
                }
            )
        except Exception:
            pass
        try:
            await websocket.close(code=1011)
        except Exception:
            pass