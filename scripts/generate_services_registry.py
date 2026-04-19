#!/usr/bin/env python3
import argparse
import difflib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "registry" / "runs"
DEFAULT_OUTPUT = ROOT / "registry" / "services.yaml"
BACKUP_DIR = ROOT / "state" / "snapshots" / "registry-services"

SERVICE_MAP = {
    "kvm2-traefik-1": {"service_id": "traefik", "category": "reverse_proxy"},
    "kvm2-ruptur-backend-1": {"service_id": "ruptur-backend", "category": "application_backend"},
    "kvm2-ruptur-web-1": {"service_id": "ruptur-web", "category": "application_frontend"},
    "kvm2-baileys-1": {"service_id": "baileys", "category": "integration_gateway"},
    "kvm2-whisper-1": {"service_id": "whisper", "category": "ai_runtime"},
    "kvm2-ruptur-db-1": {"service_id": "ruptur-db", "category": "database"},
    "kvm2-warmup-1": {"service_id": "warmup", "category": "runtime_support"},
    "proxy_socket-proxy.1.tu7yxklstw2nl4k9tm5a6usla": {"service_id": "docker-socket-proxy", "category": "docker_proxy"},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materializa registry/services.yaml a partir do último inventário válido.")
    parser.add_argument("--run-ref", help="Arquivo específico do registry/runs a ser usado como origem.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT.relative_to(ROOT)), help="Arquivo de saída relativo ao repositório.")
    return parser.parse_args()


def resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def find_latest_valid_run() -> tuple[Path, dict]:
    candidates = sorted(RUNS_DIR.glob("*baseline-server-inventory*.json"))
    for path in reversed(candidates):
        payload = load_json(path)
        execution = payload.get("execution", {})
        sections = execution.get("output", {}).get("result", {}).get("sections")
        if execution.get("status") == "done" and isinstance(sections, dict):
            return path, payload
    raise RuntimeError("Nenhum inventário válido encontrado em registry/runs para materializar registry/services.yaml")


def parse_container_line(line: str) -> dict | None:
    if not line.strip() or line.startswith("CONTAINER ID"):
        return None
    parts = re.split(r"\s{2,}", line.strip(), maxsplit=6)
    if len(parts) < 7:
        return None
    container_id, image, command, created, status, ports, names = parts
    return {
        "container_id": container_id,
        "image": image,
        "command": command,
        "created": created,
        "status": status,
        "ports": [item.strip() for item in ports.split(",") if item.strip()],
        "names": names,
    }


def build_services(run_payload: dict) -> dict:
    sections = run_payload["execution"]["output"]["result"]["sections"]
    docker_stdout = sections.get("containers", {}).get("docker_ps", {}).get("stdout", "")
    services: dict[str, dict] = {}

    for line in docker_stdout.splitlines():
        parsed = parse_container_line(line)
        if not parsed:
            continue

        container_name = parsed["names"]
        mapping = SERVICE_MAP.get(container_name)
        if not mapping:
            continue

        services[mapping["service_id"]] = {
            "service_id": mapping["service_id"],
            "category": mapping["category"],
            "runtime": "docker",
            "status": parsed["status"],
            "container_name": container_name,
            "image": parsed["image"],
            "ports": parsed["ports"],
            "source": "observed",
        }

    return services


def extract_compose_file(run_payload: dict) -> str:
    compose_stdout = (
        run_payload["execution"]["output"]["result"]["sections"]
        .get("containers", {})
        .get("docker_compose_ls", {})
        .get("stdout", "")
    )
    lines = [line for line in compose_stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return ""
    parts = re.split(r"\s{2,}", lines[1].strip(), maxsplit=2)
    return parts[-1] if len(parts) >= 3 else ""


def build_registry(run_path: Path, run_payload: dict) -> dict:
    result = run_payload["execution"]["output"]["result"]
    identity = result["sections"]["identity"]
    host = result["host"]

    return {
        "version": 1,
        "generated_from": {
            "task_id": run_payload["task"]["task_id"],
            "linear_issue_id": run_payload["task"].get("linear_issue_id", ""),
            "run_ref": str(run_path.relative_to(ROOT)),
            "generated_at": now_iso(),
        },
        "targets": {
            host: {
                "host_alias": host,
                "hostname": identity["hostname"],
                "os": identity["os_release"].get("PRETTY_NAME", ""),
                "compose_file": extract_compose_file(run_payload),
                "source": "observed",
                "services": build_services(run_payload),
            }
        },
    }


def yaml_scalar(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if text == "":
        return '""'
    if re.fullmatch(r"[A-Za-z0-9_./:@-]+", text):
        return text
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def dump_yaml(data, indent: int = 0) -> str:
    prefix = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(dump_yaml(value, indent + 2))
            elif isinstance(value, list):
                rendered = ", ".join(yaml_scalar(item) for item in value)
                lines.append(f"{prefix}{key}: [{rendered}]")
            else:
                lines.append(f"{prefix}{key}: {yaml_scalar(value)}")
        return "\n".join(lines)
    raise TypeError("dump_yaml suporta apenas mapas na raiz")


def main() -> int:
    args = parse_args()
    output_path = resolve_path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    if args.run_ref:
        run_path = resolve_path(args.run_ref)
        if not run_path.exists():
            raise SystemExit(f"Run de origem não encontrado: {run_path}")
        run_payload = load_json(run_path)
    else:
        run_path, run_payload = find_latest_valid_run()

    registry_payload = build_registry(run_path, run_payload)
    rendered_yaml = dump_yaml(registry_payload) + "\n"

    existing = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    backup_file = None
    diff_preview: list[str] = []

    if existing is not None:
        timestamp = now_iso().replace(":", "-")
        backup_path = BACKUP_DIR / f"{timestamp}_services.yaml"
        shutil.copy2(output_path, backup_path)
        backup_file = str(backup_path.relative_to(ROOT))
        diff_preview = list(
            difflib.unified_diff(
                existing.splitlines(),
                rendered_yaml.splitlines(),
                fromfile=str(output_path.relative_to(ROOT)),
                tofile=str(output_path.relative_to(ROOT)),
                lineterm="",
            )
        )

    output_path.write_text(rendered_yaml, encoding="utf-8")

    summary = {
        "status": "done",
        "generated_file": str(output_path.relative_to(ROOT)),
        "backup_file": backup_file,
        "changes_detected": existing != rendered_yaml,
        "diff_preview": diff_preview[:60],
        "generated_from": registry_payload["generated_from"],
        "target_count": len(registry_payload["targets"]),
        "service_count": len(next(iter(registry_payload["targets"].values()))["services"]),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
