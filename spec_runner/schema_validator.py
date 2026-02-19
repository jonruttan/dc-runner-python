from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spec_runner.schema_registry import compile_registry


@dataclass(frozen=True)
class SchemaDiagnostic:
    path: str
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}"


def _type_ok(value: Any, field_type: str) -> bool:
    if field_type == "any":
        return True
    if field_type == "string":
        return isinstance(value, str)
    if field_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if field_type == "bool":
        return isinstance(value, bool)
    if field_type == "list":
        return isinstance(value, list)
    if field_type == "mapping":
        return isinstance(value, dict)
    return False


def _resolve_field(case: dict[str, Any], field_path: str) -> tuple[bool, Any]:
    if "<" in field_path and ">" in field_path:
        return False, None
    parts = [p for p in str(field_path).split(".") if p]
    cur: Any = case
    for part in parts:
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur.get(part)
    return True, cur


def validate_case_shape(case: dict[str, Any], case_type: str, source_path: str) -> list[SchemaDiagnostic]:
    repo_root = Path(__file__).resolve().parents[3]
    compiled, errs = compile_registry(repo_root)
    if compiled is None:
        return [SchemaDiagnostic(path=source_path, message=e) for e in errs]

    diagnostics: list[SchemaDiagnostic] = []
    base_fields = dict(compiled.get("top_level_fields") or {})
    type_profiles = dict(compiled.get("type_profiles") or {})
    tp = type_profiles.get(case_type, {})
    profile_fields = dict(tp.get("fields") or {})
    allowed_extra = set(str(x) for x in (tp.get("allowed_top_level_extra") or []))

    allowed = set(base_fields.keys()) | set(profile_fields.keys()) | allowed_extra
    for key in case.keys():
        skey = str(key)
        if skey not in allowed:
            diagnostics.append(
                SchemaDiagnostic(
                    path=f"{source_path}",
                    message=f"unknown top-level key: {skey}",
                )
            )

    for fname, meta in {**base_fields, **profile_fields}.items():
        required = bool(meta.get("required", False))
        present, value = _resolve_field(case, fname)
        if required and not present:
            diagnostics.append(SchemaDiagnostic(path=source_path, message=f"missing required top-level key: {fname}"))
            continue
        if not present:
            continue
        field_type = str(meta.get("type", "any"))
        if not _type_ok(value, field_type):
            diagnostics.append(
                SchemaDiagnostic(path=source_path, message=f"invalid type for key {fname}: expected {field_type}")
            )
            continue
        enum = meta.get("enum")
        if isinstance(enum, list) and enum:
            if not isinstance(value, str) or value not in {str(x) for x in enum}:
                diagnostics.append(
                    SchemaDiagnostic(path=source_path, message=f"invalid enum value for key {fname}: {value!r}")
                )

    for fname in tp.get("required_top_level") or []:
        present, _ = _resolve_field(case, str(fname))
        if not present:
            diagnostics.append(SchemaDiagnostic(path=source_path, message=f"missing required key for type {case_type}: {fname}"))

    return diagnostics
