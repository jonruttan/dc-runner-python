from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from spec_runner.virtual_paths import ExternalRef, VirtualPathError, parse_external_ref


ExternalResolver = Callable[[ExternalRef, dict[str, Any]], Path]


def _as_non_empty_strings(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    out: set[str] = set()
    for item in value:
        if isinstance(item, str) and item.strip():
            out.add(item.strip())
    return out


def is_external_ref_allowed(
    raw: str,
    *,
    harness: dict[str, Any] | None,
    requires: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    ext = parse_external_ref(raw)
    if ext is None:
        return True, None

    spec_lang_cfg = dict((harness or {}).get("spec_lang") or {})
    cfg = dict(spec_lang_cfg.get("references") or {})
    mode = str(cfg.get("mode", "deny")).strip().lower() or "deny"
    if mode != "allow":
        return False, f"external ref denied by policy (harness.spec_lang.references.mode={mode!r})"

    caps = _as_non_empty_strings(dict(requires or {}).get("capabilities"))
    if "external.ref.v1" not in caps:
        return False, "external ref requires capabilities including external.ref.v1"

    allowed = _as_non_empty_strings(cfg.get("providers"))
    if ext.provider not in allowed:
        return False, f"external provider not allowlisted: {ext.provider}"
    return True, None


def resolve_external_ref(
    raw: str,
    *,
    harness: dict[str, Any] | None,
    requires: dict[str, Any] | None,
    registry: dict[str, ExternalResolver] | None = None,
) -> Path:
    ext = parse_external_ref(raw)
    if ext is None:
        raise VirtualPathError("resolve_external_ref called with non-external ref")

    ok, reason = is_external_ref_allowed(raw, harness=harness, requires=requires)
    if not ok:
        raise VirtualPathError(reason or "external ref denied")

    resolvers = dict(registry or {})
    resolver = resolvers.get(ext.provider)
    if resolver is None:
        raise VirtualPathError(f"no resolver registered for external provider: {ext.provider}")

    spec_lang_cfg = dict((harness or {}).get("spec_lang") or {})
    rules = dict((dict(spec_lang_cfg.get("references") or {}).get("rules") or {}))
    return resolver(ext, rules)
