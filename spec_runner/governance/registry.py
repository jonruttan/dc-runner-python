from __future__ import annotations

from collections import defaultdict

from spec_runner.governance.types import GovernanceCheckMap, infer_check_domain


def all_checks() -> GovernanceCheckMap:
    from spec_runner import governance_runtime as legacy

    return dict(legacy._CHECKS)


def get_check(check_id: str):
    return all_checks().get(str(check_id).strip())


def check_ids() -> list[str]:
    return sorted(all_checks().keys())


def checks_by_domain() -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = defaultdict(dict)
    for check_id, fn in all_checks().items():
        grouped[infer_check_domain(check_id)][check_id] = fn
    return dict(grouped)


def checks_for_prefix(prefixes: tuple[str, ...]) -> GovernanceCheckMap:
    raw = all_checks()
    if not prefixes:
        return raw
    selected: GovernanceCheckMap = {}
    for cid, fn in raw.items():
        if any(cid.startswith(pre) for pre in prefixes):
            selected[cid] = fn
    return selected
