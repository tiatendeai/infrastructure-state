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

Hoje, o fluxo real termina em:

`task local -> execução -> registry/log/state`

## Fronteira futura

Quando a automação entrar, o fluxo passará a ser:

1. Linear cria/comanda a demanda
2. n8n classifica e enriquece
3. Antigravity executa neste repositório
4. Git registra quando aplicável
5. observabilidade acompanha
6. state guarda a trilha canônica
7. Linear recebe status e evidência

## Regra operacional

Enquanto o fluxo completo não existir:

- documentar claramente o que é manual
- não fingir automação inexistente
- usar o state local como verdade operacional
