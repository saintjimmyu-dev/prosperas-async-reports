#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-/tmp/prosperas}"
TARGET_DIR="${2:-/opt/prosperas}"

ensure_docker_runtime() {
  if command -v docker >/dev/null 2>&1; then
    return 0
  fi

  echo "Docker no esta instalado. Instalando runtime en la instancia..."
  sudo dnf install -y docker
  sudo systemctl enable --now docker
}

ensure_compose_runtime() {
  if docker compose version >/dev/null 2>&1; then
    return 0
  fi

  if command -v docker-compose >/dev/null 2>&1; then
    return 0
  fi

  echo "Docker Compose no esta instalado. Instalando plugin oficial..."
  sudo mkdir -p /usr/local/lib/docker/cli-plugins
  sudo curl -fSL https://github.com/docker/compose/releases/download/v2.39.4/docker-compose-linux-x86_64 \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
}

ensure_docker_runtime
ensure_compose_runtime

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "Docker Compose no esta instalado en la instancia" >&2
  exit 1
fi

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
"${COMPOSE_CMD[@]}" --env-file .env.production pull
"${COMPOSE_CMD[@]}" --env-file .env.production up -d --remove-orphans

echo "Esperando healthcheck de backend..."
for _ in {1..20}; do
  if curl -fsS http://localhost:8000/health >/dev/null; then
    echo "Deploy OK"
    exit 0
  fi
  sleep 3
done

echo "El backend no quedo saludable despues del deploy" >&2
"${COMPOSE_CMD[@]}" --env-file .env.production ps
exit 1
