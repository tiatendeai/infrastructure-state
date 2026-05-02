from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_SYSTEM_PROMPT = "Você está operando dentro do Shipyard."
DEFAULT_DEVELOPER_PROMPT = "Responda de forma objetiva, canônica e alinhada ao State."


def load_prompt_envelope(path: str | Path) -> dict[str, Any]:
    envelope_path = Path(path)
    if not envelope_path.exists():
        raise FileNotFoundError(f"Prompt envelope não encontrado: {envelope_path}")
    payload = json.loads(envelope_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Prompt envelope inválido: raiz precisa ser um objeto JSON")
    return payload


def _as_list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def build_messages(envelope: dict[str, Any], user_prompt: str) -> list[dict[str, str]]:
    system_prompt = str(envelope.get("system_prompt") or DEFAULT_SYSTEM_PROMPT).strip() or DEFAULT_SYSTEM_PROMPT
    developer_prompt = str(envelope.get("developer_prompt") or DEFAULT_DEVELOPER_PROMPT).strip() or DEFAULT_DEVELOPER_PROMPT

    guardrail_lines = [developer_prompt]
    if envelope.get("strict") is True:
        guardrail_lines.append("Modo estrito ativo: não redescobrir o repositório inteiro.")

    budget = envelope.get("context_budget")
    if isinstance(budget, dict):
        guardrail_lines.append(
            "Budget de contexto: "
            f"max_files={budget.get('max_files', 'n/a')}, "
            f"max_chars={budget.get('max_chars', 'n/a')}, "
            f"prefer_whitelist={str(budget.get('prefer_whitelist', False)).lower()}."
        )

    whitelisted_refs = _as_list_of_strings(envelope.get("whitelisted_context_refs"))
    rejected_refs = _as_list_of_strings(envelope.get("rejected_context_refs"))
    if whitelisted_refs:
        guardrail_lines.append(f"Refs whitelistados: {len(whitelisted_refs)}.")
    if rejected_refs:
        guardrail_lines.append(f"Refs rejeitados: {len(rejected_refs)}.")

    prompt_text = str(user_prompt).strip()
    if not prompt_text:
        raise ValueError("Prompt do usuário não pode ser vazio")

    return [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": "\n".join(guardrail_lines)},
        {"role": "user", "content": prompt_text},
    ]


def build_provider_payload(
    *,
    envelope: dict[str, Any],
    user_prompt: str,
    model: str | None = None,
    stream: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "messages": build_messages(envelope, user_prompt),
        "stream": stream,
    }
    if model:
        payload["model"] = model

    metadata: dict[str, Any] = {}
    for key in (
        "purpose",
        "mode",
        "task_id",
        "task_source",
        "context_packet_path",
        "strict",
        "context_budget",
        "preflight",
        "whitelisted_context_refs",
        "rejected_context_refs",
        "policy_refs",
    ):
        if key in envelope:
            metadata[key] = envelope[key]
    if metadata:
        payload["metadata"] = metadata
    return payload
