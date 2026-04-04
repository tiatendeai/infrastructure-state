# Memory Layer

## Objetivo

A memory layer existe para separar claramente:

- memória curta e contextual
- memória longa e canônica
- contexto efêmero de execução

Nesta tranche, a camada é apenas **local/stub/control-plane**.

## Papéis previstos

### Redis

Papel futuro:

- memória curta
- cache contextual
- estado efêmero
- recuperação rápida

### Supabase

Papel futuro:

- memória longa
- persistência canônica
- indexação e busca estruturada
- base para recuperação futura por embeddings/pgvector

## Princípios

- runtime bruto não vira memória canônica automaticamente
- memória canônica não substitui evidência operacional bruta
- contexto de execução deve ser pequeno e derivado de fatos úteis
- nenhum backend real é ativado nesta tranche

## Backends desta tranche

- `mock`: funcional localmente para validação estrutural
- `redis`: stub sem ativação real
- `supabase`: stub sem ativação real
