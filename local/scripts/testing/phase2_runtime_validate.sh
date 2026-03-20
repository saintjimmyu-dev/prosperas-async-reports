#!/bin/bash
set -euo pipefail

# Valida Fase 2: worker concurrente, procesamiento asincrono y transiciones de estado.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCAL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$LOCAL_DIR"

systemctl start docker >/dev/null 2>&1 || true

echo "[runtime-f2] Levantando servicios con docker compose..."
docker compose up --build -d

echo "[runtime-f2] Esperando health de LocalStack..."
for _ in $(seq 1 60); do
  status="$(docker inspect -f '{{.State.Health.Status}}' prosperas-localstack 2>/dev/null || echo starting)"
  if [ "$status" = "healthy" ]; then
    break
  fi
  sleep 2
done

if [ "${status:-starting}" != "healthy" ]; then
  echo "[runtime-f2][error] LocalStack no llego a estado healthy"
  docker compose logs --no-color localstack | tail -120 || true
  exit 1
fi

echo "[runtime-f2] Esperando health del backend..."
for _ in $(seq 1 40); do
  if curl -fsS http://localhost:8000/health >/tmp/prosperas_f2_health.json; then
    break
  fi
  sleep 1
done

if ! test -s /tmp/prosperas_f2_health.json; then
  echo "[runtime-f2][error] Backend no responde en /health"
  docker compose logs --no-color backend | tail -120 || true
  exit 1
fi

echo "[runtime-f2] health=$(cat /tmp/prosperas_f2_health.json)"

echo "[runtime-f2] Verificando que el worker este arriba..."
worker_status="$(docker inspect -f '{{.State.Status}}' prosperas-worker 2>/dev/null || echo missing)"
if [ "$worker_status" != "running" ]; then
  echo "[runtime-f2][error] Contenedor worker no esta corriendo"
  docker compose ps
  docker compose logs --no-color worker | tail -120 || true
  exit 1
fi

echo "[runtime-f2] Esperando recursos inicializados en LocalStack (DynamoDB/SQS)..."
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
  echo "[runtime-f2][error] Recursos AWS locales no listos"
  docker compose logs --no-color localstack | tail -120 || true
  exit 1
fi

LOGIN_JSON='{"username":"demo","password":"demo123"}'
TOKEN="$(curl -fsS -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' -d "$LOGIN_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')"

echo "[runtime-f2] token_len=${#TOKEN}"

CREATE_OK='{"report_type":"ventas_diarias","date_range":{"start_date":"2026-03-01","end_date":"2026-03-10"},"format":"pdf"}'
CREATE_PRIORITY='{"report_type":"priority_ventas","date_range":{"start_date":"2026-03-01","end_date":"2026-03-10"},"format":"pdf"}'
CREATE_FAIL='{"report_type":"fail_demo","date_range":{"start_date":"2026-03-01","end_date":"2026-03-10"},"format":"pdf"}'

OK_RESP="$(curl -fsS -X POST http://localhost:8000/jobs -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$CREATE_OK")"
PRIORITY_RESP="$(curl -fsS -X POST http://localhost:8000/jobs -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$CREATE_PRIORITY")"
FAIL_RESP="$(curl -fsS -X POST http://localhost:8000/jobs -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$CREATE_FAIL")"

OK_JOB_ID="$(printf '%s' "$OK_RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')"
PRIORITY_JOB_ID="$(printf '%s' "$PRIORITY_RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')"
FAIL_JOB_ID="$(printf '%s' "$FAIL_RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')"

echo "[runtime-f2] job_ok=$OK_JOB_ID"
echo "[runtime-f2] job_priority=$PRIORITY_JOB_ID"
echo "[runtime-f2] job_fail=$FAIL_JOB_ID"

wait_for_status() {
  local job_id="$1"
  local expected="$2"
  local seen=""

  for _ in $(seq 1 90); do
    resp="$(curl -fsS -H "Authorization: Bearer $TOKEN" "http://localhost:8000/jobs/$job_id")"
    status="$(printf '%s' "$resp" | python3 -c 'import sys,json; print(json.load(sys.stdin)["status"])')"
    if [[ ",$seen," != *",$status,"* ]]; then
      if [ -z "$seen" ]; then
        seen="$status"
      else
        seen="$seen,$status"
      fi
    fi

    if [ "$status" = "$expected" ]; then
      echo "[runtime-f2] job=$job_id estado_final=$status estados_vistos=$seen"
      return 0
    fi

    sleep 1
  done

  echo "[runtime-f2][error] job=$job_id no alcanzo estado esperado=$expected estados_vistos=$seen"
  return 1
}

wait_for_status "$OK_JOB_ID" "COMPLETED"
wait_for_status "$PRIORITY_JOB_ID" "COMPLETED"
wait_for_status "$FAIL_JOB_ID" "FAILED"

echo "[runtime-f2] Verificando evidencia de B1 (cola de prioridad) y B4 (backoff)..."
WORKER_LOGS="$(docker compose logs --no-color worker --tail 400 || true)"

if ! printf '%s' "$WORKER_LOGS" | grep -F "job=$PRIORITY_JOB_ID" | grep -F "cola=priority" >/dev/null; then
  echo "[runtime-f2][error] No se encontro evidencia de enrutamiento por cola de prioridad para job=$PRIORITY_JOB_ID"
  exit 1
fi

if ! printf '%s' "$WORKER_LOGS" | grep -F "job_id=$FAIL_JOB_ID" | grep -F "backoff=" >/dev/null; then
  echo "[runtime-f2][error] No se encontro evidencia de backoff exponencial para job=$FAIL_JOB_ID"
  exit 1
fi

echo "[runtime-f2] Verificando RedrivePolicy configurada..."
MAIN_URL="$(docker compose exec -T localstack awslocal sqs get-queue-url --queue-name prosperas-jobs-queue --output text --query QueueUrl)"
REDRIVE="$(docker compose exec -T localstack awslocal sqs get-queue-attributes --queue-url "$MAIN_URL" --attribute-names RedrivePolicy --output text --query Attributes.RedrivePolicy)"
if [ -z "$REDRIVE" ] || [ "$REDRIVE" = "None" ]; then
  echo "[runtime-f2][error] Cola principal sin RedrivePolicy"
  exit 1
fi

echo "[runtime-f2] redrive_policy=$REDRIVE"

echo "[runtime-f2] Estado final de contenedores:"
docker compose ps

echo "[runtime-f2] Validacion Fase 2 completada correctamente"
