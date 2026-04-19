#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone


SSH_OPTIONS = [
    "-o",
    "BatchMode=yes",
    "-o",
    "ConnectTimeout=10",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_remote(host: str, command: str) -> subprocess.CompletedProcess[str]:
    remote_command = f"sh -lc {shlex.quote(command)}"
    return subprocess.run(
        ["ssh", *SSH_OPTIONS, host, remote_command],
        capture_output=True,
        text=True,
    )


def require_remote(host: str, command: str) -> str:
    result = run_remote(host, command)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit_code={result.returncode}"
        raise RuntimeError(f"Falha no acesso SSH/read-only ao host {host}: {detail}")
    return result.stdout.strip()


def optional_remote(host: str, command: str, label: str):
    result = run_remote(host, command)
    if result.returncode == 0:
        return {
            "status": "ok",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    detail = result.stderr.strip() or result.stdout.strip() or f"exit_code={result.returncode}"
    return {
        "status": "unavailable",
        "reason": detail,
        "label": label,
    }


def parse_os_release(raw: str) -> dict:
    payload = {}
    for line in raw.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        payload[key] = value.strip().strip('"')
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta inventário remoto em modo estritamente read-only.")
    parser.add_argument("--host", required=True, help="Host remoto no formato user@host.")
    args = parser.parse_args()

    host = args.host

    inventory = {
        "collected_at": now_iso(),
        "host": host,
        "execution_policy": "read_only_remote",
        "sections": {},
    }

    inventory["sections"]["identity"] = {
        "hostname": require_remote(host, "hostname"),
        "date": require_remote(host, "date"),
        "uptime": require_remote(host, "uptime"),
        "kernel": require_remote(host, "uname -a"),
        "os_release": parse_os_release(require_remote(host, "cat /etc/os-release")),
    }

    inventory["sections"]["network"] = {
        "ip_brief_address": require_remote(
            host,
            "if ip -br address >/dev/null 2>&1; then ip -br address; else ip addr; fi",
        ),
        "ip_route": require_remote(host, "ip route"),
        "listening_ports": require_remote(host, "ss -tulpn"),
    }

    inventory["sections"]["resources"] = {
        "disk": require_remote(host, "df -h"),
        "memory": require_remote(host, "free -m"),
    }

    inventory["sections"]["processes"] = {
        "top_cpu_processes": require_remote(
            host,
            "ps -eo pid,ppid,user,stat,%cpu,%mem,comm --sort=-%cpu | head -n 40",
        ),
        "running_services": optional_remote(
            host,
            "systemctl list-units --type=service --state=running --no-pager --no-legend",
            "systemd",
        ),
    }

    inventory["sections"]["containers"] = {
        "docker_ps": optional_remote(host, "docker ps -a", "docker"),
        "docker_compose_ls": optional_remote(host, "docker compose ls", "docker_compose"),
        "podman_ps": optional_remote(host, "podman ps -a", "podman"),
    }

    inventory["sections"]["reverse_proxy"] = {
        "nginx_version": optional_remote(host, "nginx -v", "nginx"),
        "nginx_sites_enabled": optional_remote(
            host,
            "if [ -d /etc/nginx/sites-enabled ]; then ls -la /etc/nginx/sites-enabled; else echo 'diretório ausente'; fi",
            "nginx_sites_enabled",
        ),
        "nginx_conf_d": optional_remote(
            host,
            "if [ -d /etc/nginx/conf.d ]; then ls -la /etc/nginx/conf.d; else echo 'diretório ausente'; fi",
            "nginx_conf_d",
        ),
    }

    print(json.dumps(inventory, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
