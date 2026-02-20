from __future__ import annotations

from typing import Any


def is_governance_case_payload(case_payload: dict[str, Any]) -> bool:
    from spec_runner import governance_runtime as legacy

    return bool(legacy._is_governance_case_payload(case_payload))


def governance_check_id(case_payload: dict[str, Any]) -> str:
    from spec_runner import governance_runtime as legacy

    return str(legacy._governance_check_id(case_payload))


def run_governance_check(case, *, ctx) -> None:
    from spec_runner import governance_runtime as legacy

    legacy.run_governance_check(case, ctx=ctx)
