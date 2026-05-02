# Mapa de Segredos do Infisical

> Documento histórico. O contrato canônico atual vive em `docs/INFISICAL_SECRET_MAP.md`
> e em `state/registry/infisical-secret-contract.json`.

Este documento lista, em termos operacionais, quais segredos devem ser tratados como **somente no Infisical** e quais podem existir apenas como **placeholder** no Git.

## Regra geral

- **Segredo real nunca vai para Git**
- **Git guarda contrato, nome e placeholder**
- **Infisical guarda o valor real**
- **Ansible/Runtime consomem o segredo via variáveis ou arquivos gerados**

## Segredos que devem viver no Infisical

### Plataforma e infraestrutura

- `shipyard_postgres_password`
- `shipyard_redis_password`
- `shipyard_n8n_password`
- `shipyard_n8n_encryption_key`
- `shipyard_minio_root_password`
- `shipyard_temporal_postgres_password`

### Infisical

- `shipyard_infisical_auth_secret`
- `shipyard_infisical_encryption_key`
- `shipyard_infisical_postgres_password`
- `shipyard_infisical_smtp_password`

### Langfuse

- `shipyard_langfuse_nextauth_secret`
- `shipyard_langfuse_salt`
- `shipyard_langfuse_encryption_key`
- `shipyard_langfuse_postgres_password`
- `shipyard_langfuse_clickhouse_password`
- `shipyard_langfuse_minio_secret`
- `shipyard_langfuse_redis_password`

### Cloudflare

- `shipyard_cloudflare_api_token`
- `shipyard_cloudflare_account_id`
- `shipyard_cloudflare_zone_id`

### UAZAPI / automações internas

- `shipyard_uazapi_api_token`
- `shipyard_uazapi_webhook_secret`
- `shipyard_jarvis_uazapi_admin_token`
- `shipyard_jarvis_uazapi_instance_token`

### LLM / agentes

- `shipyard_jarvis_gemini_api_key`
- `shipyard_jarvis_openrouter_api_key`
- `shipyard_jarvis_groq_api_key`
- `shipyard_jarvis_deepseek_api_key`

### Linear

- `LINEAR_PERSONAL_API_KEY`
- `LINEAR_OAUTH_CLIENT_ID`
- `LINEAR_OAUTH_CLIENT_SECRET`
- `LINEAR_OAUTH_ACCESS_TOKEN`
- `LINEAR_OAUTH_REFRESH_TOKEN`
- `LINEAR_WEBHOOK_SECRET`

### Outros segredos operacionais

- `SUPABASE_SERVICE_ROLE_KEY`
- `REDIS_PASSWORD`
- `LLM_API_KEY`
- `OPENAI_API_KEY`
- `N8N_ENCRYPTION_KEY`
- `JWT_SECRET`
- `SMTP_PASSWORD`

## Campos que podem ficar como contrato no Git

Estes podem existir no Git apenas como documentação, sem valor real:

- `shipyard_postgres_db`
- `shipyard_postgres_user`
- `shipyard_n8n_db`
- `shipyard_n8n_user`
- `shipyard_minio_root_user`
- `shipyard_infisical_smtp_host`
- `shipyard_infisical_smtp_port`
- `shipyard_infisical_smtp_username`
- `shipyard_infisical_smtp_from_address`
- `shipyard_infisical_smtp_from_name`
- `shipyard_jarvis_allowed_user_ids`

## Fluxo sugerido

1. declarar o segredo no contrato
2. criar o valor real no Infisical
3. gerar `.env`, `secrets.yml` ou variáveis de runtime a partir do cofre
4. manter Git somente com placeholder e documentação

## Observação

Se uma variável aparece em runtime, playbook, adapter ou template, isso **não** significa que o valor real deva ficar no repositório.
O valor real deve ser carregado do Infisical na etapa de execução.
