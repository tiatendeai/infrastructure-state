# Runbook — GCP `ruptur-shipyard-01` com Ollama + `qwen3:4b`

**Data:** 2026-04-21  
**Alvo:** `ruptur-shipyard-01` (`34.39.196.137`)  
**Objetivo:** consolidar o runtime local de LLM no GCP e reconciliar `AIOX` + `Jarvis`.

## Entregas executadas

1. **Ollama instalado no host**
   - versão validada: `0.21.0`
   - serviço ativo via `systemd`

2. **Modelo local baixado**
   - modelo: `qwen3:4b`
   - capabilities observadas: `completion`, `tools`, `thinking`

3. **Exposição do Ollama ajustada para o bridge Docker**
   - override aplicado em `ollama.service`
   - `OLLAMA_HOST=0.0.0.0:11434`
   - acesso validado de dentro do container `ruptur-aiox` via `host.docker.internal`

4. **AIOX reconciliado para `qwen3:4b`**
   - compose do GCP materializado com:
     - `AIOX_MODEL_PROFILE=qwen`
     - `AIOX_MODEL=qwen3:4b`
     - `HERMES_MODEL=qwen3:4b`
   - endpoint local validado:
     - `POST http://127.0.0.1:3211/api/hermes/chat`
   - `health` final:
     - `hermes.status = ok`

5. **Jarvis corrigido para o ADK atual**
   - `main.py` atualizado para `get_fast_api_app(agents_dir=..., web=False)`
   - `agent.py` atualizado para usar `LiteLlm(model="ollama_chat/qwen3:4b")`
   - dependência `litellm` instalada no venv
   - override aplicado em `jarvis-agent.service`:
     - `JARVIS_MODEL=ollama_chat/qwen3:4b`
     - `OLLAMA_API_BASE=http://127.0.0.1:11434`
     - `ADK_DISABLE_LOCAL_STORAGE=1`

## Validações finais

- `systemctl is-active ollama` → `active`
- `curl http://127.0.0.1:11434/api/tags` → modelo presente
- `curl http://127.0.0.1:3211/health` → `ok`
- `curl http://127.0.0.1:5000/health` → `{"status":"ok"}`
- `curl http://127.0.0.1:5000/version` → ADK online
- `curl http://127.0.0.1:5000/apps/agent/app-info` → app `agent` carregado com `rootAgentName=jarvis`

## Observações operacionais

- O host usa **CPU only**, sem GPU.
- O runtime do Jarvis ficou com **sessão em memória** porque o Python do host não possui `_sqlite3`.
- Para esse host, o caminho seguro foi **desabilitar local storage do ADK** com `ADK_DISABLE_LOCAL_STORAGE=1`.

## Próximo passo sugerido

1. substituir o Python atual do Jarvis por um build com `sqlite3` habilitado **ou**
2. ligar o ADK a um backend de sessão persistente explícito.
