# Operating Model do Linear

## Princípio central

O Linear governa. O agente executa. O state audita.

## Responsabilidades

### Linear

- backlog
- prioridade
- cadência
- dependências
- status operacional
- handoff entre humano, agente e automação

### Agente local

- ler contexto e task local
- validar contrato
- executar com segurança
- registrar evidência
- preparar retorno estruturado

### `infrastructure-state`

- armazenar tasks locais
- manter `kernel/state.json`
- registrar `registry/runs/*.json`
- registrar `logs/execution.log`

## Ciclo operacional

1. uma demanda nasce no Linear
2. ela é refletida em uma task local
3. a task é validada localmente
4. a task é executada com modo apropriado
5. a evidência fica no state, registry e log
6. o retorno ao Linear fica preparado para automação futura

## Regras desta tranche

- nenhuma automação cega
- nenhuma mudança destrutiva
- nenhuma instalação de serviço
- nenhuma implementação de memória
- nenhum bootstrap de n8n
- nenhuma alteração do servidor em `INFRA-005`

## Pré-requisitos manuais

Antes da operação plena:

1. criar o team `INFRA`
2. configurar o workflow do team
3. criar os statuses do team

Até isso acontecer, o repo usa o contrato-alvo localmente sem presumir que o Linear já esteja materializado.
