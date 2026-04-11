# Linear Runtime Integration Model

## Objetivo

Documentar a integração de runtime entre:

- `scripts/run_task.py`
- `registry/linear-mapping.yaml`
- adapter nativo do Linear
- evidência local em `registry/`, `logs/` e `kernel/state.json`

## Princípio operacional

O Linear continua sendo a camada de governança e resumo.

O repositório continua sendo a camada de evidência técnica.

Por isso, a integração de runtime publica no Linear apenas:

- transição de status
- comentário resumido e limpo
- referência aos artefatos locais

Ela **não** replica log bruto no comentário.

## Componentes da TRANCHE L2

## 1. `adapters/linear/registry.py`

Responsável por:

- ler `registry/linear-mapping.yaml`
- resolver `issue ↔ backlog_key ↔ UUID ↔ task local`
- oferecer utilitários de contexto para sincronização de runtime

## 2. `adapters/linear/runtime.py`

Responsável por:

- mapear eventos locais (`running`, `done`, `error`) para statuses do Linear
- construir comentário resumido
- publicar status e comentário pelo adapter GraphQL
- operar em modo `dry-run`

## 3. `scripts/linear_adapter.py`

Agora oferece, além da L1:

- `mapping resolve`
- `runtime publish`

## 4. `scripts/run_task.py`

Agora:

- pode chamar a sincronização de runtime do Linear sem browser
- registra o resultado da sincronização em `registry/runs/*.json`
- imprime `linear_sync` no resultado final da task quando ela conclui com sucesso

## Fluxo de runtime

## Início da execução

Quando `LINEAR_RUNTIME_SYNC_ENABLED=true`, o runner tenta publicar:

- status `Running`
- sem comentário por padrão

## Sucesso

Ao concluir a execução local:

- gera `registry/runs/*.json`
- publica status `Done`
- publica comentário resumido com:
  - task
  - modo
  - event
  - project/service target
  - artifacts esperados
  - referência para `registry_record`

## Erro

Se a execução falhar:

- gera `registry/runs/*.json` de erro
- publica status `Failed`
- publica comentário resumido com a falha sanitizada

## Regras de resolução issue ↔ task

A resolução segue esta ordem prática:

1. `linear_issue_identifier`
2. `linear_issue_uuid`
3. `linear_issue_id` legado
4. `task_source` / `local_task`

No estado atual do repo, várias tasks ainda usam `linear_issue_id` como backlog key local, por exemplo `INFRA-013`. O resolver usa o `registry/linear-mapping.yaml` para converter isso no identifier real do Linear, por exemplo `INF-13`.

## Configuração de runtime

Variáveis principais:

```bash
LINEAR_RUNTIME_SYNC_ENABLED=false
LINEAR_RUNTIME_SYNC_STRICT=false
LINEAR_RUNTIME_MAPPING_PATH=registry/linear-mapping.yaml
LINEAR_RUNTIME_STATUS_RUNNING=Running
LINEAR_RUNTIME_STATUS_DONE=Done
LINEAR_RUNTIME_STATUS_ERROR=Failed
LINEAR_RUNTIME_STATUS_ON_RUNNING=true
LINEAR_RUNTIME_STATUS_ON_DONE=true
LINEAR_RUNTIME_STATUS_ON_ERROR=true
LINEAR_RUNTIME_COMMENT_ON_RUNNING=false
LINEAR_RUNTIME_COMMENT_ON_DONE=true
LINEAR_RUNTIME_COMMENT_ON_ERROR=true
LINEAR_RUNTIME_APPEND_EXPECTED_OUTPUT=true
LINEAR_RUNTIME_COMMENT_HEADER=Execução local sincronizada pelo infrastructure-state.
```

## Exemplos operacionais

## Resolver mapping por task

```bash
python3 scripts/linear_adapter.py mapping resolve --task-file tasks/INFRA-013_validate_supabase_long_term_memory.task.json --format json
```

## Dry-run de publicação de runtime

```bash
python3 scripts/linear_adapter.py runtime publish \
  --task-file tasks/INFRA-013_validate_supabase_long_term_memory.task.json \
  --event done \
  --mode FULL \
  --registry-record registry/runs/exemplo.json \
  --dry-run \
  --format json
```

## Execução com sincronização automática

```bash
LINEAR_RUNTIME_SYNC_ENABLED=true \
LINEAR_AUTH_MODE=oauth_access_token \
LINEAR_OAUTH_ACCESS_TOKEN=seu_token \
python3 scripts/run_task.py tasks/INFRA-013_validate_supabase_long_term_memory.task.json FULL
```

## Decisão de produto

- status e comentário no Linear = **resumo operacional**
- `registry/`, `logs/`, `kernel/state.json` = **evidência técnica**
- browser/MCP não entram na fundação do runtime
- webhook permanece para a próxima tranche

## Limites desta tranche

- ainda não existe webhook consumer ativo
- ainda não existe n8n ligado ao fluxo
- ainda não existe reconciliação automática contínua
- ainda não existe deduplicação avançada de comentários
- o comentário é gerado localmente por template simples, sem motor semântico externo
