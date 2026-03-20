#!/bin/bash
set -euo pipefail

# Valida Fase 3: frontend React, disponibilidad HTTP y comunicacion con backend.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCAL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$LOCAL_DIR"

systemctl start docker >/dev/null 2>&1 || true

echo "[runtime-f3] Levantando servicios con docker compose..."
docker compose up --build -d

echo "[runtime-f3] Esperando health de LocalStack..."
for _ in $(seq 1 60); do
  status="$(docker inspect -f '{{.State.Health.Status}}' prosperas-localstack 2>/dev/null || echo starting)"
  if [ "$status" = "healthy" ]; then
    break
  fi
  sleep 2
done

if [ "${status:-starting}" != "healthy" ]; then
  echo "[runtime-f3][error] LocalStack no llego a estado healthy"
  docker compose logs --no-color localstack | tail -120 || true
  exit 1
fi

echo "[runtime-f3] Esperando backend..."
for _ in $(seq 1 40); do
  if curl -fsS http://localhost:8000/health >/tmp/prosperas_f3_backend_health.json; then
    break
  fi
  sleep 1
done

if ! test -s /tmp/prosperas_f3_backend_health.json; then
  echo "[runtime-f3][error] Backend no responde en /health"
  docker compose logs --no-color backend | tail -120 || true
  exit 1
fi

echo "[runtime-f3] Esperando frontend..."
for _ in $(seq 1 40); do
  if curl -fsS http://localhost:5173 >/tmp/prosperas_f3_frontend.html; then
    break
  fi
  sleep 1
done

if ! test -s /tmp/prosperas_f3_frontend.html; then
  echo "[runtime-f3][error] Frontend no responde en http://localhost:5173"
  docker compose logs --no-color frontend | tail -120 || true
  exit 1
fi

if ! grep -F "Prosperas Control Desk" /tmp/prosperas_f3_frontend.html >/dev/null; then
  echo "[runtime-f3][error] El frontend no expuso el shell HTML esperado"
  exit 1
fi

echo "[runtime-f3] Validando CORS entre frontend y backend..."
CORS_HEADERS="$(curl -is -X OPTIONS http://localhost:8000/auth/login -H 'Origin: http://localhost:5173' -H 'Access-Control-Request-Method: POST')"
if ! printf '%s' "$CORS_HEADERS" | grep -Fi 'access-control-allow-origin: http://localhost:5173' >/dev/null; then
  echo "[runtime-f3][error] Backend no habilito CORS para el frontend local"
  exit 1
fi

echo "[runtime-f3] Ejecutando build del frontend..."
docker compose exec -T frontend npm run build >/tmp/prosperas_f3_build.log

echo "[runtime-f3] Probando login API desde el flujo de UI..."
TOKEN="$(curl -fsS -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' -d '{"username":"demo","password":"demo123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')"
if [ -z "$TOKEN" ]; then
  echo "[runtime-f3][error] No se obtuvo JWT para el usuario demo"
  exit 1
fi

echo "[runtime-f3] Creando job para validar integracion del panel..."
CREATE_RESP="$(curl -fsS -X POST http://localhost:8000/jobs -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"report_type":"ventas_ui","date_range":{"start_date":"2026-03-01","end_date":"2026-03-10"},"format":"pdf"}')"
JOB_ID="$(printf '%s' "$CREATE_RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')"
if [ -z "$JOB_ID" ]; then
  echo "[runtime-f3][error] No se pudo crear el job de validacion de UI"
  exit 1
fi

echo "[runtime-f3] job_ui=$JOB_ID"

echo "[runtime-f3] Estado final de contenedores:"
docker compose ps

echo "[runtime-f3] Validacion Fase 3 completada correctamente"
