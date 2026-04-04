# Memory Adapter

Camada local de memória do `infrastructure-state`.

Objetivo nesta tranche:

- formalizar uma interface única de memória
- separar memória curta, memória longa e contexto efêmero
- operar apenas em modo local/control-plane/stub

Backends previstos:

- `mock`: backend local para testes estruturais
- `redis`: memória curta / cache contextual / estado efêmero
- `supabase`: memória longa / persistência canônica / busca estruturada

Restrições da tranche 3A:

- sem conexão real com Redis
- sem conexão real com Supabase
- sem gravação em produção
- sem segredos hardcoded

Arquivos principais:

- `interface/memory.py`: contrato local + backend mock
- `short_term/redis_client.py`: stub de Redis
- `long_term/supabase_client.py`: stub de Supabase
- `policy/promotion_rules.yaml`: regras declarativas de promoção
- `fixtures/sample_memories.json`: memórias de exemplo para validação local
