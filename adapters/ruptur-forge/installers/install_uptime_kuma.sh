#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
REMOTE_HOST="${RUPTUR_REMOTE_HOST:-hostinger-kvm2}"
REMOTE_DIR="${RUPTUR_UPTIME_KUMA_REMOTE_DIR:-/opt/ruptur/runtime/uptime-kuma}"
REMOTE_ENV="$REMOTE_DIR/.env"
REMOTE_COMPOSE="$REMOTE_DIR/docker-compose.yml"
LOCAL_TEMPLATE="$ROOT_DIR/adapters/ruptur-forge/templates/runtime/uptime-kuma.compose.yml"
PUBLIC_HOST="${UPTIME_KUMA_PUBLIC_HOST:-uptime-kuma.ruptur.cloud}"

ssh "$REMOTE_HOST" "mkdir -p '$REMOTE_DIR'"
scp "$LOCAL_TEMPLATE" "$REMOTE_HOST:$REMOTE_COMPOSE" >/dev/null
ssh "$REMOTE_HOST" "if [ ! -f '$REMOTE_ENV' ]; then
umask 077
cat > '$REMOTE_ENV' <<EOF
UPTIME_KUMA_PUBLIC_HOST=$PUBLIC_HOST
UPTIME_KUMA_PORT=3001
EOF
fi
docker network inspect kvm2_default >/dev/null 2>&1 || docker network create kvm2_default
cd '$REMOTE_DIR'
docker compose --env-file '$REMOTE_ENV' up -d
docker compose --env-file '$REMOTE_ENV' ps"
