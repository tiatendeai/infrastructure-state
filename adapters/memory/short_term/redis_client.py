from __future__ import annotations

import json
import os
import socket
from typing import Any
from urllib.parse import urlparse

from adapters.memory.interface.memory import MemoryBackendNotConfigured, MemoryError, MemoryRecord


class RedisMemoryBackend:
    """Backend real de memória curta usando Redis via RESP puro."""

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self._config = self._parse_url(self.redis_url)

    def _parse_url(self, redis_url: str | None) -> dict[str, Any] | None:
        if not redis_url:
            return None
        parsed = urlparse(redis_url)
        if parsed.scheme not in {"redis", "rediss"}:
            raise MemoryError(f"REDIS_URL inválido: esquema não suportado em {redis_url!r}")
        return {
            "host": parsed.hostname or "127.0.0.1",
            "port": parsed.port or 6379,
            "password": parsed.password or "",
            "db": int((parsed.path or "/0").lstrip("/") or "0"),
            "use_tls": parsed.scheme == "rediss",
        }

    def _ensure_ready(self) -> dict[str, Any]:
        if not self._config:
            raise MemoryBackendNotConfigured("Redis não configurado. Defina REDIS_URL.")
        return self._config

    def _connect(self) -> socket.socket:
        config = self._ensure_ready()
        sock = socket.create_connection((config["host"], config["port"]), timeout=5)
        if config["use_tls"]:
            raise MemoryError("rediss:// ainda não suportado por este backend local.")
        if config["password"]:
            self._command(sock, "AUTH", config["password"])
        if config["db"]:
            self._command(sock, "SELECT", str(config["db"]))
        return sock

    def _encode_bulk(self, value: str) -> bytes:
        payload = value.encode("utf-8")
        return b"$" + str(len(payload)).encode("ascii") + b"\r\n" + payload + b"\r\n"

    def _send_command(self, sock: socket.socket, *parts: str) -> None:
        payload = b"*" + str(len(parts)).encode("ascii") + b"\r\n"
        for part in parts:
            payload += self._encode_bulk(part)
        sock.sendall(payload)

    def _readline(self, sock: socket.socket) -> bytes:
        buffer = bytearray()
        while True:
            chunk = sock.recv(1)
            if not chunk:
                raise MemoryError("Conexão Redis encerrada inesperadamente.")
            buffer.extend(chunk)
            if buffer.endswith(b"\r\n"):
                return bytes(buffer[:-2])

    def _read_response(self, sock: socket.socket) -> Any:
        prefix = sock.recv(1)
        if not prefix:
            raise MemoryError("Resposta vazia do Redis.")
        if prefix == b"+":
            return self._readline(sock).decode("utf-8")
        if prefix == b"-":
            raise MemoryError(f"Erro do Redis: {self._readline(sock).decode('utf-8', errors='replace')}")
        if prefix == b":":
            return int(self._readline(sock))
        if prefix == b"$":
            size = int(self._readline(sock))
            if size == -1:
                return None
            payload = bytearray()
            remaining = size + 2
            while remaining > 0:
                chunk = sock.recv(remaining)
                if not chunk:
                    raise MemoryError("Resposta bulk truncada do Redis.")
                payload.extend(chunk)
                remaining -= len(chunk)
            return bytes(payload[:-2]).decode("utf-8")
        if prefix == b"*":
            length = int(self._readline(sock))
            if length == -1:
                return None
            return [self._read_response(sock) for _ in range(length)]
        raise MemoryError(f"Prefixo RESP não suportado: {prefix!r}")

    def _command(self, sock: socket.socket, *parts: str) -> Any:
        self._send_command(sock, *parts)
        return self._read_response(sock)

    def _ping(self) -> None:
        sock = self._connect()
        try:
            result = self._command(sock, "PING")
            if result != "PONG":
                raise MemoryError(f"PING Redis inválido: {result!r}")
        finally:
            sock.close()

    def _memory_key(self, memory_id: str) -> str:
        return f"memory:{memory_id}"

    def save(self, record: MemoryRecord) -> MemoryRecord:
        self._ping()
        payload = json.dumps(record.to_dict(), ensure_ascii=False)
        sock = self._connect()
        try:
            self._command(sock, "SET", self._memory_key(record.memory_id), payload)
            self._command(sock, "SADD", "memory:index", self._memory_key(record.memory_id))
            self._command(sock, "SADD", f"memory:index:layer:{record.layer}", self._memory_key(record.memory_id))
        finally:
            sock.close()
        return record

    def get(self, memory_id: str) -> MemoryRecord | None:
        self._ping()
        sock = self._connect()
        try:
            raw = self._command(sock, "GET", self._memory_key(memory_id))
        finally:
            sock.close()
        if raw is None:
            return None
        return MemoryRecord.from_dict(json.loads(raw))

    def search(self, query: str, *, layer: str | None = None, limit: int = 5) -> list[MemoryRecord]:
        self._ping()
        sock = self._connect()
        try:
            index_key = f"memory:index:layer:{layer}" if layer else "memory:index"
            keys = self._command(sock, "SMEMBERS", index_key) or []
            if isinstance(keys, str):
                keys = [keys]
        finally:
            sock.close()

        normalized = query.strip().lower()
        matches: list[MemoryRecord] = []
        for key in sorted(keys):
            if not isinstance(key, str):
                continue
            memory_id = key.removeprefix("memory:")
            record = self.get(memory_id)
            if not record:
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
