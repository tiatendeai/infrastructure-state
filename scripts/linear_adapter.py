#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.linear.client import (  # noqa: E402
    LinearAdapterError,
    LinearClient,
    LinearConfig,
)
from adapters.linear.issues import add_comment, get_issue, update_issue_status  # noqa: E402
from adapters.linear.projects import list_projects  # noqa: E402
from adapters.linear.registry import load_linear_mapping_registry, resolve_issue_mapping  # noqa: E402
from adapters.linear.runtime import publish_task_runtime_update  # noqa: E402
from adapters.linear.statuses import find_status_by_name, list_statuses  # noqa: E402


VIEWER_QUERY = """
query Viewer {
  viewer {
    id
    name
    email
  }
}
"""


def emit(payload: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            print(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        else:
            print(f"{key}: {value}")


def fail(message: str, *, code: str = "error", output_format: str = "text", exit_code: int = 1) -> int:
    payload = {"status": "error", "code": code, "message": message}
    emit(payload, output_format)
    return exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CLI headless do adapter nativo do Linear.")

    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser("doctor", help="Valida configuração e, opcionalmente, autenticação")
    doctor.add_argument("--format", choices=("text", "json"), default="text", help="Formato da saída")
    doctor.add_argument("--live", action="store_true", help="Também consulta o Linear com a credencial ativa")

    issue = subparsers.add_parser("issue", help="Operações com issues")
    issue_subparsers = issue.add_subparsers(dest="issue_command")

    issue_get = issue_subparsers.add_parser("get", help="Busca uma issue por identifier")
    issue_get.add_argument("identifier")
    issue_get.add_argument("--format", choices=("text", "json"), default="text", help="Formato da saída")

    issue_set_status = issue_subparsers.add_parser("set-status", help="Atualiza o status de uma issue")
    issue_set_status.add_argument("identifier")
    issue_set_status.add_argument("status_name")
    issue_set_status.add_argument("--format", choices=("text", "json"), default="text", help="Formato da saída")
    issue_set_status.add_argument("--team", help="Team alvo para resolver o status")
    issue_set_status.add_argument("--dry-run", action="store_true", help="Não executa a mutação final")

    issue_comment = issue_subparsers.add_parser("comment", help="Adiciona comentário em uma issue")
    issue_comment.add_argument("identifier")
    issue_comment.add_argument("--format", choices=("text", "json"), default="text", help="Formato da saída")
    issue_comment.add_argument("--body", help="Texto do comentário")
    issue_comment.add_argument("--body-file", help="Arquivo com o comentário")
    issue_comment.add_argument("--dry-run", action="store_true", help="Não executa a mutação final")

    mapping = subparsers.add_parser("mapping", help="Resolução local issue ↔ task ↔ mapping")
    mapping_subparsers = mapping.add_subparsers(dest="mapping_command")
    mapping_resolve = mapping_subparsers.add_parser("resolve", help="Resolve um mapping a partir de task ou issue")
    mapping_resolve.add_argument("--task-file", help="Task JSON local")
    mapping_resolve.add_argument("--issue-ref", help="backlog key, identifier ou UUID")
    mapping_resolve.add_argument("--local-task", help="Caminho local da task")
    mapping_resolve.add_argument("--format", choices=("text", "json"), default="text", help="Formato da saída")

    runtime = subparsers.add_parser("runtime", help="Publicação estruturada de avanço local no Linear")
    runtime_subparsers = runtime.add_subparsers(dest="runtime_command")
    runtime_publish = runtime_subparsers.add_parser("publish", help="Publica status e comentário resumido")
    runtime_publish.add_argument("--task-file", required=True, help="Task JSON local")
    runtime_publish.add_argument("--event", choices=("running", "done", "error"), required=True, help="Evento local")
    runtime_publish.add_argument("--mode", default="STANDARD", help="Modo local da execução")
    runtime_publish.add_argument("--registry-record", help="Arquivo de evidência em registry/runs")
    runtime_publish.add_argument("--error-message", help="Erro resumido da execução")
    runtime_publish.add_argument("--dry-run", action="store_true", help="Não chama o Linear; apenas mostra o plano")
    runtime_publish.add_argument("--format", choices=("text", "json"), default="text", help="Formato da saída")

    project = subparsers.add_parser("project", help="Operações com projects")
    project_subparsers = project.add_subparsers(dest="project_command")
    project_list = project_subparsers.add_parser("list", help="Lista projects por team")
    project_list.add_argument("--team", help="Team alvo")
    project_list.add_argument("--format", choices=("text", "json"), default="text", help="Formato da saída")

    status = subparsers.add_parser("status", help="Operações com workflow states")
    status_subparsers = status.add_subparsers(dest="status_command")
    status_list = status_subparsers.add_parser("list", help="Lista statuses por team")
    status_list.add_argument("--team", help="Team alvo")
    status_list.add_argument("--format", choices=("text", "json"), default="text", help="Formato da saída")

    return parser.parse_args()


def load_task_file(raw_path: str) -> tuple[dict, str]:
    path = Path(raw_path)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    source = str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
    return payload, source


def build_client() -> LinearClient:
    config = LinearConfig.from_env(ROOT)
    return LinearClient(config)


def resolve_team_ref(client: LinearClient, explicit_team: str | None) -> str:
    if explicit_team and explicit_team.strip():
        return explicit_team.strip()
    return client.config.default_team_ref()


def read_comment_body(args: argparse.Namespace) -> str:
    if args.body and args.body_file:
        raise LinearAdapterError("Use apenas um entre --body e --body-file")
    if args.body_file:
        path = Path(args.body_file)
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        return path.read_text(encoding="utf-8")
    if args.body:
        return args.body
    raise LinearAdapterError("Informe --body ou --body-file")


def cmd_doctor(args: argparse.Namespace, client: LinearClient) -> dict:
    payload = {
        "status": "ok",
        "mode": "local_only",
        "config": client.config.auth_summary(),
        "api_url": client.config.api_url,
        "oauth_token_url": client.config.oauth_token_url,
    }
    if args.live:
        viewer = client.graphql(VIEWER_QUERY).get("viewer") or {}
        payload["mode"] = "live"
        payload["viewer"] = viewer
    return payload


def cmd_issue_get(args: argparse.Namespace, client: LinearClient) -> dict:
    return {"status": "ok", "issue": get_issue(client, args.identifier)}


def cmd_mapping_resolve(args: argparse.Namespace) -> dict:
    registry = load_linear_mapping_registry()
    task = None
    task_source = None
    if args.task_file:
        task, task_source = load_task_file(args.task_file)
    mapping = resolve_issue_mapping(
        registry=registry,
        task=task,
        task_source=task_source,
        issue_ref=args.issue_ref,
        local_task=args.local_task,
    )
    context = {
        "status": "ok",
        "mapping": mapping.to_dict(),
        "registry": {
            "source": registry.source,
            "meta": registry.meta.to_dict(),
        },
    }
    if task is not None:
        context["task_source"] = task_source
        context["task_id"] = task.get("task_id")
    return context


def cmd_runtime_publish(args: argparse.Namespace) -> dict:
    task, task_source = load_task_file(args.task_file)
    return publish_task_runtime_update(
        task=task,
        task_source=task_source,
        mode=str(args.mode),
        event=str(args.event),
        registry_record=args.registry_record,
        error_message=args.error_message,
        dry_run=bool(args.dry_run),
    )


def cmd_project_list(args: argparse.Namespace, client: LinearClient) -> dict:
    team_ref = resolve_team_ref(client, args.team)
    payload = list_projects(client, team_ref)
    payload["status"] = "ok"
    return payload


def cmd_status_list(args: argparse.Namespace, client: LinearClient) -> dict:
    team_ref = resolve_team_ref(client, args.team)
    payload = list_statuses(client, team_ref)
    payload["status"] = "ok"
    return payload


def cmd_issue_set_status(args: argparse.Namespace, client: LinearClient) -> dict:
    issue = get_issue(client, args.identifier)
    team_ref = args.team or issue.get("team", {}).get("id") or issue.get("team", {}).get("key")
    if not team_ref:
        raise LinearAdapterError("Não foi possível determinar o team da issue para resolver o status")
    target_status = find_status_by_name(client, str(team_ref), args.status_name)
    payload = {
        "status": "ok",
        "issue_identifier": issue.get("identifier"),
        "issue_title": issue.get("title"),
        "current_state": issue.get("state"),
        "target_state": target_status,
        "dry_run": bool(args.dry_run),
    }
    if args.dry_run:
        return payload
    updated_issue = update_issue_status(client, args.identifier, str(target_status.get("id")))
    payload["updated_issue"] = updated_issue
    return payload


def cmd_issue_comment(args: argparse.Namespace, client: LinearClient) -> dict:
    issue = get_issue(client, args.identifier)
    body = read_comment_body(args)
    payload = {
        "status": "ok",
        "issue_identifier": issue.get("identifier"),
        "issue_title": issue.get("title"),
        "comment_length": len(body),
        "dry_run": bool(args.dry_run),
    }
    if args.dry_run:
        return payload
    result = add_comment(client, args.identifier, body)
    payload["result"] = result
    return payload


def main() -> int:
    args = parse_args()
    output_format = getattr(args, "format", "text")

    if not args.command:
        return fail("nenhum comando informado. Use --help.", code="usage_error", output_format=output_format, exit_code=2)

    try:
        client = build_client()
        if args.command == "doctor":
            emit(cmd_doctor(args, client), output_format)
            return 0
        if args.command == "mapping":
            if args.mapping_command == "resolve":
                emit(cmd_mapping_resolve(args), output_format)
                return 0
            return fail("subcomando de mapping inválido", code="usage_error", output_format=output_format, exit_code=2)
        if args.command == "runtime":
            if args.runtime_command == "publish":
                emit(cmd_runtime_publish(args), output_format)
                return 0
            return fail("subcomando de runtime inválido", code="usage_error", output_format=output_format, exit_code=2)
        if args.command == "issue":
            if args.issue_command == "get":
                emit(cmd_issue_get(args, client), output_format)
                return 0
            if args.issue_command == "set-status":
                emit(cmd_issue_set_status(args, client), output_format)
                return 0
            if args.issue_command == "comment":
                emit(cmd_issue_comment(args, client), output_format)
                return 0
            return fail("subcomando de issue inválido", code="usage_error", output_format=output_format, exit_code=2)
        if args.command == "project":
            if args.project_command == "list":
                emit(cmd_project_list(args, client), output_format)
                return 0
            return fail("subcomando de project inválido", code="usage_error", output_format=output_format, exit_code=2)
        if args.command == "status":
            if args.status_command == "list":
                emit(cmd_status_list(args, client), output_format)
                return 0
            return fail("subcomando de status inválido", code="usage_error", output_format=output_format, exit_code=2)
        return fail("comando inválido", code="usage_error", output_format=output_format, exit_code=2)
    except FileNotFoundError as exc:
        return fail(str(exc), code="file_not_found", output_format=output_format)
    except LinearAdapterError as exc:
        return fail(str(exc), code="linear_adapter_error", output_format=output_format)
    except Exception as exc:  # pragma: no cover - proteção final da CLI
        return fail(f"erro inesperado: {exc}", code="unexpected_error", output_format=output_format)


if __name__ == "__main__":
    raise SystemExit(main())
