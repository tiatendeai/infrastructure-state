# Adapter: llm

Ponto de integração opcional para provedores de modelos.

## Prompt envelope canônico

Quando um consumidor de IA do Shipyard precisar montar chamadas para um modelo, o fluxo recomendado é:

1. ler `state/runtime/<task_id>/prompt-envelope.json`
2. usar `adapters/llm/prompt_envelope.py` para compor as mensagens
3. preservar `strict`, `context_budget` e `whitelisted_context_refs`

O helper de linha de comando fica em:

```bash
python3 scripts/compose_prompt_request.py --envelope state/runtime/<task_id>/prompt-envelope.json --prompt "ping"
```

O atalho canônico no Shipyard fica em:

```bash
bash scripts/ruptur.sh llm compose --envelope state/runtime/<task_id>/prompt-envelope.json --prompt "ping"
```

Para enviar a chamada a um endpoint OpenAI-compatible:

```bash
python3 scripts/llm_chat_from_envelope.py --envelope state/runtime/<task_id>/prompt-envelope.json --prompt "ping" --dry-run
```

ou:

```bash
bash scripts/ruptur.sh llm chat --envelope state/runtime/<task_id>/prompt-envelope.json --prompt "ping" --dry-run
```

Remova `--dry-run` e ajuste `LLM_BASE_URL` / `LLM_API_KEY` quando quiser executar de verdade.

## Hugging Face / FLUX.1

Para geração de imagem via Hugging Face, use:

```bash
python3 scripts/generate_flux_image.py
```

O script foi pensado para um caso simples: gerar uma fazenda realista com FLUX.1, mas aceita prompt e parâmetros customizados por CLI.
