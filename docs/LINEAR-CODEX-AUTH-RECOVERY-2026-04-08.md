# Linear no Codex — recuperação oficial do acesso do ecossistema

Data: 2026-04-08

## Status

**Resolvido.** O acesso do ecossistema ao Linear voltou a funcionar pelo fluxo oficial do Codex com o MCP oficial do Linear.

## Diagnóstico real

O problema não era falta de login humano no navegador.

O gargalo estava no caminho de integração:

- sessão antiga/stale do MCP em algumas sessões
- adapter local ainda em `local_only`
- falsa sensação de que browser logado equivalia a integração autenticada

## Solução que funcionou

```bash
codex mcp login linear
```

Após autorizar no browser já autenticado, o Codex passou a operar o Linear corretamente em sessão nova.

## Como validar

Usar sessão nova do Codex e consultar o Linear de fato. Não confiar só na aba do browser.

## Evidência validada

### Workspace / Team

- Workspace: `Ruptur`
- Team: `INFRA`

### Projeto

- Projeto: `Bet A.I.`
- Project ID: `856c8e7a-53f6-4f73-8602-eff2faa2484e`
- URL: https://linear.app/ruptur/project/bet-ai-c409d3bc2513

### Issues iniciais confirmadas

- `INF-25` — Bet A.I. Platform Bootstrap
- `INF-26` — BetBoom Watchdog & Debug No-Submit
- `INF-27` — Robo Window Onboarding Wizard
- `INF-28` — Will Dados Pro Control Plane

## Regra canônica do ecossistema

1. usar o MCP oficial do Linear no Codex
2. autenticar com `codex mcp login linear`
3. validar em sessão nova quando houver dúvida
4. usar browser apenas como apoio humano
5. usar API key só para adapter headless, scripts e contingência

## Impacto

Isso remove o Linear como bloqueio estrutural para os repositórios do ecossistema.
