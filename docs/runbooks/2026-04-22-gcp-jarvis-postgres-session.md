# GCP `ruptur-shipyard-01` — Jarvis ADK com sessão persistente em Postgres

Data: 2026-04-22  
Host: `ruptur-shipyard-01` (`34.39.196.137`)

## Objetivo

Remover o modo de sessão em memória do `jarvis-agent.service` e colocar o ADK para persistir sessões em Postgres.

## Decisão

- **Sessão do ADK:** Postgres dedicado
- **Modelo local:** `ollama` com `qwen3:4b`
- **Serviço do Jarvis:** `systemd`
- **Redis:** permanece disponível para usos futuros de cache/filas, mas **não** é o backend nativo de sessão do ADK neste runtime

## Runtime aplicado no host

### Banco dedicado do Jarvis

- Compose: `/opt/ruptur/runtime/jarvis-postgres/docker-compose.yml`
- Env file: `/opt/ruptur/runtime/jarvis-postgres/.env`
- Porta local: `127.0.0.1:5433`
- Container: `jarvis-postgres`

### Jarvis

- Unit: `/etc/systemd/system/jarvis-agent.service`
- Override: `/etc/systemd/system/jarvis-agent.service.d/override.conf`
- Variáveis relevantes:
  - `JARVIS_MODEL=ollama_chat/qwen3:4b`
  - `OLLAMA_API_BASE=http://127.0.0.1:11434`
  - `JARVIS_SESSION_SERVICE_URI=postgresql+asyncpg://...@127.0.0.1:5433/jarvis_adk`

### Código ajustado

- Entrypoint: `/opt/ruptur/jarvis-v1/apps/jarvis/agent/main.py`
- O app do ADK passa `session_service_uri` para `get_fast_api_app(...)`

## Dependências adicionais

- Driver Python instalado no venv do Jarvis:
  - `asyncpg`

## Validação executada

1. `jarvis-postgres` subiu saudável
2. `jarvis-agent.service` subiu saudável
3. Tabelas do ADK criadas no Postgres:
   - `sessions`
   - `events`
   - `app_states`
   - `user_states`
   - `adk_internal_metadata`
4. Sessão smoke criada via API
5. `jarvis-agent.service` reiniciado
6. A mesma sessão continuou existindo após o restart

## Checks operacionais

```bash
ssh -i ~/.ssh/google_compute_engine diego@34.39.196.137

systemctl status jarvis-agent
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/version
curl http://127.0.0.1:5000/list-apps

sudo docker ps --filter name=jarvis-postgres
ss -tulpn | grep 5433
```

## Canonização no Shipyard

Arquivos locais adicionados/atualizados para reproduzir esse estado:

- `adapters/provisioning/ansible/playbooks/jarvis_gcp.yml`
- `adapters/provisioning/ansible/roles/jarvis/`
- `adapters/provisioning/ansible/inventories/production/group_vars/all.yml`
- `adapters/provisioning/ansible/examples/production/secrets.example.yml`

Execução prevista:

```bash
cd adapters/provisioning/ansible
ansible-playbook -i inventories/production/hosts.yml playbooks/jarvis_gcp.yml
```

## Observação operacional

O `ADK_DISABLE_LOCAL_STORAGE=1` foi removido do override do Jarvis.  
Agora a persistência de sessão depende do Postgres dedicado local ao host.
