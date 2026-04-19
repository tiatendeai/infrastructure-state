#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL_STATE = ROOT / "kernel" / "state.json"
LOG_FILE = ROOT / "logs" / "execution.log"
REGISTRY_DIR = ROOT / "registry" / "runs"
SNAPSHOT_DIR = ROOT / "state" / "snapshots"
AGENTS_RUNTIME_DIR = ROOT / ".agents" / "runtime"

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

    for field_name in ("linear_issue_id", "linear_project", "linear_team_key", "service_target", "execution_policy"):
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
        "linear_project",
        "linear_team_key",
        "service_target",
        "approval_required",
        "execution_policy",
    ):
        if field_name in task:
            payload[field_name] = task[field_name]
    return payload


def build_history_entry(task: dict, mode: str, status: str, registry_file: str, task_source: str) -> dict:
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
        "linear_project",
        "linear_team_key",
        "service_target",
        "approval_required",
        "execution_policy",
    ):
        if field_name in task:
            payload[field_name] = task[field_name]
    return payload


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

    try:
        if mode == "FULL":
            snapshot_state(task_id, "before", state)
            record_runtime(task_id, runtime_payload)

        output = execute(task, mode)
        registry_file = write_registry_record(
            {
                "task": task,
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

        state = read_state()
        state["status"] = "idle"
        state["current_task"] = None
        state.setdefault("history", []).append(build_history_entry(task, mode, "done", registry_file, task_source))
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

        state = read_state()
        state["status"] = "error"
        state["current_task"] = None
        state.setdefault("history", []).append(build_history_entry(task, mode, "error", registry_file, task_source))
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
