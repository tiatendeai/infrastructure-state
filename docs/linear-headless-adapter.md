# Linear Headless Adapter

## Objetivo

Documentar a operação headless do adapter Linear implementado na TRANCHE L1.

## Entrypoint

```bash
python3 scripts/linear_adapter.py
```

## Contrato de configuração

O adapter lê `.env` automaticamente quando o arquivo existe no root do repositório.

Também lê `.env.local` quando presente. Quando a mesma chave existe nos dois arquivos,
`.env.local` prevalece sobre `.env`.

## Estado operacional atual

Em `7 de abril de 2026`, este repositório já está apontado para:

- workspace URL key: `ruptur`
- organization id: `fe8a5818-b56d-4e8a-b47c-fc3ea9eb6ebf`
- team key: `INF`
- team id: `f1fc8b23-ac67-4c01-96c7-057726cbd8a9`

O MCP do Linear no Codex já foi autenticado via OAuth nesta máquina.

O adapter headless já está autenticado localmente em modo `live` via `LINEAR_PERSONAL_API_KEY` + `LINEAR_ALLOW_PERSONAL_API_KEY_BOOTSTRAP=true` em `.env.local`.

A sincronização automática de runtime continua opt-in e só deve ser habilitada quando o fluxo estiver estável.

### Variáveis principais

```bash
LINEAR_API_URL=https://api.linear.app/graphql
LINEAR_OAUTH_TOKEN_URL=https://api.linear.app/oauth/token
LINEAR_TIMEOUT_SECONDS=20
LINEAR_AUTH_MODE=auto
LINEAR_OAUTH_ACCESS_TOKEN=
LINEAR_OAUTH_CLIENT_ID=
LINEAR_OAUTH_CLIENT_SECRET=
LINEAR_OAUTH_SCOPES=read,write,comments:create
LINEAR_OAUTH_USE_CLIENT_CREDENTIALS=false
LINEAR_OAUTH_REDIRECT_URI=
LINEAR_PERSONAL_API_KEY=
LINEAR_ALLOW_PERSONAL_API_KEY_BOOTSTRAP=false
LINEAR_ORGANIZATION_ID=
LINEAR_WORKSPACE_URL_KEY=
LINEAR_TEAM_ID=
LINEAR_TEAM_KEY=INF
LINEAR_WEBHOOK_SECRET=
```

## Estratégia recomendada de autenticação

## Backbone recomendado

### OAuth access token já provisionado

```bash
LINEAR_AUTH_MODE=oauth_access_token
LINEAR_OAUTH_ACCESS_TOKEN=...
```

### OAuth client credentials

```bash
LINEAR_AUTH_MODE=oauth_client_credentials
LINEAR_OAUTH_CLIENT_ID=...
LINEAR_OAUTH_CLIENT_SECRET=...
```

ou:

```bash
LINEAR_AUTH_MODE=auto
LINEAR_OAUTH_USE_CLIENT_CREDENTIALS=true
LINEAR_OAUTH_CLIENT_ID=...
LINEAR_OAUTH_CLIENT_SECRET=...
```

## Bootstrap/debug controlado

```bash
LINEAR_AUTH_MODE=auto
LINEAR_ALLOW_PERSONAL_API_KEY_BOOTSTRAP=true
LINEAR_PERSONAL_API_KEY=...
```

## Comandos de operação

## Doctor

Valida configuração local do adapter:

```bash
python3 scripts/linear_adapter.py doctor --format json
```

Valida configuração e tenta autenticar no Linear:

```bash
python3 scripts/linear_adapter.py doctor --live --format json
```

## Ler issue por identifier

```bash
python3 scripts/linear_adapter.py issue get INF-13 --format json
```

## Listar projects por team

```bash
python3 scripts/linear_adapter.py project list --team INF --format json
```

Se `--team` não for informado, o adapter tenta usar `LINEAR_TEAM_ID` ou `LINEAR_TEAM_KEY`.

## Listar issue statuses por team

```bash
python3 scripts/linear_adapter.py status list --team INF --format json
```

## Atualizar status de issue

```bash
python3 scripts/linear_adapter.py issue set-status INF-13 Done --format json
```

Modo seguro de simulação:

```bash
python3 scripts/linear_adapter.py issue set-status INF-13 Done --dry-run --format json
```

## Adicionar comentário

```bash
python3 scripts/linear_adapter.py issue comment INF-13 --body "Comentário de teste" --format json
```

ou:

```bash
python3 scripts/linear_adapter.py issue comment INF-13 --body-file ./comment.md --format json
```

## Runtime integration (L2)

Comandos adicionais introduzidos na TRANCHE L2:

```bash
python3 scripts/linear_adapter.py mapping resolve --task-file tasks/INFRA-013_validate_supabase_long_term_memory.task.json --format json
python3 scripts/linear_adapter.py runtime publish --task-file tasks/INFRA-013_validate_supabase_long_term_memory.task.json --event done --mode FULL --registry-record registry/runs/exemplo.json --dry-run --format json
```

Veja também: `docs/linear-runtime-integration.md`.

## Limites conhecidos desta tranche

- ainda não existe callback real do OAuth authorization code
- ainda não existe refresh store persistente para tokens de usuário
- ainda não existe webhook consumer
- ainda não existe reconciliação contínua por polling/webhook

## Decisão operacional

Nesta tranche, o adapter já é adequado para:

- leitura e escrita headless controlada
- uso local por humano/agente
- bootstrap de integração nativa com o Linear
- resolução de `issue ↔ task ↔ mapping`
- sincronização mínima com `scripts/run_task.py`

Ainda não é, sozinho, o fluxo completo de automação com n8n/Jarvis. Isso fica para a próxima tranche.
