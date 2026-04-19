#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILE = ROOT / "catalog" / "services.yaml"
PROFILES_DIR = ROOT / "profiles"
REGISTRY_FILE = ROOT.parents[1] / "registry" / "services.yaml"
INSTALLERS_DIR = ROOT / "installers"


class YamlSubsetError(ValueError):
    pass


def fail(message: str, *, code: str = "invalid_request", output_format: str = "text", exit_code: int = 1) -> int:
    payload = {"status": "error", "code": code, "message": message}
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"erro: {message}", file=sys.stderr)
    return exit_code


def strip_comment(line: str) -> str:
    if "#" not in line:
        return line
    in_quotes = False
    result = []
    prev = ""
    for char in line:
        if char == '"' and prev != "\\":
            in_quotes = not in_quotes
        if char == "#" and not in_quotes:
            break
        result.append(char)
        prev = char
    return "".join(result).rstrip()


def parse_scalar(value: str):
    value = value.strip()
    if value == "":
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item.strip()) for item in inner.split(",")]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if value.isdigit():
        return int(value)
    return value


def parse_yaml_subset(text: str):
    lines = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if "\t" in raw:
            raise YamlSubsetError(f"indentação com TAB não suportada na linha {lineno}")
        stripped = strip_comment(raw)
        if not stripped.strip():
            continue
        content = stripped.rstrip()
        indent = len(content) - len(content.lstrip(" "))
        if indent % 2 != 0:
            raise YamlSubsetError(f"indentação deve usar múltiplos de 2 espaços na linha {lineno}")
        token = content.strip()
        if token.startswith("&") or token.startswith("*") or token in {"|", ">"} or "!!" in token:
            raise YamlSubsetError(f"recurso YAML fora do subset suportado na linha {lineno}")
        lines.append((lineno, indent, token))

    def parse_block(index: int, indent: int):
        container = None
        while index < len(lines):
            lineno, current_indent, token = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise YamlSubsetError(f"indentação inesperada na linha {lineno}")

            if token.startswith("- "):
                if container is None:
                    container = []
                if not isinstance(container, list):
                    raise YamlSubsetError(f"mistura inválida de lista e mapa na linha {lineno}")
                item = token[2:].strip()
                if not item:
                    raise YamlSubsetError(f"item de lista vazio não suportado na linha {lineno}")
                if ":" in item:
                    raise YamlSubsetError(f"lista de mapas fora do subset suportado na linha {lineno}")
                container.append(parse_scalar(item))
                index += 1
                continue

            if container is None:
                container = {}
            if not isinstance(container, dict):
                raise YamlSubsetError(f"mistura inválida de mapa e lista na linha {lineno}")

            if ":" not in token:
                raise YamlSubsetError(f"linha inválida {lineno}: esperado key: value")

            key, raw_value = token.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            if not key:
                raise YamlSubsetError(f"chave vazia na linha {lineno}")

            if raw_value == "":
                next_index = index + 1
                if next_index >= len(lines) or lines[next_index][1] <= current_indent:
                    container[key] = {}
                    index += 1
                else:
                    value, index = parse_block(next_index, current_indent + 2)
                    container[key] = value
            else:
                container[key] = parse_scalar(raw_value)
                index += 1

        if container is None:
            return {}, index
        return container, index

    parsed, index = parse_block(0, 0)
    if index != len(lines):
        raise YamlSubsetError("falha ao consumir todo o documento YAML")
    return parsed


def load_yaml_file(path: Path):
    return parse_yaml_subset(path.read_text(encoding="utf-8"))


def load_catalog():
    payload = load_yaml_file(CATALOG_FILE)
    services = payload.get("services", {})
    if not isinstance(services, dict):
        raise YamlSubsetError("catalog/services.yaml precisa ter 'services' como mapa")
    return payload


def load_profiles():
    profiles = {}
    for path in sorted(PROFILES_DIR.glob("*.yaml")):
        payload = load_yaml_file(path)
        profile_name = payload.get("profile")
        if not isinstance(profile_name, str) or not profile_name:
            raise YamlSubsetError(f"perfil inválido em {path.name}: campo 'profile' obrigatório")
        profiles[profile_name] = payload
    return profiles


def load_registry():
    if not REGISTRY_FILE.exists():
        raise YamlSubsetError("registry/services.yaml não encontrado; materialize o registry antes de usar o profile plan")
    return load_yaml_file(REGISTRY_FILE)


def validate_catalog(catalog: dict) -> list[str]:
    errors: list[str] = []
    services = catalog.get("services", {})
    for service_id, meta in services.items():
        for field in (
            "id",
            "display_name",
            "kind",
            "installer",
            "default_runtime",
            "required_capabilities",
            "dependencies",
            "default_ports",
            "env_template",
            "notes",
        ):
            if field not in meta:
                errors.append(f"serviço {service_id}: campo obrigatório ausente '{field}'")
        installer = meta.get("installer", "")
        if installer and not (ROOT / installer).exists():
            errors.append(f"serviço {service_id}: installer ausente ({installer})")
        env_template = meta.get("env_template", "")
        if env_template and not (ROOT / env_template).exists():
            errors.append(f"serviço {service_id}: env_template ausente ({env_template})")
    return errors


def iter_registry_service_ids(registry: dict) -> set[str]:
    found = set()
    for target in registry.get("targets", {}).values():
        for service_id in target.get("services", {}).keys():
            found.add(service_id)
    return found


def validate_profiles(catalog: dict, profiles: dict, registry: dict) -> list[str]:
    errors: list[str] = []
    catalog_services = set(catalog.get("services", {}).keys())
    observed_services = iter_registry_service_ids(registry)

    for profile_name, payload in profiles.items():
        for field in (
            "description",
            "target_class",
            "placement_recommendation",
            "required_capabilities",
            "desired_services",
            "prerequisites",
            "manual_checks",
            "registry_refs",
        ):
            if field not in payload:
                errors.append(f"perfil {profile_name}: campo obrigatório ausente '{field}'")

        for service_id in payload.get("desired_services", []):
            if service_id not in catalog_services:
                errors.append(f"perfil {profile_name}: desired_service inexistente '{service_id}'")

        bindings = payload.get("capability_bindings", {})
        if isinstance(bindings, dict):
            for capability, binding in bindings.items():
                observed_service_id = binding.get("observed_service_id")
                if observed_service_id and observed_service_id not in observed_services:
                    errors.append(
                        f"perfil {profile_name}: capability '{capability}' aponta para serviço observado inexistente '{observed_service_id}'"
                    )

        for registry_ref in payload.get("registry_refs", []):
            if registry_ref and not (ROOT.parents[1] / registry_ref).exists():
                errors.append(f"perfil {profile_name}: registry_ref ausente ({registry_ref})")

    return errors


def resolve_profile_plan(profile_name: str, profiles: dict, catalog: dict):
    if profile_name not in profiles:
        raise KeyError(f"perfil não encontrado: {profile_name}")
    profile = profiles[profile_name]
    catalog_services = catalog.get("services", {})
    resolved = {service_id: catalog_services[service_id] for service_id in profile.get("desired_services", [])}
    return {
        "profile": profile_name,
        "description": profile.get("description", ""),
        "target_class": profile.get("target_class", ""),
        "placement_recommendation": profile.get("placement_recommendation", ""),
        "required_capabilities": profile.get("required_capabilities", []),
        "capability_bindings": profile.get("capability_bindings", {}),
        "desired_services": resolved,
        "prerequisites": profile.get("prerequisites", []),
        "manual_checks": profile.get("manual_checks", []),
        "registry_refs": profile.get("registry_refs", []),
        "execution_mode": "plan_only",
    }


def print_payload(payload, output_format: str):
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            print(f"{key}: {value}")
        return
    if isinstance(payload, list):
        for item in payload:
            print(item)
        return
    print(payload)


def main(argv: list[str]) -> int:
    output_format = "text"
    filtered: list[str] = []
    for arg in argv:
        if arg == "--format":
            continue
        filtered.append(arg)

    args = list(argv)
    if "--format" in args:
        index = args.index("--format")
        try:
            output_format = args[index + 1]
        except IndexError:
            return fail("valor ausente para --format", code="format_missing", output_format="text", exit_code=2)
        del filtered[index:index + 2]

    if "--apply" in filtered:
        return fail("apply_disabled_in_tranche_2", code="apply_disabled_in_tranche_2", output_format=output_format, exit_code=2)

    if not filtered:
        return fail("uso: ruptur-forge <doctor|list|show|profile|install>", output_format=output_format, exit_code=2)

    command = filtered[0]

    try:
        catalog = load_catalog()
        profiles = load_profiles()
        registry = load_registry()
    except Exception as exc:
        return fail(str(exc), code="yaml_or_registry_error", output_format=output_format)

    if command == "doctor":
        errors = []
        errors.extend(validate_catalog(catalog))
        errors.extend(validate_profiles(catalog, profiles, registry))
        if errors:
            return fail("; ".join(errors), code="doctor_failed", output_format=output_format)
        payload = {
            "status": "ok",
            "catalog_services": sorted(catalog.get("services", {}).keys()),
            "profiles": sorted(profiles.keys()),
            "registry_file": str(REGISTRY_FILE.relative_to(ROOT.parents[1])),
        }
        print_payload(payload, output_format)
        return 0

    if command == "list":
        if len(filtered) < 2:
            return fail("uso: ruptur-forge list <services|profiles>", output_format=output_format, exit_code=2)
        target = filtered[1]
        if target == "services":
            payload = sorted(catalog.get("services", {}).keys())
            print_payload(payload, output_format)
            return 0
        if target == "profiles":
            payload = sorted(profiles.keys())
            print_payload(payload, output_format)
            return 0
        return fail("list suporta apenas 'services' ou 'profiles'", output_format=output_format, exit_code=2)

    if command == "show":
        if len(filtered) != 3 or filtered[1] != "service":
            return fail("uso: ruptur-forge show service <id>", output_format=output_format, exit_code=2)
        service_id = filtered[2]
        service = catalog.get("services", {}).get(service_id)
        if not service:
            return fail(f"serviço não encontrado: {service_id}", code="service_not_found", output_format=output_format, exit_code=1)
        print_payload(service, output_format)
        return 0

    if command == "profile":
        if len(filtered) >= 2 and filtered[1] == "plan":
            if len(filtered) != 3:
                return fail("uso: ruptur-forge profile plan <name>", output_format=output_format, exit_code=2)
            profile_name = filtered[2]
        else:
            if len(filtered) != 2:
                return fail("uso: ruptur-forge profile <name>", output_format=output_format, exit_code=2)
            profile_name = filtered[1]
        try:
            payload = resolve_profile_plan(profile_name, profiles, catalog)
        except KeyError as exc:
            return fail(str(exc), code="profile_not_found", output_format=output_format, exit_code=1)
        print_payload(payload, output_format)
        return 0

    if command == "install":
        if len(filtered) != 2:
            return fail("uso: ruptur-forge install <service>", output_format=output_format, exit_code=2)
        service_id = filtered[1]
        service = catalog.get("services", {}).get(service_id)
        if not service:
            return fail(f"serviço não encontrado: {service_id}", code="service_not_found", output_format=output_format, exit_code=1)
        payload = {
            "service_id": service_id,
            "service": service,
            "execution_mode": "plan_only",
            "message": "Instalação desabilitada nesta tranche; use este comando apenas como visualização do plano.",
        }
        print_payload(payload, output_format)
        return 0

    return fail(f"comando não suportado: {command}", output_format=output_format, exit_code=2)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
