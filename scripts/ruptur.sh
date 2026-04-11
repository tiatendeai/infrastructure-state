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
  mkdir -p registry/runs state/snapshots state/runtime logs tasks state kernel contexts
  [ -f registry/runs/.gitkeep ] || : > registry/runs/.gitkeep
  [ -f state/snapshots/.gitkeep ] || : > state/snapshots/.gitkeep
  [ -f state/runtime/.gitkeep ] || : > state/runtime/.gitkeep
  [ -f logs/execution.log ] || : > logs/execution.log
}

load_env_file() {
  local env_path="$1"

  if [ -f "$env_path" ]; then
    while IFS= read -r raw_line || [ -n "$raw_line" ]; do
      local line key value first_char last_char
      line="${raw_line%$'\r'}"
      line="${line#"${line%%[![:space:]]*}"}"
      line="${line%"${line##*[![:space:]]}"}"

      [ -z "$line" ] && continue
      case "$line" in
        \#*) continue
          ;;
      esac
      case "$line" in
        *=*) ;;
        *) continue
          ;;
      esac

      IFS='=' read -r key value <<< "$line"
      key="${key#"${key%%[![:space:]]*}"}"
      key="${key%"${key##*[![:space:]]}"}"
      value="${value#"${value%%[![:space:]]*}"}"
      value="${value%"${value##*[![:space:]]}"}"

      if [ "${#value}" -ge 2 ]; then
        first_char="${value:0:1}"
        last_char="${value: -1}"
        if { [ "$first_char" = '"' ] || [ "$first_char" = "'" ]; } && [ "$first_char" = "$last_char" ]; then
          value="${value:1:${#value}-2}"
        fi
      fi

      [ -n "$key" ] && export "$key=$value"
    done < "$env_path"
  fi
}

load_env() {
  load_env_file .env
  load_env_file .env.local
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

  for dir in contracts docs templates tasks registry/runs state/snapshots state/runtime scripts examples adapters contexts logs; do
    if [ -d "$dir" ]; then
      echo "OK: $dir"
    else
      error "diretório obrigatório ausente: $dir"
      has_error=1
    fi
  done

  if python3 scripts/validate_contract.py kernel/state.json contracts/state.schema.json >/dev/null 2>&1; then
    echo "OK: kernel/state.json compatível com contracts/state.schema.json"
  else
    error "kernel/state.json incompatível com contracts/state.schema.json"
    has_error=1
  fi

  if python3 scripts/run_task.py --validate-only examples/hello.task.json >/dev/null 2>&1; then
    echo "OK: examples/hello.task.json"
  else
    error "example task inválida: examples/hello.task.json"
    has_error=1
  fi

  return "$has_error"
}

clean_command() {
  rm -rf state/snapshots state/runtime
  mkdir -p state/snapshots state/runtime
  : > state/snapshots/.gitkeep
  : > state/runtime/.gitkeep
  echo "Runtime efêmero limpo com segurança."
}

reset_command() {
  rm -rf registry/runs state/snapshots state/runtime
  mkdir -p registry/runs state/snapshots state/runtime logs kernel
  : > registry/runs/.gitkeep
  : > state/snapshots/.gitkeep
  : > state/runtime/.gitkeep
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
