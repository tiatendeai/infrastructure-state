#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
REMOTE_HOST="${RUPTUR_REMOTE_HOST:-hostinger-kvm2}"
REMOTE_DIR="${RUPTUR_REDIS_REMOTE_DIR:-/opt/ruptur/runtime/redis}"
REMOTE_ENV="$REMOTE_DIR/.env"
REMOTE_COMPOSE="$REMOTE_DIR/docker-compose.yml"
LOCAL_TEMPLATE="$ROOT_DIR/adapters/ruptur-forge/templates/runtime/redis.compose.yml"
REDIS_PORT="${REDIS_PUBLISHED_PORT:-6380}"

ssh "$REMOTE_HOST" "mkdir -p '$REMOTE_DIR'"
scp "$LOCAL_TEMPLATE" "$REMOTE_HOST:$REMOTE_COMPOSE" >/dev/null
ssh "$REMOTE_HOST" "if [ ! -f '$REMOTE_ENV' ]; then umask 077; cat > '$REMOTE_ENV' <<EOF
REDIS_PASSWORD=\$(openssl rand -hex 24)
REDIS_PUBLISHED_PORT=$REDIS_PORT
EOF
fi
sudo ufw allow ${REDIS_PORT}/tcp >/dev/null 2>&1 || true
cd '$REMOTE_DIR'
docker compose --env-file '$REMOTE_ENV' up -d
docker compose --env-file '$REMOTE_ENV' ps"
