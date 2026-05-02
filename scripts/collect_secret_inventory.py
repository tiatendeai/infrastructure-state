#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

CONTRACT_PATH = ROOT / "state" / "registry" / "infisical-secret-contract.json"
SCAN_ROOTS = [
    ROOT / "adapters" / "provisioning" / "ansible",
    ROOT / "docs",
    ROOT / "state",
]


def load_contract() -> dict[str, Any]:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Contrato inválido")
    return payload


def collect_secret_names(contract: dict[str, Any]) -> dict[str, str]:
    names: dict[str, str] = {}
    categories = contract.get("categories", {})
    if not isinstance(categories, dict):
        return names
    for category, secrets in categories.items():
        if not isinstance(secrets, list):
            continue
        for secret in secrets:
            if isinstance(secret, str) and secret.strip():
                names[secret.strip()] = str(category)
    return names


def scan_repo(secret_names: set[str]) -> dict[str, list[str]]:
    pattern = re.compile(r"shipyard_[A-Za-z0-9_]+")
    found: dict[str, list[str]] = defaultdict(list)
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix in {".pyc", ".png", ".jpg", ".jpeg", ".gif"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            for match in pattern.findall(text):
                if match in secret_names:
                    rel = str(path.relative_to(ROOT))
                    if rel not in found[match]:
                        found[match].append(rel)
    return found


def build_report() -> dict[str, Any]:
    contract = load_contract()
    secret_categories = collect_secret_names(contract)
    secret_names = set(secret_categories.keys())
    found = scan_repo(secret_names)

    missing = sorted(secret_names - set(found.keys()))
    by_category: dict[str, list[str]] = defaultdict(list)
    for secret_name, category in secret_categories.items():
        by_category[category].append(secret_name)

    return {
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "total_contract_secrets": len(secret_names),
        "referenced_secrets": len(found),
        "unreferenced_secrets": missing,
        "by_category": {
            category: sorted(names)
            for category, names in sorted(by_category.items())
        },
        "references": {
            secret: found.get(secret, [])
            for secret in sorted(found.keys())
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Coleta inventário de segredos do Shipyard e cruza com o contrato do Infisical.")
    parser.add_argument("--output", help="Escreve o relatório em arquivo")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        output_path = (ROOT / args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
