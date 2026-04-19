---
activation: always
description: Regras e contexto permanente do Projeto IA Jurídica Dr. Flávio (MVP). Sempre ativo em qualquer conversa neste workspace.
---

# Projeto – IA Jurídica Dr. Flávio (MVP)

## Contexto do Projeto

- **Cliente**: Dr. Flávio Rodrigo (advogado trabalhista, Grande BH)
- **Responsável técnico**: Diego (Zaya / TI Atende AI)
- **Objetivo**: Gerar leads qualificados via WhatsApp com triagem por IA e direcionar para atendimento jurídico humano
- **Fase atual**: MVP — validação rápida. Não otimizar, não escalar, não reinventar.
- **Prazo original**: 3 dias para rodar

## ⚙️ Governança de Workflows (REGRA CRÍTICA)

```
PROD (hJ43Lnwg1nxzqpxc) → MODELO DE REFERÊNCIA — NUNCA MODIFICAR
DEV  (oZaITKQjdW4KnTf7) → ONDE TODA EVOLUÇÃO ACONTECE
LOCAL (workflows/dr_flavio_dev.json) → ONDE TRABALHAMOS
```

### Fluxo de Trabalho Obrigatório

1. **Editar sempre** o arquivo local `workflows/dr_flavio_dev.json`
2. **Testar**: executar `workflows/sync_dev.sh` para subir ao n8n DEV
3. **Validar** os testes no n8n DEV (`https://n8n.atendezaya.com/workflow/oZaITKQjdW4KnTf7`)
4. **PROD**: nunca alterar diretamente — apenas quando o DEV estiver aprovado e Diego autorizar

### Arquivos Locais dos Workflows

| Arquivo | Propósito |
|---|---|
| `workflows/dr_flavio_dev.json` | Cópia de trabalho do DEV (sempre atualizada) |
| `workflows/dr_flavio_prod_reference.json` | Snapshot do PROD — modelo congelado, não editar |
| `workflows/sync_dev.sh` | Script de push local → n8n DEV |

## Estratégia de Funil

```
Meta Ads → WhatsApp → IA (qualificação) → Resumo → Atendimento humano (Dr. Flávio)
```

## Infraestrutura

| Componente | Detalhe |
|---|---|
| **n8n** | `https://n8n.atendezaya.com` — workflows de automação |
| **PROD workflow** | ID `hJ43Lnwg1nxzqpxc` — referência congelada |
| **DEV workflow** | ID `oZaITKQjdW4KnTf7` — ambiente de evolução |
| **Workflow criarTag** | ID `edOuFjTpR3ME3Lux` — chamado como tool pela Alice |
| **Notion** | Página do MVP — ID `3331b632-c5e8-80e5-bdec-d562ba79fefd` |
| **AtendéZaya API** | `api.atendezaya.com/v2/api/external/c8f2f11c-711a-46f8-a1b1-f62df2ae9c80` |
| **PostgreSQL** | Banco `atendezaya` — tabelas: `Tickets`, `Messages` |
| **AI Model** | OpenAI `gpt-5-nano` — credencial `NegDigitais` (ID: `qmuIz6UC9bVjp4zQ`) |
| **DataTable n8n** | `controleFollowUp_Produtosdigitais` — projeto `H1QTWucyTzYZRQlj` |

## Arquitetura dos Workflows

### Fluxo Principal (tempo real)
```
[Webhook POST] → [If fromMe=false AND status=pending]
    ↓ TRUE
[Edit Fields] → [AI Agent (Alice)] → [HTTP Request → AtendéZaya API]
                      ↓ (tool)
                [toolWorkflow: criarTag → workflow edOuFjTpR3ME3Lux]
    ↓ FALSE
[No Operation]
```

### Fluxo de Follow-up (agendado a cada 59 min)
```
[Schedule Trigger] → [DataTable GET controleFollowUp]
    ↓
[Code JS: calcula tempo em SP] → [Switch: roteia por 2h/24h/48h/72h/96h/120h]
    ↓ (cada ramo)
[Postgres SELECT Tickets] → [Postgres SELECT Messages]
    ↓
[Code JS: verifica frases mapeadas] → [HTTP Request /addTag → AtendéZaya]
```

## Fluxo Obrigatório da IA (Alice)

A IA deve seguir este fluxo **exatamente**, sem desvios:

1. Saudação
2. Pergunta faturamento → *"Qual é o faturamento médio mensal da sua empresa?"*
3. Pergunta funcionários → *"Quantos funcionários você possui atualmente?"*
4. Pergunta registro → *"Todos os funcionários estão registrados em carteira?"*
5. Pergunta crescimento → *"Sua empresa está em crescimento neste momento?"*
6. Pergunta histórico → *"Você já teve algum problema trabalhista ou preocupação recente?"*
7. Classificação de risco
8. Geração de resumo
9. Convite para falar com o advogado

## Regras Rígidas da IA

- 1 pergunta por vez
- Respostas curtas e diretas
- Não explicar demais
- Não fugir do fluxo
- Não inventar perguntas extras
- Encerrar após resumo + convite

## Lógica de Classificação de Risco

| Nível | Critérios |
|---|---|
| 🔴 **Alto Risco** | Funcionário sem registro + 3 ou mais funcionários + empresa em crescimento |
| 🟡 **Médio Risco** | Funcionários registrados + crescimento ativo |
| 🟢 **Baixo Risco** | Todos registrados + sem crescimento + sem histórico de problemas |

## Público-Alvo (Meta Ads)

- Empresários da Grande BH
- Faturamento acima de R$50.000/mês
- Possuem funcionários
- Possível risco trabalhista (crescimento desorganizado, sem registro)

## Scripts de Deploy

```bash
# Sincronizar workflow local → n8n produção
/Users/diego/Documents/GitHub/zaya/scripts/n8n_sync.sh
```

## Regra de Idioma

Toda comunicação com Diego deve ser em **português do Brasil (pt-BR)**, exceto código, nomes de variáveis, APIs e comandos técnicos.
