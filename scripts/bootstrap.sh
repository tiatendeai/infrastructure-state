#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

write_default_state() {
  cat > kernel/state.json <<'STATE'
{
  "status": "idle",
  "current_task": null,
  "history": [],
  "version": 1
}
STATE
}

ensure_runtime_layout() {
  mkdir -p kernel state registry/runs tasks logs state/snapshots .agents/runtime
  [ -f registry/runs/.gitkeep ] || : > registry/runs/.gitkeep
  [ -f state/snapshots/.gitkeep ] || : > state/snapshots/.gitkeep
  [ -f .agents/runtime/.gitkeep ] || : > .agents/runtime/.gitkeep
  [ -f logs/execution.log ] || : > logs/execution.log
}

echo "Inicializando projeto Ruptur..."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Arquivo .env criado a partir de .env.example"
else
  echo "Arquivo .env já existe; mantendo configuração atual"
fi

ensure_runtime_layout

if [ ! -f kernel/state.json ]; then
  write_default_state
fi

echo "Projeto pronto."
