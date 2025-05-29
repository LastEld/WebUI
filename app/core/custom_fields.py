#app/core/custom_fields.py
from datetime import datetime
import re
from typing import Any, Dict, List, Optional

# === ВАЛИДАТОРЫ ===

def validate_story_points(value: Any) -> bool:
    try:
        v = int(value)
        return 0 <= v <= 100
    except Exception:
        return False

def validate_deadline_type(value: Any) -> bool:
    return value in ["hard", "soft"]

def validate_external_id(value: Any) -> bool:
    return bool(re.match(r"^[A-Z]{2,}-\d{1,6}$", str(value)))

def validate_reviewed(value: Any) -> bool:
    return str(value).lower() in ("true", "false", "yes", "no", "1", "0")

def validate_date(value: Any) -> bool:
    try:
        datetime.strptime(str(value), "%Y-%m-%d")
        return True
    except Exception:
        return False

def validate_list(value: Any) -> bool:
    return isinstance(value, list)

def validate_dict(value: Any) -> bool:
    return isinstance(value, dict)

# === ГЛОБАЛЬНАЯ СХЕМА КАСТОМНЫХ ПОЛЕЙ ===

CUSTOM_FIELDS_SCHEMA: Dict[str, Dict[str, Any]] = {
    "story_points": {
        "type": "int",
        "validator": validate_story_points,
        "default": 0,
        "label": "Story Points",
        "help": "Integer from 0 to 100",
        "required": False
    },
    "deadline_type": {
        "type": "choice",
        "validator": validate_deadline_type,
        "choices": ["hard", "soft"],
        "default": "soft",
        "label": "Deadline Type",
        "help": "Type of deadline (hard/soft)",
        "required": False
    },
    "external_id": {
        "type": "str",
        "validator": validate_external_id,
        "default": "",
        "label": "External ID",
        "help": "Format: AB-12345",
        "required": False
    },
    "reviewed": {
        "type": "bool",
        "validator": validate_reviewed,
        "default": False,
        "label": "Reviewed",
        "help": "True/False",
        "required": False
    },
    "deadline_ext": {
        "type": "date",
        "validator": validate_date,
        "default": None,
        "label": "Extended Deadline",
        "help": "YYYY-MM-DD",
        "required": False
    },
    # Пример вложенных структур
    "linked_files": {
        "type": "list",
        "validator": validate_list,
        "default": [],
        "label": "Linked Files",
        "help": "List of file URLs",
        "required": False
    },
    "meta_data": {
        "type": "dict",
        "validator": validate_dict,
        "default": {},
        "label": "Metadata",
        "help": "Arbitrary key-value data",
        "required": False
    },
}

def extend_custom_fields_schema(new_fields: Dict[str, Dict[str, Any]]) -> None:
    """
    Добавить новые кастомные поля в схему на лету.
    """
    for key, value in new_fields.items():
        # Проверка choices
        if value.get("type") == "choice":
            choices = value.get("choices", [])
            default = value.get("default")
            if default is not None and default not in choices:
                raise ValueError(f"Default value '{default}' not in choices for field '{key}'")
        CUSTOM_FIELDS_SCHEMA[key] = value

def validate_custom_fields_payload(custom_fields: Dict[str, Any]) -> None:
    """
    Строгая валидация типа, choices и required для custom_fields (используй в CRUD).
    """
    for key, value in custom_fields.items():
        schema = CUSTOM_FIELDS_SCHEMA.get(key)
        if not schema:
            raise ValueError(f"Unknown custom field: {key}")
        # Проверка required
        if schema.get("required", False) and (value is None or value == ""):
            raise ValueError(f"Custom field '{key}' is required.")
        # Проверка choices
        if schema.get("type") == "choice" and "choices" in schema:
            if value not in schema["choices"]:
                raise ValueError(f"Value '{value}' not allowed for field '{key}' (choices: {schema['choices']})")
        # Проверка типа (очень базовая)
        expected_type = schema.get("type")
        if expected_type == "int" and not isinstance(value, int):
            raise ValueError(f"Value '{value}' for '{key}' must be int")
        if expected_type == "bool" and not isinstance(value, bool):
            raise ValueError(f"Value '{value}' for '{key}' must be bool")
        if expected_type == "str" and not isinstance(value, str):
            raise ValueError(f"Value '{value}' for '{key}' must be str")
        if expected_type == "date":
            if not validate_date(value):
                raise ValueError(f"Value '{value}' for '{key}' must be date in YYYY-MM-DD format")
        if expected_type == "list" and not isinstance(value, list):
            raise ValueError(f"Value '{value}' for '{key}' must be list")
        if expected_type == "dict" and not isinstance(value, dict):
            raise ValueError(f"Value '{value}' for '{key}' must be dict")
        # Индивидуальный валидатор
        if "validator" in schema and not schema["validator"](value):
            raise ValueError(f"Value '{value}' failed custom validation for '{key}'")

def get_common_keys() -> list:
    return list(CUSTOM_FIELDS_SCHEMA.keys())

def get_schema_for_key(key: str) -> Dict[str, Any]:
    return CUSTOM_FIELDS_SCHEMA.get(key, None)
