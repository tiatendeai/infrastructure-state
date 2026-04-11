#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.schema_tools import SchemaValidationError, load_json, validate_instance  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida um artefato JSON local contra um schema JSON local.")
    parser.add_argument("instance", help="Arquivo JSON da instância")
    parser.add_argument("schema", help="Arquivo JSON do schema")
    return parser.parse_args()


def resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return path


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    instance_path = resolve_path(args.instance)
    schema_path = resolve_path(args.schema)

    instance = load_json(instance_path)
    schema = load_json(schema_path)

    try:
        validate_instance(instance, schema)
    except SchemaValidationError as exc:
        print(
            json.dumps(
                {
                    "status": "invalid",
                    "instance": rel(instance_path),
                    "schema": rel(schema_path),
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    print(
        json.dumps(
            {
                "status": "valid",
                "instance": rel(instance_path),
                "schema": rel(schema_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
