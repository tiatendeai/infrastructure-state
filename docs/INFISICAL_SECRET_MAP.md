# Mapa Canônico de Segredos — Infisical / Shipyard

Este documento define os nomes canônicos dos segredos operacionais do ecossistema.

## Princípios

- segredos reais não ficam em Git
- o repositório guarda contrato, nome e intenção
- o runtime recebe valores via Infisical, override local seguro ou extra-vars controladas
- um segredo sem dono operacional é débito técnico

## Segredos do próprio Infisical

Esses itens pertencem ao cofre e à sua operação:

- `shipyard_infisical_auth_secret`
- `shipyard_infisical_encryption_key`
- `shipyard_infisical_postgres_password`

## Segredos de borda / edge

- `shipyard_cloudflare_api_token`

## Segredos da base operacional

- `shipyard_postgres_password`
- `shipyard_redis_password`
- `shipyard_n8n_password`
- `shipyard_minio_root_password`

## Segredos de workflow / plataforma

- `shipyard_temporal_postgres_password`
- `shipyard_langfuse_nextauth_secret`
- `shipyard_langfuse_postgres_password`
- `shipyard_langfuse_clickhouse_password`
- `shipyard_langfuse_minio_secret`
- `shipyard_langfuse_redis_password`

## Segredos de integração externa

- `shipyard_uazapi_api_token`
- `shipyard_uazapi_webhook_secret`
- `shipyard_jarvis_uazapi_admin_token`
- `shipyard_jarvis_uazapi_instance_token`
- `shipyard_jarvis_gemini_api_key`
- `shipyard_jarvis_openrouter_api_key`
- `shipyard_jarvis_groq_api_key`
- `shipyard_jarvis_deepseek_api_key`

## Convenção de consumo

1. o nome do segredo é definido aqui
2. o valor real é provisionado no Infisical
3. o Ansible lê o contrato e injeta o valor no host alvo
4. o runtime nunca assume valor ausente como se fosse válido
5. ausência explícita é tratada como estado operacional, não como improviso

## Inventário e validação

O inventário atual do repositório e o cruzamento com este contrato podem ser gerados por:

```bash
python3 scripts/collect_secret_inventory.py
```

Contrato canônico machine-readable:

- `state/registry/infisical-secret-contract.json`

## Observação

O token encaminhado nesta conversa deve ser tratado como segredo do cofre e nunca reimpresso em documentação, logs ou commits.
