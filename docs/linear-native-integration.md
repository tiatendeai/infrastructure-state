# Linear Native Integration

## TRANCHE L0 — Linear Native Integration Discovery

Data: 2026-04-03

## Objetivo

Documentar o caminho **canônico, nativo e suportado pelo Linear** para integrar o `infrastructure-state` ao workspace Ruptur sem depender de browser automation, MCP de sessão ou hacks operacionais.

## Premissas

- `infrastructure-state` é o plano de execução e auditoria.
- Linear é a camada de governança operacional.
- O backbone da integração deve ser **API oficial + autenticação oficial + webhooks oficiais**.
- MCP e browser podem existir no máximo como ferramentas auxiliares de operação humana, nunca como fundação.

## Respostas objetivas da tranche

### 1) Token pessoal, OAuth ou combinação?

**Decisão:** **combinação com papéis diferentes**.

- **Fundação canônica para automação compartilhada:** **OAuth 2.0**.
- **Modo recomendado para agentes/serviços:** **OAuth com `actor=app`**.
- **Modo server-to-server sem fluxo interativo:** **OAuth `client_credentials`**, quando o app estiver configurado para isso.
- **Uso aceitável de token pessoal:** apenas **bootstrap local, descoberta inicial, debug e break-glass**.

### 2) GraphQL direto ou `@linear/sdk`?

**Decisão:**

- **Fundação nativa do Linear:** **GraphQL API oficial**.
- **Cliente recomendado pelo Linear quando a implementação for TypeScript:** `@linear/sdk`.
- **Para este repositório, a recomendação prática é GraphQL direto**, porque o núcleo atual é Bash + Python e não vale acoplar a fundação a Node apenas para operar 5–10 chamadas.

> Esta última conclusão é uma **inferência arquitetural para o nosso repo**, não uma afirmação universal do Linear.

### 3) Webhooks oficiais cobrem o fluxo com Linear, n8n e `infrastructure-state`?

**Sim.** O modelo oficial de webhooks do Linear cobre bem o fluxo desejado:

- criação, atualização e remoção de issues
- comentários
- projetos
- project updates
- labels e outros eventos úteis

Além disso:

- webhooks podem ser por organização, por time único ou para todos os times públicos
- OAuth apps podem registrar webhooks como parte da instalação
- o Linear recomenda **webhooks em vez de polling** para acompanhar mudanças

### 4) O MCP oficial do Linear é fundação, opcional ou contingência?

**Decisão:** **opcional/contingência**, nunca fundação.

Motivos:

- o próprio material oficial do Linear para MCP informa que conexões remotas ainda estão em estágio inicial e podem falhar ou exigir múltiplas tentativas
- MCP atende bem fluxos interativos com IDE/agente
- não é o caminho mais estável para uma integração operacional reprodutível entre sistema local, n8n e orquestração futura

### 5) Modelo nativo ideal para as operações principais

#### Listar issues

Usar `issues(...)` ou `team(id) { issues(...) }` na GraphQL API com:

- filtros oficiais (`filter`)
- paginação cursor-based (`first`, `after`)
- ordenação por `updatedAt` quando houver reconciliação incremental

#### Atualizar status

Usar `issueUpdate(id, input: { stateId })`.

Observação importante:

- status no Linear é representado por **workflow state**
- portanto, a transição de status deve trabalhar com **`stateId`**, não com string solta

#### Adicionar comentário

Usar `commentCreate` na GraphQL API, ou `createComment` se a implementação for via SDK.

#### Listar projects

Usar `projects(...)` com paginação e, quando necessário, filtros.

#### Listar issue statuses

Usar `workflowStates` como fonte nativa de statuses/workflow states.

#### Sincronizar issue ↔ task ↔ mapping

Modelo recomendado:

- **Linear** continua sendo verdade para a issue viva
- **`registry/linear-mapping.yaml`** vira a tabela de vínculo local
- **task local** continua sendo a unidade executável
- **webhook** vira o gatilho de ingestão de mudança
- **polling** fica só para reconciliação controlada e backfill

## Decisões técnicas explícitas

| Tema | Decisão |
|---|---|
| Autenticação | **OAuth 2.0** como backbone; token pessoal só para uso local/contingência |
| Ator de automação | **`actor=app`** para agentes/serviços |
| Server-to-server | **`client_credentials`** quando não houver fluxo interativo |
| Superfície da API | **GraphQL oficial** |
| SDK vs GraphQL | **GraphQL direto no `infrastructure-state`**; SDK só se o adapter nascer em TypeScript |
| Eventos | **Webhooks oficiais** |
| Polling | Apenas reconciliação e backfill restritos |
| MCP | **Opcional/contingência**, não backbone |

## Modelo nativo recomendado para o ecossistema Ruptur

## 1. `infrastructure-state`

Responsável por:

- executar operações locais e auditáveis
- materializar tasks
- persistir `kernel/state.json`
- persistir evidência em `registry/runs/` e `logs/execution.log`
- hospedar o adapter oficial do Linear

## 2. `registry/linear-mapping.yaml`

Responsável por manter o vínculo local entre:

- `workspace`
- `team`
- `project`
- `linear_issue_identifier` (ex.: `INF-13`)
- `linear_issue_uuid`
- `backlog_key` local (ex.: `INFRA-013`)
- `local_task`

Regra proposta:

- **mapping local = join table canônica do repo**
- **estado live da issue = API do Linear**

## 3. n8n

Responsável por:

- receber webhook do Linear
- validar assinatura
- normalizar evento
- acionar o adapter local ou fila/orquestração interna
- postar retorno estruturado quando aplicável

## 4. Jarvis

Responsável por:

- coordenar decisões e fluxos de maior nível
- chamar o adapter headless do Linear
- correlacionar issue ↔ task ↔ evidência ↔ automações futuras

## Papel do polling

Polling **não** deve ser o mecanismo principal.

Uso permitido:

- bootstrap inicial do espelho local
- reconciliação agendada de baixo volume
- recuperação após falha de webhook
- auditoria comparativa por `updatedAt`

## Papel do MCP

MCP do Linear deve ser tratado como:

- útil para IDE/agente em contexto interativo
- conveniente para consulta humana assistida
- inadequado como contrato-base entre sistemas

## Proposta da próxima tranche

## TRANCHE L1 — Linear Native Adapter Foundation

Escopo sugerido, agora já alinhado com o caminho nativo descoberto:

- `adapters/linear/`
- autenticação oficial por OAuth/app token e fallback local por personal API key
- client GraphQL local e headless
- operações mínimas:
  - `get_issue`
  - `list_issues`
  - `update_issue_status`
  - `add_comment`
  - `list_projects`
  - `list_workflow_states`
- resolução local de referências entre:
  - backlog key local
  - issue identifier do Linear
  - UUID do Linear
- documentação de configuração
- integração futura com webhook consumer do n8n

## Referências oficiais

- Linear Developers: https://linear.app/developers
- GraphQL API / Getting started: https://linear.app/developers/graphql
- Filtering: https://linear.app/developers/filtering
- Pagination: https://linear.app/developers/pagination
- OAuth 2.0 authentication: https://linear.app/developers/oauth-2-0-authentication
- OAuth actor authorization: https://linear.app/developers/oauth-actor-authorization
- Webhooks: https://linear.app/developers/webhooks
- API and Webhooks (workspace docs): https://linear.app/docs/api-and-webhooks
- Cursor MCP Integration: https://linear.app/integrations/cursor-mcp
