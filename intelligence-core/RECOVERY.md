# RECOVERY.md — J.A.R.V.I.S.

## Fonte canônica de recovery

A documentação canônica de restauração e preparação para formatação desta casa está em:

- `../infrastructure-state/recovery/dev_inventory.yaml`
- `../infrastructure-state/recovery/recovery_matrix.yaml`
- `../infrastructure-state/recovery/local_backup_manifest.yaml`
- `../infrastructure-state/recovery/format-recovery-playbook.md`

## Bootstrap mínimo desta casa

```bash
cd /Users/diego/dev/J.A.R.V.I.S.
nvm use
npm ci
npm run ci
```

## Dependências de restore

- Node via `.nvmrc`
- backup criptografado de `$HOME/.codex` e `$HOME/.ssh`
- repositório `state` restaurado em `/Users/diego/dev/state`
- repositório `infrastructure-state` restaurado em `/Users/diego/dev/infrastructure-state`

## Observação

Arquivos locais efêmeros como `*.code-workspace`, `full_dev_tree_infra.txt` e bancos gerados em `data/a2a/` **não** são fonte canônica de recovery.
