<<<<<<< HEAD
# infrastructure-state
Infraestrutura IaC
=======
# Ruptur Farm Framework

> Instância ativa: `infrastructure-state` — diretório operacional de infraestrutura e IaC.

Framework operacional para execução de tarefas por agentes e automações com foco em simplicidade, portabilidade e estado determinístico.

Este README também funciona como **bússola operacional** para qualquer diretório instanciado a partir do framework, servindo como referência rápida para humanos e agentes.

## Missão do Diretório

Este diretório existe para concentrar o estado operacional de infraestrutura e IaC.

Ele deve servir como base para:

- provisionamento e mudança controlada de infraestrutura
- validação e auditoria de ambientes
- registro de execuções, decisões e trilhas operacionais
- operação previsível por humanos e agentes

## Escopo de IaC

Dentro deste diretório devem viver principalmente:

- tasks declarativas de infraestrutura
- automações reutilizáveis de provisionamento, validação e mudança
- estado, logs e registros operacionais
- documentação mínima para execução segura e reproduzível

Fora do escopo:

- segredos versionados em texto puro
- scripts soltos sem task, sem contrato ou sem trilha operacional
- mudanças críticas dependentes apenas de contexto humano implícito

## Filosofia

O Ruptur Farm Framework foi desenhado para inteligência modular e efêmera:

- **modular**: cada tarefa tem contrato explícito
- **efêmero**: contexto runtime pode ser limpo sem afetar o núcleo
- **portátil**: roda sem dependência de ferramentas proprietárias
- **determinístico**: estado, histórico e logs ficam em arquivos previsíveis
- **automatizável**: shell + arquivos + contratos simples para uso por devs e agentes

## Estrutura

```text
/
├── README.md
├── TEMPLATE_INIT.md
├── .env.example
├── .agents/
├── .archive/
├── adapters/
├── contracts/
├── docs/
├── examples/
├── kernel/
├── logs/
├── registry/
├── scripts/
├── state/
├── tasks/
└── templates/
```

## Kernel

- `kernel/state.json`: estado canônico da execução

## Contracts

- `contracts/task.schema.json`: contrato formal de task
- `contracts/state.schema.json`: contrato formal de state

As tasks podem incluir metadados opcionais de governança para integração com o Linear:

- `linear_issue_id`
- `linear_project`
- `linear_team_key`
- `service_target`
- `context_refs`
- `infra_refs`
- `expected_output`
- `approval_required`
- `execution_policy`

## Modos de operação

### FAST
- execução direta
- validação mínima
- ideal para tarefas simples como `echo` e `noop`

### STANDARD
- validação estrutural leve
- registro de execução
- modo padrão para automação local e tasks `command`

### FULL
- validação completa do contrato
- snapshot de estado
- trilha runtime em `.agents/runtime/`
- ideal para mudanças críticas, inventário remoto ou fluxos auditáveis

A escolha do modo pode ser:
1. passada por argumento na CLI
2. definida na própria task
3. inferida pelo tipo da task

## Como iniciar

```bash
bash scripts/ruptur.sh init
```

## Como executar a primeira task

```bash
bash scripts/ruptur.sh run examples/hello.task.json FAST
```

## Como validar uma task sem executar

```bash
bash scripts/ruptur.sh validate examples/hello.task.json FAST
```

## Como ver o estado atual

```bash
bash scripts/ruptur.sh status
```

## Como verificar o ambiente

```bash
bash scripts/ruptur.sh doctor
```

## Como limpar artefatos efêmeros

```bash
bash scripts/ruptur.sh clean
```

## Como resetar runtime, logs e registry

```bash
bash scripts/ruptur.sh reset
```

## Fluxo recomendado

1. inicialize com `init`
2. ajuste `.env`
3. se quiser declarar identidade do projeto, copie `templates/project.yaml.tpl` para um `project.yaml`
4. crie uma task a partir de `templates/task.json.tpl`
5. valide com `validate`
6. execute com `run`
7. consulte `kernel/state.json`, `registry/runs/` e `logs/execution.log`

## Regra de imutabilidade da task-fonte

As tasks versionadas em `tasks/*.json` são consideradas **fonte declarativa**.

Durante a execução, o runner **não reescreve** a task-fonte. Toda evidência operacional fica em:

- `kernel/state.json`
- `registry/runs/*.json`
- `logs/execution.log`
- `.agents/runtime/`

Isso preserva auditoria, diff limpo e reprodutibilidade.

## Tipo `command`

Além de `echo` e `noop`, o framework suporta o tipo `command` para executar entrypoints allowlisted do próprio repositório.

Nesta tranche, a allowlist contém apenas:

- `scripts/collect_server_inventory.py`
- `scripts/generate_services_registry.py`

O objetivo é permitir tasks auditáveis de coleta e validação sem abrir espaço para execução arbitrária.

## O que este framework não assume

- nenhum path absoluto
- nenhum orquestrador específico
- nenhum provedor de LLM específico
- nenhuma ferramenta externa para o fluxo básico

## Adapters

O diretório `adapters/` existe para integrações opcionais. O núcleo funciona sem eles.

- `adapters/n8n/`
- `adapters/llm/`
- `adapters/storage/`
- `adapters/ruptur-forge/`

## O que um diretório criado com este framework ganha

Quando este framework é aplicado a um diretório, ele deixa de ser apenas uma pasta com arquivos e passa a ser um workspace operacional com:

- **estado explícito** em `kernel/state.json`
- **contratos formais** em `contracts/`
- **execução por tarefas** via `scripts/ruptur.sh`
- **trilha operacional** em `registry/runs/` e `logs/execution.log`
- **runtime efêmero separado** em `.agents/runtime/` e `state/snapshots/`

Na prática, isso significa que o diretório fica preparado para:

- inicializar a própria estrutura com `init`
- validar tasks antes de executar com `validate`
- executar tasks simples e rastreáveis com `run`
- expor seu estado atual com `status`
- checar saúde estrutural com `doctor`
- limpar runtime efêmero com `clean`
- resetar artefatos operacionais com `reset`

## O que ele tem de diferente de um diretório comum

Um diretório comum apenas armazena arquivos. Um diretório criado com este framework também:

- sabe em que estado operacional está
- mantém histórico de execução
- registra logs e resultados
- pode ser operado por CLI de forma previsível
- pode ser entendido por humano ou agente sem contexto prévio
- pode ser recriado em outra máquina com baixa fricção

## Superpoderes que o framework entrega

### 1. Estado canônico
O diretório tem uma fonte de verdade para execução atual em `kernel/state.json`.

### 2. Execução auditável
Toda execução pode deixar rastro em:

- `logs/execution.log`
- `registry/runs/`

### 3. Operação declarativa
O trabalho pode ser descrito em tasks JSON, validadas e executadas por um fluxo padrão.

### 4. Compatibilidade com automação e IA
O diretório já nasce com convenções claras para:

- entrada de tarefas
- validação
- execução
- leitura de estado
- limpeza de runtime

### 5. Portabilidade
O núcleo não depende de ferramentas externas para o fluxo básico e pode ser inicializado com:

```bash
bash scripts/ruptur.sh init
```

### 6. Separação limpa de responsabilidades
- `kernel/` guarda estado canônico
- `contracts/` guarda contratos formais
- `templates/` guarda pontos de partida
- `registry/`, `state/` e `.agents/` guardam runtime e trilha operacional

## O que ele ainda não faz sozinho

O framework já entrega operação básica, estado, contratos, CLI e rastreabilidade. O que ele **não** entrega automaticamente é a lógica específica do seu domínio.

Exemplos:

- um projeto de infraestrutura ainda precisa de tasks reais de provisionamento
- um projeto de IaC ainda precisa de módulos, playbooks ou scripts específicos
- integrações externas continuam opcionais e entram depois, via `adapters/` ou tasks próprias

## Resultado

Comandos simples, estado explícito e base limpa para qualquer máquina ou pipeline.
>>>>>>> d47f5b0 (chore: commit inicial do infrastructure-state até a tranche 2)
