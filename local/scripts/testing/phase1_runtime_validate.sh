#!/bin/bash
set -euo pipefail

# Ejecuta la validacion completa de Fase 1 en una sola sesion WSL.
# Esto evita que Docker pierda estado entre llamadas separadas.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCAL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$LOCAL_DIR"

systemctl start docker >/dev/null 2>&1 || true

echo "[runtime] Levantando servicios con docker compose..."
docker compose up --build -d

echo "[runtime] Esperando health de LocalStack..."
for _ in $(seq 1 60); do
  status="$(docker inspect -f '{{.State.Health.Status}}' prosperas-localstack 2>/dev/null || echo starting)"
  if [ "$status" = "healthy" ]; then
    break
  fi
  sleep 2
done

if [ "${status:-starting}" != "healthy" ]; then
  echo "[runtime][error] LocalStack no llego a estado healthy"
  docker compose logs --no-color localstack | tail -50 || true
  exit 1
fi

echo "[runtime] Esperando health del backend..."
for _ in $(seq 1 40); do
  if curl -fsS http://localhost:8000/health >/tmp/prosperas_health.json; then
    break
  fi
  sleep 1
done

if ! test -s /tmp/prosperas_health.json; then
  echo "[runtime][error] Backend no responde en /health"
  docker compose logs --no-color backend | tail -80 || true
  exit 1
fi

echo "[runtime] health=$(cat /tmp/prosperas_health.json)"

echo "[runtime] Esperando recursos inicializados en LocalStack (DynamoDB/SQS)..."
resources_ready=0
for _ in $(seq 1 60); do
  if docker compose exec -T localstack awslocal dynamodb describe-table --table-name prosperas-jobs >/dev/null 2>&1 \
    && docker compose exec -T localstack awslocal sqs get-queue-url --queue-name prosperas-jobs-queue >/dev/null 2>&1 \
    && docker compose exec -T localstack awslocal sqs get-queue-url --queue-name prosperas-jobs-priority-queue >/dev/null 2>&1 \
    && docker compose exec -T localstack awslocal sqs get-queue-url --queue-name prosperas-jobs-dlq >/dev/null 2>&1; then
    resources_ready=1
    break
  fi
  sleep 2
done

if [ "$resources_ready" -ne 1 ]; then
  echo "[runtime][error] Recursos AWS locales no listos (tabla o colas no disponibles)"
  docker compose logs --no-color localstack | tail -120 || true
  exit 1
fi

LOGIN_JSON='{"username":"demo","password":"demo123"}'
TOKEN="$(curl -fsS -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' -d "$LOGIN_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')"

echo "[runtime] token_len=${#TOKEN}"

CREATE_JSON='{"report_type":"ventas_diarias","date_range":{"start_date":"2026-03-01","end_date":"2026-03-10"},"format":"pdf"}'
if ! CREATE_RESP="$(curl -fsS -X POST http://localhost:8000/jobs -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$CREATE_JSON")"; then
  echo "[runtime][error] Fallo POST /jobs"
  docker compose logs --no-color backend | tail -120 || true
  docker compose logs --no-color localstack | tail -120 || true
  exit 1
fi
JOB_ID="$(printf '%s' "$CREATE_RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')"

DETAIL_RESP="$(curl -fsS -H "Authorization: Bearer $TOKEN" "http://localhost:8000/jobs/$JOB_ID")"
LIST_RESP="$(curl -fsS -H "Authorization: Bearer $TOKEN" 'http://localhost:8000/jobs?page_size=20')"

echo "[runtime] create=$CREATE_RESP"
echo "[runtime] detail=$DETAIL_RESP"
echo "[runtime] list=$LIST_RESP"

echo "[runtime] Estado final de contenedores:"
docker compose ps

echo "[runtime] Validacion Fase 1 completada correctamente"
