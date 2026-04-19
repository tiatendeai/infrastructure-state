# Adapter: ruptur-forge

`ruptur-forge` é a camada de bootstrap **plan-only** do `infrastructure-state`.

Nesta tranche ele:

- valida catálogo e perfis
- lista serviços e perfis disponíveis
- gera planos de bootstrap sem executar nada
- referencia o estado observado em `registry/services.yaml`

Nesta tranche ele **não**:

- instala serviços
- executa bootstrap remoto
- altera servidores
- integra com `scripts/ruptur.sh`

## Comandos

```bash
bash adapters/ruptur-forge/bin/ruptur-forge doctor
bash adapters/ruptur-forge/bin/ruptur-forge list services
bash adapters/ruptur-forge/bin/ruptur-forge list profiles
bash adapters/ruptur-forge/bin/ruptur-forge show service n8n
bash adapters/ruptur-forge/bin/ruptur-forge profile plan kvm2-core --format json
```

Qualquer tentativa de usar `--apply` retorna erro explícito:

- `apply_disabled_in_tranche_2`
