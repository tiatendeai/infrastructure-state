from __future__ import annotations

import os
from typing import Any

from adapters.memory.interface.memory import (
    MemoryBackendActivationDisabled,
    MemoryBackendNotConfigured,
    MemoryRecord,
)


class SupabaseMemoryBackend:
    """Stub local para futura ativação de Supabase."""

    def __init__(self, url: str | None = None, service_role_key: str | None = None) -> None:
        self.url = url or os.getenv("SUPABASE_URL")
        self.service_role_key = service_role_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    def _ensure_ready(self) -> None:
        if not self.url or not self.service_role_key:
            raise MemoryBackendNotConfigured(
                "Supabase não configurado. Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY quando a ativação real for autorizada."
            )
        raise MemoryBackendActivationDisabled(
            "Ativação real de Supabase está fora do escopo da tranche 3A."
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
