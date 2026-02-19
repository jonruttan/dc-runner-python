from __future__ import annotations

import os
from typing import Any, Mapping


def _to_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, list):
        return [_to_json_value(v) for v in value]
    if isinstance(value, tuple):
        return [_to_json_value(v) for v in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            out[str(k)] = _to_json_value(v)
        return out
    return str(value)


def build_meta_subject(
    *,
    case: Any,
    ctx: Any,
    case_key: str,
    harness: Mapping[str, Any],
    artifacts: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    chain_payload = dict(ctx.get_case_chain_payload(case_key=case_key))
    sanitized_harness = {str(k): v for k, v in harness.items() if str(k) != "_chain_imports"}
    doc_path = getattr(case, "doc_path", None)
    if doc_path is not None and hasattr(doc_path, "as_posix"):
        doc_path_value = str(doc_path.as_posix())
    else:
        doc_path_value = str(doc_path or "")
    return {
        "case": {
            "id": str(getattr(case, "id", "")),
            "type": str(getattr(case, "type", "")),
            "title": getattr(case, "title", None),
            "doc_path": doc_path_value,
            "metadata": _to_json_value(getattr(case, "metadata", {})),
            "raw": _to_json_value(getattr(case, "raw_case", {})),
        },
        "harness": _to_json_value(sanitized_harness),
        "runtime": {
            "impl": str(os.environ.get("SPEC_RUNNER_IMPL", "unknown")),
            "profile_enabled": bool(getattr(ctx, "profile_enabled", False)),
            "chain_trace_count": len(getattr(ctx, "chain_trace", []) or []),
            "profile_row_count": len(getattr(ctx, "profile_rows", []) or []),
            "tmp_path": str(getattr(getattr(ctx, "tmp_path", None), "as_posix", lambda: "")()),
        },
        "chain": _to_json_value(chain_payload),
        "artifacts": {
            "target_keys": sorted(str(k) for k in (artifacts or {}).keys()),
        },
    }
