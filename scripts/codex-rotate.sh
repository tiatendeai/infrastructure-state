#!/usr/bin/env bash
# ============================================================
# codex-rotate.sh — Rotação de contas OpenAI / Codex CLI
# Uso: codex-rotate.sh [login|logout|rotate|status|add-key]
# ============================================================
set -euo pipefail

ACCOUNTS_DIR="$HOME/.codex/accounts"
AUTH_FILE="$HOME/.codex/auth.json"
ENV_FILE="$(dirname "$(dirname "$(realpath "$0")")")/../../ruptur-lab-main/apps/jarvis/hitl-panel/.env.local"
LOG_FILE="$HOME/.codex/rotation.log"
ACTIVE_FILE="$HOME/.codex/active_account.json"

mkdir -p "$ACCOUNTS_DIR"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"; }

# Testa se uma key API tem quota (retorna 0=ok, 1=sem quota)
test_api_key() {
  local key="$1"
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 \
    -H "Authorization: Bearer $key" \
    -H "Content-Type: application/json" \
    -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"1"}],"max_tokens":1}' \
    https://api.openai.com/v1/chat/completions)
  [[ "$status" == "200" ]] && return 0 || return 1
}

# Ativa uma conta por nome de arquivo
activate_account() {
  local account_file="$1"
  local name type

  name=$(python3 -c "import json,sys; d=json.load(open('$account_file')); print(d.get('name','?'))")
  type=$(python3 -c "import json,sys; d=json.load(open('$account_file')); print(d.get('type','api_key'))")

  if [[ "$type" == "api_key" ]]; then
    local key
    key=$(python3 -c "import json,sys; d=json.load(open('$account_file')); print(d.get('key',''))")
    # Atualiza .env.local
    if [[ -f "$ENV_FILE" ]]; then
      sed -i.bak "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$key|" "$ENV_FILE"
    fi
    # Atualiza auth.json para modo api_key
    python3 -c "
import json
auth = {'auth_mode': 'api_key', 'OPENAI_API_KEY': '$key', 'tokens': None}
with open('$AUTH_FILE', 'w') as f:
    json.dump(auth, f, indent=2)
"
  elif [[ "$type" == "chatgpt" ]]; then
    # Copia o auth.json completo do account para o ativo
    python3 -c "
import json
d = json.load(open('$account_file'))
auth = d.get('auth', {})
with open('$AUTH_FILE', 'w') as f:
    json.dump(auth, f, indent=2)
"
    # Atualiza .env.local para remover api_key (modo chatgpt)
    if [[ -f "$ENV_FILE" ]]; then
      sed -i.bak "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=|" "$ENV_FILE"
    fi
  fi

  cp "$account_file" "$ACTIVE_FILE"
  log "✅ ATIVADO: $name ($type) — arquivo: $(basename "$account_file")"
  echo "$name"
}

# COMANDO: status — mostra conta ativa e quota de todas
cmd_status() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  📋 STATUS DAS CONTAS OPENAI/CODEX"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  local active_name="(nenhuma)"
  if [[ -f "$ACTIVE_FILE" ]]; then
    active_name=$(python3 -c "import json; print(json.load(open('$ACTIVE_FILE')).get('name','?'))")
  fi
  echo "  Conta ativa: $active_name"
  echo ""

  local count=0
  for f in "$ACCOUNTS_DIR"/*.json; do
    [[ -f "$f" ]] || { echo "  ⚠️  Nenhuma conta cadastrada em $ACCOUNTS_DIR"; break; }
    count=$((count + 1))
    local name type key status_str
    name=$(python3 -c "import json; print(json.load(open('$f')).get('name','?'))")
    type=$(python3 -c "import json; print(json.load(open('$f')).get('type','api_key'))")

    if [[ "$type" == "api_key" ]]; then
      key=$(python3 -c "import json; print(json.load(open('$f')).get('key',''))")
      if test_api_key "$key"; then
        status_str="✅ COM CRÉDITO"
      else
        status_str="❌ SEM CRÉDITO (429)"
      fi
    else
      status_str="🌐 ChatGPT Session (não testável via curl)"
    fi

    echo "  [$count] $name ($type) — $status_str"
  done
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# COMANDO: rotate — encontra e ativa a primeira conta com crédito
cmd_rotate() {
  log "🔄 Iniciando rotação automática de contas..."
  local found=0

  for f in "$ACCOUNTS_DIR"/*.json; do
    [[ -f "$f" ]] || continue
    local name type key
    name=$(python3 -c "import json; print(json.load(open('$f')).get('name','?'))")
    type=$(python3 -c "import json; print(json.load(open('$f')).get('type','api_key'))")

    if [[ "$type" == "api_key" ]]; then
      key=$(python3 -c "import json; print(json.load(open('$f')).get('key',''))")
      log "🧪 Testando: $name..."
      if test_api_key "$key"; then
        activate_account "$f"
        found=1
        break
      else
        log "⚠️  $name sem quota — pulando"
      fi
    elif [[ "$type" == "chatgpt" ]]; then
      # ChatGPT sessions: ativa sem testar (CLI cuida do refresh)
      log "🌐 $name (chatgpt session) — ativando..."
      activate_account "$f"
      found=1
      break
    fi
  done

  if [[ $found -eq 0 ]]; then
    log "❌ TODAS AS CONTAS SEM QUOTA. Adicione créditos ou cadastre nova conta."
    echo "❌ Nenhuma conta disponível."
    exit 1
  fi
}

# COMANDO: logout — desativa conta atual sem ativar outra
cmd_logout() {
  local active_name="nenhuma"
  if [[ -f "$ACTIVE_FILE" ]]; then
    active_name=$(python3 -c "import json; print(json.load(open('$ACTIVE_FILE')).get('name','?'))")
  fi
  # Limpa auth.json
  echo '{"auth_mode": null, "OPENAI_API_KEY": null, "tokens": null}' > "$AUTH_FILE"
  rm -f "$ACTIVE_FILE"
  # Limpa .env.local
  if [[ -f "$ENV_FILE" ]]; then
    sed -i.bak "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=|" "$ENV_FILE"
  fi
  log "🚪 DESLOGADO: $active_name"
  echo "🚪 Conta '$active_name' deslogada."
}

# COMANDO: login <nome-da-conta> — ativa conta específica por nome
cmd_login() {
  local target="${1:-}"
  if [[ -z "$target" ]]; then
    echo "Uso: codex-rotate.sh login <nome-da-conta>"
    exit 1
  fi
  for f in "$ACCOUNTS_DIR"/*.json; do
    [[ -f "$f" ]] || continue
    local name
    name=$(python3 -c "import json; print(json.load(open('$f')).get('name',''))")
    if [[ "$name" == "$target" ]]; then
      activate_account "$f"
      return 0
    fi
  done
  echo "❌ Conta '$target' não encontrada em $ACCOUNTS_DIR"
  exit 1
}

# COMANDO: add-key <nome> <sk-...> — cadastra nova conta API key
cmd_add_key() {
  local name="${1:-}"
  local key="${2:-}"
  if [[ -z "$name" || -z "$key" ]]; then
    echo "Uso: codex-rotate.sh add-key <nome> <sk-...>"
    exit 1
  fi
  local slug
  slug=$(echo "$name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
  local out="$ACCOUNTS_DIR/${slug}.json"
  python3 -c "
import json
data = {'name': '$name', 'type': 'api_key', 'key': '$key'}
with open('$out', 'w') as f:
    json.dump(data, f, indent=2)
"
  log "➕ Conta cadastrada: $name → $out"
  echo "✅ Conta '$name' cadastrada."
}

# COMANDO: add-chatgpt <nome> — importa sessão atual do auth.json como nova conta
cmd_add_chatgpt() {
  local name="${1:-}"
  if [[ -z "$name" ]]; then
    echo "Uso: codex-rotate.sh add-chatgpt <nome>"
    exit 1
  fi
  local slug
  slug=$(echo "$name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
  local out="$ACCOUNTS_DIR/${slug}.json"
  python3 -c "
import json
auth = json.load(open('$AUTH_FILE'))
data = {'name': '$name', 'type': 'chatgpt', 'auth': auth}
with open('$out', 'w') as f:
    json.dump(data, f, indent=2)
"
  log "➕ Sessão ChatGPT cadastrada: $name → $out"
  echo "✅ Sessão '$name' cadastrada a partir do auth.json atual."
}

# Router principal
CMD="${1:-status}"
shift || true

case "$CMD" in
  status)        cmd_status ;;
  rotate)        cmd_rotate ;;
  logout)        cmd_logout ;;
  login)         cmd_login "$@" ;;
  add-key)       cmd_add_key "$@" ;;
  add-chatgpt)   cmd_add_chatgpt "$@" ;;
  *)
    echo "Comandos: status | rotate | logout | login <nome> | add-key <nome> <sk-...> | add-chatgpt <nome>"
    exit 1
    ;;
esac
