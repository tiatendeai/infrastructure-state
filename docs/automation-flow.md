# Automation Flow

## Fluxo-alvo

`Linear -> n8n -> Antigravity -> Git -> Deploy -> Observabilidade -> state`

## Escopo desta tranche

Esta tranche **não** implementa o fluxo completo. Ela prepara o terreno para isso.

O que entra agora:

- modelagem documental do fluxo
- contrato issue -> task
- task runner auditável
- evidência local de execução

O que fica para depois:

- webhook/polling do Linear
- orquestração no n8n
- retorno automático de evidência ao Linear
- trilha Git/PR automatizada
- observabilidade e promotion flow

## Fronteira atual

Hoje, o fluxo real já cobre:

`issue mapeada -> task local -> context packet -> memory retrieval local -> execução -> registry/log/state -> update Linear`

## Fronteira futura

Quando a automação entrar, o fluxo passará a ser:

1. Linear cria/comanda a demanda
2. n8n classifica e enriquece
3. Antigravity executa neste repositório
4. Git registra quando aplicável
5. observabilidade acompanha
6. state guarda a trilha canônica
7. Linear recebe status e resumo operacional

## Regra operacional

Enquanto webhook/n8n ainda não entram:

- usar o adapter nativo do Linear como superfície oficial de update
- usar `registry/linear-mapping.yaml` como vínculo issue ↔ task
- usar o state local como verdade operacional
