# Runbook — KVM2 reerguida com Ollama local

**Data:** 2026-04-12  
**Status:** concluído  
**Origem:** execução operacional do Jarvis + automação canonizada em `infrastructure-state`

## Resumo

A KVM2 foi:

1. preservada em bruto na `oracle-test`;
2. congelada com snapshots finais dos dados críticos;
3. limpa de forma destrutiva;
4. reconstruída com um core mínimo novo;
5. religada com Jarvis operando em provider local via Ollama.

## Preservação garantida antes da faxina

Dados preservados no cofre da `oracle-test`:

- banco Ruptur
- dados Baileys
- `jarvis_data`
- `n8n` consistente
- `langfuse` (postgres, minio e clickhouse consistente)
- certificados `letsencrypt`
- restore-kit de configs/envs

Também houve backup local do `.env` na KVM2:

- `.env.backup-20260412-201746`

## Estado final da KVM2

### Runtime

- host: `srv1503897`
- disco livre observado após rebuild: ~`72G`
- Docker limpo
- sem legado antigo rodando junto

### Ollama

- instalado e ativo
- versão: `0.20.5`
- modelo local: `qwen3:4b`

### Jarvis

- repositório sincronizado no commit `24cbee8`
- commit: `feat: add ollama local provider support`
- container: `jarvis-agent`
- status: `healthy`
- porta: `3010 -> 3000`

### Provider ativo

- `CORE_PROVIDER=ollama`
- `ROUTER_PROVIDER=ollama`
- `OLLAMA_BASE_URL=http://host.docker.internal:11434/v1`
- `OLLAMA_MODEL=qwen3:4b`

### Checks validados

- `/healthz` → `ok`
- `/readyz` → `ready`
- `/statusz` → `ok`

### Status report observado

- `provider: ollama`
- `routerProvider: ollama`
- `tools: 3`
- `skills: 8`

## Implicação operacional

A KVM2 passa a ser um nó **local-first**, limpo e mínimo, pronto para retomada seletiva de novas camadas, sem dependência do legado anterior.

## Próxima fase sugerida

1. decidir quais serviços retornam;
2. reintroduzir por camadas:
   - Slack
   - WhatsApp
   - ledger
   - watchdog
   - state sync reforçado
3. reconciliar o Terraform Oracle em trilha separada, sem misturar com o rebuild já concluído da KVM2.
