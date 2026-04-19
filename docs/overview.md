# Visão Geral

O framework separa:

- **kernel**: somente o estado canônico
- **contracts**: contratos formais de task e state
- **runtime**: `registry/runs/`, `state/snapshots/`, `logs/`
- **templates**: pontos de partida reutilizáveis
- **adapters**: integrações opcionais e desacopladas

A meta é garantir que qualquer pessoa ou agente consiga iniciar, executar e limpar o ambiente com poucos comandos.
