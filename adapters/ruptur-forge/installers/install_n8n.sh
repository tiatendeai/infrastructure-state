#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
REMOTE_HOST="${RUPTUR_REMOTE_HOST:-hostinger-kvm2}"
REMOTE_DIR="${RUPTUR_N8N_REMOTE_DIR:-/opt/ruptur/runtime/n8n}"
REMOTE_ENV="$REMOTE_DIR/.env"
REMOTE_COMPOSE="$REMOTE_DIR/docker-compose.yml"
LOCAL_TEMPLATE="$ROOT_DIR/adapters/ruptur-forge/templates/runtime/n8n.compose.yml"

ssh "$REMOTE_HOST" "mkdir -p '$REMOTE_DIR'"
scp "$LOCAL_TEMPLATE" "$REMOTE_HOST:$REMOTE_COMPOSE" >/dev/null
ssh "$REMOTE_HOST" "if [ ! -f '$REMOTE_ENV' ]; then umask 077; cat > '$REMOTE_ENV' <<EOF
N8N_HOST=n8n.ruptur.cloud
N8N_PROTOCOL=https
N8N_PORT=5678
WEBHOOK_URL=https://n8n.ruptur.cloud/
N8N_EDITOR_BASE_URL=https://n8n.ruptur.cloud/
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=ruptur
N8N_BASIC_AUTH_PASSWORD=\$(openssl rand -base64 24 | tr -d '\n')
N8N_ENCRYPTION_KEY=\$(openssl rand -hex 24)
N8N_SECURE_COOKIE=true
GENERIC_TIMEZONE=America/Sao_Paulo
TZ=America/Sao_Paulo
EOF
fi
docker network inspect kvm2_default >/dev/null 2>&1 || docker network create kvm2_default
cd '$REMOTE_DIR'
docker compose --env-file '$REMOTE_ENV' up -d
docker compose --env-file '$REMOTE_ENV' ps"
