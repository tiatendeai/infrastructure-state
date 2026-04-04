from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol
import json


class MemoryError(RuntimeError):
    """Erro base da camada de memória."""


class MemoryBackendNotConfigured(MemoryError):
    """Backend não configurado."""


class MemoryBackendActivationDisabled(MemoryError):
    """Ativação real do backend desabilitada nesta tranche."""


@dataclass
class MemoryRecord:
    memory_id: str
    layer: str
    summary: str
    source: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MemoryRecord":
        return cls(
            memory_id=str(payload["memory_id"]),
            layer=str(payload["layer"]),
            summary=str(payload["summary"]),
            source=str(payload["source"]),
            title=str(payload.get("title", "")),
            metadata=dict(payload.get("metadata", {})),
        )


class MemoryBackend(Protocol):
    def save(self, record: MemoryRecord) -> MemoryRecord: ...
    def get(self, memory_id: str) -> MemoryRecord | None: ...
    def search(self, query: str, *, layer: str | None = None, limit: int = 5) -> list[MemoryRecord]: ...
    def update(self, memory_id: str, patch: dict[str, Any]) -> MemoryRecord: ...


class MockMemoryBackend:
    def __init__(self, records: list[MemoryRecord] | None = None) -> None:
        self._records: dict[str, MemoryRecord] = {}
        for record in records or []:
            self._records[record.memory_id] = record

    @classmethod
    def from_fixture(cls, fixture_path: str | Path) -> "MockMemoryBackend":
        path = Path(fixture_path)
        if not path.exists():
            return cls([])
        payload = json.loads(path.read_text(encoding="utf-8"))
        records = [MemoryRecord.from_dict(item) for item in payload.get("records", [])]
        return cls(records)

    def save(self, record: MemoryRecord) -> MemoryRecord:
        self._records[record.memory_id] = record
        return record

    def get(self, memory_id: str) -> MemoryRecord | None:
        return self._records.get(memory_id)

    def search(self, query: str, *, layer: str | None = None, limit: int = 5) -> list[MemoryRecord]:
        normalized = query.strip().lower()
        matches: list[MemoryRecord] = []
        for record in self._records.values():
            if layer and record.layer != layer:
                continue
            haystack = " ".join(
                [record.memory_id, record.title, record.summary, json.dumps(record.metadata, ensure_ascii=False)]
            ).lower()
            if not normalized or normalized in haystack:
                matches.append(record)
        matches.sort(key=lambda item: (item.layer, item.memory_id))
        return matches[:limit]

    def update(self, memory_id: str, patch: dict[str, Any]) -> MemoryRecord:
        current = self.get(memory_id)
        if current is None:
            raise MemoryError(f"Memória não encontrada: {memory_id}")
        payload = current.to_dict()
        payload.update(patch)
        updated = MemoryRecord.from_dict(payload)
        self._records[memory_id] = updated
        return updated


def serialize_records(records: list[MemoryRecord]) -> list[dict[str, Any]]:
    return [record.to_dict() for record in records]
