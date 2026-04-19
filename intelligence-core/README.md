# J.A.R.V.I.S.

Casa operacional do J.A.R.V.I.S. em Node.js + TypeScript, com entrada via WhatsApp/UAZAPI, memória local em SQLite e governança conectada ao `state`.

## Governança

- **Casa local:** este repositório
- **Governança canônica:** `../state`
- **Contrato local com o state:** `.agents/maestro_ativo/state_linkage.yaml`
- **Capinhas internas:** `.agents/maestro_ativo/protocolos_mensagens_internas.yaml`
- **Fila de promoção para o state:** `.agents/maestro_ativo/state_outbox.md`
- **Spec de sinergia:** `specs/state-synergy.md`
- **Gate de release crítico:** `specs/protocolo-release-critico.md`
- **Decision OS da casa:** `specs/decision-os-v1.md`
- **Schema do contrato de demanda:** `specs/demand-contract.schema.json`

## Módulos laterais do Maestro

- `auto-research` — investigação paralela de gaps, falhas iterativas e melhorias estruturais
- `ecosystem-reviewer` — QA, smoke tests, backlog e bloqueio/liberação via `⌬ gate://jarvis`

Esses módulos vivem em `.agents/skills/` e complementam o loop principal sem travar a thread do Maestro.

## Runtime

- `npm start` — sobe o webhook
- `npm run dev` — modo desenvolvimento
- `npm run build` — compila TypeScript
- `npm run typecheck` — valida tipagem sem gerar artefatos
- `npm run ci` — valida typecheck + build

## Endpoints operacionais

- `POST /webhook` — entrada do WhatsApp/UAZAPI
- `GET /healthz` — healthcheck da casa
- `GET /readyz` — readiness básica de configuração
- `GET /statusz` — snapshot operacional rico
- `GET /metrics` — métricas em formato Prometheus

## Tools nativas do Jarvis

- `get_operational_status`
- `read_curated_context`
- `append_state_outbox_notice`

## CI

- workflow mínimo em `.github/workflows/ci.yml`
- executa `npm ci`, `npm run typecheck` e `npm run build`

## Fluxo operacional

1. receber input no WhatsApp;
2. carregar memória e skills;
3. aplicar DNA/governança ativa;
4. revisar o `state` por ciclos;
5. responder e capitalizar descobertas.


## Execução local com Ollama

Para rodar o Jarvis de forma proprietária/local, use `CORE_PROVIDER=ollama` e `ROUTER_PROVIDER=ollama`.

Variáveis mínimas:

- `OLLAMA_BASE_URL=http://host.docker.internal:11434/v1`
- `OLLAMA_MODEL=qwen3:4b`

O provider `ollama` usa a camada OpenAI-compatible do Ollama (`/v1/chat/completions`) e não exige API key.

## Operação rápida no Warp

Há atalhos locais em `bin/` para operar o Jarvis da KVM2 sem decorar comandos longos.

Se quiser usar como comandos diretos no terminal:

```bash
export PATH="$PWD/bin:$PATH"
```

Comandos disponíveis:

- `jarvis-status` — mostra `healthz`, `readyz` e `statusz`
- `jarvis-logs` — acompanha logs ao vivo do container `jarvis-agent`
- `jarvis-smoke` — valida Jarvis + Ollama local com um prompt de smoke test
- `jarvis-lateral-smoke` — dispara 3 prompts paralelos direto no `AgentController` para validar classificação, hipótese e método analítico no runtime remoto
- `jarvis-kvm2-a2a` — ativa uma vertical mínima de multiagentes C-level -> Ops na KVM2
- `jarvis-uaz-status` — mostra status da instância UAZAPI e webhooks configurados
- `jarvis-uaz-webhook-set` — aponta a instância UAZAPI atual para o `POST /webhook` público do Jarvis

Variáveis opcionais:

- `JARVIS_HOST` — default `hostinger-kvm2`
- `JARVIS_PORT` — default `3010`
- `JARVIS_CONTAINER` — default `jarvis-agent`
- `JARVIS_MODEL` — default `qwen3:4b`
- `JARVIS_PUBLIC_WEBHOOK_URL` — URL pública que a UAZAPI deve usar para entregar mensagens ao Jarvis

## Operação do canal UAZAPI

Quando o Jarvis estiver saudável na KVM2, o próximo gargalo costuma ser o **webhook da instância**.

Verifique o estado atual:

```bash
bin/jarvis-uaz-status
```

Para apontar a instância ativa para o webhook público do Jarvis:

```bash
export JARVIS_PUBLIC_WEBHOOK_URL=http://SEU_HOST_PUBLICO:3010/webhook
bin/jarvis-uaz-webhook-set
```

Também é possível passar a URL direto:

```bash
bin/jarvis-uaz-webhook-set http://SEU_HOST_PUBLICO:3010/webhook
```

Defaults operacionais do bootstrap:

- eventos: `messages`
- exclusões: `wasSentByApi,isGroupYes`

Se precisar ajustar isso sem editar script:

```bash
JARVIS_UAZAPI_EVENTS=messages,connection \
JARVIS_UAZAPI_EXCLUDE=wasSentByApi,isGroupYes \
bin/jarvis-uaz-webhook-set http://SEU_HOST_PUBLICO:3010/webhook
```
