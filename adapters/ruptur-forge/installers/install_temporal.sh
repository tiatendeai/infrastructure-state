#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
REMOTE_HOST="${RUPTUR_REMOTE_HOST:-hostinger-kvm2}"
REMOTE_DIR="${RUPTUR_TEMPORAL_REMOTE_DIR:-/opt/ruptur/runtime/temporal}"
REMOTE_ENV="$REMOTE_DIR/.env"
REMOTE_COMPOSE="$REMOTE_DIR/docker-compose.yml"
LOCAL_TEMPLATE="$ROOT_DIR/adapters/ruptur-forge/templates/runtime/temporal.compose.yml"
LOCAL_DYNAMICCONFIG="$ROOT_DIR/adapters/ruptur-forge/templates/runtime/temporal/dynamicconfig/development-sql.yaml"
PUBLIC_HOST="${TEMPORAL_PUBLIC_HOST:-temporal.ruptur.cloud}"
PUBLIC_URL="${TEMPORAL_PUBLIC_URL:-https://${PUBLIC_HOST}}"

ssh "$REMOTE_HOST" "mkdir -p '$REMOTE_DIR/dynamicconfig'"
scp "$LOCAL_TEMPLATE" "$REMOTE_HOST:$REMOTE_COMPOSE" >/dev/null
scp "$LOCAL_DYNAMICCONFIG" "$REMOTE_HOST:$REMOTE_DIR/dynamicconfig/development-sql.yaml" >/dev/null
ssh "$REMOTE_HOST" "if [ ! -f '$REMOTE_ENV' ]; then
umask 077
POSTGRES_PASSWORD=\$(openssl rand -hex 24)
cat > '$REMOTE_ENV' <<EOF
COMPOSE_PROJECT_NAME=temporal
TEMPORAL_VERSION=1.29.1
TEMPORAL_ADMINTOOLS_VERSION=1.29.1-tctl-1.18.4-cli-1.5.0
TEMPORAL_UI_VERSION=2.34.0
POSTGRESQL_VERSION=16
POSTGRES_USER=temporal
POSTGRES_DB=temporal
POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
TEMPORAL_PUBLIC_HOST=$PUBLIC_HOST
TEMPORAL_PUBLIC_URL=$PUBLIC_URL
TEMPORAL_CORS_ORIGINS=$PUBLIC_URL
EOF
fi
docker network inspect kvm2_default >/dev/null 2>&1 || docker network create kvm2_default
cd '$REMOTE_DIR'
docker compose --env-file '$REMOTE_ENV' up -d
docker compose --env-file '$REMOTE_ENV' ps"
