# Adapter: ruptur-forge

`ruptur-forge` é a camada operacional de bootstrap do `infrastructure-state`.

Hoje ele:

- valida catálogo e perfis
- lista serviços e perfis disponíveis
- mantém instaladores operacionais para runtime real
- referencia o estado observado em `registry/services.yaml`

Serviços com instalador operacional:

- Redis
- n8n
- Langfuse

## Comandos

```bash
bash adapters/ruptur-forge/bin/ruptur-forge doctor
bash adapters/ruptur-forge/bin/ruptur-forge list services
bash adapters/ruptur-forge/bin/ruptur-forge list profiles
bash adapters/ruptur-forge/bin/ruptur-forge show service n8n
bash adapters/ruptur-forge/bin/ruptur-forge profile plan kvm2-core --format json
bash adapters/ruptur-forge/installers/install_redis.sh
bash adapters/ruptur-forge/installers/install_n8n.sh
bash adapters/ruptur-forge/installers/install_langfuse.sh
```
