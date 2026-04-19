# Integração com Linear

## Papel do Linear nesta arquitetura

O Linear é a camada de **governança operacional** do `infrastructure-state`.

O `infrastructure-state` continua sendo a camada de:

- execução local
- estado canônico
- trilha de evidência
- preparação para automação futura

## O que já é suportado no ambiente atual

Pela integração disponível nesta sessão, o ambiente já consegue operar:

- issues
- projects
- labels
- comments em issues
- updates de projeto/iniciativa

## O que ainda é manual

Os seguintes itens continuam fora do suporte automatizado disponível aqui e devem ser feitos via UI do Linear:

- criação do team `INFRA`
- edição do workflow do team
- criação/edição dos statuses do team:
  - `Inbox`
  - `Planned`
  - `Ready`
  - `Running`
  - `Review`
  - `Blocked`
  - `Done`
  - `Failed`

## Estratégia adotada

A estratégia oficial desta tranche é **híbrida**:

- operação assistida hoje pela integração atual do Linear
- automação futura por API/webhooks para n8n/Jarvis

## Contrato local

- issue do Linear = unidade de governança
- task local = unidade executável
- `kernel/state.json` = estado atual
- `registry/runs/*.json` = trilha estruturada
- `logs/execution.log` = trilha linear

## Convenções

### Naming

- convenção final: `tasks/INFRA-123_<slug>.task.json`
- seed local desta tranche: `tasks/LIN-001_baseline_server_inventory.task.json`

### Campos de governança em task

- `linear_issue_id`
- `linear_project`
- `linear_team_key`
- `service_target`
- `context_refs`
- `infra_refs`
- `expected_output`
- `approval_required`
- `execution_policy`

## Fluxo-alvo documentado

O fluxo-alvo é:

`Linear -> task local -> execução -> registry/log/state -> retorno ao Linear`

Nesta tranche, o retorno ao Linear é **somente documentado**. A materialização por automação fica para fase posterior.
