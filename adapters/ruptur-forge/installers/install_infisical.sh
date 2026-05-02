#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
REMOTE_HOST="${RUPTUR_REMOTE_HOST:-ruptur-shipyard-01}"
REMOTE_DIR="${RUPTUR_INFISICAL_REMOTE_DIR:-/opt/ruptur/runtime/infisical}"
REMOTE_ENV="$REMOTE_DIR/.env"
REMOTE_COMPOSE="$REMOTE_DIR/docker-compose.yml"
LOCAL_TEMPLATE="$ROOT_DIR/adapters/ruptur-forge/templates/runtime/infisical.compose.yml"
PUBLIC_HOST="${INFISICAL_PUBLIC_HOST:-infisical.ruptur.cloud}"
PUBLIC_URL="${INFISICAL_PUBLIC_URL:-https://${PUBLIC_HOST}}"

ssh "$REMOTE_HOST" "mkdir -p '$REMOTE_DIR'"
scp "$LOCAL_TEMPLATE" "$REMOTE_HOST:$REMOTE_COMPOSE" >/dev/null
ssh "$REMOTE_HOST" "if [ ! -f '$REMOTE_ENV' ]; then
umask 077
POSTGRES_PASSWORD=\$(openssl rand -hex 24)
AUTH_SECRET=\$(openssl rand -base64 32 | tr -d '\n')
ENCRYPTION_KEY=\$(openssl rand -hex 16)
cat > '$REMOTE_ENV' <<EOF
NODE_ENV=production
INFISICAL_PUBLIC_HOST=$PUBLIC_HOST
SITE_URL=$PUBLIC_URL
HTTPS_ENABLED=false
POSTGRES_USER=infisical
POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
POSTGRES_DB=infisical
DB_CONNECTION_URI=postgres://infisical:\${POSTGRES_PASSWORD}@db:5432/infisical
REDIS_URL=redis://redis:6379
AUTH_SECRET=\${AUTH_SECRET}
ENCRYPTION_KEY=\${ENCRYPTION_KEY}
EOF
fi
if [ -n \"\${SMTP_HOST:-}\" ] && [ -n \"\${SMTP_USERNAME:-}\" ] && [ -n \"\${SMTP_PASSWORD:-}\" ] && [ -n \"\${SMTP_FROM_ADDRESS:-}\" ]; then
cat >> '$REMOTE_ENV' <<EOF
SMTP_HOST=\${SMTP_HOST}
SMTP_PORT=\${SMTP_PORT:-587}
SMTP_USERNAME=\${SMTP_USERNAME}
SMTP_PASSWORD=\${SMTP_PASSWORD}
SMTP_FROM_ADDRESS=\${SMTP_FROM_ADDRESS}
SMTP_FROM_NAME=\${SMTP_FROM_NAME:-Infisical}
SMTP_REQUIRE_TLS=\${SMTP_REQUIRE_TLS:-true}
SMTP_TLS_REJECT_UNAUTHORIZED=\${SMTP_TLS_REJECT_UNAUTHORIZED:-true}
EOF
fi
docker network inspect ruptur-edge >/dev/null 2>&1 || docker network create ruptur-edge
cd '$REMOTE_DIR'
docker compose --env-file '$REMOTE_ENV' up -d
docker compose --env-file '$REMOTE_ENV' ps"
