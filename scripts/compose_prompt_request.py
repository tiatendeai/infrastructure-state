#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.llm.prompt_envelope import build_provider_payload, load_prompt_envelope  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compõe um payload de prompt canônico a partir de um prompt envelope.")
    parser.add_argument("--envelope", required=True, help="Caminho para o prompt-envelope.json")
    parser.add_argument("--prompt", required=True, help="Prompt do usuário")
    parser.add_argument("--model", help="Modelo alvo opcional")
    parser.add_argument("--stream", action="store_true", help="Habilita stream no payload")
    parser.add_argument("--output", help="Escreve o payload em arquivo")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    envelope = load_prompt_envelope((ROOT / args.envelope).resolve())
    payload = build_provider_payload(envelope=envelope, user_prompt=args.prompt, model=args.model, stream=args.stream)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output_path = (ROOT / args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
