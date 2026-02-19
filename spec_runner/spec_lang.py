from __future__ import annotations

import json
import math
import os
import re
import subprocess
import time
from fnmatch import fnmatch
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from spec_runner.spec_lang_std_names import FLAT_TO_STD, SPECIAL_FORMS, STD_TO_FLAT, namespace_index


@dataclass(frozen=True)
class SpecLangLimits:
    max_steps: int = 20000
    max_nodes: int = 20000
    max_literal_bytes: int = 262144
    timeout_ms: int = 200


@dataclass(frozen=True)
class _Closure:
    params: tuple[str, ...]
    body: Any
    env: "_Env"


@dataclass(frozen=True)
class _BuiltinFn:
    symbol: str
    arity: int
    bound_args: tuple[Any, ...] = ()


@dataclass(frozen=True)
class _Env:
    vars: dict[str, Any]
    parent: "_Env | None"

    def lookup(self, name: str) -> Any:
        cur: _Env | None = self
        while cur is not None:
            if name in cur.vars:
                value = cur.vars[name]
                if value is _UNSET:
                    raise ValueError(f"uninitialized variable: {name}")
                return value
            cur = cur.parent
        raise ValueError(f"undefined variable: {name}")


@dataclass
class _EvalState:
    subject: Any
    limits: SpecLangLimits
    imports: dict[str, str]
    capabilities: frozenset[str] = frozenset()
    last_exit_code: int | None = None
    dispatch_depth: int = 0
    last_dispatch_result: Any = None
    steps: int = 0
    started: float = 0.0

    def tick(self) -> None:
        self.steps += 1
        if self.steps > self.limits.max_steps:
            raise RuntimeError("spec_lang budget exceeded: steps")
        if self.limits.timeout_ms > 0:
            elapsed_ms = (time.perf_counter() - self.started) * 1000.0
            if elapsed_ms > float(self.limits.timeout_ms):
                raise RuntimeError("spec_lang budget exceeded: timeout")


_UNSET = object()


def _is_json_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (str, bool, int, float)):
        return True
    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and _is_json_value(v) for k, v in value.items())
    return False


def _literal_size(v: Any) -> int:
    if isinstance(v, str):
        return len(v.encode("utf-8"))
    if isinstance(v, (bytes, bytearray)):
        return len(v)
    return 0


def validate_expr_shape(expr: Any, *, limits: SpecLangLimits) -> None:
    stack = [expr]
    nodes = 0
    literal_bytes = 0
    while stack:
        cur = stack.pop()
        nodes += 1
        if nodes > limits.max_nodes:
            raise RuntimeError("spec_lang budget exceeded: nodes")
        literal_bytes += _literal_size(cur)
        if literal_bytes > limits.max_literal_bytes:
            raise RuntimeError("spec_lang budget exceeded: literal_size")
        if isinstance(cur, list):
            for child in cur:
                stack.append(child)


def _require_arity(op: str, args: list[Any], n: int) -> None:
    if len(args) != n:
        raise ValueError(f"spec_lang arity error for {op}: expected {n} got {len(args)}")


def _require_min_arity(op: str, args: list[Any], n: int) -> None:
    if len(args) < n:
        raise ValueError(f"spec_lang arity error for {op}: expected at least {n} got {len(args)}")


def _is_list_like(v: Any) -> bool:
    return isinstance(v, list)


def _is_dict_like(v: Any) -> bool:
    return isinstance(v, dict)


def _json_type_name(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if _is_list_like(v):
        return "list"
    if _is_dict_like(v):
        return "dict"
    return "unknown"


def _normalize_json_type_token(value: Any) -> str:
    token = str(value).strip().lower()
    aliases = {
        "boolean": "bool",
        "array": "list",
        "object": "dict",
    }
    return aliases.get(token, token)


def _truthy(v: Any) -> bool:
    return bool(v)


def _deep_equals(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        if len(left) != len(right):
            return False
        return all(_deep_equals(a, b) for a, b in zip(left, right))
    if isinstance(left, dict):
        if set(left.keys()) != set(right.keys()):
            return False
        return all(_deep_equals(left[k], right[k]) for k in left)
    return left == right


def _is_integer_number(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _includes_deep(seq: list[Any], value: Any) -> bool:
    return any(_deep_equals(item, value) for item in seq)


def _distinct_deep(seq: list[Any]) -> list[Any]:
    out: list[Any] = []
    for item in seq:
        if not _includes_deep(out, item):
            out.append(item)
    return out


def _require_list_arg(op: str, value: Any) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"spec_lang {op} expects list")
    return value


def _require_dict_arg(op: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"spec_lang {op} expects dict")
    return value


def _deep_merge_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    out = dict(left)
    for k, rv in right.items():
        lv = out.get(k)
        if isinstance(lv, dict) and isinstance(rv, dict):
            out[k] = _deep_merge_dicts(lv, rv)
        else:
            out[k] = rv
    return out


def _get_in_path(obj: Any, path: list[Any]) -> tuple[bool, Any]:
    cur = obj
    for seg in path:
        if isinstance(cur, dict):
            key = str(seg)
            if key not in cur:
                return False, None
            cur = cur[key]
            continue
        if isinstance(cur, list):
            if not isinstance(seg, int):
                return False, None
            if seg < 0 or seg >= len(cur):
                return False, None
            cur = cur[seg]
            continue
        return False, None
    return True, cur


def _schema_type_ok(value: Any, expected: str) -> bool:
    token = _normalize_json_type_token(expected)
    if token == "integer":
        return _is_integer_number(value)
    return _json_type_name(value) == token


def _schema_validate(value: Any, schema: Any, path: str, out: list[str]) -> None:
    if not isinstance(schema, dict):
        out.append(f"{path}: schema node must be mapping")
        return
    allowed = {
        "type",
        "required",
        "properties",
        "allow_extra",
        "items",
        "min_items",
        "max_items",
        "min_length",
        "max_length",
        "pattern",
        "const",
        "enum",
        "all_of",
        "any_of",
        "not",
    }
    for key in schema:
        if str(key) not in allowed:
            out.append(f"{path}: unknown schema key {key!r}")

    if "type" in schema:
        typ = schema["type"]
        if not isinstance(typ, str) or not typ.strip():
            out.append(f"{path}.type: must be non-empty string")
        elif not _schema_type_ok(value, typ):
            out.append(f"{path}: type mismatch expected {typ}")

    if "const" in schema and not _deep_equals(value, schema["const"]):
        out.append(f"{path}: const mismatch")

    if "enum" in schema:
        enum_values = schema["enum"]
        if not isinstance(enum_values, list) or not enum_values:
            out.append(f"{path}.enum: must be non-empty list")
        elif not any(_deep_equals(value, item) for item in enum_values):
            out.append(f"{path}: enum mismatch")

    if "pattern" in schema:
        pat = schema["pattern"]
        if not isinstance(pat, str) or not pat:
            out.append(f"{path}.pattern: must be non-empty string")
        elif not isinstance(value, str):
            out.append(f"{path}: pattern requires string value")
        elif re.search(pat, value) is None:
            out.append(f"{path}: pattern mismatch")

    if "min_length" in schema:
        ml = schema["min_length"]
        if not isinstance(ml, int) or ml < 0:
            out.append(f"{path}.min_length: must be non-negative int")
        elif not isinstance(value, str):
            out.append(f"{path}: min_length requires string value")
        elif len(value) < ml:
            out.append(f"{path}: min_length violation")
    if "max_length" in schema:
        ml = schema["max_length"]
        if not isinstance(ml, int) or ml < 0:
            out.append(f"{path}.max_length: must be non-negative int")
        elif not isinstance(value, str):
            out.append(f"{path}: max_length requires string value")
        elif len(value) > ml:
            out.append(f"{path}: max_length violation")

    if "required" in schema:
        required = schema["required"]
        if not isinstance(required, list) or any(not isinstance(x, str) or not x.strip() for x in required):
            out.append(f"{path}.required: must be list of non-empty strings")
        elif not isinstance(value, dict):
            out.append(f"{path}: required requires object value")
        else:
            for key in required:
                if key not in value:
                    out.append(f"{path}.{key}: missing required key")

    if "properties" in schema:
        props = schema["properties"]
        if not isinstance(props, dict):
            out.append(f"{path}.properties: must be mapping")
        elif not isinstance(value, dict):
            out.append(f"{path}: properties requires object value")
        else:
            for key, child in props.items():
                skey = str(key)
                if skey in value:
                    _schema_validate(value[skey], child, f"{path}.{skey}", out)
            allow_extra = schema.get("allow_extra", True)
            if not isinstance(allow_extra, bool):
                out.append(f"{path}.allow_extra: must be boolean")
            elif not allow_extra:
                allowed_keys = {str(k) for k in props.keys()}
                for key in value.keys():
                    if str(key) not in allowed_keys:
                        out.append(f"{path}.{key}: extra key not allowed")

    if "items" in schema:
        child_schema = schema["items"]
        if not isinstance(value, list):
            out.append(f"{path}: items requires array value")
        else:
            for idx, item in enumerate(value):
                _schema_validate(item, child_schema, f"{path}[{idx}]", out)

    if "min_items" in schema:
        mi = schema["min_items"]
        if not isinstance(mi, int) or mi < 0:
            out.append(f"{path}.min_items: must be non-negative int")
        elif not isinstance(value, list):
            out.append(f"{path}: min_items requires array value")
        elif len(value) < mi:
            out.append(f"{path}: min_items violation")
    if "max_items" in schema:
        mi = schema["max_items"]
        if not isinstance(mi, int) or mi < 0:
            out.append(f"{path}.max_items: must be non-negative int")
        elif not isinstance(value, list):
            out.append(f"{path}: max_items requires array value")
        elif len(value) > mi:
            out.append(f"{path}: max_items violation")

    if "all_of" in schema:
        all_of = schema["all_of"]
        if not isinstance(all_of, list) or not all_of:
            out.append(f"{path}.all_of: must be non-empty list")
        else:
            for idx, child in enumerate(all_of):
                _schema_validate(value, child, f"{path}.all_of[{idx}]", out)
    if "any_of" in schema:
        any_of = schema["any_of"]
        if not isinstance(any_of, list) or not any_of:
            out.append(f"{path}.any_of: must be non-empty list")
        else:
            matched = False
            for child in any_of:
                tmp: list[str] = []
                _schema_validate(value, child, path, tmp)
                if not tmp:
                    matched = True
                    break
            if not matched:
                out.append(f"{path}: any_of mismatch")
    if "not" in schema:
        tmp = []
        _schema_validate(value, schema["not"], path, tmp)
        if not tmp:
            out.append(f"{path}: not mismatch")


def _require_numeric_arg(op: str, value: Any) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"spec_lang {op} expects numeric args")
    return value


def _require_int_arg(op: str, value: Any) -> int:
    if not _is_integer_number(value):
        raise ValueError(f"spec_lang {op} expects integer args")
    return value


def _require_ops_os_capability(op: str, st: _EvalState) -> None:
    if "ops.os" not in st.capabilities:
        raise ValueError(f"capability.ops_os.required: {op}")


def _require_capability(op: str, st: _EvalState, capability: str) -> None:
    if capability not in st.capabilities:
        raise ValueError(f"capability.{capability.replace('.', '_')}.required: {op}")


def _coerce_exec_command(op: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"spec_lang {op} expects non-empty list command")
    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            token = item.strip()
        else:
            token = str(item).strip()
        if not token:
            raise ValueError(f"spec_lang {op} command entries must be non-empty strings")
        out.append(token)
    return out


def _load_json_env_mapping(name: str) -> dict[str, Any]:
    raw = str(os.environ.get(name, "")).strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must contain valid JSON mapping") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{name} must contain JSON mapping")
    out: dict[str, Any] = {}
    for raw_k, value in payload.items():
        k = str(raw_k).strip()
        if k:
            out[k] = value
    return out


def _run_helper_call(helper_id: str, payload: Any) -> Any:
    helpers = _load_json_env_mapping("SPEC_RUNNER_SPEC_LANG_HELPERS_JSON")
    entry = helpers.get(helper_id)
    if entry is None:
        raise ValueError(f"ops.helper.call error: unsupported helper id: {helper_id}")
    if not isinstance(entry, dict):
        return entry
    if "error" in entry:
        raise ValueError(f"ops.helper.call error: {entry['error']}")
    if "result" in entry:
        return entry.get("result")
    command = entry.get("command")
    if not isinstance(command, list) or not command or any(not str(x).strip() for x in command):
        raise ValueError("ops.helper.call error: helper entry requires result or non-empty command list")
    env = os.environ.copy()
    extra_env = entry.get("env")
    if isinstance(extra_env, dict):
        for k, v in extra_env.items():
            key = str(k).strip()
            if key:
                env[key] = str(v)
    proc = subprocess.run(
        [str(x).strip() for x in command],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        raise ValueError(f"ops.helper.call error: helper command failed (exit={proc.returncode})")
    out = str(proc.stdout or "").strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def _round_half_away_from_zero(v: int | float) -> int:
    return math.floor(v + 0.5) if v >= 0 else math.ceil(v - 0.5)


def _fs_normalize_path(path: str) -> str:
    raw = path.strip()
    if raw == "":
        return "."
    absolute = raw.startswith("/")
    segments: list[str] = []
    for part in raw.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if segments and segments[-1] != "..":
                segments.pop()
            elif not absolute:
                segments.append("..")
            continue
        segments.append(part)
    normalized = "/".join(segments)
    if absolute:
        return f"/{normalized}" if normalized else "/"
    return normalized if normalized else "."


def _fs_split_segments(path: str) -> list[str]:
    normalized = _fs_normalize_path(path)
    if normalized in {".", "/"}:
        return []
    return [part for part in normalized.split("/") if part and part != "."]


def _fs_basename(path: str) -> str:
    normalized = _fs_normalize_path(path)
    if normalized == "/":
        return ""
    if normalized == ".":
        return "."
    parts = _fs_split_segments(normalized)
    return parts[-1] if parts else ""


def _fs_dirname(path: str) -> str:
    normalized = _fs_normalize_path(path)
    if normalized == "/":
        return "/"
    absolute = normalized.startswith("/")
    parts = _fs_split_segments(normalized)
    if not parts:
        return "/" if absolute else "."
    parent = parts[:-1]
    if not parent:
        return "/" if absolute else "."
    joined = "/".join(parent)
    return f"/{joined}" if absolute else joined


def _fs_extname(path: str) -> str:
    base = _fs_basename(path)
    if not base or base in {".", ".."}:
        return ""
    idx = base.rfind(".")
    if idx <= 0:
        return ""
    return base[idx:]


def _fs_stem(path: str) -> str:
    base = _fs_basename(path)
    ext = _fs_extname(path)
    if ext:
        return base[: -len(ext)]
    return base


def _fs_normalize_ext(ext: str) -> str:
    token = ext.strip()
    if token == "":
        return ""
    return token if token.startswith(".") else f".{token}"


def _fs_relativize(base: str, path: str) -> str:
    base_norm = _fs_normalize_path(base)
    path_norm = _fs_normalize_path(path)
    base_abs = base_norm.startswith("/")
    path_abs = path_norm.startswith("/")
    if base_abs != path_abs:
        return path_norm
    base_parts = _fs_split_segments(base_norm)
    path_parts = _fs_split_segments(path_norm)
    i = 0
    while i < len(base_parts) and i < len(path_parts) and base_parts[i] == path_parts[i]:
        i += 1
    up = [".."] * (len(base_parts) - i)
    down = path_parts[i:]
    rel_parts = up + down
    if not rel_parts:
        return "."
    return "/".join(rel_parts)


def _fs_common_prefix(paths: list[str]) -> str:
    if not paths:
        return "."
    normalized = [_fs_normalize_path(p) for p in paths]
    abs_flags = [p.startswith("/") for p in normalized]
    if any(flag != abs_flags[0] for flag in abs_flags):
        return "."
    split_paths = [_fs_split_segments(p) for p in normalized]
    prefix: list[str] = []
    idx = 0
    while True:
        current: str | None = None
        for parts in split_paths:
            if idx >= len(parts):
                current = None
                break
            value = parts[idx]
            if current is None:
                current = value
                continue
            if value != current:
                current = None
                break
        if current is None:
            break
        prefix.append(current)
        idx += 1
    if not prefix:
        return "/" if abs_flags[0] else "."
    joined = "/".join(prefix)
    return f"/{joined}" if abs_flags[0] else joined


def _fs_parents(path: str) -> list[str]:
    normalized = _fs_normalize_path(path)
    if normalized in {"/", "."}:
        return []
    out: list[str] = []
    current = normalized
    while True:
        parent = _fs_dirname(current)
        if parent == current or parent in out:
            break
        out.append(parent)
        if parent in {"/", "."}:
            break
        current = parent
    return out


def _fs_within(base: str, path: str) -> bool:
    base_norm = _fs_normalize_path(base)
    path_norm = _fs_normalize_path(path)
    base_abs = base_norm.startswith("/")
    path_abs = path_norm.startswith("/")
    if base_abs != path_abs:
        return False
    if base_norm == path_norm:
        return True
    if base_norm == "/" and path_abs:
        return True
    if base_norm == "." and not path_abs:
        return True
    base_parts = _fs_split_segments(base_norm)
    path_parts = _fs_split_segments(path_norm)
    if len(path_parts) < len(base_parts):
        return False
    return path_parts[: len(base_parts)] == base_parts


def _builtin_arity_table() -> dict[str, int]:
    # Fixed arity table used by builtin currying.
    flat = {
        "subject": 0,
        "contains": 2,
        "starts_with": 2,
        "ends_with": 2,
        "regex_match": 2,
        "matches": 2,
        "eq": 2,
        "neq": 2,
        "equals": 2,
        "in": 2,
        "includes": 2,
        "lt": 2,
        "lte": 2,
        "gt": 2,
        "gte": 2,
        "add": 2,
        "sub": 2,
        "mul": 2,
        "div": 2,
        "mod": 2,
        "pow": 2,
        "abs": 1,
        "negate": 1,
        "inc": 1,
        "dec": 1,
        "clamp": 3,
        "round": 1,
        "floor": 1,
        "ceil": 1,
        "compare": 2,
        "between": 3,
        "xor": 2,
        "json_type": 2,
        "is_null": 1,
        "is_bool": 1,
        "is_boolean": 1,
        "is_number": 1,
        "is_integer": 1,
        "is_string": 1,
        "is_list": 1,
        "is_array": 1,
        "is_dict": 1,
        "is_object": 1,
        "has_key": 2,
        "get": 2,
        "get_in": 2,
        "get_or": 3,
        "has_path": 2,
        "len": 1,
        "count": 1,
        "first": 1,
        "rest": 1,
        "last": 1,
        "nth": 2,
        "trim": 1,
        "lower": 1,
        "upper": 1,
        "split": 2,
        "join": 2,
        "map": 2,
        "filter": 2,
        "reject": 2,
        "find": 2,
        "reduce": 3,
        "partition": 2,
        "group_by": 2,
        "uniq_by": 2,
        "flatten": 1,
        "concat": 2,
        "append": 2,
        "prepend": 2,
        "take": 2,
        "drop": 2,
        "slice": 3,
        "reverse": 1,
        "zip": 2,
        "zip_with": 3,
        "range": 2,
        "repeat": 2,
        "any": 1,
        "all": 1,
        "none": 1,
        "is_empty": 1,
        "distinct": 1,
        "sort": 1,
        "coalesce": 2,
        "default_to": 2,
        "contains_all": 2,
        "contains_any": 2,
        "pluck": 2,
        "sort_by": 2,
        "keys": 1,
        "values": 1,
        "entries": 1,
        "merge": 2,
        "merge_deep": 2,
        "assoc": 3,
        "dissoc": 2,
        "pick": 2,
        "omit": 2,
        "keys_exact": 2,
        "keys_include": 2,
        "keys_exclude": 2,
        "prop_eq": 3,
        "where": 2,
        "compose": 3,
        "pipe": 3,
        "identity": 1,
        "always": 2,
        "replace": 3,
        "pad_left": 3,
        "pad_right": 3,
        "sum": 1,
        "min": 1,
        "max": 1,
        "matches_all": 2,
        "union": 2,
        "intersection": 2,
        "difference": 2,
        "symmetric_difference": 2,
        "is_subset": 2,
        "is_superset": 2,
        "set_equals": 2,
        "json_parse": 1,
        "json_stringify": 1,
        "schema_match": 2,
        "schema_errors": 2,
        "ops_fs_path_normalize": 1,
        "ops_fs_path_join": 2,
        "ops_fs_path_split": 1,
        "ops_fs_path_dirname": 1,
        "ops_fs_path_basename": 1,
        "ops_fs_path_extname": 1,
        "ops_fs_path_stem": 1,
        "ops_fs_path_is_abs": 1,
        "ops_fs_path_has_ext": 2,
        "ops_fs_path_change_ext": 2,
        "ops_fs_path_relativize": 2,
        "ops_fs_path_common_prefix": 1,
        "ops_fs_path_parents": 1,
        "ops_fs_path_within": 2,
        "ops_fs_path_compare": 2,
        "ops_fs_path_sort": 1,
        "ops_fs_file_exists": 1,
        "ops_fs_file_is_file": 1,
        "ops_fs_file_is_dir": 1,
        "ops_fs_file_size_bytes": 1,
        "ops_fs_file_path": 1,
        "ops_fs_file_name": 1,
        "ops_fs_file_parent": 1,
        "ops_fs_file_ext": 1,
        "ops_fs_file_get": 3,
        "ops_fs_walk": 2,
        "ops_fs_file_set": 2,
        "ops_fs_file_append": 2,
        "ops_fs_file_mkdir_p": 1,
        "ops_fs_file_remove": 1,
        "ops_fs_json_parse": 1,
        "ops_fs_json_get": 2,
        "ops_fs_json_get_or": 3,
        "ops_fs_json_has_path": 2,
        "ops_fs_yaml_parse": 1,
        "ops_fs_yaml_stringify": 1,
        "ops_fs_yaml_get": 2,
        "ops_fs_yaml_get_or": 3,
        "ops_fs_yaml_has_path": 2,
        "ops_fs_glob_match": 2,
        "ops_fs_glob_filter": 2,
        "ops_fs_glob_any": 2,
        "ops_fs_glob_all": 2,
        "ops_os_exec": 2,
        "ops_os_exec_capture": 2,
        "ops_os_exec_capture_ex": 2,
        "ops_os_env_get": 2,
        "ops_os_env_has": 1,
        "ops_os_cwd": 0,
        "ops_os_pid": 0,
        "ops_os_sleep_ms": 1,
        "ops_os_exit_code": 0,
        "ops_helper_call": 2,
        "ops_job_dispatch": 1,
        "and": 2,
        "or": 2,
        "not": 1,
    }
    return {FLAT_TO_STD[name]: arity for name, arity in flat.items()}


_BUILTIN_ARITY = _builtin_arity_table()
_STD_NAMESPACE_INDEX = namespace_index()


def _flat_symbol_for_runtime(symbol: str) -> str:
    if symbol.startswith("ops."):
        return symbol
    return STD_TO_FLAT.get(symbol, symbol)


def compile_import_bindings(
    harness_spec_lang: Mapping[str, Any] | None,
) -> dict[str, str]:
    cfg = dict(harness_spec_lang or {})
    raw_imports = cfg.get("imports")
    if raw_imports is None:
        return {}
    if not isinstance(raw_imports, list):
        raise ValueError("harness.spec_lang.imports must be a list")

    out: dict[str, str] = {}
    for idx, item in enumerate(raw_imports):
        field = f"harness.spec_lang.imports[{idx}]"
        if not isinstance(item, dict):
            raise ValueError(f"{field} must be a mapping")
        ns = str(item.get("from", "")).strip()
        if not ns:
            raise ValueError(f"{field}.from must be a non-empty string")
        allowed = _STD_NAMESPACE_INDEX.get(ns)
        if allowed is None:
            raise ValueError(f"{field}.from unknown namespace: {ns}")

        names = item.get("names")
        if not isinstance(names, list) or not names:
            raise ValueError(f"{field}.names must be a non-empty list")

        alias_raw = item.get("as")
        alias_map: dict[str, str] = {}
        if alias_raw is not None:
            if not isinstance(alias_raw, dict):
                raise ValueError(f"{field}.as must be a mapping")
            for raw_from, raw_to in alias_raw.items():
                from_name = str(raw_from).strip()
                to_name = str(raw_to).strip()
                if not from_name or not to_name:
                    raise ValueError(f"{field}.as keys/values must be non-empty strings")
                alias_map[from_name] = to_name

        for j, raw_name in enumerate(names):
            short = str(raw_name).strip()
            if not short:
                raise ValueError(f"{field}.names[{j}] must be a non-empty string")
            if short not in allowed:
                raise ValueError(f"{field}.names[{j}] unknown symbol in namespace {ns}: {short}")
            local = alias_map.get(short, short)
            if local in SPECIAL_FORMS:
                raise ValueError(f"{field} import collides with reserved special form: {local}")
            if local in out and out[local] != f"{ns}.{short}":
                raise ValueError(f"{field} import collision for local name: {local}")
            out[local] = f"{ns}.{short}"

    return out


def _resolve_op_symbol(head: str, imports: Mapping[str, str]) -> str:
    if head in SPECIAL_FORMS:
        return head
    if head in _BUILTIN_ARITY:
        return head
    if head.startswith("std."):
        raise ValueError(f"unsupported spec_lang symbol: {head}")
    if head in imports:
        return imports[head]
    if head in FLAT_TO_STD:
        # Internal list-token AST may still carry flat names; normalize at runtime.
        return FLAT_TO_STD[head]
    raise ValueError(f"unsupported spec_lang symbol: {head}")


def _eval_non_tail(expr: Any, env: _Env, st: _EvalState) -> Any:
    return _eval_tail(expr, env, st)


def _is_callable_like(v: Any) -> bool:
    return isinstance(v, (_Closure, _BuiltinFn))


def _as_builtin_fn(v: Any) -> _BuiltinFn | None:
    if isinstance(v, _BuiltinFn):
        return v
    if isinstance(v, str) and v in _BUILTIN_ARITY:
        return _BuiltinFn(symbol=v, arity=_BUILTIN_ARITY[v])
    return None


def _apply_builtin_curried(fn_val: _BuiltinFn, call_args: list[Any], st: _EvalState) -> Any:
    all_args = [*fn_val.bound_args, *call_args]
    if len(all_args) < fn_val.arity:
        return _BuiltinFn(fn_val.symbol, fn_val.arity, tuple(all_args))
    consumed = all_args[: fn_val.arity]
    remainder = all_args[fn_val.arity :]
    result = _eval_builtin_eager(fn_val.symbol, consumed, st)
    if not remainder:
        return result
    if not _is_callable_like(result):
        raise ValueError(
            f"spec_lang over-application error for {fn_val.symbol}: result is not callable"
        )
    return _eval_callable_like(result, remainder, st)


def _eval_callable_like(fn_val: Any, call_args: list[Any], st: _EvalState) -> Any:
    if isinstance(fn_val, _Closure):
        if len(call_args) != len(fn_val.params):
            raise ValueError("spec_lang call argument count mismatch")
        next_env = _Env(vars={k: v for k, v in zip(fn_val.params, call_args)}, parent=fn_val.env)
        return _eval_tail(fn_val.body, next_env, st)
    builtin_fn = _as_builtin_fn(fn_val)
    if builtin_fn is not None:
        return _apply_builtin_curried(builtin_fn, call_args, st)
    raise ValueError("spec_lang callable expects fn closure or builtin function")


def _eval_builtin_eager(op: str, args: list[Any], st: _EvalState) -> Any:
    op = _flat_symbol_for_runtime(op)
    if op == "subject":
        _require_arity(op, args, 0)
        return st.subject
    if op == "contains":
        _require_arity(op, args, 2)
        return str(args[1]) in str(args[0])
    if op == "starts_with":
        _require_arity(op, args, 2)
        return str(args[0]).startswith(str(args[1]))
    if op == "ends_with":
        _require_arity(op, args, 2)
        return str(args[0]).endswith(str(args[1]))
    if op in {"regex_match", "matches"}:
        _require_arity(op, args, 2)
        return re.search(str(args[1]), str(args[0])) is not None
    if op == "eq":
        _require_arity(op, args, 2)
        return args[0] == args[1]
    if op == "neq":
        _require_arity(op, args, 2)
        return args[0] != args[1]
    if op == "equals":
        _require_arity(op, args, 2)
        return _deep_equals(args[0], args[1])
    if op == "lt":
        _require_arity(op, args, 2)
        return args[0] < args[1]
    if op == "lte":
        _require_arity(op, args, 2)
        return args[0] <= args[1]
    if op == "gt":
        _require_arity(op, args, 2)
        return args[0] > args[1]
    if op == "gte":
        _require_arity(op, args, 2)
        return args[0] >= args[1]
    if op == "in":
        _require_arity(op, args, 2)
        member, container = args
        if _is_list_like(container):
            return member in container
        if _is_dict_like(container):
            return str(member) in container
        if isinstance(container, str):
            return str(member) in container
        raise ValueError("spec_lang in expects list/dict/string container")
    if op == "includes":
        _require_arity(op, args, 2)
        seq = _require_list_arg(op, args[0])
        return _includes_deep(seq, args[1])
    if op == "add":
        _require_arity(op, args, 2)
        return _require_numeric_arg(op, args[0]) + _require_numeric_arg(op, args[1])
    if op == "sub":
        _require_arity(op, args, 2)
        return _require_numeric_arg(op, args[0]) - _require_numeric_arg(op, args[1])
    if op == "mul":
        _require_arity(op, args, 2)
        return _require_numeric_arg(op, args[0]) * _require_numeric_arg(op, args[1])
    if op == "div":
        _require_arity(op, args, 2)
        left = _require_numeric_arg(op, args[0])
        right = _require_numeric_arg(op, args[1])
        if right == 0:
            raise ValueError("spec_lang div expects non-zero divisor")
        return left / right
    if op == "mod":
        _require_arity(op, args, 2)
        left = _require_int_arg(op, args[0])
        right = _require_int_arg(op, args[1])
        if right == 0:
            raise ValueError("spec_lang mod expects non-zero divisor")
        return left % right
    if op == "pow":
        _require_arity(op, args, 2)
        return _require_numeric_arg(op, args[0]) ** _require_numeric_arg(op, args[1])
    if op == "abs":
        _require_arity(op, args, 1)
        return abs(_require_numeric_arg(op, args[0]))
    if op == "negate":
        _require_arity(op, args, 1)
        return -_require_numeric_arg(op, args[0])
    if op == "inc":
        _require_arity(op, args, 1)
        return _require_numeric_arg(op, args[0]) + 1
    if op == "dec":
        _require_arity(op, args, 1)
        return _require_numeric_arg(op, args[0]) - 1
    if op == "clamp":
        _require_arity(op, args, 3)
        low = _require_numeric_arg(op, args[0])
        high = _require_numeric_arg(op, args[1])
        value = _require_numeric_arg(op, args[2])
        if low > high:
            raise ValueError("spec_lang clamp expects low <= high")
        return min(max(value, low), high)
    if op == "round":
        _require_arity(op, args, 1)
        return _round_half_away_from_zero(_require_numeric_arg(op, args[0]))
    if op == "floor":
        _require_arity(op, args, 1)
        return math.floor(_require_numeric_arg(op, args[0]))
    if op == "ceil":
        _require_arity(op, args, 1)
        return math.ceil(_require_numeric_arg(op, args[0]))
    if op == "compare":
        _require_arity(op, args, 2)
        left, right = args
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return -1 if left < right else (1 if left > right else 0)
        if isinstance(left, str) and isinstance(right, str):
            return -1 if left < right else (1 if left > right else 0)
        raise ValueError("spec_lang compare expects both args to be numbers or strings")
    if op == "between":
        _require_arity(op, args, 3)
        low = _require_numeric_arg(op, args[0])
        high = _require_numeric_arg(op, args[1])
        value = _require_numeric_arg(op, args[2])
        if low > high:
            raise ValueError("spec_lang between expects low <= high")
        return low <= value <= high
    if op == "xor":
        _require_arity(op, args, 2)
        return _truthy(args[0]) != _truthy(args[1])
    if op == "json_type":
        _require_arity(op, args, 2)
        return _json_type_name(args[0]) == _normalize_json_type_token(args[1])
    if op in {
        "is_null",
        "is_bool",
        "is_boolean",
        "is_number",
        "is_integer",
        "is_string",
        "is_list",
        "is_array",
        "is_dict",
        "is_object",
    }:
        _require_arity(op, args, 1)
        kind = _json_type_name(args[0])
        return {
            "is_null": kind == "null",
            "is_bool": kind == "bool",
            "is_boolean": kind == "bool",
            "is_number": kind == "number",
            "is_integer": _is_integer_number(args[0]),
            "is_string": kind == "string",
            "is_list": kind == "list",
            "is_array": kind == "list",
            "is_dict": kind == "dict",
            "is_object": kind == "dict",
        }[op]
    if op == "has_key":
        _require_arity(op, args, 2)
        if not _is_dict_like(args[0]):
            return False
        return str(args[1]) in args[0]
    if op == "get":
        _require_arity(op, args, 2)
        obj, key = args
        if _is_dict_like(obj):
            return obj.get(str(key))
        if _is_list_like(obj):
            if not isinstance(key, int):
                raise ValueError("spec_lang get list index must be int")
            if key < 0 or key >= len(obj):
                return None
            return obj[key]
        raise ValueError("spec_lang get expects dict or list")
    if op == "get_in":
        _require_arity(op, args, 2)
        path = _require_list_arg(op, args[1])
        ok, value = _get_in_path(args[0], path)
        return value if ok else None
    if op == "get_or":
        _require_arity(op, args, 3)
        path = _require_list_arg(op, args[1])
        ok, value = _get_in_path(args[0], path)
        return value if ok else args[2]
    if op == "has_path":
        _require_arity(op, args, 2)
        path = _require_list_arg(op, args[1])
        ok, _ = _get_in_path(args[0], path)
        return ok
    if op in {"len", "count"}:
        _require_arity(op, args, 1)
        v = args[0]
        if isinstance(v, (str, list, dict)):
            return len(v)
        raise ValueError(f"spec_lang {op} expects string/list/dict")
    if op == "first":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        return seq[0] if seq else None
    if op == "rest":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        return seq[1:] if len(seq) > 1 else []
    if op == "last":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        return seq[-1] if seq else None
    if op == "nth":
        _require_arity(op, args, 2)
        seq = _require_list_arg(op, args[0])
        idx = _require_int_arg(op, args[1])
        if idx < 0 or idx >= len(seq):
            return None
        return seq[idx]
    if op == "any":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        return any(_truthy(x) for x in seq)
    if op == "all":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        return all(_truthy(x) for x in seq)
    if op == "none":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        return not any(_truthy(x) for x in seq)
    if op == "is_empty":
        _require_arity(op, args, 1)
        seq = args[0]
        if isinstance(seq, (list, dict, str)):
            return len(seq) == 0
        raise ValueError("spec_lang is_empty expects list/dict/string")
    if op == "distinct":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        return _distinct_deep(seq)
    if op == "sort":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        if not seq:
            return []
        first_type = type(seq[0])
        if first_type not in {str, int, float, bool}:
            raise ValueError("spec_lang sort expects scalar list values")
        if any(type(x) is not first_type for x in seq):
            raise ValueError("spec_lang sort expects homogeneous list element types")
        return sorted(seq)
    if op == "coalesce":
        _require_arity(op, args, 2)
        for got in args:
            if got is None:
                continue
            if isinstance(got, str) and got == "":
                continue
            return got
        return None
    if op == "trim":
        _require_arity(op, args, 1)
        return str(args[0]).strip()
    if op == "lower":
        _require_arity(op, args, 1)
        return str(args[0]).lower()
    if op == "upper":
        _require_arity(op, args, 1)
        return str(args[0]).upper()
    if op == "split":
        _require_arity(op, args, 2)
        return str(args[0]).split(str(args[1]))
    if op == "join":
        _require_arity(op, args, 2)
        seq = _require_list_arg(op, args[0])
        return str(args[1]).join(str(x) for x in seq)
    if op == "sum":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        total: float = 0.0
        saw_float = False
        for item in seq:
            if not isinstance(item, (int, float)):
                raise ValueError("spec_lang sum expects numeric list values")
            if isinstance(item, float):
                saw_float = True
            total += float(item)
        return total if saw_float else int(total)
    if op == "min":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        if not seq:
            raise ValueError("spec_lang min expects non-empty list")
        return min(seq)
    if op == "max":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        if not seq:
            raise ValueError("spec_lang max expects non-empty list")
        return max(seq)
    if op == "matches_all":
        _require_arity(op, args, 2)
        hay = str(args[0])
        patterns = _require_list_arg(op, args[1])
        return all(re.search(str(p), hay) is not None for p in patterns)
    if op == "pluck":
        _require_arity(op, args, 2)
        seq = _require_list_arg(op, args[0])
        key = str(args[1])
        plucked: list[Any] = []
        for item in seq:
            if isinstance(item, dict):
                plucked.append(item.get(key))
            else:
                plucked.append(None)
        return plucked
    if op == "keys":
        _require_arity(op, args, 1)
        return list(_require_dict_arg(op, args[0]).keys())
    if op == "values":
        _require_arity(op, args, 1)
        return list(_require_dict_arg(op, args[0]).values())
    if op == "entries":
        _require_arity(op, args, 1)
        obj = _require_dict_arg(op, args[0])
        return [[k, v] for k, v in obj.items()]
    if op == "merge":
        _require_arity(op, args, 2)
        left_obj = _require_dict_arg(op, args[0])
        right_obj = _require_dict_arg(op, args[1])
        return {**left_obj, **right_obj}
    if op == "merge_deep":
        _require_arity(op, args, 2)
        left_obj = _require_dict_arg(op, args[0])
        right_obj = _require_dict_arg(op, args[1])
        return _deep_merge_dicts(left_obj, right_obj)
    if op == "assoc":
        _require_arity(op, args, 3)
        key = str(args[0])
        value = args[1]
        obj = _require_dict_arg(op, args[2])
        out = dict(obj)
        out[key] = value
        return out
    if op == "dissoc":
        _require_arity(op, args, 2)
        key = str(args[0])
        obj = _require_dict_arg(op, args[1])
        out = dict(obj)
        out.pop(key, None)
        return out
    if op == "pick":
        _require_arity(op, args, 2)
        keys = _require_list_arg(op, args[0])
        obj = _require_dict_arg(op, args[1])
        wanted = {str(k) for k in keys}
        return {k: v for k, v in obj.items() if k in wanted}
    if op == "omit":
        _require_arity(op, args, 2)
        keys = _require_list_arg(op, args[0])
        obj = _require_dict_arg(op, args[1])
        blocked = {str(k) for k in keys}
        return {k: v for k, v in obj.items() if k not in blocked}
    if op == "keys_exact":
        _require_arity(op, args, 2)
        obj = _require_dict_arg(op, args[0])
        keys = _require_list_arg(op, args[1])
        expected = {str(k) for k in keys}
        return set(obj.keys()) == expected
    if op == "keys_include":
        _require_arity(op, args, 2)
        obj = _require_dict_arg(op, args[0])
        keys = _require_list_arg(op, args[1])
        required = {str(k) for k in keys}
        return required.issubset(set(obj.keys()))
    if op == "keys_exclude":
        _require_arity(op, args, 2)
        obj = _require_dict_arg(op, args[0])
        keys = _require_list_arg(op, args[1])
        blocked = {str(k) for k in keys}
        return blocked.isdisjoint(set(obj.keys()))
    if op == "prop_eq":
        _require_arity(op, args, 3)
        key = str(args[0])
        expected = args[1]
        obj = _require_dict_arg(op, args[2])
        return _deep_equals(obj.get(key), expected)
    if op == "identity":
        _require_arity(op, args, 1)
        return args[0]
    if op == "always":
        _require_arity(op, args, 2)
        return args[0]
    if op == "replace":
        _require_arity(op, args, 3)
        return str(args[0]).replace(str(args[1]), str(args[2]))
    if op == "pad_left":
        _require_arity(op, args, 3)
        text = str(args[0])
        width = _require_int_arg(op, args[1])
        fill = str(args[2])
        if fill == "":
            raise ValueError("spec_lang pad_left expects non-empty pad string")
        while len(text) < width:
            text = fill + text
        return text[-width:] if width > 0 else ""
    if op == "pad_right":
        _require_arity(op, args, 3)
        text = str(args[0])
        width = _require_int_arg(op, args[1])
        fill = str(args[2])
        if fill == "":
            raise ValueError("spec_lang pad_right expects non-empty pad string")
        while len(text) < width:
            text = text + fill
        return text[:width] if width > 0 else ""
    if op == "concat":
        _require_arity(op, args, 2)
        left_seq = _require_list_arg(op, args[0])
        right_seq = _require_list_arg(op, args[1])
        return [*left_seq, *right_seq]
    if op == "append":
        _require_arity(op, args, 2)
        seq = _require_list_arg(op, args[1])
        return [*seq, args[0]]
    if op == "prepend":
        _require_arity(op, args, 2)
        seq = _require_list_arg(op, args[1])
        return [args[0], *seq]
    if op == "take":
        _require_arity(op, args, 2)
        n = args[0]
        seq = _require_list_arg(op, args[1])
        if not isinstance(n, int):
            raise ValueError("spec_lang take expects integer count")
        return seq[: max(n, 0)]
    if op == "drop":
        _require_arity(op, args, 2)
        n = args[0]
        seq = _require_list_arg(op, args[1])
        if not isinstance(n, int):
            raise ValueError("spec_lang drop expects integer count")
        return seq[max(n, 0) :]
    if op == "slice":
        _require_arity(op, args, 3)
        start = _require_int_arg(op, args[0])
        end = _require_int_arg(op, args[1])
        seq = _require_list_arg(op, args[2])
        return seq[start:end]
    if op == "reverse":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])
        return list(reversed(seq))
    if op == "zip":
        _require_arity(op, args, 2)
        left_seq = _require_list_arg(op, args[0])
        right_seq = _require_list_arg(op, args[1])
        return [[a, b] for a, b in zip(left_seq, right_seq)]
    if op == "range":
        _require_arity(op, args, 2)
        start = _require_int_arg(op, args[0])
        end = _require_int_arg(op, args[1])
        return list(range(start, end))
    if op == "repeat":
        _require_arity(op, args, 2)
        value = args[0]
        count = _require_int_arg(op, args[1])
        if count < 0:
            raise ValueError("spec_lang repeat expects non-negative count")
        return [value for _ in range(count)]
    if op == "flatten":
        _require_arity(op, args, 1)
        seq = _require_list_arg(op, args[0])

        def _flatten(xs: list[Any], out: list[Any]) -> None:
            for item in xs:
                if isinstance(item, list):
                    _flatten(item, out)
                else:
                    out.append(item)

        flat: list[Any] = []
        _flatten(seq, flat)
        return flat
    if op == "union":
        _require_arity(op, args, 2)
        left_seq = _require_list_arg(op, args[0])
        right_seq = _require_list_arg(op, args[1])
        return _distinct_deep([*left_seq, *right_seq])
    if op == "intersection":
        _require_arity(op, args, 2)
        left_seq = _require_list_arg(op, args[0])
        right_seq = _require_list_arg(op, args[1])
        out_list: list[Any] = []
        for item in left_seq:
            if _includes_deep(right_seq, item) and not _includes_deep(out_list, item):
                out_list.append(item)
        return out_list
    if op == "difference":
        _require_arity(op, args, 2)
        left_seq = _require_list_arg(op, args[0])
        right_seq = _require_list_arg(op, args[1])
        out_diff: list[Any] = []
        for item in left_seq:
            if not _includes_deep(right_seq, item) and not _includes_deep(out_diff, item):
                out_diff.append(item)
        return out_diff
    if op == "symmetric_difference":
        _require_arity(op, args, 2)
        left_seq = _require_list_arg(op, args[0])
        right_seq = _require_list_arg(op, args[1])
        out_sym: list[Any] = []
        for item in left_seq:
            if not _includes_deep(right_seq, item) and not _includes_deep(out_sym, item):
                out_sym.append(item)
        for item in right_seq:
            if not _includes_deep(left_seq, item) and not _includes_deep(out_sym, item):
                out_sym.append(item)
        return out_sym
    if op == "set_equals":
        _require_arity(op, args, 2)
        left_set = _distinct_deep(_require_list_arg(op, args[0]))
        right_set = _distinct_deep(_require_list_arg(op, args[1]))
        if len(left_set) != len(right_set):
            return False
        return all(_includes_deep(right_set, item) for item in left_set)
    if op == "contains_all":
        _require_arity(op, args, 2)
        container = _require_list_arg(op, args[0])
        required_items = _require_list_arg(op, args[1])
        return all(_includes_deep(container, item) for item in required_items)
    if op == "contains_any":
        _require_arity(op, args, 2)
        container = _require_list_arg(op, args[0])
        candidate = _require_list_arg(op, args[1])
        return any(_includes_deep(container, item) for item in candidate)
    if op == "is_subset":
        _require_arity(op, args, 2)
        left_set = _distinct_deep(_require_list_arg(op, args[0]))
        right_set = _distinct_deep(_require_list_arg(op, args[1]))
        return all(_includes_deep(right_set, item) for item in left_set)
    if op == "is_superset":
        _require_arity(op, args, 2)
        left_set = _distinct_deep(_require_list_arg(op, args[0]))
        right_set = _distinct_deep(_require_list_arg(op, args[1]))
        return all(_includes_deep(left_set, item) for item in right_set)
    if op == "json_parse":
        _require_arity(op, args, 1)
        raw = args[0]
        if not isinstance(raw, str):
            raise ValueError("spec_lang json_parse expects string input")
        return json.loads(raw)
    if op == "json_stringify":
        _require_arity(op, args, 1)
        return json.dumps(args[0], ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if op == "schema_match":
        _require_arity(op, args, 2)
        errs: list[str] = []
        _schema_validate(args[0], args[1], "$", errs)
        return not errs
    if op == "schema_errors":
        _require_arity(op, args, 2)
        errs = []
        _schema_validate(args[0], args[1], "$", errs)
        return errs
    if op == "ops.fs.path.normalize":
        _require_arity(op, args, 1)
        if not isinstance(args[0], str):
            raise ValueError("spec_lang ops.fs.path.normalize expects string path")
        return _fs_normalize_path(args[0])
    if op == "ops.fs.path.join":
        _require_arity(op, args, 2)
        if not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ValueError("spec_lang ops.fs.path.join expects string args")
        base = args[0]
        part = args[1]
        combined = f"{base.rstrip('/')}/{part}" if base else part
        return _fs_normalize_path(combined)
    if op == "ops.fs.path.split":
        _require_arity(op, args, 1)
        if not isinstance(args[0], str):
            raise ValueError("spec_lang ops.fs.path.split expects string path")
        return _fs_split_segments(args[0])
    if op == "ops.fs.path.dirname":
        _require_arity(op, args, 1)
        if not isinstance(args[0], str):
            raise ValueError("spec_lang ops.fs.path.dirname expects string path")
        return _fs_dirname(args[0])
    if op == "ops.fs.path.basename":
        _require_arity(op, args, 1)
        if not isinstance(args[0], str):
            raise ValueError("spec_lang ops.fs.path.basename expects string path")
        return _fs_basename(args[0])
    if op == "ops.fs.path.extname":
        _require_arity(op, args, 1)
        if not isinstance(args[0], str):
            raise ValueError("spec_lang ops.fs.path.extname expects string path")
        return _fs_extname(args[0])
    if op == "ops.fs.path.stem":
        _require_arity(op, args, 1)
        if not isinstance(args[0], str):
            raise ValueError("spec_lang ops.fs.path.stem expects string path")
        return _fs_stem(args[0])
    if op == "ops.fs.path.is_abs":
        _require_arity(op, args, 1)
        if not isinstance(args[0], str):
            raise ValueError("spec_lang ops.fs.path.is_abs expects string path")
        return _fs_normalize_path(args[0]).startswith("/")
    if op == "ops.fs.path.has_ext":
        _require_arity(op, args, 2)
        if not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ValueError("spec_lang ops.fs.path.has_ext expects string args")
        return _fs_extname(args[0]) == _fs_normalize_ext(args[1])
    if op == "ops.fs.path.change_ext":
        _require_arity(op, args, 2)
        if not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ValueError("spec_lang ops.fs.path.change_ext expects string args")
        normalized = _fs_normalize_path(args[0])
        new_ext = _fs_normalize_ext(args[1])
        base = _fs_basename(normalized)
        if base in {"", "."}:
            return normalized
        parent = _fs_dirname(normalized)
        stem = _fs_stem(normalized)
        next_base = f"{stem}{new_ext}"
        if parent == "/":
            return f"/{next_base}"
        if parent == ".":
            return next_base
        return f"{parent}/{next_base}"
    if op == "ops.fs.path.relativize":
        _require_arity(op, args, 2)
        if not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ValueError("spec_lang ops.fs.path.relativize expects string args")
        return _fs_relativize(args[0], args[1])
    if op == "ops.fs.path.common_prefix":
        _require_arity(op, args, 1)
        raw_paths = _require_list_arg(op, args[0])
        paths: list[str] = []
        for raw in raw_paths:
            if not isinstance(raw, str):
                raise ValueError("spec_lang ops.fs.path.common_prefix expects list of strings")
            paths.append(raw)
        return _fs_common_prefix(paths)
    if op == "ops.fs.path.parents":
        _require_arity(op, args, 1)
        if not isinstance(args[0], str):
            raise ValueError("spec_lang ops.fs.path.parents expects string path")
        return _fs_parents(args[0])
    if op == "ops.fs.path.within":
        _require_arity(op, args, 2)
        if not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ValueError("spec_lang ops.fs.path.within expects string args")
        return _fs_within(args[0], args[1])
    if op == "ops.fs.path.compare":
        _require_arity(op, args, 2)
        if not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ValueError("spec_lang ops.fs.path.compare expects string args")
        path_left = _fs_normalize_path(args[0])
        path_right = _fs_normalize_path(args[1])
        return -1 if path_left < path_right else (1 if path_left > path_right else 0)
    if op == "ops.fs.path.sort":
        _require_arity(op, args, 1)
        raw_paths = _require_list_arg(op, args[0])
        normalized_paths: list[str] = []
        for raw in raw_paths:
            if not isinstance(raw, str):
                raise ValueError("spec_lang ops.fs.path.sort expects list of strings")
            normalized_paths.append(_fs_normalize_path(raw))
        return sorted(normalized_paths)
    if op == "ops.fs.file.exists":
        _require_arity(op, args, 1)
        meta = _require_dict_arg(op, args[0])
        return bool(meta.get("exists"))
    if op == "ops.fs.file.is_file":
        _require_arity(op, args, 1)
        meta = _require_dict_arg(op, args[0])
        return str(meta.get("type", "")).strip() == "file"
    if op == "ops.fs.file.is_dir":
        _require_arity(op, args, 1)
        meta = _require_dict_arg(op, args[0])
        return str(meta.get("type", "")).strip() == "dir"
    if op == "ops.fs.file.size_bytes":
        _require_arity(op, args, 1)
        meta = _require_dict_arg(op, args[0])
        size = meta.get("size_bytes")
        if isinstance(size, int) and not isinstance(size, bool):
            return size
        return None
    if op == "ops.fs.file.path":
        _require_arity(op, args, 1)
        meta = _require_dict_arg(op, args[0])
        raw = meta.get("path")
        return raw if isinstance(raw, str) else None
    if op == "ops.fs.file.name":
        _require_arity(op, args, 1)
        meta = _require_dict_arg(op, args[0])
        raw = meta.get("path")
        if not isinstance(raw, str):
            return None
        return _fs_basename(raw)
    if op == "ops.fs.file.parent":
        _require_arity(op, args, 1)
        meta = _require_dict_arg(op, args[0])
        raw = meta.get("path")
        if not isinstance(raw, str):
            return None
        return _fs_dirname(raw)
    if op == "ops.fs.file.ext":
        _require_arity(op, args, 1)
        meta = _require_dict_arg(op, args[0])
        raw = meta.get("path")
        if not isinstance(raw, str):
            return None
        return _fs_extname(raw)
    if op == "ops.fs.file.get":
        _require_arity(op, args, 3)
        meta = _require_dict_arg(op, args[0])
        key = str(args[1])
        return meta.get(key, args[2])
    if op == "ops.fs.walk":
        _require_arity(op, args, 2)
        root_path = args[0]
        options = _require_dict_arg(op, args[1])
        if not isinstance(root_path, str) or not root_path.strip():
            raise ValueError("spec_lang ops.fs.walk expects non-empty root path")
        pattern = str(options.get("pattern", "*"))
        include_dirs = bool(options.get("include_dirs", False))
        relative = bool(options.get("relative", True))
        walk_root = Path(root_path)
        if not walk_root.exists():
            return []
        walk_rows: list[dict[str, Any]] = []
        for dirpath, dirnames, filenames in os.walk(walk_root):
            current = Path(dirpath)
            if include_dirs:
                for name in sorted(dirnames):
                    walk_candidate = current / name
                    rel = str(walk_candidate.relative_to(walk_root)) if relative else str(walk_candidate)
                    if fnmatch(rel, pattern):
                        walk_rows.append({"path": rel, "type": "dir", "exists": True})
            for name in sorted(filenames):
                walk_candidate = current / name
                rel = str(walk_candidate.relative_to(walk_root)) if relative else str(walk_candidate)
                if not fnmatch(rel, pattern):
                    continue
                size = walk_candidate.stat().st_size if walk_candidate.exists() else None
                walk_rows.append(
                    {
                        "path": rel,
                        "type": "file",
                        "exists": walk_candidate.exists(),
                        "size_bytes": int(size) if isinstance(size, int) else None,
                    }
                )
        return walk_rows
    if op == "ops.fs.file.set":
        _require_arity(op, args, 2)
        path, content = args
        if not isinstance(path, str) or not path.strip():
            raise ValueError("spec_lang ops.fs.file.set expects non-empty path")
        if not isinstance(content, str):
            raise ValueError("spec_lang ops.fs.file.set expects string content")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return True
    if op == "ops.fs.file.append":
        _require_arity(op, args, 2)
        path, content = args
        if not isinstance(path, str) or not path.strip():
            raise ValueError("spec_lang ops.fs.file.append expects non-empty path")
        if not isinstance(content, str):
            raise ValueError("spec_lang ops.fs.file.append expects string content")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(content)
        return True
    if op == "ops.fs.file.mkdir_p":
        _require_arity(op, args, 1)
        path = args[0]
        if not isinstance(path, str) or not path.strip():
            raise ValueError("spec_lang ops.fs.file.mkdir_p expects non-empty path")
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    if op == "ops.fs.file.remove":
        _require_arity(op, args, 1)
        path = args[0]
        if not isinstance(path, str) or not path.strip():
            raise ValueError("spec_lang ops.fs.file.remove expects non-empty path")
        target = Path(path)
        if not target.exists():
            return False
        if target.is_dir():
            raise ValueError("spec_lang ops.fs.file.remove expects file path, got directory")
        target.unlink()
        return True
    if op == "ops.fs.json.parse":
        _require_arity(op, args, 1)
        raw = args[0]
        if not isinstance(raw, str):
            raise ValueError("spec_lang ops.fs.json.parse expects string input")
        return json.loads(raw)
    if op == "ops.fs.json.get":
        _require_arity(op, args, 2)
        path = _require_list_arg(op, args[1])
        ok, value = _get_in_path(args[0], path)
        return value if ok else None
    if op == "ops.fs.json.get_or":
        _require_arity(op, args, 3)
        path = _require_list_arg(op, args[1])
        ok, value = _get_in_path(args[0], path)
        return value if ok else args[2]
    if op == "ops.fs.json.has_path":
        _require_arity(op, args, 2)
        path = _require_list_arg(op, args[1])
        ok, _ = _get_in_path(args[0], path)
        return ok
    if op == "ops.fs.yaml.parse":
        _require_arity(op, args, 1)
        raw = args[0]
        if not isinstance(raw, str):
            raise ValueError("spec_lang ops.fs.yaml.parse expects string input")
        return yaml.safe_load(raw)
    if op == "ops.fs.yaml.stringify":
        _require_arity(op, args, 1)
        return yaml.safe_dump(args[0], sort_keys=True)
    if op == "ops.fs.yaml.get":
        _require_arity(op, args, 2)
        path = _require_list_arg(op, args[1])
        ok, value = _get_in_path(args[0], path)
        return value if ok else None
    if op == "ops.fs.yaml.get_or":
        _require_arity(op, args, 3)
        path = _require_list_arg(op, args[1])
        ok, value = _get_in_path(args[0], path)
        return value if ok else args[2]
    if op == "ops.fs.yaml.has_path":
        _require_arity(op, args, 2)
        path = _require_list_arg(op, args[1])
        ok, _ = _get_in_path(args[0], path)
        return ok
    if op == "ops.fs.glob.match":
        _require_arity(op, args, 2)
        if not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ValueError("spec_lang ops.fs.glob.match expects string args")
        return fnmatch(args[0], args[1])
    if op == "ops.fs.glob.filter":
        _require_arity(op, args, 2)
        paths = _require_list_arg(op, args[0])
        pattern = args[1]
        if not isinstance(pattern, str):
            raise ValueError("spec_lang ops.fs.glob.filter expects string pattern")
        matched_paths: list[str] = []
        for raw in paths:
            if not isinstance(raw, str):
                raise ValueError("spec_lang ops.fs.glob.filter expects list of strings")
            if fnmatch(raw, pattern):
                matched_paths.append(raw)
        return matched_paths
    if op == "ops.fs.glob.any":
        _require_arity(op, args, 2)
        paths = _require_list_arg(op, args[0])
        pattern = args[1]
        if not isinstance(pattern, str):
            raise ValueError("spec_lang ops.fs.glob.any expects string pattern")
        for raw in paths:
            if not isinstance(raw, str):
                raise ValueError("spec_lang ops.fs.glob.any expects list of strings")
            if fnmatch(raw, pattern):
                return True
        return False
    if op == "ops.fs.glob.all":
        _require_arity(op, args, 2)
        paths = _require_list_arg(op, args[0])
        pattern = args[1]
        if not isinstance(pattern, str):
            raise ValueError("spec_lang ops.fs.glob.all expects string pattern")
        for raw in paths:
            if not isinstance(raw, str):
                raise ValueError("spec_lang ops.fs.glob.all expects list of strings")
            if not fnmatch(raw, pattern):
                return False
        return True
    if op == "ops.os.exec":
        _require_arity(op, args, 2)
        _require_ops_os_capability(op, st)
        cmd = _coerce_exec_command(op, args[0])
        timeout_ms = _require_int_arg(op, args[1])
        if timeout_ms < 0:
            raise ValueError("spec_lang ops.os.exec expects non-negative timeout_ms")
        started = time.perf_counter()
        timed_out = False
        code = -1
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=(timeout_ms / 1000.0) if timeout_ms > 0 else None,
            )
            code = int(proc.returncode)
        except subprocess.TimeoutExpired:
            timed_out = True
            code = -9
        st.last_exit_code = int(code)
        _ = int((time.perf_counter() - started) * 1000.0)
        if timed_out:
            return code
        return code
    if op == "ops.os.exec_capture":
        _require_arity(op, args, 2)
        _require_ops_os_capability(op, st)
        cmd = _coerce_exec_command(op, args[0])
        timeout_ms = _require_int_arg(op, args[1])
        if timeout_ms < 0:
            raise ValueError("spec_lang ops.os.exec_capture expects non-negative timeout_ms")
        started = time.perf_counter()
        code = -1
        stdout = ""
        stderr = ""
        timed_out = False
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=(timeout_ms / 1000.0) if timeout_ms > 0 else None,
            )
            code = int(proc.returncode)
            stdout = str(proc.stdout or "")
            stderr = str(proc.stderr or "")
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            code = -9
            stdout = str(exc.stdout or "")
            stderr = str(exc.stderr or "")
        duration_ms = int((time.perf_counter() - started) * 1000.0)
        st.last_exit_code = int(code)
        return {
            "code": int(code),
            "stdout": stdout,
            "stderr": stderr,
            "duration_ms": duration_ms,
            "timed_out": bool(timed_out),
        }
    if op == "ops.os.exec_capture_ex":
        _require_arity(op, args, 2)
        _require_ops_os_capability(op, st)
        cmd = _coerce_exec_command(op, args[0])
        options = _require_dict_arg(op, args[1])
        timeout_raw = options.get("timeout_ms", 0)
        timeout_ms = _require_int_arg(op, timeout_raw)
        if timeout_ms < 0:
            raise ValueError("spec_lang ops.os.exec_capture_ex expects non-negative timeout_ms")
        cwd = options.get("cwd")
        if cwd is not None and not isinstance(cwd, str):
            raise ValueError("spec_lang ops.os.exec_capture_ex expects cwd string when provided")
        stdin_text = options.get("stdin_text", "")
        if stdin_text is not None and not isinstance(stdin_text, str):
            raise ValueError("spec_lang ops.os.exec_capture_ex expects stdin_text string when provided")
        proc_env = os.environ.copy()
        extra_env = options.get("env")
        if extra_env is not None:
            if not isinstance(extra_env, dict):
                raise ValueError("spec_lang ops.os.exec_capture_ex expects env mapping when provided")
            for k, v in extra_env.items():
                key = str(k).strip()
                if key:
                    proc_env[key] = "" if v is None else str(v)
        started = time.perf_counter()
        code = -1
        stdout = ""
        stderr = ""
        timed_out = False
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                input=stdin_text if isinstance(stdin_text, str) else None,
                check=False,
                cwd=cwd if isinstance(cwd, str) and cwd.strip() else None,
                env=proc_env,
                timeout=(timeout_ms / 1000.0) if timeout_ms > 0 else None,
            )
            code = int(proc.returncode)
            stdout = str(proc.stdout or "")
            stderr = str(proc.stderr or "")
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            code = -9
            stdout = str(exc.stdout or "")
            stderr = str(exc.stderr or "")
        duration_ms = int((time.perf_counter() - started) * 1000.0)
        st.last_exit_code = int(code)
        return {
            "code": int(code),
            "stdout": stdout,
            "stderr": stderr,
            "duration_ms": duration_ms,
            "timed_out": bool(timed_out),
        }
    if op == "ops.os.env_get":
        _require_arity(op, args, 2)
        _require_ops_os_capability(op, st)
        key = str(args[0]).strip()
        if not key:
            raise ValueError("spec_lang ops.os.env_get expects non-empty env key")
        default = args[1]
        return os.environ.get(key, default)
    if op == "ops.os.env_has":
        _require_arity(op, args, 1)
        _require_ops_os_capability(op, st)
        key = str(args[0]).strip()
        if not key:
            raise ValueError("spec_lang ops.os.env_has expects non-empty env key")
        return key in os.environ
    if op == "ops.os.cwd":
        _require_arity(op, args, 0)
        _require_ops_os_capability(op, st)
        return os.getcwd()
    if op == "ops.os.pid":
        _require_arity(op, args, 0)
        _require_ops_os_capability(op, st)
        return int(os.getpid())
    if op == "ops.os.sleep_ms":
        _require_arity(op, args, 1)
        _require_ops_os_capability(op, st)
        delay_ms = _require_int_arg(op, args[0])
        if delay_ms < 0:
            raise ValueError("spec_lang ops.os.sleep_ms expects non-negative delay")
        time.sleep(delay_ms / 1000.0)
        return True
    if op == "ops.os.exit_code":
        _require_arity(op, args, 0)
        _require_ops_os_capability(op, st)
        return st.last_exit_code
    if op == "ops.helper.call":
        _require_arity(op, args, 2)
        _require_capability(op, st, "ops.helper")
        helper_id = args[0]
        if not isinstance(helper_id, str) or not helper_id.strip():
            raise ValueError("ops.helper.call expects string helper_id")
        return _run_helper_call(helper_id.strip(), args[1])
    if op == "ops.job.dispatch":
        _require_min_arity(op, args, 1)
        _require_capability(op, st, "ops.job")
        if st.dispatch_depth > 0:
            raise ValueError("runtime.dispatch.nested_forbidden: ops.job.dispatch")
        job_name = args[0]
        if not isinstance(job_name, str) or not job_name.strip():
            raise ValueError("ops.job.dispatch expects job_name to evaluate to string")
        jobs = _load_json_env_mapping("SPEC_RUNNER_SPEC_LANG_JOBS_JSON")
        entry = jobs.get(job_name.strip())
        if not isinstance(entry, dict):
            raise ValueError(f"runtime.dispatch.job_not_found: {job_name.strip()}")
        helper_id = str(entry.get("helper", "")).strip()
        if not helper_id:
            raise ValueError(f"runtime.dispatch.helper_required: {job_name.strip()}")
        inputs = entry.get("inputs", {})
        if not isinstance(inputs, dict):
            raise ValueError(f"runtime.dispatch.inputs_must_be_mapping: {job_name.strip()}")
        merged: dict[str, Any] = dict(inputs)
        raw_overrides = str(os.environ.get("SPEC_RUNNER_JOB_INPUT_OVERRIDES_JSON", "")).strip()
        if raw_overrides:
            try:
                parsed_overrides = json.loads(raw_overrides)
            except json.JSONDecodeError as exc:
                raise ValueError("SPEC_RUNNER_JOB_INPUT_OVERRIDES_JSON must be valid JSON mapping") from exc
            if isinstance(parsed_overrides, dict):
                merged.update(parsed_overrides)
        if len(args) > 1:
            overrides = args[1]
            if overrides is not None and not isinstance(overrides, dict):
                raise ValueError("ops.job.dispatch overrides must evaluate to mapping or null")
            if isinstance(overrides, dict):
                merged.update(overrides)
        merged["_job_name"] = job_name.strip()
        merged["_mode"] = str(entry.get("mode", "custom"))
        merged["_outputs"] = entry.get("outputs", {})
        st.dispatch_depth += 1
        try:
            result = _run_helper_call(helper_id, merged)
        finally:
            st.dispatch_depth -= 1
        st.last_dispatch_result = result
        return result
    if op == "and":
        _require_arity(op, args, 2)
        return _truthy(args[0]) and _truthy(args[1])
    if op == "or":
        _require_arity(op, args, 2)
        return _truthy(args[0]) or _truthy(args[1])
    if op == "not":
        _require_arity(op, args, 1)
        return not _truthy(args[0])
    raise ValueError(f"unsupported spec_lang symbol: {op}")


def _eval_builtin(op: str, args: list[Any], env: _Env, st: _EvalState) -> Any:
    op = _flat_symbol_for_runtime(op)
    if op == "var":
        _require_arity(op, args, 1)
        name = args[0]
        if not isinstance(name, str) or not name.strip():
            raise ValueError("spec_lang var requires non-empty string name")
        key = name.strip()
        try:
            return env.lookup(key)
        except ValueError:
            if key in _BUILTIN_ARITY:
                return _BuiltinFn(key, _BUILTIN_ARITY[key])
            raise

    if op == "and":
        _require_min_arity(op, args, 1)
        for a in args:
            if not _truthy(_eval_non_tail(a, env, st)):
                return False
        return True

    if op == "or":
        _require_min_arity(op, args, 1)
        for a in args:
            if _truthy(_eval_non_tail(a, env, st)):
                return True
        return False

    if op == "not":
        _require_arity(op, args, 1)
        return not _truthy(_eval_non_tail(args[0], env, st))

    if op in {"contains", "starts_with", "ends_with", "json_type", "has_key"}:
        if len(args) == 1:
            eval_args = [st.subject, _eval_non_tail(args[0], env, st)]
        elif len(args) == 2:
            eval_args = [_eval_non_tail(args[0], env, st), _eval_non_tail(args[1], env, st)]
        else:
            raise ValueError(f"spec_lang arity error for {op}")
        return _eval_builtin_eager(op, eval_args, st)

    if op == "split":
        if len(args) == 1:
            text = _eval_non_tail(args[0], env, st)
            return str(text).split()
        if len(args) == 2:
            eval_args = [_eval_non_tail(args[0], env, st), _eval_non_tail(args[1], env, st)]
            return _eval_builtin_eager(op, eval_args, st)
        raise ValueError("spec_lang arity error for split")

    if op == "coalesce":
        _require_min_arity(op, args, 1)
        for a in args:
            got = _eval_non_tail(a, env, st)
            if got is None:
                continue
            if isinstance(got, str) and got == "":
                continue
            return got
        return None
    if op == "default_to":
        _require_arity(op, args, 2)
        default_value = _eval_non_tail(args[0], env, st)
        got = _eval_non_tail(args[1], env, st)
        if got is None:
            return default_value
        if isinstance(got, str) and got == "":
            return default_value
        return got

    if op in {"map", "filter", "reject", "find", "partition", "group_by", "uniq_by", "reduce"}:
        _require_arity(op, args, 2 if op != "reduce" else 3)
        if op == "reduce":
            fn_val = _eval_non_tail(args[0], env, st)
            acc = _eval_non_tail(args[1], env, st)
            seq = _eval_non_tail(args[2], env, st)
            seq = _require_list_arg(op, seq)
            for item in seq:
                acc = _eval_callable_like(fn_val, [acc, item], st)
            return acc

        fn_val = _eval_non_tail(args[0], env, st)
        seq = _eval_non_tail(args[1], env, st)
        seq = _require_list_arg(op, seq)

        if op == "map":
            return [_eval_callable_like(fn_val, [item], st) for item in seq]
        if op == "filter":
            return [item for item in seq if _truthy(_eval_callable_like(fn_val, [item], st))]
        if op == "reject":
            return [item for item in seq if not _truthy(_eval_callable_like(fn_val, [item], st))]
        if op == "find":
            for item in seq:
                if _truthy(_eval_callable_like(fn_val, [item], st)):
                    return item
            return None
        if op == "partition":
            yes: list[Any] = []
            no: list[Any] = []
            for item in seq:
                if _truthy(_eval_callable_like(fn_val, [item], st)):
                    yes.append(item)
                else:
                    no.append(item)
            return [yes, no]
        if op == "group_by":
            grouped: dict[str, list[Any]] = {}
            for item in seq:
                key = str(_eval_callable_like(fn_val, [item], st))
                grouped.setdefault(key, []).append(item)
            return grouped
        if op == "uniq_by":
            out: list[Any] = []
            seen: list[Any] = []
            for item in seq:
                marker = _eval_callable_like(fn_val, [item], st)
                if not _includes_deep(seen, marker):
                    seen.append(marker)
                    out.append(item)
            return out
        if op == "sort_by":
            return sorted(seq, key=lambda item: _eval_callable_like(fn_val, [item], st))

    if op == "zip_with":
        _require_arity(op, args, 3)
        fn_val = _eval_non_tail(args[0], env, st)
        left = _require_list_arg(op, _eval_non_tail(args[1], env, st))
        right = _require_list_arg(op, _eval_non_tail(args[2], env, st))
        return [_eval_callable_like(fn_val, [a, b], st) for a, b in zip(left, right)]

    if op == "where":
        _require_arity(op, args, 2)
        spec_map = _require_dict_arg(op, _eval_non_tail(args[0], env, st))
        obj = _require_dict_arg(op, _eval_non_tail(args[1], env, st))
        for key, predicate in spec_map.items():
            actual = obj.get(str(key))
            if _is_callable_like(predicate):
                if not _truthy(_eval_callable_like(predicate, [actual], st)):
                    return False
                continue
            if not _deep_equals(actual, predicate):
                return False
        return True

    if op == "compose":
        _require_arity(op, args, 3)
        f = _eval_non_tail(args[0], env, st)
        g = _eval_non_tail(args[1], env, st)
        x = _eval_non_tail(args[2], env, st)
        gx = _eval_callable_like(g, [x], st)
        return _eval_callable_like(f, [gx], st)

    if op == "pipe":
        _require_arity(op, args, 3)
        f = _eval_non_tail(args[0], env, st)
        g = _eval_non_tail(args[1], env, st)
        x = _eval_non_tail(args[2], env, st)
        fx = _eval_callable_like(f, [x], st)
        return _eval_callable_like(g, [fx], st)

    if op == "sort_by":
        _require_arity(op, args, 2)
        seq = _eval_non_tail(args[0], env, st)
        key = _eval_non_tail(args[1], env, st)
        seq = _require_list_arg(op, seq)
        if isinstance(key, str):
            return sorted(seq, key=lambda item: str(item.get(key)) if isinstance(item, dict) else str(item))
        return sorted(seq, key=lambda item: _eval_callable_like(key, [item], st))

    eval_args = [_eval_non_tail(a, env, st) for a in args]
    return _eval_builtin_eager(op, eval_args, st)


def _eval_tail(expr: Any, env: _Env, st: _EvalState) -> Any:
    current_expr = expr
    current_env = env
    while True:
        st.tick()
        if isinstance(current_expr, (str, int, float, bool)) or current_expr is None:
            return current_expr
        if isinstance(current_expr, dict):
            out: dict[str, Any] = {}
            for k, v in current_expr.items():
                out[str(k)] = _eval_non_tail(v, current_env, st)
            return out
        if not isinstance(current_expr, list):
            raise ValueError("spec_lang expression must be list-based s-expr or scalar literal")
        if len(current_expr) == 0:
            raise ValueError("spec_lang expression list must not be empty")
        head = current_expr[0]
        if not isinstance(head, str):
            return [_eval_non_tail(item, current_env, st) for item in current_expr]
        if not head:
            raise ValueError("spec_lang expression head must be non-empty string symbol")
        op = _resolve_op_symbol(head, st.imports)
        args = list(current_expr[1:])

        if op == "if":
            _require_arity(op, args, 3)
            cond = _eval_non_tail(args[0], current_env, st)
            current_expr = args[1] if _truthy(cond) else args[2]
            continue
        if op == "lit":
            _require_arity(op, args, 1)
            return args[0]

        if op == "let":
            _require_arity(op, args, 2)
            raw_bindings = args[0]
            body = args[1]
            if not isinstance(raw_bindings, list):
                raise ValueError("spec_lang let bindings must be a list")
            slots: dict[str, Any] = {}
            next_env = _Env(vars=slots, parent=current_env)
            pairs: list[tuple[str, Any]] = []
            for b in raw_bindings:
                if not isinstance(b, list) or len(b) != 2:
                    raise ValueError("spec_lang let binding must be [name, expr]")
                name = b[0]
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("spec_lang let binding name must be non-empty string")
                key = name.strip()
                if key in slots:
                    raise ValueError(f"duplicate let binding: {key}")
                slots[key] = _UNSET
                pairs.append((key, b[1]))
            for key, rhs in pairs:
                slots[key] = _eval_non_tail(rhs, next_env, st)
            current_expr = body
            current_env = next_env
            continue

        if op == "fn":
            _require_arity(op, args, 2)
            raw_params = args[0]
            body = args[1]
            if not isinstance(raw_params, list):
                raise ValueError("spec_lang fn params must be a list")
            params: list[str] = []
            seen: set[str] = set()
            for p in raw_params:
                if not isinstance(p, str) or not p.strip():
                    raise ValueError("spec_lang fn param must be non-empty string")
                key = p.strip()
                if key in seen:
                    raise ValueError(f"duplicate fn param: {key}")
                seen.add(key)
                params.append(key)
            return _Closure(params=tuple(params), body=body, env=current_env)

        if op == "call":
            _require_min_arity(op, args, 1)
            fn_val = _eval_non_tail(args[0], current_env, st)
            eval_args = [_eval_non_tail(a, current_env, st) for a in args[1:]]
            if isinstance(fn_val, _Closure):
                if len(eval_args) != len(fn_val.params):
                    raise ValueError("spec_lang call argument count mismatch")
                current_env = _Env(
                    vars={k: v for k, v in zip(fn_val.params, eval_args)},
                    parent=fn_val.env,
                )
                current_expr = fn_val.body
                continue
            return _eval_callable_like(fn_val, eval_args, st)

        return _eval_builtin(op, args, current_env, st)


def compile_symbol_bindings(
    bindings: Mapping[str, Any],
    *,
    limits: SpecLangLimits | None = None,
) -> dict[str, Any]:
    cfg = limits or SpecLangLimits()
    st = _EvalState(subject=None, limits=cfg, imports={}, started=time.perf_counter())
    slots: dict[str, Any] = {}
    env = _Env(vars=slots, parent=None)
    for raw_name in bindings:
        name = str(raw_name).strip()
        if not name:
            raise ValueError("spec_lang symbol binding name must be non-empty")
        if name in slots:
            raise ValueError(f"duplicate symbol binding: {name}")
        slots[name] = _UNSET
    for raw_name, raw_expr in bindings.items():
        name = str(raw_name).strip()
        validate_expr_shape(raw_expr, limits=cfg)
        slots[name] = _eval_non_tail(raw_expr, env, st)
    return dict(slots)


def eval_expr(
    expr: Any,
    *,
    subject: Any,
    limits: SpecLangLimits | None = None,
    symbols: Mapping[str, Any] | None = None,
    imports: Mapping[str, str] | None = None,
    capabilities: set[str] | frozenset[str] | None = None,
) -> Any:
    cfg = limits or SpecLangLimits()
    validate_expr_shape(expr, limits=cfg)
    if not _is_json_value(subject):
        raise ValueError("spec_lang subject must be a JSON value")
    resolved_imports: dict[str, str] = {}
    if imports:
        for raw_name, raw_symbol in imports.items():
            name = str(raw_name).strip()
            symbol = str(raw_symbol).strip()
            if not name or not symbol:
                raise ValueError("spec_lang imports must use non-empty string names and symbols")
            if name in SPECIAL_FORMS:
                raise ValueError(f"spec_lang imports cannot shadow special form: {name}")
            if symbol not in _BUILTIN_ARITY:
                raise ValueError(f"spec_lang imports unknown symbol: {symbol}")
            resolved_imports[name] = symbol

    st = _EvalState(
        subject=subject,
        limits=cfg,
        imports=resolved_imports,
        capabilities=frozenset(str(x).strip() for x in (capabilities or set()) if str(x).strip()),
        started=time.perf_counter(),
    )
    root_symbols: dict[str, Any] = {}
    if symbols:
        for raw_name, value in symbols.items():
            name = str(raw_name).strip()
            if not name:
                raise ValueError("spec_lang symbol name must be non-empty")
            root_symbols[name] = value
    for local_name, canonical_symbol in resolved_imports.items():
        root_symbols[local_name] = _BuiltinFn(canonical_symbol, _BUILTIN_ARITY[canonical_symbol])
    return _eval_tail(expr, _Env(vars=root_symbols, parent=None), st)


def eval_predicate(
    expr: Any,
    *,
    subject: Any,
    limits: SpecLangLimits | None = None,
    symbols: Mapping[str, Any] | None = None,
    imports: Mapping[str, str] | None = None,
    capabilities: set[str] | frozenset[str] | None = None,
) -> bool:
    got = eval_expr(
        expr,
        subject=subject,
        limits=limits,
        symbols=symbols,
        imports=imports,
        capabilities=capabilities,
    )
    return bool(got)


def limits_from_harness(harness: Mapping[str, Any] | None) -> SpecLangLimits:
    cfg = dict((harness or {}).get("spec_lang") or {})
    if not cfg:
        return SpecLangLimits()
    if not isinstance(cfg, dict):
        raise TypeError("harness.spec_lang must be a mapping")

    def _int_field(name: str, *, min_value: int) -> int:
        raw = cfg.get(name)
        if raw is None:
            return getattr(SpecLangLimits(), name)
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise TypeError(f"harness.spec_lang.{name} must be an integer")
        if raw < min_value:
            raise ValueError(f"harness.spec_lang.{name} must be >= {min_value}")
        return raw

    return SpecLangLimits(
        max_steps=_int_field("max_steps", min_value=1),
        max_nodes=_int_field("max_nodes", min_value=1),
        max_literal_bytes=_int_field("max_literal_bytes", min_value=1),
        timeout_ms=_int_field("timeout_ms", min_value=0),
    )


def capabilities_from_harness(harness: Mapping[str, Any] | None) -> frozenset[str]:
    raw_spec_lang = (harness or {}).get("spec_lang") or {}
    if not isinstance(raw_spec_lang, Mapping):
        raise TypeError("harness.spec_lang must be a mapping")
    raw_caps = raw_spec_lang.get("capabilities") or []
    if raw_caps is None:
        return frozenset()
    if not isinstance(raw_caps, list):
        raise TypeError("harness.spec_lang.capabilities must be a list")
    caps: set[str] = set()
    for idx, raw in enumerate(raw_caps):
        cap = str(raw).strip()
        if not cap:
            raise ValueError(f"harness.spec_lang.capabilities[{idx}] must be a non-empty string")
        caps.add(cap)
    return frozenset(caps)
