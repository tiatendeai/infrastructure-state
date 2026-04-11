from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import os

from adapters.linear.client import LinearClient, LinearConfig, LinearConfigError, parse_bool
from adapters.linear.issues import add_comment, update_issue_status
from adapters.linear.registry import (
    DEFAULT_MAPPING_PATH,
    LinearIssueMapping,
    load_linear_mapping_registry,
    resolve_issue_mapping,
)
from adapters.linear.statuses import find_status_by_name

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class LinearRuntimeConfig:
    enabled: bool = False
    strict: bool = False
    mapping_path: Path = DEFAULT_MAPPING_PATH
    status_running: str = "Running"
    status_done: str = "Done"
    status_error: str = "Failed"
    comment_on_running: bool = False
    comment_on_done: bool = True
    comment_on_error: bool = True
    status_on_running: bool = True
    status_on_done: bool = True
    status_on_error: bool = True
    append_expected_output: bool = True
    comment_header: str = "Execução local sincronizada pelo infrastructure-state."

    @classmethod
    def from_env(cls, root: Path | None = None) -> "LinearRuntimeConfig":
        if root is None:
            root = ROOT
        config = cls(
            enabled=parse_bool(os.getenv("LINEAR_RUNTIME_SYNC_ENABLED"), False),
            strict=parse_bool(os.getenv("LINEAR_RUNTIME_SYNC_STRICT"), False),
            mapping_path=_resolve_mapping_path(os.getenv("LINEAR_RUNTIME_MAPPING_PATH", ""), root),
            status_running=os.getenv("LINEAR_RUNTIME_STATUS_RUNNING", "Running").strip() or "Running",
            status_done=os.getenv("LINEAR_RUNTIME_STATUS_DONE", "Done").strip() or "Done",
            status_error=os.getenv("LINEAR_RUNTIME_STATUS_ERROR", "Failed").strip() or "Failed",
            comment_on_running=parse_bool(os.getenv("LINEAR_RUNTIME_COMMENT_ON_RUNNING"), False),
            comment_on_done=parse_bool(os.getenv("LINEAR_RUNTIME_COMMENT_ON_DONE"), True),
            comment_on_error=parse_bool(os.getenv("LINEAR_RUNTIME_COMMENT_ON_ERROR"), True),
            status_on_running=parse_bool(os.getenv("LINEAR_RUNTIME_STATUS_ON_RUNNING"), True),
            status_on_done=parse_bool(os.getenv("LINEAR_RUNTIME_STATUS_ON_DONE"), True),
            status_on_error=parse_bool(os.getenv("LINEAR_RUNTIME_STATUS_ON_ERROR"), True),
            append_expected_output=parse_bool(os.getenv("LINEAR_RUNTIME_APPEND_EXPECTED_OUTPUT"), True),
            comment_header=os.getenv(
                "LINEAR_RUNTIME_COMMENT_HEADER",
                "Execução local sincronizada pelo infrastructure-state.",
            ).strip()
            or "Execução local sincronizada pelo infrastructure-state.",
        )
        return config


@dataclass
class LinearRuntimePublishResult:
    status: str
    event: str
    issue_identifier: str | None = None
    issue_uuid: str | None = None
    dry_run: bool = False
    mapping: dict[str, Any] = field(default_factory=dict)
    target_status_name: str | None = None
    status_update: dict[str, Any] | None = None
    comment: dict[str, Any] | None = None
    comment_preview: str | None = None
    skipped_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "status": self.status,
            "event": self.event,
            "issue_identifier": self.issue_identifier,
            "issue_uuid": self.issue_uuid,
            "dry_run": self.dry_run,
            "mapping": self.mapping,
            "target_status_name": self.target_status_name,
            "status_update": self.status_update,
            "comment": self.comment,
            "comment_preview": self.comment_preview,
            "skipped_reason": self.skipped_reason,
        }
        return {key: value for key, value in payload.items() if value not in (None, {}, [])}


def publish_task_runtime_update(
    *,
    task: dict[str, Any],
    task_source: str,
    mode: str,
    event: str,
    registry_record: str | None = None,
    output: dict[str, Any] | None = None,
    error_message: str | None = None,
    dry_run: bool = False,
    context_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime_config = LinearRuntimeConfig.from_env(ROOT)
    if not runtime_config.enabled and not dry_run:
        return LinearRuntimePublishResult(status="skipped", event=event, skipped_reason="runtime_sync_disabled").to_dict()

    registry = load_linear_mapping_registry(runtime_config.mapping_path)
    mapping = resolve_issue_mapping(registry=registry, task=task, task_source=task_source)
    issue_identifier = mapping.linear_issue_identifier or mapping.backlog_key
    if not issue_identifier:
        raise LinearConfigError("Mapping encontrado, mas sem linear_issue_identifier")

    comment_preview = build_runtime_comment(
        task=task,
        task_source=task_source,
        mode=mode,
        event=event,
        mapping=mapping,
        registry_record=registry_record,
        output=output,
        error_message=error_message,
        runtime_config=runtime_config,
        context_info=context_info,
    )

    result = LinearRuntimePublishResult(
        status="ok" if dry_run else "pending",
        event=event,
        issue_identifier=issue_identifier,
        issue_uuid=mapping.linear_issue_uuid or None,
        dry_run=dry_run,
        mapping=mapping.to_dict(),
        target_status_name=resolve_status_name(runtime_config, event),
        comment_preview=comment_preview,
    )

    if dry_run:
        result.status = "ok"
        return result.to_dict()

    client = LinearClient(LinearConfig.from_env(ROOT))

    if should_update_status(runtime_config, event):
        target_status = find_status_by_name(client, registry.meta.team_id or registry.meta.team_key, result.target_status_name or "")
        updated_issue = update_issue_status(client, issue_identifier, str(target_status.get("id")))
        result.status_update = {
            "status_name": target_status.get("name"),
            "state_id": target_status.get("id"),
            "issue": updated_issue,
        }

    if should_add_comment(runtime_config, event):
        comment = add_comment(client, issue_identifier, comment_preview)
        result.comment = comment

    result.status = "ok"
    return result.to_dict()


def build_runtime_comment(
    *,
    task: dict[str, Any],
    task_source: str,
    mode: str,
    event: str,
    mapping: LinearIssueMapping,
    registry_record: str | None,
    output: dict[str, Any] | None,
    error_message: str | None,
    runtime_config: LinearRuntimeConfig,
    context_info: dict[str, Any] | None,
) -> str:
    lines = [runtime_config.comment_header, "", "Resumo:"]
    lines.extend(
        [
            f"- task_id: `{task.get('task_id', '')}`",
            f"- task_source: `{_rel(task_source)}`",
            f"- event: `{event}`",
            f"- status local: `{event}`",
            f"- mode: `{mode}`",
            f"- backlog_key local: `{mapping.backlog_key or task.get('linear_issue_id', '')}`",
            f"- issue Linear: `{mapping.linear_issue_identifier}`",
        ]
    )

    service_target = str(task.get("service_target", "")).strip()
    if service_target:
        lines.append(f"- service_target: `{service_target}`")
    linear_project = str(task.get("linear_project", "") or mapping.project).strip()
    if linear_project:
        lines.append(f"- project: `{linear_project}`")
    execution_policy = str(task.get("execution_policy", "")).strip()
    if execution_policy:
        lines.append(f"- execution_policy: `{execution_policy}`")
    if registry_record:
        lines.append(f"- registry_record: `{_rel(registry_record)}`")
    if context_info and context_info.get("context_packet_path"):
        lines.append(f"- context_packet: `{_rel(str(context_info['context_packet_path']))}`")
    if context_info and context_info.get("memory_backend"):
        lines.append(f"- memory_backend: `{context_info['memory_backend']}`")
    if context_info and context_info.get("retrieved_memory_count") is not None:
        lines.append(f"- retrieved_memories: `{context_info['retrieved_memory_count']}`")

    output_lines = summarize_output(output)
    if output_lines:
        lines.append("")
        lines.append("Saída resumida:")
        lines.extend(f"- {item}" for item in output_lines)

    if error_message:
        lines.append("")
        lines.append("Falha resumida:")
        lines.append(f"- {sanitize_one_line(error_message, limit=400)}")

    if runtime_config.append_expected_output:
        expected_output = task.get("expected_output", [])
        if isinstance(expected_output, list) and expected_output:
            lines.append("")
            lines.append("Artefatos esperados:")
            for item in expected_output[:8]:
                lines.append(f"- `{item}`")

    lines.append("")
    lines.append("Evidência técnica:")
    lines.append("- `kernel/state.json`")
    lines.append("- `logs/execution.log`")
    if registry_record:
        lines.append(f"- `{_rel(registry_record)}`")
    lines.append("")
    lines.append("Observação:")
    lines.append("- Este comentário resume o resultado operacional. A evidência técnica completa permanece no repositório.")
    return "\n".join(lines).strip()


def summarize_output(output: dict[str, Any] | None) -> list[str]:
    if not isinstance(output, dict) or not output:
        return []
    items: list[str] = []
    if output.get("entrypoint"):
        entrypoint = str(output.get("entrypoint"))
        args = output.get("args", [])
        if isinstance(args, list) and args:
            rendered_args = " ".join(json.dumps(str(arg), ensure_ascii=False) for arg in args[:8])
            items.append(f"entrypoint `{entrypoint}` executado com args {rendered_args}")
        else:
            items.append(f"entrypoint `{entrypoint}` executado")
    if output.get("result") and isinstance(output.get("result"), dict):
        keys = sorted(str(key) for key in output["result"].keys())
        if keys:
            items.append(f"resultado estruturado com chaves: {', '.join(keys[:8])}")
    if output.get("message"):
        items.append(sanitize_one_line(str(output.get("message")), limit=220))
    if output.get("stdout"):
        items.append(f"stdout resumido: {sanitize_one_line(str(output.get('stdout')), limit=220)}")
    return items[:5]


def sanitize_one_line(message: str, *, limit: int = 220) -> str:
    normalized = " ".join(part for part in message.replace("\r", "\n").splitlines() if part.strip())
    normalized = " ".join(normalized.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1] + "…"


def resolve_status_name(runtime_config: LinearRuntimeConfig, event: str) -> str:
    normalized = event.strip().lower()
    if normalized == "running":
        return runtime_config.status_running
    if normalized == "done":
        return runtime_config.status_done
    if normalized == "error":
        return runtime_config.status_error
    raise LinearConfigError(f"Evento de runtime não suportado: {event}")


def should_add_comment(runtime_config: LinearRuntimeConfig, event: str) -> bool:
    normalized = event.strip().lower()
    if normalized == "running":
        return runtime_config.comment_on_running
    if normalized == "done":
        return runtime_config.comment_on_done
    if normalized == "error":
        return runtime_config.comment_on_error
    return False


def should_update_status(runtime_config: LinearRuntimeConfig, event: str) -> bool:
    normalized = event.strip().lower()
    if normalized == "running":
        return runtime_config.status_on_running
    if normalized == "done":
        return runtime_config.status_on_done
    if normalized == "error":
        return runtime_config.status_on_error
    return False


def _resolve_mapping_path(raw: str, root: Path) -> Path:
    if raw.strip():
        path = Path(raw.strip())
        if not path.is_absolute():
            path = (root / path).resolve()
        return path
    return DEFAULT_MAPPING_PATH


def _rel(path_like: str) -> str:
    path = Path(path_like)
    if path.is_absolute():
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)
    return str(path).replace("\\", "/")
