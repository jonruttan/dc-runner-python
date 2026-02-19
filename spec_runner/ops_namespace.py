from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")


@dataclass(frozen=True)
class OpsSymbol:
    raw: str
    segments: tuple[str, ...]

    @property
    def depth(self) -> int:
        return len(self.segments)


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str


def is_legacy_underscore_form(symbol: str) -> bool:
    s = str(symbol).strip()
    if not s.startswith("ops."):
        return False
    # Legacy shorthand forms being hard-cut.
    return s in {
        "ops.read_file",
        "ops.write_file",
        "ops.list_dir",
        "ops.path_exists",
        "ops.now_utc",
        "ops.exec",
        "ops.fs.read_file",
        "ops.fs.write_file",
        "ops.fs.list_dir",
        "ops.fs.path_exists",
        "ops.time.now_utc",
        "ops.proc.exec",
    }


def parse_ops_symbol(symbol: str) -> OpsSymbol:
    s = str(symbol).strip()
    if not s:
        raise ValueError("ops symbol must be a non-empty string")
    if not s.startswith("ops."):
        raise ValueError("ops symbol must start with 'ops.'")
    parts = s.split(".")
    if len(parts) < 3:
        raise ValueError("ops symbol must have at least three segments: ops.<...>")
    if any(not p for p in parts):
        raise ValueError("ops symbol must not contain empty segments")
    for idx, seg in enumerate(parts):
        if idx == 0:
            continue
        if not _SEGMENT_RE.match(seg):
            raise ValueError(f"ops symbol segment must match [a-z0-9_]+: {seg}")
    return OpsSymbol(raw=s, segments=tuple(parts))


def validate_ops_symbol(symbol: str, *, context: str) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    s = str(symbol).strip()
    try:
        parse_ops_symbol(s)
    except ValueError as exc:
        diags.append(
            Diagnostic(
                code="ORCHESTRATION_OPS_DEEP_DOT_REQUIRED",
                message=f"{context}: {exc}",
            )
        )
        return diags

    if is_legacy_underscore_form(s):
        diags.append(
            Diagnostic(
                code="ORCHESTRATION_OPS_UNDERSCORE_LEGACY_FORBIDDEN",
                message=f"{context}: legacy underscore-form op is forbidden: {s}",
            )
        )
    return diags


def normalize_ops_symbol(symbol: str) -> str:
    return parse_ops_symbol(symbol).raw


def validate_registry_entry(entry: dict[str, Any], *, where: str) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    effect_symbol = str(entry.get("effect_symbol", "")).strip()
    if not effect_symbol:
        diags.append(
            Diagnostic(
                code="ORCHESTRATION_OPS_REGISTRY_DECLARED_REQUIRED",
                message=f"{where}: missing effect_symbol",
            )
        )
    else:
        diags.extend(validate_ops_symbol(effect_symbol, context=f"{where}.effect_symbol"))

    capability_id = str(entry.get("capability_id", "")).strip()
    if not capability_id:
        diags.append(
            Diagnostic(
                code="ORCHESTRATION_OPS_CAPABILITY_BINDING_REQUIRED",
                message=f"{where}: missing capability_id",
            )
        )
    return diags
