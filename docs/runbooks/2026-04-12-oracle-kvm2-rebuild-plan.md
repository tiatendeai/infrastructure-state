# Runbook — Oracle + KVM2 Rebuild Plan

Data: 2026-04-12

## Objetivo

Concluir a preservação do estado atual, consolidar o bruto na `oracle-test` e só então:

1. reprovisionar Oracle de forma limpa
2. destruir/limpar KVM2
3. reerguer o core com Ollama + Jarvis mínimo

## Princípios

- nada destrutivo antes de preservação validada
- Git guarda trilha e automação
- Oracle guarda bruto temporário
- `infrastructure-state` é a casa canônica da automação
- `J.A.R.V.I.S.` é o maestro

## Estado já preservado

### KVM2 → oracle-test

- ruptur DB
- baileys auth/data
- traefik letsencrypt
- warmup runtime
- whisper models
- n8n data
- langfuse postgres
- langfuse minio
- jarvis data
- langfuse clickhouse (export consistente)

### Oracle → oracle-test

Em consolidação:

- host2_ruptur_db_data
- host2_baileys_data
- host2_traefik_letsencrypt
- host2_whisper_models
- host1_letsencrypt


## Mapa de exposição pública observado em 2026-04-12

### Rotas hoje respondendo na KVM2 (IP 187.77.242.208)

- `api.ruptur.cloud`
- `webhook.ruptur.cloud`
- `baileys.ruptur.cloud`
- `n8n.ruptur.cloud`

### Rotas que a oracle-prod também consegue servir (teste direto por Host header no IP 167.234.228.71)

- `app.ruptur.cloud` → 307
- `api.ruptur.cloud` → 401
- `webhook.ruptur.cloud` → 401
- `ruptur.cloud` → 301
- `site.ruptur.cloud` → 301
- `aquecimento.ruptur.cloud` → 301
- `baileys.ruptur.cloud` → 404 de aplicação, mas responde na borda

### Rota que continua única da KVM2 neste momento

- `n8n.ruptur.cloud`

### Implicação operacional

A KVM2 pode ser abatida mais cedo se aceitarmos uma das opções abaixo para `n8n.ruptur.cloud`:

1. janela curta de indisponibilidade
2. migração do n8n para outro host antes do corte
3. publicação temporária do n8n em novo destino antes do rebuild completo

Para o restante do tráfego Ruptur, a oracle-prod já consegue atuar como retaguarda temporária.

## Gate de destruição

Só avançar para destroy quando:

1. `oracle-test:/srv/jarvis-archive/raw` contiver todos os exports obrigatórios
2. checksums estiverem registrados nos manifests locais
3. os placeholders inválidos da primeira tentativa forem removidos
4. houver inventário salvo da KVM2 e das Oracle
5. a KVM2 estiver operacionalmente livre para derrubada

## Ordem de execução

### Fase A — Preservação

1. fechar exports pendentes
2. validar manifests
3. limpar arquivos inválidos de tentativa anterior

### Fase B — Oracle

1. decidir se `oracle-test` permanece como cofre temporário
2. destruir/recriar `oracle-prod`
3. opcionalmente importar `oracle-test` ao Terraform ou substituí-la depois
4. corrigir drift do Terraform (`x86_2`, `arm`, imports pendentes)

### Fase C — KVM2

1. confirmar que o bruto da KVM2 está íntegro
2. registrar checklist de restore mínimo
3. destruir/limpar KVM2
4. reerguer:
   - Ollama
   - Jarvis Core
   - gateway
   - ledger
   - watchdog
   - state sync

## Observações

- `oracle-prod` atual tem pouco espaço livre e legado útil
- `oracle-test` atual é o cofre mais folgado
- o Terraform hoje não reflete integralmente o estado real das Oracle
