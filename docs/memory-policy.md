# Promotion Policy de Memória

## Camadas

### raw_event
- evento bruto local
- retenção curta
- não sobe para o Linear
- pode permanecer apenas em logs, runs e snapshots

### summary
- resumo operacional limpo
- pode alimentar comentário/status no Linear
- não deve carregar payloads sensíveis

### canonical_memory
- fatos persistentes e reutilizáveis
- deve representar decisões, capacidades, mapeamentos e contratos estáveis

### context_packet
- montagem efêmera para a execução atual
- não substitui memória canônica
- não recebe histórico bruto despejado

## Promover para canonical_memory quando houver
- decisão arquitetural
- mapeamento de serviço
- convenção de naming
- vínculo issue ↔ task
- capability observada ou validada
- requisito de integração sem expor segredo

## Não promover
- logs brutos
- stack traces transitórios
- payloads sensíveis
- runtime efêmero
- falhas episódicas sem relevância estrutural

## Regra operacional

- Linear recebe somente resumo limpo
- runtime bruto fica no repositório
- memory layer serve para retenção útil e recuperação seletiva
