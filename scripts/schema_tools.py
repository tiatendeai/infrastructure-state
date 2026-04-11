from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SchemaValidationError(ValueError):
    """Erro de validação estrutural baseado em um subconjunto de JSON Schema."""


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check_type(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "null":
        return instance is None
    return True


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> None:
    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        last_errors: list[str] = []
        for option in any_of:
            try:
                validate_instance(instance, option, path)
                break
            except SchemaValidationError as exc:
                last_errors.append(str(exc))
        else:
            detail = "; ".join(last_errors[:3])
            raise SchemaValidationError(f"{path}: valor inválido para anyOf ({detail})")
        return

    expected_type = schema.get("type")
    if isinstance(expected_type, list):
        if not any(check_type(instance, item) for item in expected_type):
            raise SchemaValidationError(f"{path}: tipo inválido, esperado um entre {', '.join(expected_type)}")
    elif expected_type and not check_type(instance, expected_type):
        raise SchemaValidationError(f"{path}: tipo inválido, esperado {expected_type}")

    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaValidationError(f"{path}: valor fora do enum")

    if expected_type == "object":
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            allowed = set(properties.keys())
            extra = set(instance.keys()) - allowed
            if extra:
                raise SchemaValidationError(f"{path}: propriedades não permitidas: {', '.join(sorted(extra))}")

        for field_name in schema.get("required", []):
            if field_name not in instance:
                raise SchemaValidationError(f"{path}: campo obrigatório ausente: {field_name}")

        for field_name, child_schema in properties.items():
            if field_name in instance:
                validate_instance(instance[field_name], child_schema, f"{path}.{field_name}")

        additional_properties = schema.get("additionalProperties")
        if isinstance(additional_properties, dict):
            for field_name, value in instance.items():
                if field_name not in properties:
                    validate_instance(value, additional_properties, f"{path}.{field_name}")
        return

    if expected_type == "array":
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                validate_instance(item, item_schema, f"{path}[{index}]")
        return

    if expected_type == "string" and "minLength" in schema and len(instance) < schema["minLength"]:
        raise SchemaValidationError(f"{path}: tamanho mínimo não atendido")

    if expected_type in {"integer", "number"} and "minimum" in schema and instance < schema["minimum"]:
        raise SchemaValidationError(f"{path}: valor abaixo do mínimo")
