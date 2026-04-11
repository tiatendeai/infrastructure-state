# Linear Adapter

Adapter headless do `infrastructure-state` para integração nativa com o Linear via **GraphQL oficial**.

## Objetivo da tranche L1

Materializar uma base local, repetível e sem browser para operar o Linear com o seguinte contrato mínimo:

- ler issue por identifier
- listar projects por team
- listar statuses por team
- atualizar status de issue
- adicionar comentário em issue

## Princípios desta implementação

- **native-first**: somente API e autenticação oficiais do Linear
- **headless-first**: sem browser automation, sem Playwright, sem CDP, sem AppleScript
- **GraphQL-first**: sem acoplamento ao MCP
- **OAuth-first**: backbone preparado para OAuth 2.0
- **bootstrap controlado**: personal API key só para debug/bootstrap, nunca como backbone

## Modos de autenticação suportados nesta tranche

## 1. OAuth access token já emitido

Se você já possui um token OAuth válido:

- `LINEAR_AUTH_MODE=oauth_access_token`
- `LINEAR_OAUTH_ACCESS_TOKEN=...`

## 2. OAuth client credentials

Para comunicação server-to-server com app configurado no Linear:

- `LINEAR_AUTH_MODE=oauth_client_credentials`
- `LINEAR_OAUTH_CLIENT_ID=...`
- `LINEAR_OAUTH_CLIENT_SECRET=...`

Ou modo automático:

- `LINEAR_OAUTH_USE_CLIENT_CREDENTIALS=true`

## 3. Bootstrap/debug com personal API key

Permitido apenas como contingência controlada:

- `LINEAR_ALLOW_PERSONAL_API_KEY_BOOTSTRAP=true`
- `LINEAR_PERSONAL_API_KEY=...`

## CLI

Entrypoint principal:

```bash
python3 scripts/linear_adapter.py --help
```

Comandos principais:

```bash
python3 scripts/linear_adapter.py doctor --format json
python3 scripts/linear_adapter.py issue get INF-13 --format json
python3 scripts/linear_adapter.py project list --team INF --format json
python3 scripts/linear_adapter.py status list --team INF --format json
python3 scripts/linear_adapter.py issue set-status INF-13 Done --format json
python3 scripts/linear_adapter.py issue comment INF-13 --body "comentário" --format json
```

## O que fica pronto nesta tranche

- cliente GraphQL headless
- resolução básica de autenticação
- fallback controlado para token pessoal
- resolução básica de team por `id`, `key` ou `name`
- operações mínimas da CLI
- resolução local via `registry/linear-mapping.yaml`
- publicação resumida de runtime para status/comentário
- integração mínima com `scripts/run_task.py`
- documentação operacional

## O que fica para a próxima tranche

- callback real de OAuth authorization code
- persistência/refresh lifecycle mais completo para OAuth de usuário
- consumer de webhook
- reconciliação contínua issue ↔ task ↔ state
- n8n/Jarvis como consumidores oficiais do adapter

## Referências oficiais

- GraphQL API / Getting started: https://linear.app/developers/graphql
- OAuth 2.0 authentication: https://linear.app/developers/oauth-2-0-authentication
- OAuth actor authorization: https://linear.app/developers/oauth-actor-authorization
- Webhooks: https://linear.app/developers/webhooks
- SDK / Fetching & modifying data: https://linear.app/developers/sdk-fetching-and-modifying-data
- SDK / Advanced usage: https://linear.app/developers/advanced-usage
