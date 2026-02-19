from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping

from spec_runner.spec_lang import eval_expr
from spec_runner.spec_lang_yaml_ast import SpecLangYamlAstError, compile_yaml_expr_to_sexpr

_HOOK_KEYS = ("must", "may", "must_not", "fail", "complete")


@dataclass(frozen=True)
class HookClauseContext:
    index: int
    id: str | None
    class_name: str
    assert_path: str
    target: str | None


@dataclass(frozen=True)
class HookTotals:
    passed_clauses: int
    failed_clauses: int
    must_passed: int
    may_passed: int
    must_not_passed: int


def parse_on_hooks(*, raw_case: Mapping[str, Any]) -> dict[str, list[Any]]:
    harness = raw_case.get("harness")
    if isinstance(harness, Mapping):
        if "on" in harness:
            raise ValueError("when.harness_on_forbidden: harness.on is not supported; use case.when")
        if "when" in harness:
            raise ValueError("when.harness_when_forbidden: harness.when is not supported; use case.when")
    elif harness is not None:
        raise ValueError("when.invalid_shape: harness must be a mapping when present")
    raw_when = raw_case.get("when")
    if raw_when is None:
        return {}
    if not isinstance(raw_when, Mapping):
        raise ValueError("when.invalid_shape: when must be a mapping")
    out: dict[str, list[Any]] = {}
    for raw_key, raw_list in raw_when.items():
        key = str(raw_key).strip()
        if key not in _HOOK_KEYS:
            raise ValueError(f"when.unknown_key: {key}")
        if not isinstance(raw_list, list) or not raw_list:
            raise ValueError(f"when.invalid_shape: when.{key} must be a non-empty list")
        compiled: list[Any] = []
        for idx, expr in enumerate(raw_list):
            if not isinstance(expr, Mapping):
                raise ValueError(f"when.expr_invalid: when.{key}[{idx}] must be mapping expression")
            try:
                compiled.append(compile_yaml_expr_to_sexpr(expr, field_path=f"when.{key}[{idx}]"))
            except SpecLangYamlAstError as exc:
                raise ValueError(f"when.expr_invalid: {exc}") from exc
        out[key] = compiled
    return out


def build_hook_event_envelope(
    *,
    event: str,
    case_id: str,
    case_type: str,
    doc_path: str,
    clause: HookClauseContext,
    status: str,
    totals: HookTotals,
    profile_enabled: bool,
    failure: BaseException | None = None,
) -> dict[str, Any]:
    token = None
    failure_message = None
    if failure is not None:
        failure_message = str(failure)
        prefix = failure_message.split(":", 1)[0].strip() if failure_message else ""
        if "." in prefix:
            token = prefix
    envelope: dict[str, Any] = {
        "event": event,
        "case": {
            "id": case_id,
            "type": case_type,
            "doc_path": doc_path,
        },
        "clause": {
            "index": int(clause.index),
            "id": clause.id,
            "class": clause.class_name,
            "assert_path": clause.assert_path,
            "target": clause.target,
        },
        "runtime": {
            "impl": str(os.environ.get("SPEC_RUNNER_IMPL", "unknown")),
            "profile_enabled": bool(profile_enabled),
        },
        "status": status,
        "totals": {
            "passed_clauses": int(totals.passed_clauses),
            "failed_clauses": int(totals.failed_clauses),
            "must_passed": int(totals.must_passed),
            "may_passed": int(totals.may_passed),
            "must_not_passed": int(totals.must_not_passed),
        },
    }
    if failure is not None:
        envelope["failure"] = {
            "message": failure_message,
            "token": token,
        }
    return envelope


def execute_hook_list(
    *,
    event: str,
    hook_exprs: list[Any],
    subject: Mapping[str, Any],
    limits,
    symbols: Mapping[str, Any] | None,
    imports: Mapping[str, str] | None,
    capabilities: set[str] | frozenset[str] | None,
) -> None:
    for idx, expr in enumerate(hook_exprs):
        try:
            value = eval_expr(
                expr,
                subject=subject,
                limits=limits,
                symbols=symbols,
                imports=imports,
                capabilities=capabilities,
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"runtime.on_hook.failed: event={event} index={idx}: {exc}") from exc
        if not bool(value):
            raise RuntimeError(f"runtime.on_hook.failed: event={event} index={idx}: expression returned falsy")
