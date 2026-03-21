#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-/tmp/prosperas}"
TARGET_DIR="${2:-/opt/prosperas}"

if [[ ! -f "${SOURCE_DIR}/docker-compose.prod.yml" ]]; then
  echo "Falta docker-compose.prod.yml en ${SOURCE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${SOURCE_DIR}/.env.production" ]]; then
  echo "Falta .env.production en ${SOURCE_DIR}" >&2
  exit 1
fi

sudo mkdir -p "${TARGET_DIR}"
sudo cp "${SOURCE_DIR}/docker-compose.prod.yml" "${TARGET_DIR}/docker-compose.prod.yml"
sudo cp "${SOURCE_DIR}/.env.production" "${TARGET_DIR}/.env.production"

sudo chown -R ec2-user:ec2-user "${TARGET_DIR}"

cd "${TARGET_DIR}"
docker compose --env-file .env.production pull
docker compose --env-file .env.production up -d --remove-orphans

echo "Esperando healthcheck de backend..."
for _ in {1..20}; do
  if curl -fsS http://localhost:8000/health >/dev/null; then
    echo "Deploy OK"
    exit 0
  fi
  sleep 3
done

echo "El backend no quedo saludable despues del deploy" >&2
docker compose --env-file .env.production ps
exit 1
