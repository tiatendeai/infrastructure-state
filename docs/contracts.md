# Contratos

## Task
Uma task precisa declarar:
- `task_id`
- `type`
- `input`
- `output`
- `status`

Campos opcionais de governança suportados:

- `mode`
- `linear_issue_id`
- `linear_project`
- `linear_team_key`
- `service_target`
- `context_refs`
- `infra_refs`
- `expected_output`
- `approval_required`
- `execution_policy`

### Convenção por papel

- issue do Linear = unidade de governança
- task local = unidade executável
- registry/log/state = evidência

### Tipo `command`

Tasks do tipo `command` executam apenas entrypoints allowlisted do próprio repositório.

Nesta tranche, a allowlist contém somente:

- `scripts/collect_server_inventory.py`
- `scripts/generate_services_registry.py`
- `scripts/build_context_packet.py`

O `input` recomendado para `command` contém:

- `entrypoint`
- `args`
- `service_target`
- `context_refs`
- `infra_refs`
- `expected_output`

## State
O estado global precisa declarar:
- `status`
- `current_task`
- `history`
- `version`

`current_task` e `history` aceitam metadados opcionais de execução, como:

- `task_source`
- `linear_issue_id`
- `linear_project`
- `linear_team_key`
- `service_target`
- `approval_required`
- `execution_policy`

Os contratos formais ficam em `contracts/`.


## Context Packet
O context packet é um artefato efêmero para execução de tasks/agentes.

Contrato formal:
- `contracts/context-packet.schema.json`

Template base:
- `templates/context-packet.json.tpl`

Campos obrigatórios:
- `project`
- `branch`
- `linear_issue`
- `task`
- `objective`
- `latest_actions`
- `canonical_facts`
- `retrieved_memories`
- `policy_refs`

Regra:
- deve ser pequeno
- deve derivar de fatos canônicos
- não deve carregar runtime bruto
