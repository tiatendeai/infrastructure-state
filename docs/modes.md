# Modos de Operação

## FAST
Para tarefas simples e diretas.

## STANDARD
Para tarefas comuns com validação leve e registro.

É o modo padrão para:

- validações locais
- sincronizações leves
- tasks `command` simples quando a task não fixa outro modo

## FULL
Para tarefas auditáveis com snapshot e trilha runtime.

É o modo recomendado para:

- inventário remoto
- mudanças críticas
- execução com `approval_required: true`
- fluxos com trilha forte de auditoria

## Heurística por tipo

Quando o modo não for informado explicitamente:
- `echo` e `noop` -> `FAST`
- `validate`, `transform`, `sync` e `command` -> `STANDARD`
- `change`, `release` e `deploy` -> `FULL`

## Regra de imutabilidade

O modo não altera a task-fonte em `tasks/*.json`.

Toda evidência de execução deve ser escrita em:

- `kernel/state.json`
- `registry/runs/*.json`
- `logs/execution.log`
- `state/runtime/`
