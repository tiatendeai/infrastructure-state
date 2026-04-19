# 🤖 Guia de Modelos — Claude Code via OpenRouter

## Estrutura das Variáveis

O Claude Code usa estas variáveis para escolher modelos em diferentes contextos:

| Variável | Contexto de uso |
|---|---|
| `ANTHROPIC_MODEL` | Modelo principal para coding e chat |
| `ANTHROPIC_SMALL_FAST_MODEL` | Modelo rápido para tarefas leves |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Quando o Claude Code quer o modelo "mais capaz" |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Quando quer um modelo "balanceado" |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Quando quer o modelo "mais rápido/barato" |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Modelo usado por sub-agentes delegados |

---

## ✅ Configuração Ativa Agora (`settings.local.json`)

```json
"ANTHROPIC_DEFAULT_OPUS_MODEL":   "z-ai/glm-5",
"ANTHROPIC_DEFAULT_SONNET_MODEL": "minimax/minimax-m2.7",
"ANTHROPIC_DEFAULT_HAIKU_MODEL":  "google/gemini-3.1-flash-lite-preview",
"CLAUDE_CODE_SUBAGENT_MODEL":     "google/gemini-3-flash-preview"
```

---

## 🆓 Modelos FREE TIER (orçamento zero, tudo testado e existente)

### ⭐⭐⭐ Top picks da comunidade

| Modelo | Context | Por que usar |
|---|---|---|
| `qwen/qwen3-coder:free` | 262k | 🏆 **O "poney"** — mais badalado agora pra código, toda a comunidade usando |
| `qwen/qwen3-next-80b-a3b-instruct:free` | 262k | Qwen 3 80B — raciocínio forte, grátis |
| `openai/gpt-oss-120b:free` | 131k | GPT open source 120B — gigante e grátis |
| `openai/gpt-oss-20b:free` | 131k | GPT open source menor, mais rápido |
| `meta-llama/llama-3.3-70b-instruct:free` | 65k | Llama 70B — clássico confiável, muito usado |
| `nousresearch/hermes-3-llama-3.1-405b:free` | 131k | Hermes 405B — ENORME, grátis |

### 🎯 Free com specialização

| Modelo | Context | Por que usar |
|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | 262k | NVIDIA 120B — MoE eficiente |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256k | NVIDIA Nano — rápido |
| `google/gemma-4-31b-it:free` | 262k | Gemma 4 — Google grátis |
| `google/gemma-4-26b-a4b-it:free` | 262k | Gemma 4 menor |
| `minimax/minimax-m2.5:free` | 196k | MiniMax grátis (irmão do m2.7 pago) |
| `z-ai/glm-4.5-air:free` | 131k | GLM 4.5 grátis (irmão do glm-5 pago) |
| `stepfun/step-3.5-flash:free` | 256k | Step Flash — rápido e grátis |
| `openrouter/free` | 200k | Modelo livre do próprio OpenRouter |
| `arcee-ai/trinity-large-preview:free` | 131k | Trinity Large — grátis |

---

## 💰 Modelos Pagos Recomendados (low-cost)

| Modelo | Contexto | Custo aprox. |
|---|---|---|
| `anthropic/claude-sonnet-4-5` | 200k | $$$ — Melhor para coding |
| `minimax/minimax-m2.7` | 1M | $$ — Excelente custo-benefício |
| `z-ai/glm-5` | 128k | $ — Barato e capaz |
| `google/gemini-3.1-flash-lite-preview` | 1M | $ — Ultra rápido e barato |
| `google/gemini-3-flash-preview` | 1M | $$ — Mais capaz que o lite |
| `openai/gpt-4o-mini` | 128k | $ — OpenAI econômico |
| `openai/o4-mini` | 200k | $$ — OpenAI com raciocínio |
| `perplexity/sonar` | 200k | $$ — Com busca na web |
| `perplexity/sonar-pro` | 200k | $$$ — Busca web avançada |

---

## 🔀 Estratégias de Uso

### Estratégia FREE-FIRST (orçamento zero)
```json
"ANTHROPIC_MODEL":                "qwen/qwen3-coder:free",
"ANTHROPIC_SMALL_FAST_MODEL":     "google/gemini-3.1-flash-lite-preview",
"ANTHROPIC_DEFAULT_OPUS_MODEL":   "openai/gpt-oss-120b:free",
"ANTHROPIC_DEFAULT_SONNET_MODEL": "qwen/qwen3-next-80b-a3b-instruct:free",
"ANTHROPIC_DEFAULT_HAIKU_MODEL":  "google/gemma-4-31b-it:free",
"CLAUDE_CODE_SUBAGENT_MODEL":     "meta-llama/llama-3.3-70b-instruct:free"
```

### Estratégia DO AMIGO (nomenclatura original, modelos testados)
```json
"ANTHROPIC_DEFAULT_OPUS_MODEL":   "z-ai/glm-5",
"ANTHROPIC_DEFAULT_SONNET_MODEL": "minimax/minimax-m2.7",
"ANTHROPIC_DEFAULT_HAIKU_MODEL":  "google/gemini-3.1-flash-lite-preview",
"CLAUDE_CODE_SUBAGENT_MODEL":     "google/gemini-3-flash-preview"
```

### Estratégia ESCALADA (começa free, sobe quando necessário)
```json
"ANTHROPIC_MODEL":                "anthropic/claude-sonnet-4-5",
"ANTHROPIC_SMALL_FAST_MODEL":     "google/gemini-3.1-flash-lite-preview",
"ANTHROPIC_DEFAULT_OPUS_MODEL":   "openai/o4-mini",
"ANTHROPIC_DEFAULT_SONNET_MODEL": "minimax/minimax-m2.7",
"ANTHROPIC_DEFAULT_HAIKU_MODEL":  "meta-llama/llama-3.3-70b-instruct:free",
"CLAUDE_CODE_SUBAGENT_MODEL":     "qwen/qwen3-coder:free"
```

---

## 🔑 Para adicionar suas chaves diretas

Coloque no `settings.local.json`:
```json
"OPENAI_API_KEY":      "sk-...",
"OPENAI_BASE_URL":     "https://api.openai.com/v1",
"PERPLEXITY_API_KEY":  "pplx-...",
"PERPLEXITY_BASE_URL": "https://api.perplexity.ai"
```

> **Nota:** Para o Claude Code usar um modelo específico do OpenAI ou Perplexity via OpenRouter, 
> basta colocar o ID no ANTHROPIC_DEFAULT_* correspondente. A `ANTHROPIC_BASE_URL` do OpenRouter
> já dá acesso a todos os providers sem precisar de chave separada.
