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
