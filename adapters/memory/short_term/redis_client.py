from __future__ import annotations

import os
from typing import Any

from adapters.memory.interface.memory import (
    MemoryBackendActivationDisabled,
    MemoryBackendNotConfigured,
    MemoryRecord,
)


class RedisMemoryBackend:
    """Stub local para futura ativação de Redis."""

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or os.getenv("REDIS_URL")

    def _ensure_ready(self) -> None:
        if not self.redis_url:
            raise MemoryBackendNotConfigured(
                "Redis não configurado. Defina REDIS_URL quando a ativação real for autorizada."
            )
        raise MemoryBackendActivationDisabled(
            "Ativação real de Redis está fora do escopo da tranche 3A."
        )

    def save(self, record: MemoryRecord) -> MemoryRecord:
        self._ensure_ready()
        return record

    def get(self, memory_id: str) -> MemoryRecord | None:
        self._ensure_ready()
        return None

    def search(self, query: str, *, layer: str | None = None, limit: int = 5) -> list[MemoryRecord]:
        self._ensure_ready()
        return []

    def update(self, memory_id: str, patch: dict[str, Any]) -> MemoryRecord:
        self._ensure_ready()
        raise RuntimeError("unreachable")
