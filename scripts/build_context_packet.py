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

DEFAULT_CONTEXT_BUDGET = {
    "max_files": 20,
    "max_chars": 8000,
    "prefer_diffs": True,
    "prefer_whitelist": True,
    "heartbeat_seconds_min": 300,
    "allow_repo_rediscovery": False,
}


CANONICAL_CONTEXT_SOURCES: list[tuple[Path, str]] = [
    (ROOT / "contexts" / "agent_bootstrap.md", "Bootstrap canônico curto: ordem obrigatória de leitura, alertas vermelhos e frentes críticas."),
    (ROOT / "intelligence-core" / "alpha.md", "Alpha: gênese e identidade raiz; state-first; aprendizados duráveis sobem ao state_outbox."),
    (ROOT / "intelligence-core" / "omega.md", "Omega: lifecycle de sessões, replay/recovery e fechamento obrigatório."),
    ((ROOT.parent / "state" / "AGENTS.md"), "State AGENTS: selo obrigatório, hierarquia Alpha→State→Omega e consulta obrigatória a entities/agent_multiverse."),
    ((ROOT.parent / "state" / "memory" / "jarvis.memory.md"), "Memória curada: invariantes estáveis, continuidade, sessões pertencem ao Omega e dívidas abertas."),
    ((ROOT.parent / "state" / "registry" / "entities.yaml"), "Entities: Jarvis/ops/vcfo/vcvo/vceo/iazinha; manifestação canônica e governança do control plane."),
    ((ROOT.parent / "state" / "registry" / "agent_multiverse.yaml"), "Multiverse: sessão ativa, engaged/hot_standby, linhagem e source refs."),
    (ROOT / "DNA_DE_INTELIGENCIA.md", "DNA de inteligência: STATE como cérebro de contexto; auditoria proativa; RTK; graphify; anotações viram protocolos ativos."),
    (ROOT / "AGENTS.md", "Shipyard AGENTS: o estaleiro é a execução viva e lê o State antes de agir."),
]


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
    parser.add_argument("--context-ref", action="append", default=[])
    parser.add_argument("--context-budget")
    parser.add_argument("--strict", action="store_true")
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
                "metadata": record.metadata,
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


def strip_comment(line: str) -> str:
    if "#" not in line:
        return line
    in_quotes = False
    result = []
    prev = ""
    for char in line:
        if char == '"' and prev != "\\":
            in_quotes = not in_quotes
        if char == "#" and not in_quotes:
            break
        result.append(char)
        prev = char
    return "".join(result).rstrip()


def parse_scalar(value: str):
    value = value.strip()
    if value == "":
        return ""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item.strip()) for item in inner.split(",")]
    if value.isdigit():
        return int(value)
    return value


def parse_yaml_subset(text: str) -> dict[str, Any]:
    lines: list[tuple[int, int, str]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if "\t" in raw:
            raise ValueError(f"YAML com TAB não suportado na linha {lineno}")
        stripped = strip_comment(raw)
        if not stripped.strip():
            continue
        content = stripped.rstrip()
        indent = len(content) - len(content.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError(f"Indentação deve usar múltiplos de 2 espaços na linha {lineno}")
        token = content.strip()
        if token.startswith("&") or token.startswith("*") or token in {"|", ">"} or "!!" in token:
            raise ValueError(f"Recurso YAML fora do subset suportado na linha {lineno}")
        lines.append((lineno, indent, token))

    def parse_block(index: int, indent: int):
        container: dict[str, Any] | list[Any] | None = None
        while index < len(lines):
            lineno, current_indent, token = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ValueError(f"Indentação inesperada na linha {lineno}")

            if token.startswith("- "):
                if container is None:
                    container = []
                if not isinstance(container, list):
                    raise ValueError(f"Mistura inválida de lista e mapa na linha {lineno}")
                item = token[2:].strip()
                if not item:
                    raise ValueError(f"Item de lista vazio não suportado na linha {lineno}")
                if ":" in item:
                    raise ValueError(f"Lista de mapas fora do subset suportado na linha {lineno}")
                container.append(parse_scalar(item))
                index += 1
                continue

            if container is None:
                container = {}
            if not isinstance(container, dict):
                raise ValueError(f"Mistura inválida de mapa e lista na linha {lineno}")
            if ":" not in token:
                raise ValueError(f"Linha inválida {lineno}: esperado key: value")
            key, raw_value = token.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            if not key:
                raise ValueError(f"Chave vazia na linha {lineno}")

            if raw_value == "":
                next_index = index + 1
                if next_index >= len(lines) or lines[next_index][1] <= current_indent:
                    container[key] = {}
                    index += 1
                else:
                    value, index = parse_block(next_index, current_indent + 2)
                    container[key] = value
            else:
                container[key] = parse_scalar(raw_value)
                index += 1

        if container is None:
            return {}, index
        return container, index

    parsed, index = parse_block(0, 0)
    if index != len(lines):
        raise ValueError("Falha ao consumir todo o documento YAML")
    if not isinstance(parsed, dict):
        raise ValueError("Budget YAML inválido: raiz precisa ser mapa")
    return parsed


def load_yaml_file(path: Path) -> dict[str, Any]:
    return parse_yaml_subset(path.read_text(encoding="utf-8"))


def load_context_budget(explicit_path: str | None) -> dict[str, Any]:
    candidates = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    env_path = os.getenv("RTK_CONTEXT_BUDGET_PATH", "").strip()
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            Path.home() / ".config" / "rtk" / "context-budget.yaml",
            ROOT / ".claude" / "rtk" / "context-budget.yaml",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            try:
                payload = load_yaml_file(candidate)
            except Exception:
                continue
            return {
                "path": str(candidate),
                "values": {
                    key: payload.get(key, default)
                    for key, default in DEFAULT_CONTEXT_BUDGET.items()
                },
            }

    return {
        "path": None,
        "values": dict(DEFAULT_CONTEXT_BUDGET),
    }


def relativize(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        try:
            return str(path.relative_to(ROOT.parent))
        except Exception:
            return str(path)


def normalize_refs(values: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        ref = str(value).strip()
        if not ref or ref in seen:
            continue
        seen.add(ref)
        normalized.append(ref)
    return normalized


def build_preflight(context_refs: list[str], budget: dict[str, Any]) -> dict[str, Any]:
    max_files = int(budget.get("max_files", DEFAULT_CONTEXT_BUDGET["max_files"]))
    prefer_whitelist = bool(budget.get("prefer_whitelist", True))
    allow_repo_rediscovery = bool(budget.get("allow_repo_rediscovery", False))

    declared_refs = normalize_refs(context_refs)
    whitelisted_refs: list[str] = []
    rejected_refs: list[str] = []
    seen: set[str] = set()
    for ref in declared_refs:
        if len(whitelisted_refs) >= max_files:
            rejected_refs.append(ref)
            continue
        candidate = (ROOT / ref).resolve()
        if not candidate.exists() and prefer_whitelist and not allow_repo_rediscovery:
            rejected_refs.append(ref)
            continue
        if ref in seen:
            continue
        seen.add(ref)
        whitelisted_refs.append(ref)

    return {
        "budget": budget,
        "declared_context_refs": declared_refs,
        "whitelisted_context_refs": whitelisted_refs,
        "rejected_context_refs": rejected_refs,
        "context_ref_count": len(whitelisted_refs),
        "has_repo_rediscovery": bool(rejected_refs) and not allow_repo_rediscovery,
        "strict_violations": len(rejected_refs),
        "enforced": {
            "max_files": max_files,
            "prefer_whitelist": prefer_whitelist,
            "allow_repo_rediscovery": allow_repo_rediscovery,
        },
    }


def estimate_packet_chars(*, canonical_facts: list[str], latest_actions: list[str], memories: list[dict[str, Any]], policy_refs: list[str], declared_refs: list[str]) -> int:
    total = 0
    for value in canonical_facts + latest_actions + policy_refs + declared_refs:
        total += len(str(value))
    for memory in memories:
        total += len(str(memory.get("summary", "")))
        total += len(str(memory.get("title", "")))
        total += len(str(memory.get("source", "")))
    return total


def enforce_char_budget(
    *,
    max_chars: int,
    canonical_facts: list[str],
    latest_actions: list[str],
    retrieved_memories: list[dict[str, Any]],
    policy_refs: list[str],
    declared_refs: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if max_chars <= 0:
        return retrieved_memories, {
            "max_chars": max_chars,
            "estimated_chars": estimate_packet_chars(
                canonical_facts=canonical_facts,
                latest_actions=latest_actions,
                memories=retrieved_memories,
                policy_refs=policy_refs,
                declared_refs=declared_refs,
            ),
            "trimmed_memories": 0,
        }

    trimmed = list(retrieved_memories)
    estimated_chars = estimate_packet_chars(
        canonical_facts=canonical_facts,
        latest_actions=latest_actions,
        memories=trimmed,
        policy_refs=policy_refs,
        declared_refs=declared_refs,
    )
    trimmed_memories = 0
    while trimmed and estimated_chars > max_chars:
        trimmed.pop()
        trimmed_memories += 1
        estimated_chars = estimate_packet_chars(
            canonical_facts=canonical_facts,
            latest_actions=latest_actions,
            memories=trimmed,
            policy_refs=policy_refs,
            declared_refs=declared_refs,
        )

    return trimmed, {
        "max_chars": max_chars,
        "estimated_chars": estimated_chars,
        "trimmed_memories": trimmed_memories,
    }


def load_canonical_context() -> tuple[list[str], list[str]]:
    facts: list[str] = []
    actions: list[str] = []

    for path, summary in CANONICAL_CONTEXT_SOURCES:
        if path.exists():
            facts.append(summary)
            actions.append(f"base canônica carregada: {path.relative_to(ROOT.parent) if path.is_relative_to(ROOT.parent) else path.relative_to(ROOT)}")
        else:
            actions.append(f"ALERTA VERMELHO: fonte canônica ausente: {path}")

    if facts:
        actions.insert(0, "contexto canônico inicializado a partir de Alpha, Omega, State e Shipyard")
    else:
        actions.insert(0, "ALERTA VERMELHO: nenhuma fonte canônica pôde ser carregada")

    return facts, actions


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
    context_budget = load_context_budget(args.context_budget)
    budget_values = context_budget["values"]
    max_files = int(budget_values.get("max_files", DEFAULT_CONTEXT_BUDGET["max_files"]))
    effective_memory_limit = min(max(1, args.memory_limit), max_files)
    retrieved_memories = load_memories(args.memory_backend, ROOT / args.memory_fixture, search_query, effective_memory_limit)
    canonical_context_facts, canonical_context_actions = load_canonical_context()
    preflight = build_preflight(args.context_ref, context_budget["values"])
    latest_actions = canonical_context_actions + args.latest_action
    canonical_facts = canonical_context_facts + args.canonical_fact
    policy_refs = list(dict.fromkeys((args.policy_ref or []) + [
        "docs/memory-policy.md",
        "intelligence-core/alpha.md",
        "intelligence-core/omega.md",
        "DNA_DE_INTELIGENCIA.md",
        "../state/AGENTS.md",
        "../state/memory/jarvis.memory.md",
    ]))
    retrieved_memories, char_budget = enforce_char_budget(
        max_chars=int(budget_values.get("max_chars", DEFAULT_CONTEXT_BUDGET["max_chars"])),
        canonical_facts=canonical_facts,
        latest_actions=latest_actions,
        retrieved_memories=retrieved_memories,
        policy_refs=policy_refs,
        declared_refs=preflight["declared_context_refs"],
    )
    preflight["character_budget"] = char_budget
    preflight["effective_memory_limit"] = effective_memory_limit

    if args.strict:
        strict_errors: list[str] = []
        if preflight["rejected_context_refs"]:
            strict_errors.append(
                "refs rejeitados: " + ", ".join(preflight["rejected_context_refs"])
            )
        if preflight["character_budget"]["trimmed_memories"] > 0:
            strict_errors.append(
                f"memórias cortadas pelo budget de caracteres: {preflight['character_budget']['trimmed_memories']}"
            )
        if strict_errors:
            raise SystemExit("Preflight estrito falhou: " + " | ".join(strict_errors))

    packet = {
        "project": args.project,
        "branch": branch,
        "generated_at": now_iso(),
        "memory_backend": args.memory_backend,
        "context_budget": {
            "path": context_budget["path"] or "",
            **context_budget["values"],
        },
        "linear_issue": {
            "identifier": args.linear_identifier,
            "title": args.linear_title,
        },
        "task": {
            "task_id": task["task_id"],
            "mode": task.get("mode", "STANDARD"),
            "source": relativize(task_path),
        },
        "objective": args.objective,
        "latest_actions": latest_actions,
        "canonical_facts": canonical_facts,
        "retrieved_memories": retrieved_memories,
        "declared_context_refs": preflight["declared_context_refs"],
        "whitelisted_context_refs": preflight["whitelisted_context_refs"],
        "rejected_context_refs": preflight["rejected_context_refs"],
        "preflight": preflight,
        "policy_refs": policy_refs,
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
