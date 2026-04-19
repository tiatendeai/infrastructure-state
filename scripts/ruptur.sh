#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<'EOF'
Uso:
  bash scripts/ruptur.sh help
  bash scripts/ruptur.sh init
  bash scripts/ruptur.sh run <task-file> [mode]
  bash scripts/ruptur.sh validate <task-file> [mode]
  bash scripts/ruptur.sh status
  bash scripts/ruptur.sh doctor
  bash scripts/ruptur.sh clean
  bash scripts/ruptur.sh reset

Comandos:
  help      Exibe esta ajuda.
  init      Inicializa o projeto e garante a estrutura base.
  run       Executa uma task.
  validate  Valida uma task sem executá-la.
  status    Exibe o estado canônico atual.
  doctor    Verifica pré-requisitos e estrutura essencial.
  clean     Limpa somente runtime efêmero.
  reset     Limpa runtime, logs, registry e reseta o state base.
EOF
}

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
  mkdir -p registry/runs state/snapshots .agents/runtime logs tasks state kernel
  [ -f registry/runs/.gitkeep ] || : > registry/runs/.gitkeep
  [ -f state/snapshots/.gitkeep ] || : > state/snapshots/.gitkeep
  [ -f .agents/runtime/.gitkeep ] || : > .agents/runtime/.gitkeep
  [ -f logs/execution.log ] || : > logs/execution.log
}

load_env() {
  if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.env
    set +a
  fi
}

error() {
  printf 'Erro: %s\n' "$*" >&2
}

run_task_command() {
  local task_file="${1:-examples/hello.task.json}"
  local mode="${2:-${RUPTUR_MODE:-}}"

  if [ -n "${mode:-}" ]; then
    python3 scripts/run_task.py "$task_file" "$mode"
  else
    python3 scripts/run_task.py "$task_file"
  fi
}

validate_task_command() {
  local task_file="${1:-examples/hello.task.json}"
  local mode="${2:-${RUPTUR_MODE:-}}"

  if [ -n "${mode:-}" ]; then
    python3 scripts/run_task.py --validate-only "$task_file" "$mode"
  else
    python3 scripts/run_task.py --validate-only "$task_file"
  fi
}

doctor_command() {
  local has_error=0

  if ! command -v python3 >/dev/null 2>&1; then
    error "python3 não encontrado no PATH"
    has_error=1
  else
    echo "OK: python3 disponível"
  fi

  for path in .env.example kernel/state.json contracts/task.schema.json contracts/state.schema.json; do
    if [ -e "$path" ]; then
      echo "OK: $path"
    else
      error "arquivo obrigatório ausente: $path"
      has_error=1
    fi
  done

  for dir in contracts docs templates tasks registry/runs state/snapshots scripts examples adapters logs .agents/runtime; do
    if [ -d "$dir" ]; then
      echo "OK: $dir"
    else
      error "diretório obrigatório ausente: $dir"
      has_error=1
    fi
  done

  return "$has_error"
}

clean_command() {
  rm -rf state/snapshots .agents/runtime
  mkdir -p state/snapshots .agents/runtime
  : > state/snapshots/.gitkeep
  : > .agents/runtime/.gitkeep
  echo "Runtime efêmero limpo com segurança."
}

reset_command() {
  rm -rf registry/runs state/snapshots .agents/runtime
  mkdir -p registry/runs state/snapshots .agents/runtime logs kernel
  : > registry/runs/.gitkeep
  : > state/snapshots/.gitkeep
  : > .agents/runtime/.gitkeep
  : > logs/execution.log
  write_default_state
  echo "Runtime, registry, logs e state foram resetados."
}

status_command() {
  if [ ! -f kernel/state.json ]; then
    error "kernel/state.json não encontrado. Rode 'bash scripts/ruptur.sh init'."
    return 1
  fi

  cat kernel/state.json
}

load_env
COMMAND="${1:-help}"

case "$COMMAND" in
  help|-h|--help)
    usage
    ;;
  init)
    bash scripts/bootstrap.sh
    ;;
  run)
    run_task_command "${2:-examples/hello.task.json}" "${3:-${RUPTUR_MODE:-}}"
    ;;
  validate)
    validate_task_command "${2:-examples/hello.task.json}" "${3:-${RUPTUR_MODE:-}}"
    ;;
  status)
    status_command
    ;;
  doctor)
    doctor_command
    ;;
  clean)
    ensure_runtime_layout
    clean_command
    ;;
  reset)
    reset_command
    ;;
  *)
    error "comando inválido: $COMMAND"
    usage >&2
    exit 1
    ;;
esac
