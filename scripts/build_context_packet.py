#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.memory.interface.memory import MockMemoryBackend, serialize_records  # noqa: E402
from adapters.memory.long_term.supabase_client import SupabaseMemoryBackend  # noqa: E402
from adapters.memory.short_term.redis_client import RedisMemoryBackend  # noqa: E402
from scripts.schema_tools import load_json, validate_instance  # noqa: E402


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_dotenv(path: Path, overwrite: bool = False) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or (key in os.environ and not overwrite):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[key] = value


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


def load_memories(backend_name: str, fixture: Path, query: str, limit: int) -> list[dict[str, Any]]:
    def render(records: list[Any]) -> list[dict[str, Any]]:
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

    if backend_name == "mock":
        backend = MockMemoryBackend.from_fixture(fixture)
    elif backend_name == "redis":
        backend = RedisMemoryBackend()
    else:
        backend = SupabaseMemoryBackend()

    records = backend.search(query, limit=limit)
    if not records and query.strip():
        records = backend.search("", limit=limit)
    return render(records)


def main() -> int:
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT / ".env.local", overwrite=True)
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
