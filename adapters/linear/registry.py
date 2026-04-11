from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from adapters.linear.client import LinearConfigError

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAPPING_PATH = ROOT / "registry" / "linear-mapping.yaml"


@dataclass
class LinearRegistryMeta:
    organization_id: str = ""
    organization_url_key: str = ""
    team_id: str = ""
    team_key: str = ""
    team_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LinearIssueMapping:
    backlog_key: str = ""
    linear_issue_identifier: str = ""
    linear_issue_id: str = ""
    local_task: str = ""
    project: str = ""
    local_status: str = ""

    @property
    def linear_issue_uuid(self) -> str:
        return self.linear_issue_id

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["linear_issue_uuid"] = self.linear_issue_uuid
        return payload


@dataclass
class LinearMappingRegistry:
    meta: LinearRegistryMeta
    mappings: list[LinearIssueMapping]
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "meta": self.meta.to_dict(),
            "mappings": [item.to_dict() for item in self.mappings],
            "source": self.source,
        }


def load_linear_mapping_registry(path: Path | None = None) -> LinearMappingRegistry:
    mapping_path = path or DEFAULT_MAPPING_PATH
    if not mapping_path.exists():
        raise LinearConfigError(f"registry de mapping não encontrado: {mapping_path}")

    meta = LinearRegistryMeta()
    mappings: list[LinearIssueMapping] = []
    section = ""
    subsection = ""
    current_mapping: dict[str, str] | None = None

    for raw_line in mapping_path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw_line)
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        token = line.strip()

        if indent == 0 and token.endswith(":"):
            section = token[:-1]
            subsection = ""
            continue

        if section == "linear":
            if indent == 2 and token.endswith(":"):
                subsection = token[:-1]
                continue
            if indent == 4 and ":" in token:
                key, value = _split_key_value(token)
                if subsection == "organization":
                    if key == "id":
                        meta.organization_id = value
                    elif key == "url_key":
                        meta.organization_url_key = value
                elif subsection == "team":
                    if key == "id":
                        meta.team_id = value
                    elif key == "key":
                        meta.team_key = value
                    elif key == "name":
                        meta.team_name = value
                continue

        if section == "mappings":
            if indent == 2 and token.startswith("- "):
                if current_mapping:
                    mappings.append(_build_mapping(current_mapping))
                current_mapping = {}
                rest = token[2:].strip()
                if rest and ":" in rest:
                    key, value = _split_key_value(rest)
                    current_mapping[key] = value
                continue
            if indent == 4 and current_mapping is not None and ":" in token:
                key, value = _split_key_value(token)
                current_mapping[key] = value
                continue

    if current_mapping:
        mappings.append(_build_mapping(current_mapping))

    return LinearMappingRegistry(
        meta=meta,
        mappings=mappings,
        source=str(mapping_path.relative_to(ROOT) if mapping_path.is_relative_to(ROOT) else mapping_path),
    )


def resolve_issue_mapping(
    *,
    registry: LinearMappingRegistry,
    task: dict[str, Any] | None = None,
    task_source: str | None = None,
    issue_ref: str | None = None,
    local_task: str | None = None,
) -> LinearIssueMapping:
    candidates: list[str] = []
    if issue_ref:
        candidates.append(issue_ref.strip())
    if local_task:
        candidates.append(_normalize_relpath(local_task))

    if task:
        for field_name in ("linear_issue_identifier", "linear_issue_uuid", "linear_issue_id"):
            raw = str(task.get(field_name, "")).strip()
            if raw:
                candidates.append(raw)
        if task_source:
            candidates.append(_normalize_relpath(task_source))
        task_input = task.get("input", {})
        if isinstance(task_input, dict):
            for field_name in ("task_file", "source_task", "source"):
                raw = str(task_input.get(field_name, "")).strip()
                if raw:
                    candidates.append(_normalize_relpath(raw))

    normalized = [item for item in dict.fromkeys(_normalize_candidate(value) for value in candidates if value)]
    if not normalized:
        raise LinearConfigError("Não foi possível resolver mapping: nenhuma referência de issue/task foi informada")

    matches = [item for item in registry.mappings if _mapping_matches(item, normalized)]
    if not matches:
        refs = ", ".join(normalized)
        raise LinearConfigError(f"Nenhum mapping do Linear encontrado para: {refs}")
    if len(matches) > 1:
        refs = ", ".join(normalized)
        raise LinearConfigError(f"Mapping do Linear ambíguo para: {refs}")
    return matches[0]


def build_runtime_context(
    *,
    task: dict[str, Any],
    task_source: str,
    mapping_path: Path | None = None,
) -> dict[str, Any]:
    registry = load_linear_mapping_registry(mapping_path)
    mapping = resolve_issue_mapping(registry=registry, task=task, task_source=task_source)
    return {
        "registry": registry.to_dict(),
        "mapping": mapping.to_dict(),
        "task_source": _normalize_relpath(task_source),
    }


def _normalize_candidate(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""
    if raw.startswith("tasks/") or raw.endswith(".task.json"):
        return _normalize_relpath(raw)
    return raw


def _mapping_matches(mapping: LinearIssueMapping, candidates: list[str]) -> bool:
    possible_values = {
        mapping.backlog_key.strip(),
        mapping.linear_issue_identifier.strip(),
        mapping.linear_issue_uuid.strip(),
        _normalize_relpath(mapping.local_task),
    }
    possible_values = {value for value in possible_values if value}
    return any(candidate in possible_values for candidate in candidates)


def _normalize_relpath(raw_path: str) -> str:
    path = Path(raw_path)
    if path.is_absolute():
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)
    return str(path).replace("\\", "/")


def _split_key_value(token: str) -> tuple[str, str]:
    key, value = token.split(":", 1)
    return key.strip(), _parse_scalar(value.strip())


def _parse_scalar(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"\"", "'"}:
        return raw[1:-1]
    if raw in {"true", "false", "null"}:
        return raw
    return raw


def _strip_comment(line: str) -> str:
    in_quotes = False
    prev = ""
    result: list[str] = []
    for char in line:
        if char == '"' and prev != "\\":
            in_quotes = not in_quotes
        if char == "#" and not in_quotes:
            break
        result.append(char)
        prev = char
    return "".join(result).rstrip()


def _build_mapping(payload: dict[str, str]) -> LinearIssueMapping:
    return LinearIssueMapping(
        backlog_key=payload.get("backlog_key", ""),
        linear_issue_identifier=payload.get("linear_issue_identifier", ""),
        linear_issue_id=payload.get("linear_issue_id", ""),
        local_task=payload.get("local_task", ""),
        project=payload.get("project", ""),
        local_status=payload.get("local_status", ""),
    )
