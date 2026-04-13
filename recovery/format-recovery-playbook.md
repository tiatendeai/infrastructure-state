# Playbook — Formatação com Observabilidade, Controle e Recuperação

Atualizado em **2026-04-13**.

## Objetivo

Garantir que a máquina possa ser formatada sem perda de:

- governança canônica
- código e branches de trabalho
- capacidade de religamento
- segredos e autenticações críticas
- arquivos locais sem remote

## Princípio operacional

Separar tudo em três destinos:

1. **Remote versionado** — código, manifests, runbooks e conhecimento promovido
2. **Backup criptografado off-git** — segredos, auth local, arquivos sem remote, históricos brutos
3. **Descartar** — lixo local e artefato efêmero

## Antes da formatação

### 1. Validar remotes

Use `recovery/dev_inventory.yaml` e confirme que os repositórios críticos foram enviados:

- `state`
- `infrastructure-state`
- `omega`
- `J.A.R.V.I.S.`
- `alpha`
- `ruptur`
- `lab/ruptur-revenue-engine-os-ai`
- `2dl-automated-tech-farm-and-cash-factory-co`
- `vps-oracle`

### 2. Gerar backup criptografado off-git

Consultar `recovery/local_backup_manifest.yaml` e copiar para destino seguro:

- `$HOME/.ssh`
- `$HOME/.codex`
- shell dotfiles relevantes
- repositórios sem remote
- históricos locais (`GitHub/brute-ai-agent-histories`)

### 3. Validar o que pode ser descartado

Pode sumir da máquina sem dano canônico, desde que os manifests já estejam publicados:

- `**/.DS_Store`
- `*.code-workspace`
- `full_dev_tree_infra.txt`
- `.turbo/`
- logs de build efêmeros

## Depois da formatação

### Ordem de religamento

Seguir `recovery/recovery_matrix.yaml`.

Resumo:

1. `state`
2. `infrastructure-state`
3. `omega`
4. `J.A.R.V.I.S.`
5. demais repositórios operacionais
6. restaurar bundle criptografado
7. revalidar autenticações

### Critério de aceite mínimo

A restauração só conta como concluída quando:

- o control plane foi clonado
- o bundle criptografado foi restaurado
- `J.A.R.V.I.S.` executa `npm run ci`
- GitHub CLI/autenticação voltaram
- os manifests de recovery continuam coerentes com a máquina restaurada

## Observação importante

**Git não é backup de segredo.**

Git guarda:

- controle
- auditabilidade
- manifests
- recuperação declarativa

O backup criptografado guarda:

- segredos
- autenticação
- arquivos locais sem remote
- históricos brutos
