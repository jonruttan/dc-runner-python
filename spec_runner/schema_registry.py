from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REGISTRY_ROOT = Path("specs/schema/registry/v1")
REGISTRY_SCHEMA_PATH = Path("specs/schema/registry_schema_v1.yaml")


@dataclass(frozen=True)
class RegistryError:
    path: str
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}"


def _as_str_list(value: Any, *, field: str, errs: list[RegistryError], path: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        errs.append(RegistryError(path=path, message=f"{field} must be a list"))
        return []
    out: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errs.append(RegistryError(path=path, message=f"{field}[{i}] must be a non-empty string"))
            continue
        out.append(item.strip())
    return out


def _normalize_field_meta(raw: Any, *, field: str, path: str, errs: list[RegistryError]) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        errs.append(RegistryError(path=path, message=f"{field} metadata must be a mapping"))
        return None
    field_type = str(raw.get("type", "")).strip()
    if field_type not in {"string", "int", "bool", "list", "mapping", "any"}:
        errs.append(
            RegistryError(path=path, message=f"{field}.type must be one of string|int|bool|list|mapping|any")
        )
        return None
    required = bool(raw.get("required", False))
    enum = raw.get("enum")
    if enum is not None and (not isinstance(enum, list) or not all(isinstance(x, str) and x.strip() for x in enum)):
        errs.append(RegistryError(path=path, message=f"{field}.enum must be a list of non-empty strings"))
        enum = None
    out: dict[str, Any] = {
        "type": field_type,
        "required": required,
        "since": str(raw.get("since", "v1")).strip() or "v1",
    }
    for opt in ("deprecated", "removed", "replacement", "description"):
        if opt in raw and raw[opt] is not None:
            out[opt] = str(raw[opt]).strip()
    if enum is not None:
        out["enum"] = [str(x).strip() for x in enum]
    return out


def load_registry_schema(repo_root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = repo_root / REGISTRY_SCHEMA_PATH
    if not path.exists():
        return None, [f"{REGISTRY_SCHEMA_PATH}:1: missing registry schema"]
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None, [f"{REGISTRY_SCHEMA_PATH}:1: registry schema must be a mapping"]
    return payload, []


def load_registry_profiles(repo_root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    base = repo_root / REGISTRY_ROOT
    if not base.exists() or not base.is_dir():
        return {}, [f"{REGISTRY_ROOT}:1: missing registry root directory"]

    profiles: dict[str, dict[str, Any]] = {}
    errs: list[RegistryError] = []
    for p in sorted(base.rglob("*.yaml")):
        rel = p.relative_to(repo_root).as_posix()
        payload = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            errs.append(RegistryError(path=f"{rel}:1", message="profile file must be a mapping"))
            continue
        profile_id = str(payload.get("id", "")).strip()
        profile_type = str(payload.get("type", "")).strip()
        if not profile_id:
            errs.append(RegistryError(path=f"{rel}:1", message="profile id must be non-empty"))
            continue
        if profile_type not in {"core", "assertions", "harness", "path_model", "type"}:
            errs.append(
                RegistryError(path=f"{rel}:1", message="type must be core|assertions|harness|path_model|type")
            )
            continue
        if profile_id in profiles:
            errs.append(RegistryError(path=f"{rel}:1", message=f"duplicate profile id {profile_id}"))
            continue
        include = _as_str_list(payload.get("include"), field="include", errs=errs, path=f"{rel}:1")
        fields_raw = payload.get("fields", {})
        if not isinstance(fields_raw, dict):
            errs.append(RegistryError(path=f"{rel}:1", message="fields must be a mapping"))
            fields_raw = {}
        fields: dict[str, dict[str, Any]] = {}
        for name, meta in sorted(fields_raw.items()):
            fname = str(name).strip()
            if not fname:
                errs.append(RegistryError(path=f"{rel}:1", message="field names must be non-empty"))
                continue
            norm = _normalize_field_meta(meta, field=f"fields.{fname}", path=f"{rel}:1", errs=errs)
            if norm is not None:
                fields[fname] = norm

        profile: dict[str, Any] = {
            "id": profile_id,
            "type": profile_type,
            "path": rel,
            "include": include,
            "fields": fields,
        }
        if profile_type == "type":
            case_type = str(payload.get("case_type", "")).strip()
            if not case_type:
                errs.append(RegistryError(path=f"{rel}:1", message="type profile requires non-empty case_type"))
            profile["case_type"] = case_type
            profile["required_top_level"] = _as_str_list(
                payload.get("required_top_level"), field="required_top_level", errs=errs, path=f"{rel}:1"
            )
            profile["allowed_top_level_extra"] = _as_str_list(
                payload.get("allowed_top_level_extra"), field="allowed_top_level_extra", errs=errs, path=f"{rel}:1"
            )
        profiles[profile_id] = profile
    return profiles, [e.render() for e in errs]


def compile_registry(repo_root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    profiles, errs = load_registry_profiles(repo_root)
    if errs:
        return None, errs
    if not profiles:
        return None, [f"{REGISTRY_ROOT}:1: no registry profiles found"]

    by_type: dict[str, list[dict[str, Any]]] = {}
    for p in profiles.values():
        by_type.setdefault(str(p["type"]), []).append(p)

    core_fields: dict[str, dict[str, Any]] = {}
    merge_order = ("core", "assertions", "harness", "path_model")
    out_errs: list[str] = []
    for profile_type in merge_order:
        for p in sorted(by_type.get(profile_type, []), key=lambda x: str(x["id"])):
            for name, meta in sorted(dict(p.get("fields") or {}).items()):
                if name in core_fields:
                    existing = core_fields[name]
                    if (
                        str(existing.get("type")) != str(meta.get("type"))
                        or bool(existing.get("required")) != bool(meta.get("required"))
                    ):
                        out_errs.append(
                            f"{p['path']}:1: field collision for {name}: profile metadata differs from existing definition"
                        )
                        continue
                    merged = dict(existing)
                    for k, v in dict(meta).items():
                        if k not in merged and v is not None:
                            merged[k] = v
                    core_fields[name] = merged
                    continue
                core_fields[name] = dict(meta)

    type_profiles: dict[str, dict[str, Any]] = {}
    for p in sorted(by_type.get("type", []), key=lambda x: str(x["id"])):
        case_type = str(p.get("case_type", "")).strip()
        if not case_type:
            continue
        if case_type in type_profiles:
            out_errs.append(f"{p['path']}:1: duplicate type profile for case_type {case_type}")
            continue
        type_profiles[case_type] = {
            "id": p["id"],
            "path": p["path"],
            "fields": dict(p.get("fields") or {}),
            "required_top_level": list(p.get("required_top_level") or []),
            "allowed_top_level_extra": list(p.get("allowed_top_level_extra") or []),
        }

    if out_errs:
        return None, out_errs

    compiled: dict[str, Any] = {
        "version": 1,
        "registry_root": REGISTRY_ROOT.as_posix(),
        "profile_count": len(profiles),
        "profiles": {k: {"type": v["type"], "path": v["path"]} for k, v in sorted(profiles.items())},
        "top_level_fields": core_fields,
        "type_profiles": type_profiles,
    }
    return compiled, []


def write_compiled_registry_artifact(repo_root: Path, compiled: dict[str, Any]) -> Path:
    out = repo_root / ".artifacts/schema_registry_compiled.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    import json

    out.write_text(json.dumps(compiled, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
