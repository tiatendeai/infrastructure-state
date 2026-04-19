---
activation: always
description: Bússola Técnica do Projeto Zaya. O Agente NUNCA deve tomar decisões técnicas baseadas em suposições. Sempre consulte a documentação oficial via Context7 antes de agir.
---

# Bússola Técnica — Regra de Decisão Baseada em Documentação

## O Princípio Fundamental

> **Nunca opere no escuro.**
> Antes de criar, modificar ou configurar qualquer componente técnico, consulte a documentação oficial da tecnologia envolvida via Context7.
> Se a documentação não puder ser encontrada, informe Diego antes de agir.

Este projeto usa tecnologias reais em produção. Erros causados por suposições incorretas afetam leads reais do Dr. Flávio. **A documentação é a fonte da verdade, não a memória de treinamento do modelo.**

---

## Como Usar o Context7 (Fluxo Obrigatório)

Sempre que for realizar uma ação técnica:

```
Passo 1 → mcp_context7-api_resolve-library-id   (encontrar a biblioteca correta)
Passo 2 → mcp_context7-api_query-docs            (consultar a documentação específica)
Passo 3 → Aplicar exatamente o que a doc diz     (sem improvisar)
```

---

## Stack Atual do Projeto — Bibliotecas Prioritárias

Consulte estas bibliotecas antes de qualquer ação relacionada:

| Tecnologia | Quando Consultar | Library ID no Context7 |
|---|---|---|
| **n8n** | Criar/editar nós, configurar workflows, entender parâmetros | `/n8n-io/n8n-docs` |
| **Notion API** | Ler/escrever páginas, propriedades, blocos via MCP | `/makenotion/notion-mcp-server` |
| **Antigravity** | Regras, skills, workflows, MCPs, artifacts | `/alphaperseii3000/google-antigravity-docs` |

---

## Stack Futura e Outras Tecnologias

Para qualquer outra tecnologia que entrar no projeto, aplique o mesmo fluxo:

```
1. Identifique a tecnologia (ex: "estou configurando um nó HTTP Request no n8n")
2. Execute resolve-library-id para encontrar a documentação
3. Execute query-docs para buscar a regra/padrão específico
4. Aplique a solução baseada na documentação
```

### Exemplos de busca para tecnologias comuns do projeto:

```bash
# JSON Schema (usado extensivamente no n8n)
resolve-library-id → "JSON Schema specification"

# WhatsApp / Baileys (integração de mensagens)
resolve-library-id → "baileys whatsapp nodejs"

# OpenAI / LangChain (modelos de IA no n8n)
resolve-library-id → "langchain n8n ai agent"

# Meta Ads API (tráfego pago)
resolve-library-id → "meta marketing api facebook ads"

# Node.js / Express (se usado em integrações customizadas)
resolve-library-id → "nodejs express api"
```

---

## Regras Específicas por Tecnologia

### n8n (Regra Crítica)
- O n8n usa **JSON** para praticamente tudo: expressões, configurações de nós, payloads
- Antes de escrever qualquer expressão n8n (ex: `{{ $json.campo }}`), verifique a sintaxe na doc
- Antes de configurar um nó **AI Agent**, **HTTP Request** ou **Code**, busque os parâmetros exatos
- Nunca assuma que um campo existe no `$json` sem validar com a estrutura real do workflow

### Notion API
- A API do Notion tem tipos de blocos com estruturas JSON específicas (rich_text, paragraph, heading, etc.)
- Sempre consulte antes de criar ou atualizar blocos para garantir a estrutura correta

### JSON em Geral
- Valide sempre a estrutura antes de enviar payloads
- Use a documentação da API destino para confirmar os campos obrigatórios e opcionais

---

## O Que Fazer Quando o Context7 Não Encontrar

1. Informe Diego que a documentação não está disponível no Context7
2. Proponha buscar via `search_web` como alternativa
3. **Nunca prossiga com suposições** em ações que afetam produção

---

## Expansão Contínua

À medida que novas tecnologias entrarem no projeto, adicione-as neste arquivo com:
- O nome da tecnologia
- Quando consultar
- O Library ID do Context7 (via `resolve-library-id`)
