#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.memory.interface.memory import MockMemoryBackend, serialize_records  # noqa: E402
from adapters.memory.long_term.supabase_client import SupabaseMemoryBackend  # noqa: E402
from adapters.memory.short_term.redis_client import RedisMemoryBackend  # noqa: E402


class SchemaValidationError(ValueError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monta um context packet local para tasks.")
    parser.add_argument("--task-file", required=True)
    parser.add_argument("--linear-identifier", required=True)
    parser.add_argument("--linear-title", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--project", default="infrastructure-state")
    parser.add_argument("--branch")
    parser.add_argument("--memory-backend", choices=["mock", "redis", "supabase"], default="mock")
    parser.add_argument("--memory-fixture", default="adapters/memory/fixtures/sample_memories.json")
    parser.add_argument("--search-query")
    parser.add_argument("--memory-limit", type=int, default=3)
    parser.add_argument("--policy-ref", action="append", default=[])
    parser.add_argument("--latest-action", action="append", default=[])
    parser.add_argument("--canonical-fact", action="append", default=[])
    parser.add_argument("--schema")
    parser.add_argument("--validate-schema", action="store_true")
    parser.add_argument("--output")
    return parser.parse_args()


def resolve_branch(explicit: str | None) -> str:
    if explicit:
        return explicit
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        return branch or "master"
    except Exception:
        return "master"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_type(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "null":
        return instance is None
    return True


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> None:
    expected_type = schema.get("type")
    if expected_type and not check_type(instance, expected_type):
        raise SchemaValidationError(f"{path}: tipo inválido, esperado {expected_type}")

    if expected_type == "object":
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}).keys())
            extra = set(instance.keys()) - allowed
            if extra:
                raise SchemaValidationError(f"{path}: propriedades não permitidas: {', '.join(sorted(extra))}")
        for field_name in schema.get("required", []):
            if field_name not in instance:
                raise SchemaValidationError(f"{path}: campo obrigatório ausente: {field_name}")
        for field_name, child_schema in schema.get("properties", {}).items():
            if field_name in instance:
                value = instance[field_name]
                if "enum" in child_schema and value not in child_schema["enum"]:
                    raise SchemaValidationError(f"{path}.{field_name}: valor fora do enum")
                if child_schema.get("type") == "string" and "minLength" in child_schema and len(value) < child_schema["minLength"]:
                    raise SchemaValidationError(f"{path}.{field_name}: tamanho mínimo não atendido")
                validate_instance(value, child_schema, f"{path}.{field_name}")
    elif expected_type == "array":
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                validate_instance(item, item_schema, f"{path}[{index}]")
    else:
        if "enum" in schema and instance not in schema["enum"]:
            raise SchemaValidationError(f"{path}: valor fora do enum")
        if expected_type == "string" and "minLength" in schema and len(instance) < schema["minLength"]:
            raise SchemaValidationError(f"{path}: tamanho mínimo não atendido")


def load_memories(backend_name: str, fixture: Path, query: str, limit: int) -> list[dict[str, Any]]:
    if backend_name == "mock":
        backend = MockMemoryBackend.from_fixture(fixture)
        records = backend.search(query, limit=limit)
        return [
            {
                "memory_id": record.memory_id,
                "layer": record.layer,
                "title": record.title,
                "summary": record.summary,
                "source": record.source,
            }
            for record in records
        ]
    if backend_name == "redis":
        backend = RedisMemoryBackend()
        return serialize_records(backend.search(query, limit=limit))
    backend = SupabaseMemoryBackend()
    return serialize_records(backend.search(query, limit=limit))


def main() -> int:
    args = parse_args()
    task_path = (ROOT / args.task_file).resolve()
    if not task_path.exists():
        raise SystemExit(f"Task não encontrada: {task_path}")

    task = load_json(task_path)
    branch = resolve_branch(args.branch)
    search_query = args.search_query or args.objective or args.linear_title
    retrieved_memories = load_memories(args.memory_backend, ROOT / args.memory_fixture, search_query, args.memory_limit)

    packet = {
        "project": args.project,
        "branch": branch,
        "generated_at": now_iso(),
        "memory_backend": args.memory_backend,
        "linear_issue": {
            "identifier": args.linear_identifier,
            "title": args.linear_title,
        },
        "task": {
            "task_id": task["task_id"],
            "mode": task.get("mode", "STANDARD"),
            "source": str(task_path.relative_to(ROOT)),
        },
        "objective": args.objective,
        "latest_actions": args.latest_action,
        "canonical_facts": args.canonical_fact,
        "retrieved_memories": retrieved_memories,
        "policy_refs": args.policy_ref or ["docs/memory-policy.md"],
    }

    if args.validate_schema:
        if not args.schema:
            raise SystemExit("Use --schema ao validar o context packet")
        schema = load_json((ROOT / args.schema).resolve())
        validate_instance(packet, schema)

    payload = json.dumps(packet, ensure_ascii=False, indent=2)
    if args.output:
        output_path = (ROOT / args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
