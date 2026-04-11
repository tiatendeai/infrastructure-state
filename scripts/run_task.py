#!/usr/bin/env python3
import argparse
import glob
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
KERNEL_STATE = ROOT / "kernel" / "state.json"
LOG_FILE = ROOT / "logs" / "execution.log"
REGISTRY_DIR = ROOT / "registry" / "runs"
SNAPSHOT_DIR = ROOT / "state" / "snapshots"
AGENTS_RUNTIME_DIR = ROOT / "state" / "runtime"
CONTEXT_PACKET_SCHEMA = "contracts/context-packet.schema.json"
DEFAULT_CONTEXT_PACKET = "context-packet.json"

DEFAULT_STATE = {
    "status": "idle",
    "current_task": None,
    "history": [],
    "version": 1,
}

ALLOWED_TASK_STATUS = {"pending", "running", "done", "error"}
ALLOWED_MODES = {"FAST", "STANDARD", "FULL"}
ALLOWED_COMMAND_ENTRYPOINTS = {
    "scripts/collect_server_inventory.py",
    "scripts/generate_services_registry.py",
    "scripts/build_context_packet.py",
    "scripts/linear_adapter.py",
}
TYPE_TO_MODE = {
    "echo": "FAST",
    "noop": "FAST",
    "validate": "STANDARD",
    "transform": "STANDARD",
    "sync": "STANDARD",
    "command": "STANDARD",
    "change": "FULL",
    "release": "FULL",
    "deploy": "FULL",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


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


def ensure_runtime() -> None:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    AGENTS_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    KERNEL_STATE.parent.mkdir(parents=True, exist_ok=True)

    if not KERNEL_STATE.exists():
        save_json(KERNEL_STATE, DEFAULT_STATE)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")

    for keep in (
        REGISTRY_DIR / ".gitkeep",
        SNAPSHOT_DIR / ".gitkeep",
        AGENTS_RUNTIME_DIR / ".gitkeep",
    ):
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido em {path}: linha {exc.lineno}, coluna {exc.colno}") from exc


def save_json(path: Path, payload) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def append_log(task_id: str, status: str, message: str) -> None:
    entry = {
        "timestamp": now_iso(),
        "task_id": task_id,
        "status": status,
        "message": message,
    }
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def basic_validate(task: dict) -> None:
    required = ["task_id", "type", "input", "output", "status"]
    missing = [field for field in required if field not in task]
    if missing:
        raise ValueError(f"Task inválida: campos ausentes: {', '.join(missing)}")


def validate_list_of_strings(task: dict, field_name: str) -> None:
    if field_name not in task:
        return
    value = task[field_name]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Task inválida: {field_name} deve ser lista de strings")


def validate_optional_string(task: dict, field_name: str) -> None:
    if field_name in task and not isinstance(task[field_name], str):
        raise ValueError(f"Task inválida: {field_name} deve ser string")


def validate_command_task(task: dict) -> None:
    payload = task.get("input", {})
    entrypoint = payload.get("entrypoint")
    if not isinstance(entrypoint, str) or not entrypoint.strip():
        raise ValueError("Task command inválida: input.entrypoint deve ser string não vazia")
    if Path(entrypoint).is_absolute():
        raise ValueError("Task command inválida: input.entrypoint deve ser relativo ao repositório")
    if entrypoint not in ALLOWED_COMMAND_ENTRYPOINTS:
        raise ValueError(f"Task command inválida: entrypoint fora da allowlist ({entrypoint})")

    args = payload.get("args", [])
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        raise ValueError("Task command inválida: input.args deve ser lista de strings")

    execution_policy = task.get("execution_policy")
    approval_required = task.get("approval_required")
    if execution_policy in {"read_only_remote", "human_in_the_loop"} and approval_required is not True:
        raise ValueError("Task command inválida: approval_required deve ser true para execução governada")


def standard_validate(task: dict) -> None:
    basic_validate(task)
    if not isinstance(task["task_id"], str) or not task["task_id"].strip():
        raise ValueError("Task inválida: task_id deve ser string não vazia")
    if not isinstance(task["type"], str) or not task["type"].strip():
        raise ValueError("Task inválida: type deve ser string não vazia")
    if not isinstance(task["input"], dict):
        raise ValueError("Task inválida: input deve ser objeto")
    if not isinstance(task["output"], dict):
        raise ValueError("Task inválida: output deve ser objeto")
    if task["status"] not in ALLOWED_TASK_STATUS:
        raise ValueError("Task inválida: status fora do contrato")
    if "mode" in task and task["mode"] not in ALLOWED_MODES:
        raise ValueError("Task inválida: mode fora do contrato")

    for field_name in ("linear_issue_id", "linear_issue_identifier", "linear_issue_uuid", "linear_project", "linear_team_key", "service_target", "execution_policy"):
        validate_optional_string(task, field_name)

    for field_name in ("context_refs", "infra_refs", "expected_output"):
        validate_list_of_strings(task, field_name)

    if "approval_required" in task and not isinstance(task["approval_required"], bool):
        raise ValueError("Task inválida: approval_required deve ser boolean")

    if task["type"] == "command":
        validate_command_task(task)


def resolve_mode(task: dict, explicit_mode: str | None) -> str:
    mode = explicit_mode or task.get("mode") or TYPE_TO_MODE.get(task.get("type", ""), "STANDARD")
    mode = mode.upper()
    if mode not in ALLOWED_MODES:
        raise ValueError(f"Modo inválido: {mode}")
    return mode


def validate_task(task: dict, mode: str) -> None:
    if mode == "FAST":
        basic_validate(task)
    else:
        standard_validate(task)


def read_state() -> dict:
    if not KERNEL_STATE.exists():
        return DEFAULT_STATE.copy()
    state = load_json(KERNEL_STATE)
    if not isinstance(state.get("history"), list):
        state["history"] = []
    return state


def write_state(state: dict) -> None:
    save_json(KERNEL_STATE, state)


def snapshot_state(task_id: str, label: str, state: dict) -> str:
    safe_label = label.replace(" ", "-")
    filename = f"{now_iso().replace(':', '-')}_{task_id}_{safe_label}.json"
    path = SNAPSHOT_DIR / filename
    save_json(path, state)
    return str(path.relative_to(ROOT))


def record_runtime(task_id: str, payload: dict) -> str:
    task_dir = AGENTS_RUNTIME_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    runtime_file = task_dir / "session.json"
    save_json(runtime_file, payload)
    return str(runtime_file.relative_to(ROOT))


def write_registry_record(record: dict, task_id: str) -> str:
    safe_task_id = task_id.replace("/", "-").replace(" ", "-")
    filename = f"{now_iso().replace(':', '-')}_{safe_task_id}.json"
    path = REGISTRY_DIR / filename
    save_json(path, record)
    return str(path.relative_to(ROOT))


def write_failure_record(
    *,
    task_id: str,
    mode: str,
    source: str,
    stage: str,
    error_message: str,
    task: dict | None = None,
) -> str:
    payload = {
        "task": task,
        "meta": {
            "mode": mode,
            "source": source,
            "recorded_at": now_iso(),
            "status": "error",
            "stage": stage,
            "error": error_message,
        },
    }
    return write_registry_record(payload, task_id)


def build_current_task(task: dict, mode: str, task_source: str) -> dict:
    payload = {
        "task_id": task["task_id"],
        "type": task["type"],
        "mode": mode,
        "task_source": task_source,
    }
    for field_name in (
        "linear_issue_id",
        "linear_issue_identifier",
        "linear_issue_uuid",
        "linear_project",
        "linear_team_key",
        "service_target",
        "approval_required",
        "execution_policy",
    ):
        if field_name in task:
            payload[field_name] = task[field_name]
    return payload


def build_history_entry(task: dict, mode: str, status: str, registry_file: str, task_source: str, context_info: dict | None = None) -> dict:
    payload = {
        "task_id": task["task_id"],
        "type": task["type"],
        "mode": mode,
        "status": status,
        "timestamp": now_iso(),
        "registry_record": registry_file,
        "task_source": task_source,
    }
    for field_name in (
        "linear_issue_id",
        "linear_issue_identifier",
        "linear_issue_uuid",
        "linear_project",
        "linear_team_key",
        "service_target",
        "approval_required",
        "execution_policy",
    ):
        if field_name in task:
            payload[field_name] = task[field_name]
    if context_info:
        if context_info.get("issue_identifier"):
            payload["resolved_linear_issue_identifier"] = context_info["issue_identifier"]
        if context_info.get("context_packet_path"):
            payload["context_packet"] = context_info["context_packet_path"]
        if context_info.get("memory_backend"):
            payload["memory_backend"] = context_info["memory_backend"]
        if context_info.get("retrieved_memory_count") is not None:
            payload["retrieved_memory_count"] = context_info["retrieved_memory_count"]
    return payload


def verify_declared_paths(paths: list[str]) -> dict:
    present: list[str] = []
    missing: list[str] = []
    for raw_path in paths:
        ref = str(raw_path).strip()
        if not ref:
            continue
        matches = glob.glob(str(ROOT / ref), recursive=True)
        if matches:
            present.append(ref)
        else:
            missing.append(ref)
    return {
        "present": present,
        "missing": missing,
        "present_count": len(present),
        "missing_count": len(missing),
    }


def execute_change_task(task: dict, mode: str) -> dict:
    expected_output = verify_declared_paths(task.get("expected_output", []))
    context_refs = verify_declared_paths(task.get("context_refs", []))
    infra_refs = verify_declared_paths(task.get("infra_refs", []))
    missing_total = (
        expected_output["missing_count"]
        + context_refs["missing_count"]
        + infra_refs["missing_count"]
    )
    status_label = "verificada" if missing_total == 0 else "verificada_com_ressalvas"
    return {
        "message": "Change task verificada localmente a partir dos artefatos já materializados no repositório.",
        "mode": mode,
        "executed_at": now_iso(),
        "verification_status": status_label,
        "verification": {
            "expected_output": expected_output,
            "context_refs": context_refs,
            "infra_refs": infra_refs,
        },
    }


def task_objective(task: dict) -> str:
    payload = task.get("input", {})
    if isinstance(payload, dict):
        for field_name in ("objective", "message", "description"):
            value = payload.get(field_name)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return str(task.get("task_id", "Executar task local")).strip()


def try_resolve_linear_issue(task: dict, task_source: str) -> dict:
    try:
        from adapters.linear.registry import load_linear_mapping_registry, resolve_issue_mapping
    except Exception:
        return {}

    try:
        registry = load_linear_mapping_registry()
        mapping = resolve_issue_mapping(registry=registry, task=task, task_source=task_source)
    except Exception:
        return {}

    issue_identifier = (
        mapping.linear_issue_identifier
        or str(task.get("linear_issue_identifier", "")).strip()
        or str(task.get("linear_issue_id", "")).strip()
    )
    issue_title = ""
    if issue_identifier:
        try:
            from adapters.linear.client import LinearClient, LinearConfig
            from adapters.linear.issues import get_issue

            client = LinearClient(LinearConfig.from_env(ROOT))
            issue = get_issue(client, issue_identifier)
            issue_title = str(issue.get("title", "")).strip()
        except Exception:
            issue_title = ""

    if not issue_title:
        issue_title = task_objective(task)

    return {
        "mapping": mapping.to_dict(),
        "issue_identifier": issue_identifier,
        "issue_title": issue_title,
    }


def prepare_context_packet(task: dict, task_id: str, task_source: str, mode: str) -> dict:
    linear_context = try_resolve_linear_issue(task, task_source)
    issue_identifier = str(linear_context.get("issue_identifier", "")).strip()
    if not issue_identifier:
        return {}

    issue_title = str(linear_context.get("issue_title", "")).strip() or task_objective(task)
    objective = task_objective(task)
    runtime_dir = AGENTS_RUNTIME_DIR / task_id
    runtime_dir.mkdir(parents=True, exist_ok=True)
    output_path = runtime_dir / DEFAULT_CONTEXT_PACKET
    output_rel = str(output_path.relative_to(ROOT))

    command = [
        sys.executable,
        str((ROOT / "scripts" / "build_context_packet.py").resolve()),
        "--task-file",
        task_source,
        "--linear-identifier",
        issue_identifier,
        "--linear-title",
        issue_title,
        "--objective",
        objective,
        "--memory-backend",
        os.getenv("RUPTUR_MEMORY_BACKEND", "mock").strip() or "mock",
        "--memory-limit",
        os.getenv("RUPTUR_MEMORY_LIMIT", "3").strip() or "3",
        "--schema",
        CONTEXT_PACKET_SCHEMA,
        "--validate-schema",
        "--output",
        output_rel,
        "--latest-action",
        f"task validada localmente em modo {mode}",
        "--latest-action",
        f"binding Linear resolvido para {issue_identifier}",
        "--latest-action",
        "context packet preparado pelo runner local",
        "--canonical-fact",
        "O Linear governa; o infrastructure-state registra a evidência técnica.",
    ]

    mapping = linear_context.get("mapping")
    if isinstance(mapping, dict):
        backlog_key = str(mapping.get("backlog_key", "")).strip()
        if backlog_key:
            command.extend(["--canonical-fact", f"binding local: {backlog_key} -> {issue_identifier}"])

    project = str(task.get("linear_project", "")).strip()
    if project:
        command.extend(["--canonical-fact", f"project: {project}"])
    service_target = str(task.get("service_target", "")).strip()
    if service_target:
        command.extend(["--canonical-fact", f"service_target: {service_target}"])

    policy_refs = [ref for ref in task.get("context_refs", []) if isinstance(ref, str) and "memory" in ref.lower()]
    if "docs/memory-policy.md" not in policy_refs:
        policy_refs.append("docs/memory-policy.md")
    for ref in policy_refs:
        command.extend(["--policy-ref", ref])

    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit_code={result.returncode}"
        raise ValueError(f"Falha ao montar context packet: {detail}")

    stdout = result.stdout.strip()
    if not stdout:
        raise ValueError("Falha ao montar context packet: saída vazia")

    try:
        packet = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("Falha ao montar context packet: JSON inválido") from exc

    return {
        "issue_identifier": issue_identifier,
        "issue_title": issue_title,
        "objective": objective,
        "context_packet_path": output_rel,
        "context_packet": packet,
        "mapping": mapping,
        "memory_backend": packet.get("memory_backend"),
        "retrieved_memory_count": len(packet.get("retrieved_memories", [])) if isinstance(packet.get("retrieved_memories"), list) else 0,
    }


def execute_command_task(task: dict) -> dict:
    payload = task.get("input", {})
    entrypoint_rel = payload["entrypoint"]
    entrypoint_path = (ROOT / entrypoint_rel).resolve()

    if not entrypoint_path.exists():
        raise ValueError(f"Entrypoint não encontrado: {entrypoint_rel}")
    if entrypoint_rel not in ALLOWED_COMMAND_ENTRYPOINTS:
        raise ValueError(f"Entrypoint fora da allowlist: {entrypoint_rel}")

    args = payload.get("args", [])
    command = [sys.executable, str(entrypoint_path), *args]
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit_code={result.returncode}"
        raise ValueError(f"Falha ao executar command task: {detail}")

    stdout = result.stdout.strip()
    parsed_stdout = None
    if stdout:
        try:
            parsed_stdout = json.loads(stdout)
        except json.JSONDecodeError:
            parsed_stdout = None

    output = {
        "entrypoint": entrypoint_rel,
        "args": args,
        "exit_code": result.returncode,
        "executed_at": now_iso(),
    }
    if parsed_stdout is not None:
        output["result"] = parsed_stdout
    elif stdout:
        output["stdout"] = stdout
    if result.stderr.strip():
        output["stderr"] = result.stderr.strip()
    return output



def update_registry_record(registry_file: str, patch: dict) -> None:
    path = ROOT / registry_file
    if not path.exists():
        return
    payload = load_json(path)
    payload.update(patch)
    save_json(path, payload)


def try_persist_runtime_memory(*, task: dict, task_source: str, mode: str, registry_file: str, output: dict | None = None, context_info: dict | None = None, status: str = "done", error_message: str | None = None) -> dict:
    try:
        from adapters.memory.interface.memory import MemoryRecord
        from adapters.memory.long_term.supabase_client import SupabaseMemoryBackend
        from adapters.memory.short_term.redis_client import RedisMemoryBackend
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

    task_id = str(task.get("task_id", "unknown-task")).strip() or "unknown-task"
    issue_identifier = str((context_info or {}).get("issue_identifier", "")).strip()
    issue_title = str((context_info or {}).get("issue_title", "")).strip()
    objective = str((context_info or {}).get("objective", "")).strip() or task_objective(task)
    packet_path = str((context_info or {}).get("context_packet_path", "")).strip()
    service_target = str(task.get("service_target", "")).strip()

    summary_parts = [
        f"task {task_id}",
        f"status {status}",
        f"modo {mode}",
    ]
    if issue_identifier:
        summary_parts.append(f"issue {issue_identifier}")
    if service_target:
        summary_parts.append(f"service_target {service_target}")
    if issue_title:
        summary_parts.append(issue_title)
    if objective:
        summary_parts.append(objective)
    if error_message:
        summary_parts.append(f"erro: {error_message}")
    clean_summary = " | ".join(summary_parts)

    saved: list[dict] = []

    try:
        redis = RedisMemoryBackend()
        summary_record = MemoryRecord(
            memory_id=f"summary::{task_id}",
            layer="summary",
            title=f"Resumo operacional {task_id}",
            summary=clean_summary,
            source=task_source,
            metadata={
                "registry_record": registry_file,
                "issue_identifier": issue_identifier,
                "service_target": service_target,
                "mode": mode,
                "status": status,
            },
        )
        redis.save(summary_record)
        saved.append({"backend": "redis", "memory_id": summary_record.memory_id, "layer": summary_record.layer})

        if packet_path:
            context_record = MemoryRecord(
                memory_id=f"context::{task_id}",
                layer="context_packet",
                title=f"Context packet {task_id}",
                summary=f"Context packet real gerado para {task_id} em {packet_path}",
                source=task_source,
                metadata={
                    "registry_record": registry_file,
                    "context_packet_path": packet_path,
                    "issue_identifier": issue_identifier,
                },
            )
            redis.save(context_record)
            saved.append({"backend": "redis", "memory_id": context_record.memory_id, "layer": context_record.layer})
    except Exception as exc:
        saved.append({"backend": "redis", "status": "error", "message": str(exc)})

    try:
        supabase = SupabaseMemoryBackend()
        canonical_summary = (
            f"Capability validated: {service_target or task_id}. "
            f"Binding issue-task: {issue_identifier or 'sem-issue'} <-> {task_id}. "
            f"Registry: {registry_file}. "
            f"Objective: {objective}."
        )
        if status == "error" and error_message:
            canonical_summary = (
                f"Execution error recorded for {task_id}. "
                f"Registry: {registry_file}. "
                f"Objective: {objective}. "
                f"Error: {error_message}."
            )
        canonical_record = MemoryRecord(
            memory_id=f"canonical::{task_id}",
            layer="canonical_memory",
            title=f"Capability {service_target or task_id}",
            summary=canonical_summary,
            source=task_source,
            metadata={
                "registry_record": registry_file,
                "issue_identifier": issue_identifier,
                "issue_title": issue_title,
                "service_target": service_target,
                "mode": mode,
                "status": status,
                "context_packet_path": packet_path,
                "output_keys": sorted((output or {}).keys()) if isinstance(output, dict) else [],
            },
        )
        supabase.save(canonical_record)
        saved.append({"backend": "supabase", "memory_id": canonical_record.memory_id, "layer": canonical_record.layer})
    except Exception as exc:
        saved.append({"backend": "supabase", "status": "error", "message": str(exc)})

    has_success = any(item.get("memory_id") for item in saved)
    return {
        "status": "ok" if has_success else "error",
        "saved": saved,
    }


def try_publish_linear_runtime(*, task: dict, task_source: str, mode: str, event: str, registry_file: str | None = None, output: dict | None = None, error_message: str | None = None, context_info: dict | None = None) -> dict:
    try:
        from adapters.linear.runtime import publish_task_runtime_update

        payload = publish_task_runtime_update(
            task=task,
            task_source=task_source,
            mode=mode,
            event=event,
            registry_record=registry_file,
            output=output,
            error_message=error_message,
            dry_run=str(os.getenv("LINEAR_RUNTIME_SYNC_DRY_RUN", "")).strip().lower() in {"1", "true", "yes", "on"},
            context_info=context_info,
        )
    except Exception as exc:
        payload = {
            "status": "error",
            "event": event,
            "message": str(exc),
        }
    return payload


def log_linear_sync(task_id: str, payload: dict) -> None:
    status = str(payload.get("status", "unknown"))
    event = str(payload.get("event", ""))
    if status == "skipped" and payload.get("skipped_reason") == "runtime_sync_disabled":
        return
    if status == "ok":
        issue_identifier = str(payload.get("issue_identifier", "")).strip()
        comment_posted = "sim" if payload.get("comment") else "não"
        append_log(task_id, "linear_sync", f"Linear sync {event} OK para {issue_identifier or 'issue-desconhecida'} (comentário: {comment_posted})")
        return
    append_log(task_id, "linear_sync_error", f"Linear sync {event} falhou: {payload.get('message', payload.get('skipped_reason', 'erro desconhecido'))}")

def execute(task: dict, mode: str) -> dict:
    task_type = task["type"]
    payload = task.get("input", {})

    if task_type == "echo":
        return {
            "message": payload.get("message", ""),
            "mode": mode,
            "executed_at": now_iso(),
        }
    if task_type == "noop":
        return {
            "message": "No-op concluído",
            "mode": mode,
            "executed_at": now_iso(),
        }
    if task_type == "command":
        return execute_command_task(task)
    if task_type == "change":
        return execute_change_task(task, mode)

    raise ValueError(f"Tipo de task não suportado para execução: {task_type}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa ou valida tasks do Ruptur Farm Framework.")
    parser.add_argument("--validate-only", action="store_true", help="Valida a task sem executá-la.")
    parser.add_argument("task_file", help="Caminho da task JSON.")
    parser.add_argument("mode", nargs="?", help="Modo opcional: FAST, STANDARD ou FULL.")
    return parser.parse_args()


def resolve_task_path(raw_path: str) -> Path:
    task_path = Path(raw_path)
    if not task_path.is_absolute():
        task_path = (ROOT / task_path).resolve()
    return task_path


def main() -> int:
    args = parse_args()
    task_file = resolve_task_path(args.task_file)
    task_source = str(task_file.relative_to(ROOT)) if task_file.is_relative_to(ROOT) else str(task_file)
    fallback_task_id = task_file.stem or "unknown-task"
    requested_mode = args.mode.upper() if args.mode else "unknown"

    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT / ".env.local", overwrite=True)
    ensure_runtime()

    if not task_file.exists():
        error_message = f"Task não encontrada: {task_file}"
        write_failure_record(
            task_id=fallback_task_id,
            mode=requested_mode,
            source=task_source,
            stage="preflight",
            error_message=error_message,
        )
        append_log(fallback_task_id, "error", error_message)
        eprint(error_message)
        return 1

    try:
        task = load_json(task_file)
        mode = resolve_mode(task, args.mode)
        validate_task(task, mode)
    except ValueError as exc:
        error_message = str(exc)
        write_failure_record(
            task_id=fallback_task_id,
            mode=requested_mode,
            source=task_source,
            stage="validation",
            error_message=error_message,
        )
        append_log(fallback_task_id, "error", error_message)
        eprint(error_message)
        return 1

    task_id = task["task_id"]

    if args.validate_only:
        print(
            json.dumps(
                {
                    "task_id": task_id,
                    "status": "valid",
                    "mode": mode,
                    "source": task_source,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    append_log(task_id, "running", f"Execução iniciada em modo {mode}")

    state = read_state()
    state["status"] = "running"
    state["current_task"] = build_current_task(task, mode, task_source)
    write_state(state)

    runtime_payload = {
        "task": task,
        "mode": mode,
        "task_source": task_source,
        "started_at": now_iso(),
    }
    context_info: dict = {}
    try:
        context_info = prepare_context_packet(task, task_id, task_source, mode)
        if context_info:
            runtime_payload["context"] = {
                "issue_identifier": context_info.get("issue_identifier"),
                "issue_title": context_info.get("issue_title"),
                "objective": context_info.get("objective"),
                "context_packet_path": context_info.get("context_packet_path"),
                "memory_backend": context_info.get("memory_backend"),
                "retrieved_memory_count": context_info.get("retrieved_memory_count"),
                "mapping": context_info.get("mapping"),
            }
            state = read_state()
            state["current_task"] = {
                **build_current_task(task, mode, task_source),
                "resolved_linear_issue_identifier": context_info.get("issue_identifier"),
                "context_packet": context_info.get("context_packet_path"),
                "memory_backend": context_info.get("memory_backend"),
                "retrieved_memory_count": context_info.get("retrieved_memory_count"),
            }
            write_state(state)
            append_log(
                task_id,
                "context_packet",
                f"Context packet pronto em {context_info.get('context_packet_path')} (memory_backend: {context_info.get('memory_backend')}, retrieved_memories: {context_info.get('retrieved_memory_count')})",
            )

        running_sync = try_publish_linear_runtime(
            task=task,
            task_source=task_source,
            mode=mode,
            event="running",
            context_info=context_info,
        )
        log_linear_sync(task_id, running_sync)

        if mode == "FULL":
            snapshot_state(task_id, "before", state)
            record_runtime(task_id, runtime_payload)

        output = execute(task, mode)
        registry_file = write_registry_record(
            {
                "task": task,
                "context": runtime_payload.get("context"),
                "execution": {
                    "mode": mode,
                    "status": "done",
                    "source": task_source,
                    "recorded_at": now_iso(),
                    "output": output,
                },
            },
            task_id,
        )

        memory_sync = try_persist_runtime_memory(
            task=task,
            task_source=task_source,
            mode=mode,
            registry_file=registry_file,
            output=output,
            context_info=context_info,
            status="done",
        )
        update_registry_record(registry_file, {"memory_sync": memory_sync})
        append_log(task_id, "memory_sync", f"Memory sync done: {memory_sync.get('status')}")

        linear_sync = try_publish_linear_runtime(
            task=task,
            task_source=task_source,
            mode=mode,
            event="done",
            registry_file=registry_file,
            output=output,
            context_info=context_info,
        )
        log_linear_sync(task_id, linear_sync)
        update_registry_record(registry_file, {"linear_sync": linear_sync})

        state = read_state()
        state["status"] = "idle"
        state["current_task"] = None
        state.setdefault("history", []).append(build_history_entry(task, mode, "done", registry_file, task_source, context_info))
        write_state(state)

        if mode == "FULL":
            snapshot_state(task_id, "after", state)
            record_runtime(
                task_id,
                {
                    **runtime_payload,
                    "completed_at": now_iso(),
                    "status": "done",
                    "output": output,
                    "registry_record": registry_file,
                },
            )

        append_log(task_id, "done", f"Task concluída com sucesso em modo {mode}")
        print(
            json.dumps(
                {
                    "task_id": task_id,
                    "status": "done",
                    "mode": mode,
                    "registry_record": registry_file,
                    "linear_sync": linear_sync,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        error_message = str(exc)
        registry_file = write_failure_record(
            task_id=task_id,
            mode=mode,
            source=task_source,
            stage="execution",
            error_message=error_message,
            task=task,
        )
        update_registry_record(registry_file, {"context": runtime_payload.get("context")})

        memory_sync = try_persist_runtime_memory(
            task=task,
            task_source=task_source,
            mode=mode,
            registry_file=registry_file,
            context_info=context_info,
            status="error",
            error_message=error_message,
        )
        update_registry_record(registry_file, {"memory_sync": memory_sync})
        append_log(task_id, "memory_sync", f"Memory sync error-path: {memory_sync.get('status')}")

        linear_sync = try_publish_linear_runtime(
            task=task,
            task_source=task_source,
            mode=mode,
            event="error",
            registry_file=registry_file,
            error_message=error_message,
            context_info=context_info,
        )
        log_linear_sync(task_id, linear_sync)
        update_registry_record(registry_file, {"linear_sync": linear_sync})

        state = read_state()
        state["status"] = "error"
        state["current_task"] = None
        state.setdefault("history", []).append(build_history_entry(task, mode, "error", registry_file, task_source, context_info))
        write_state(state)

        if mode == "FULL":
            snapshot_state(task_id, "error", state)
            record_runtime(
                task_id,
                {
                    **runtime_payload,
                    "failed_at": now_iso(),
                    "status": "error",
                    "error": error_message,
                    "registry_record": registry_file,
                },
            )

        append_log(task_id, "error", error_message)
        eprint(f"Erro ao executar task: {error_message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
