#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KERNEL_STATE = ROOT / "kernel" / "state.json"
TASKS_DIR = ROOT / "tasks"
RUNS_DIR = ROOT / "registry" / "runs"
OUTPUT_PATH = ROOT / "state" / "runtime" / "hitl-board.json"
SOURCE_MANIFEST_PATH = ROOT / "state" / "registry" / "hitl-sources.json"
MIRROR_PATH = ROOT.parent / "saas" / "web" / "dashboard-dist" / "hitl-board.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def default_source_manifest() -> dict[str, Any]:
    return {
        "version": 1,
        "sources": [
            {
                "source_id": "google_adk_a2a_prod",
                "label": "Torre Google ADK/A2A — Produção",
                "tier": "production",
                "authority": "google-adk-a2a",
                "status": "unavailable",
                "kind": "external_remote",
                "priority": 1,
                "evidence": [
                    "env:HITL_GOOGLE_ADK_BOARD_PATH",
                    "env:HITL_GOOGLE_ADK_API_URL",
                    "env:HITL_GOOGLE_ADK_SOURCE_URL",
                ],
                "notes": "Fonte soberana de produção quando conectada; não deve ser confundida com dados locais.",
            },
            {
                "source_id": "macbook_local",
                "label": "MacBook Local — Estaleiro",
                "tier": "local",
                "authority": "shipyard",
                "status": "available",
                "kind": "local_state",
                "priority": 2,
                "evidence": [
                    "kernel/state.json",
                    "tasks/*.json",
                    "registry/runs/*.json",
                    "logs/execution.log",
                ],
                "notes": "Fonte operacional local do estaleiro; útil para execução, fila e histórico do trabalho.",
            },
            {
                "source_id": "dashboard_mirror",
                "label": "Mirror do HITL / Dashboard",
                "tier": "mirror",
                "authority": "dashboard",
                "status": "available",
                "kind": "ui_mirror",
                "priority": 3,
                "evidence": [
                    "../saas/web/dashboard-dist/hitl-board.json",
                    "../saas/web/dashboard-dist/metrics.html",
                ],
                "notes": "Mirror visual para o painel; não é a fonte primária, apenas espelho de leitura.",
            },
        ],
    }


def load_source_manifest() -> dict[str, Any]:
    manifest = load_json(SOURCE_MANIFEST_PATH, default=None)
    if isinstance(manifest, dict) and isinstance(manifest.get("sources"), list):
        return manifest
    manifest = default_source_manifest()
    save_json(SOURCE_MANIFEST_PATH, manifest)
    return manifest


def read_task(task_file: Path) -> dict[str, Any] | None:
    data = load_json(task_file)
    if not isinstance(data, dict):
        return None
    return data


def summarize_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": task.get("task_id"),
        "type": task.get("type"),
        "status": task.get("status"),
        "mode": task.get("mode"),
        "linear_issue_id": task.get("linear_issue_id"),
        "linear_project": task.get("linear_project"),
        "service_target": task.get("service_target"),
        "approval_required": task.get("approval_required"),
        "execution_policy": task.get("execution_policy"),
        "expected_output": task.get("expected_output", [])[:6] if isinstance(task.get("expected_output"), list) else [],
    }


def build_source_payload(source: dict[str, Any], *, local_state: dict[str, Any], open_tasks: list[dict[str, Any]], recent_history: list[dict[str, Any]], recent_runs: list[dict[str, Any]], metrics: dict[str, Any], board_path: str) -> dict[str, Any]:
    source_id = str(source.get("source_id", "")).strip()
    tier = str(source.get("tier", "local")).strip()
    status = str(source.get("status", "available")).strip()
    evidence = source.get("evidence", [])
    notes = source.get("notes", "")

    payload = {
        "source_id": source_id,
        "label": source.get("label"),
        "tier": tier,
        "authority": source.get("authority"),
        "kind": source.get("kind"),
        "status": status,
        "priority": source.get("priority", 99),
        "evidence": evidence if isinstance(evidence, list) else [],
        "notes": notes,
    }

    if source_id == "google_adk_a2a_prod":
        external_path_raw = str(
            os.environ.get("HITL_GOOGLE_ADK_BOARD_PATH")
            or os.environ.get("HITL_GOOGLE_ADK_SOURCE_PATH")
            or ""
        ).strip()
        external_path = Path(external_path_raw) if external_path_raw else None
        if external_path is not None and external_path.exists():
            external_board = load_json(external_path, default={}) or {}
            payload.update({
                "status": "connected",
                "board_ref": str(external_path),
                "freshness": external_board.get("generated_at"),
                "snapshot": {
                    "current_task": external_board.get("current_task"),
                    "queue": external_board.get("queue"),
                    "metrics": external_board.get("metrics"),
                },
            })
        else:
            payload.update({
                "status": "declarada_sem_conector",
                "board_ref": None,
                "freshness": None,
                "snapshot": None,
            })

    elif source_id == "macbook_local":
        payload.update({
            "status": "connected",
            "board_ref": str(KERNEL_STATE.relative_to(ROOT)),
            "freshness": local_state.get("status"),
            "snapshot": {
                "current_task": local_state.get("current_task"),
                "queue": {
                    "open": open_tasks,
                    "open_count": len(open_tasks),
                },
                "history": {
                    "recent": recent_history,
                    "recent_runs": recent_runs,
                },
                "metrics": metrics,
            },
        })
    elif source_id == "dashboard_mirror":
        payload.update({
            "status": "connected",
            "board_ref": board_path,
            "freshness": None,
            "snapshot": {
                "mirror_of": board_path,
            },
        })

    return payload


def collect_open_tasks(limit: int = 100) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for task_file in sorted(TASKS_DIR.glob("*.json")):
        task = read_task(task_file)
        if not task:
            continue
        if task.get("status") in {"pending", "in_progress"}:
            items.append(summarize_task(task))
    priority = {"in_progress": 0, "pending": 1}
    items.sort(key=lambda item: (priority.get(str(item.get("status")), 99), str(item.get("task_id", ""))))
    return items[:limit]


def collect_recent_history(state: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    history = state.get("history", [])
    if not isinstance(history, list):
        return []
    recent = history[-limit:]
    return [
        {
            "task_id": entry.get("task_id"),
            "status": entry.get("status"),
            "type": entry.get("type"),
            "mode": entry.get("mode"),
            "timestamp": entry.get("timestamp"),
            "linear_project": entry.get("linear_project"),
            "service_target": entry.get("service_target"),
            "resolved_linear_issue_identifier": entry.get("resolved_linear_issue_identifier"),
        }
        for entry in recent
        if isinstance(entry, dict)
    ]


def collect_recent_runs(limit: int = 6) -> list[dict[str, Any]]:
    records: list[tuple[str, dict[str, Any]]] = []
    for run_file in sorted(RUNS_DIR.glob("*.json")):
        payload = load_json(run_file)
        if not isinstance(payload, dict):
            continue
        execution = payload.get("execution", {})
        task = payload.get("task", {})
        records.append(
            (
                str(payload.get("execution", {}).get("recorded_at") or payload.get("meta", {}).get("recorded_at") or run_file.name),
                {
                    "task_id": task.get("task_id"),
                    "status": execution.get("status") or payload.get("meta", {}).get("status"),
                    "mode": execution.get("mode") or payload.get("meta", {}).get("mode"),
                    "recorded_at": execution.get("recorded_at") or payload.get("meta", {}).get("recorded_at"),
                    "source": execution.get("source") or payload.get("meta", {}).get("source"),
                    "service_target": task.get("service_target"),
                    "linear_project": task.get("linear_project"),
                },
            )
        )
    records.sort(key=lambda item: item[0])
    return [payload for _, payload in records[-limit:]]


def build_resolution_blocks(pending_tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    task_by_id = {str(item.get("task_id")): item for item in pending_tasks if isinstance(item, dict)}

    blocks = [
        {
            "block_id": "tokens-p0",
            "title": "Tokens + sessão + login",
            "priority": "P0",
            "status": "blocked",
            "reason": "Sessão, login e revogação precisam ficar coerentes antes de declarar o projeto pronto.",
            "task_refs": [
                "INFRA-027-sprint-final-sessao-login-observabilidade-seguranca",
                "INFRA-028-tokens-p0-sessao-login-seguranca-observabilidade",
            ],
            "next_action": "Fechar contrato de sessão, token opaco, revogação e auditoria no Agent Hub.",
        },
        {
            "block_id": "debug-triage",
            "title": "Debug + falhas + erros",
            "priority": "P0",
            "status": "open",
            "reason": "Erros e falhas recorrentes precisam virar triagem explícita com evidências e resolução.",
            "task_refs": [
                "INFRA-017-ligar-legado-kvm2-no-ruptur-cloud-lab",
                "INFRA-021-jarvis-p0-ansible-terraform-iac-dns",
                "INFRA-029-debug-falhas-erros-triagem",
                "INFRA-027-sprint-final-sessao-login-observabilidade-seguranca",
            ],
            "next_action": "Classificar falhas por causa raiz, impacto e bloqueio operacional.",
        },
        {
            "block_id": "technical-debt",
            "title": "Dívida técnica canônica",
            "priority": "P1",
            "status": "open",
            "reason": "Débitos devem permanecer visíveis até haver decisão explícita de fechamento.",
            "task_refs": [
                "INFRA-019-rtk-shipyard-state-governance",
                "INFRA-020-instalar-novas-funcionalidades-e-ferramentas-no-gcp-ruptur-cloud-labs",
                "INFRA-027-sprint-final-sessao-login-observabilidade-seguranca",
            ],
            "next_action": "Manter os débitos como backlog governado e rastreável no HITL.",
        },
        {
            "block_id": "external-integrations",
            "title": "Integrações externas bloqueadoras",
            "priority": "P0",
            "status": "open",
            "reason": "Linear e Supabase exigem validação explícita; ausência de credencial/CA não pode virar erro ambíguo.",
            "task_refs": [
                "INFRA-030-linear-credential-gap-and-runtime-sync",
                "INFRA-031-supabase-tls-ssl-backend-sync",
            ],
            "next_action": "Separar ausência de configuração de falha real e registrar decisão no HITL.",
        },
    ]

    for block in blocks:
        block["task_count"] = sum(1 for task_id in block["task_refs"] if task_id in task_by_id)
        block["linked_tasks"] = [task_by_id[task_id] for task_id in block["task_refs"] if task_id in task_by_id]

    return blocks


def read_registry_state(state: dict[str, Any]) -> dict[str, Any]:
    current_task = state.get("current_task") if isinstance(state, dict) else None
    if not isinstance(current_task, dict):
        current_task = None

    history = state.get("history", [])
    counts = Counter()
    if isinstance(history, list):
        for entry in history:
            if isinstance(entry, dict):
                counts[str(entry.get("status", "unknown"))] += 1

    pending_tasks = collect_open_tasks()
    recent_history = collect_recent_history(state)
    recent_runs = collect_recent_runs()
    source_manifest = load_source_manifest()

    current_agent = None
    if current_task:
        current_agent = (
            current_task.get("service_target")
            or current_task.get("linear_project")
            or current_task.get("task_id")
        )

    last_done = next((entry for entry in reversed(recent_history) if entry.get("status") == "done"), None)
    last_error = next((entry for entry in reversed(recent_history) if entry.get("status") == "error"), None)
    running_task = current_task if current_task else next((task for task in pending_tasks if task.get("status") == "in_progress"), None)

    now = datetime.now(timezone.utc)
    day_window = now - timedelta(hours=24)
    last_24h = 0
    success_24h = 0
    error_24h = 0
    if isinstance(history, list):
        for entry in history:
            if not isinstance(entry, dict):
                continue
            timestamp = entry.get("timestamp")
            try:
                ts = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            except Exception:
                continue
            if ts >= day_window:
                last_24h += 1
                if entry.get("status") == "done":
                    success_24h += 1
                elif entry.get("status") == "error":
                    error_24h += 1

    total_terminal = counts.get("done", 0) + counts.get("error", 0)
    success_rate = round((counts.get("done", 0) / total_terminal) * 100, 1) if total_terminal else 100.0

    service_targets = Counter()
    active_targets = []
    for entry in pending_tasks:
        target = entry.get("service_target")
        if target:
            service_targets[str(target)] += 1
            if entry.get("status") == "in_progress":
                active_targets.append(str(target))

    local_metrics = {
        "adk": {
            "active_sessions": 1 if current_task else 0,
            "runs_24h": last_24h,
            "success_24h": success_24h,
            "error_24h": error_24h,
            "success_rate_pct": success_rate,
            "last_success": last_done,
            "last_error": last_error,
        },
        "a2a": {
            "active_agents": 1 if current_task else 0,
            "handoffs_24h": last_24h,
            "active_links": len(active_targets),
            "primary_link": current_agent,
            "pending_approvals": sum(1 for task in pending_tasks if task.get("approval_required") is True),
        },
    }

    source_views = []
    for source in sorted(source_manifest.get("sources", []), key=lambda item: item.get("priority", 99)):
        if isinstance(source, dict):
            source_views.append(
                build_source_payload(
                    source,
                    local_state=state,
                    open_tasks=pending_tasks,
                    recent_history=recent_history,
                    recent_runs=recent_runs,
                    metrics=local_metrics,
                    board_path=str(MIRROR_PATH.relative_to(ROOT.parent)),
                )
            )

    connected_sources = [item for item in source_views if item.get("status") == "connected"]
    session_layer = {
        "layer_id": "session",
        "label": "Sessão",
        "status": "not_wired",
        "source_ref": "browser/ui",
        "summary": "A sessão do usuário precisa ser lida da UI e não do runtime local.",
        "details": {
            "browser_session": "não conectada neste board",
            "distinction": "esta camada não deve ser inferida da runtime local",
        },
    }
    runtime_layer = {
        "layer_id": "runtime",
        "label": "Runtime",
        "status": "connected" if state.get("status") in {"idle", "running", "error"} else "unknown",
        "source_ref": str(KERNEL_STATE.relative_to(ROOT)),
        "summary": "Estado operacional do estaleiro e execução local do trabalho.",
        "details": {
            "current_task": current_task,
            "open_tasks": len(pending_tasks),
            "recent_runs": len(recent_runs),
        },
    }
    source_layer = {
        "layer_id": "source",
        "label": "Fontes",
        "status": "mixed" if len(connected_sources) != len(source_views) else "connected",
        "source_ref": str(SOURCE_MANIFEST_PATH.relative_to(ROOT)),
        "summary": "Fontes separadas por proveniência e autoridade.",
        "details": {
            "connected_sources": [item.get("source_id") for item in connected_sources],
            "all_sources": [item.get("source_id") for item in source_views],
            "count": len(source_views),
        },
    }
    mirror_layer = {
        "layer_id": "mirror",
        "label": "Mirror",
        "status": "connected" if MIRROR_PATH.exists() else "missing",
        "source_ref": str(MIRROR_PATH.relative_to(ROOT.parent)),
        "summary": "Espelho visual do board para leitura na UI.",
        "details": {
            "mirror_path": str(MIRROR_PATH.relative_to(ROOT.parent)),
            "freshness": now_iso(),
        },
    }

    board = {
        "generated_at": now_iso(),
        "status": state.get("status", "idle"),
        "current_task": current_task,
        "active_agent": current_agent,
        "resolution_blocks": build_resolution_blocks(pending_tasks),
        "source_views": source_views,
        "status_layers": [session_layer, runtime_layer, source_layer, mirror_layer],
        "queue": {
            "open": pending_tasks,
            "open_count": len(pending_tasks),
            "service_targets": dict(service_targets),
            "active_targets": active_targets[:6],
        },
        "history": {
            "recent": recent_history,
            "recent_runs": recent_runs,
            "counts": dict(counts),
        },
        "metrics": local_metrics,
        "source_index": {
            "kernel_state": str(KERNEL_STATE.relative_to(ROOT)),
            "tasks_dir": str(TASKS_DIR.relative_to(ROOT)),
            "runs_dir": str(RUNS_DIR.relative_to(ROOT)),
            "manifest": str(SOURCE_MANIFEST_PATH.relative_to(ROOT)),
        },
    }
    return board


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera o snapshot do HITL para o painel.")
    parser.add_argument("--output", default=str(OUTPUT_PATH))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = load_json(KERNEL_STATE, default={}) or {}
    if not isinstance(state, dict):
        state = {}
    board = read_registry_state(state)
    output = Path(args.output)
    save_json(output, board)
    try:
        if MIRROR_PATH.parent.exists():
            save_json(MIRROR_PATH, board)
    except Exception:
        pass
    print(json.dumps(board, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
