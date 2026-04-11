# Linear Event Model

## Objetivo

Definir o modelo nativo de eventos do Linear para sincronização entre:

- Linear
- n8n
- `infrastructure-state`
- futura orquestração do Jarvis

## Decisão principal

O mecanismo oficial e prioritário para reagir a mudanças no Linear deve ser:

- **webhook oficial do Linear**

Polling entra apenas como:

- reconciliação
- backfill
- recuperação de falha
- verificação periódica de consistência

## O que os webhooks do Linear cobrem

O Linear envia webhooks para eventos de criação, atualização e remoção. Para o nosso caso, os recursos mais importantes são:

- `Issue`
- `Issue comments`
- `Projects`
- `Project updates`
- `Issue labels` (se necessário)

Também existem eventos auxiliares como `OAuthApp revoked`.

## Escopo dos webhooks

Os webhooks são específicos por organização, mas podem ser configurados para:

- um único team
- todos os public teams

Isso encaixa bem com o nosso cenário atual do team `INFRA` e também com futura expansão para múltiplos times/projetos.

## Requisitos operacionais do endpoint

O consumer de webhook precisa:

- estar em URL pública HTTPS
- responder `200 OK`
- responder em até 5 segundos

Se falhar, o Linear tenta novamente com backoff:

- após 1 minuto
- após 1 hora
- após 6 horas

Se o endpoint continuar falhando, o webhook pode ser desabilitado manualmente.

## Segurança do webhook

O Linear recomenda validar:

1. **assinatura HMAC-SHA256** no header `Linear-Signature`
2. **timestamp** do payload (`webhookTimestamp`) para evitar replay
3. opcionalmente, **IP de origem**

### Regras recomendadas para o Ruptur

- validar a assinatura sobre o **raw body**
- rejeitar payload fora de uma janela curta, por exemplo 60s
- logar `Linear-Delivery` como id de entrega
- tornar o processamento idempotente por `Linear-Delivery` + `webhookTimestamp`

## Campos do payload relevantes

Os webhooks de data change trazem campos úteis para o nosso modelo:

- `action` — `create`, `update`, `remove`
- `type` — entidade afetada
- `actor` — usuário, app OAuth ou integração
- `data` — estado serializado atual
- `updatedFrom` — valores anteriores nas mudanças
- `url` — URL da entidade no Linear
- `webhookTimestamp` — instante de envio

Isso é suficiente para alimentar:

- espelho local de metadados
- reconciliação de mapping
- automações por regra
- auditoria básica de sincronização

## Modelo recomendado de fluxo

## Fluxo principal

`Linear Webhook -> n8n ingress -> validação de assinatura -> normalização -> roteamento -> adapter local -> state/registry/log -> retorno opcional ao Linear`

## Responsabilidade por camada

### Linear

- gera o evento oficial
- mantém a verdade sobre issue/projeto/status

### n8n

- recebe e valida o webhook
- faz roteamento e enriquecimento
- desacopla recepção de execução

### `infrastructure-state`

- resolve vínculo issue ↔ task
- executa trabalho local/auditável
- grava trilha em `registry/`, `logs/` e `kernel/state.json`

### Jarvis

- decide políticas de automação
- coordena jobs compostos
- chama adapter e/ou workflows do n8n

## Modelo de sincronização issue ↔ task ↔ mapping

## Fonte de verdade por domínio

- **Issue live:** Linear
- **Vínculo local:** `registry/linear-mapping.yaml`
- **Execução:** task local
- **Evidência:** `registry/runs/*`, `logs/execution.log`, `kernel/state.json`

## Campos que o mapping deve consolidar

Sugestão de evolução do mapping local:

- `organization_id`
- `team_id`
- `team_key`
- `project_id`
- `linear_issue_identifier`
- `linear_issue_uuid`
- `backlog_key`
- `local_task`
- `last_seen_updated_at`
- `last_webhook_delivery`
- `last_sync_status`

## Papel do polling

Polling deve ser restrito a um job de reconciliação, por exemplo:

- consultar issues ordenadas por `updatedAt`
- aplicar filtro por team/projeto/intervalo
- atualizar o espelho local apenas quando necessário

Nunca usar polling por issue individual nem como motor principal de automação.

## Papel do MCP

Para o modelo de eventos, o MCP não entra no caminho principal.

Uso aceitável:

- leitura interativa por agente humano
- inspeção assistida em IDE
- contingência operacional pontual

Uso não recomendado:

- ingestion de evento
- automação headless
- sincronização contínua
- backbone entre sistemas

## Proposta para a próxima tranche

## TRANCHE L1 — Linear Native Adapter Foundation

Implementar:

- adapter headless em `adapters/linear/`
- operações GraphQL mínimas
- resolução de ids/identifiers locais
- leitura e escrita controladas
- contrato de saída JSON estável
- integração posterior com consumer de webhook do n8n

## Referências oficiais

- Webhooks: https://linear.app/developers/webhooks
- GraphQL / Getting started: https://linear.app/developers/graphql
- Pagination: https://linear.app/developers/pagination
- Filtering: https://linear.app/developers/filtering
- API and Webhooks: https://linear.app/docs/api-and-webhooks
