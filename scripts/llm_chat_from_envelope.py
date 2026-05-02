#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.llm.prompt_envelope import build_provider_payload, load_prompt_envelope  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Envia um prompt canônico usando um prompt envelope do Shipyard.")
    parser.add_argument("--envelope", required=True, help="Caminho para o prompt-envelope.json")
    parser.add_argument("--prompt", required=True, help="Prompt do usuário")
    parser.add_argument("--model", help="Modelo alvo opcional")
    parser.add_argument("--base-url", default=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"), help="Base URL OpenAI-compatible")
    parser.add_argument("--api-key", default=os.getenv("LLM_API_KEY", ""), help="Chave de API opcional")
    parser.add_argument("--timeout", type=int, default=int(os.getenv("LLM_TIMEOUT_SECONDS", "60")), help="Timeout em segundos")
    parser.add_argument("--dry-run", action="store_true", help="Só mostra o payload e não faz a chamada")
    parser.add_argument("--output", help="Escreve a resposta em arquivo")
    return parser.parse_args()


def _join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def _auth_headers(api_key: str) -> dict[str, str]:
    headers = {"content-type": "application/json"}
    if api_key.strip():
        headers["authorization"] = f"Bearer {api_key.strip()}"
    return headers


def post_chat_completions(*, base_url: str, api_key: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    url = _join_url(base_url, "/chat/completions")
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=body, headers=_auth_headers(api_key), method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw)
            return {
                "ok": True,
                "status": response.status,
                "url": url,
                "response": parsed,
            }
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw}
        return {
            "ok": False,
            "status": exc.code,
            "url": url,
            "response": parsed,
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": "error",
            "url": url,
            "error": str(exc),
        }


def main() -> int:
    args = parse_args()
    envelope = load_prompt_envelope((ROOT / args.envelope).resolve())
    payload = build_provider_payload(
        envelope=envelope,
        user_prompt=args.prompt,
        model=args.model,
        stream=False,
    )

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    result = post_chat_completions(
        base_url=args.base_url,
        api_key=args.api_key,
        payload=payload,
        timeout=args.timeout,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output_path = (ROOT / args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
