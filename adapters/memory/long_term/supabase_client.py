from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from adapters.memory.interface.memory import MemoryBackendNotConfigured, MemoryError, MemoryRecord


class SupabaseMemoryBackend:
    """Backend real de memória longa usando Supabase REST sobre tabelas Jarvis existentes."""

    def __init__(
        self,
        url: str | None = None,
        service_role_key: str | None = None,
        anchor_title: str | None = None,
    ) -> None:
        self.url = (url or os.getenv("SUPABASE_URL") or os.getenv("RUPTUR_SUPABASE_URL") or "").rstrip("/")
        self.service_role_key = service_role_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
        self.anchor_title = anchor_title or os.getenv("SUPABASE_MEMORY_ANCHOR_TITLE", "Memory Layer Anchor")
        self.created_by = os.getenv("SUPABASE_MEMORY_CREATED_BY", "codex")
        self._anchor_id: str | None = None

    def _ensure_ready(self) -> None:
        if not self.url or not self.service_role_key:
            raise MemoryBackendNotConfigured("Supabase não configurado. Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY.")

    def _headers(self, *, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _request(
        self,
        path: str,
        *,
        method: str = "GET",
        query: list[tuple[str, str]] | None = None,
        payload: Any | None = None,
        prefer: str | None = None,
    ) -> Any:
        self._ensure_ready()
        url = f"{self.url}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=self._headers(prefer=prefer), method=method)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise MemoryError(f"Erro HTTP do Supabase ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise MemoryError(f"Falha de rede ao chamar o Supabase: {exc.reason}") from exc

        if not raw.strip():
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MemoryError("Resposta inválida do Supabase: JSON malformado") from exc

    def _anchor(self) -> str:
        if self._anchor_id:
            return self._anchor_id
        rows = self._request(
            "/rest/v1/jarvis_missions",
            query=[("select", "id,title"), ("title", f"eq.{self.anchor_title}"), ("limit", "1")],
        ) or []
        if rows:
            self._anchor_id = str(rows[0]["id"])
            return self._anchor_id
        created = self._request(
            "/rest/v1/jarvis_missions",
            method="POST",
            payload={
                "title": self.anchor_title,
                "demand": "Âncora de memória longa do infrastructure-state",
                "status": "active",
                "source": "infrastructure-state",
                "priority": "medium",
                "metadata": {"kind": "memory_anchor"},
            },
            prefer="return=representation",
        )
        if not created:
            raise MemoryError("Falha ao criar a âncora de memória no Supabase.")
        self._anchor_id = str(created[0]["id"])
        return self._anchor_id

    def _row_to_record(self, row: dict[str, Any]) -> MemoryRecord | None:
        message = row.get("message")
        if not isinstance(message, str):
            return None
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            return None
        required = {"memory_id", "layer", "summary", "source"}
        if not required.issubset(payload):
            return None
        metadata = dict(payload.get("metadata", {}))
        metadata["_supabase_row_id"] = row.get("id")
        payload["metadata"] = metadata
        return MemoryRecord.from_dict(payload)

    def _rows(self) -> list[dict[str, Any]]:
        anchor_id = self._anchor()
        rows = self._request(
            "/rest/v1/jarvis_mission_updates",
            query=[
                ("select", "id,mission_id,kind,message,created_at,created_by"),
                ("mission_id", f"eq.{anchor_id}"),
                ("order", "created_at.desc"),
                ("limit", "500"),
            ],
        ) or []
        if not isinstance(rows, list):
            return []
        return rows

    def _records_by_latest_id(self) -> dict[str, MemoryRecord]:
        records: dict[str, MemoryRecord] = {}
        for row in self._rows():
            record = self._row_to_record(row)
            if record and record.memory_id not in records:
                records[record.memory_id] = record
        return records

    def save(self, record: MemoryRecord) -> MemoryRecord:
        existing = self.get(record.memory_id)
        payload = record.to_dict()
        if existing and existing.metadata.get("_supabase_row_id"):
            row_id = str(existing.metadata["_supabase_row_id"])
            self._request(
                "/rest/v1/jarvis_mission_updates",
                method="PATCH",
                query=[("id", f"eq.{row_id}")],
                payload={
                    "kind": record.layer,
                    "message": json.dumps(payload, ensure_ascii=False),
                    "created_by": self.created_by,
                },
                prefer="return=representation",
            )
            payload.setdefault("metadata", {})["_supabase_row_id"] = row_id
            return MemoryRecord.from_dict(payload)

        created = self._request(
            "/rest/v1/jarvis_mission_updates",
            method="POST",
            payload={
                "mission_id": self._anchor(),
                "kind": record.layer,
                "message": json.dumps(payload, ensure_ascii=False),
                "created_by": self.created_by,
            },
            prefer="return=representation",
        )
        if created:
            payload.setdefault("metadata", {})["_supabase_row_id"] = created[0].get("id")
        return MemoryRecord.from_dict(payload)

    def get(self, memory_id: str) -> MemoryRecord | None:
        return self._records_by_latest_id().get(memory_id)

    def search(self, query: str, *, layer: str | None = None, limit: int = 5) -> list[MemoryRecord]:
        normalized = query.strip().lower()
        matches: list[MemoryRecord] = []
        for record in self._records_by_latest_id().values():
            if layer and record.layer != layer:
                continue
            haystack = " ".join(
                [
                    record.memory_id,
                    record.layer,
                    record.title,
                    record.summary,
                    record.source,
                    json.dumps(record.metadata, ensure_ascii=False),
                ]
            ).lower()
            if normalized and normalized not in haystack:
                continue
            matches.append(record)
        matches.sort(key=lambda item: (item.layer, item.memory_id))
        return matches[:limit]

    def update(self, memory_id: str, patch: dict[str, Any]) -> MemoryRecord:
        current = self.get(memory_id)
        if current is None:
            raise MemoryError(f"Memória não encontrada: {memory_id}")
        payload = current.to_dict()
        payload.update(patch)
        metadata_patch = patch.get("metadata")
        if isinstance(metadata_patch, dict):
            merged = dict(current.metadata)
            merged.update(metadata_patch)
            payload["metadata"] = merged
        updated = MemoryRecord.from_dict(payload)
        return self.save(updated)
