from __future__ import annotations

from typing import Any


def normalize_case_domain(raw: object) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise TypeError("domain must be a non-empty string when provided")
    value = raw.strip()
    if not value:
        raise ValueError("domain must be a non-empty string when provided")
    return value


def normalize_export_symbol(domain: str | None, raw_as: str) -> str:
    name = str(raw_as).strip()
    if not name:
        raise ValueError("harness.exports[].as must be a non-empty string")
    if not domain:
        return name
    prefix = f"{domain}."
    if name.startswith(prefix):
        return name
    return f"{prefix}{name}"


def normalize_export_entries(case: dict[str, Any]) -> list[dict[str, Any]]:
    harness = case.get("harness")
    exports = harness.get("exports") if isinstance(harness, dict) else None
    if not isinstance(exports, list):
        return []
    domain = normalize_case_domain(case.get("domain"))
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(exports):
        if not isinstance(item, dict):
            raise TypeError(f"harness.exports[{idx}] must be mapping")
        raw_as = item.get("as")
        if not isinstance(raw_as, str) or not raw_as.strip():
            raise ValueError(f"harness.exports[{idx}].as must be non-empty")
        out = dict(item)
        out["raw_as"] = raw_as.strip()
        out["canonical_as"] = normalize_export_symbol(domain, raw_as)
        normalized.append(out)
    return normalized
