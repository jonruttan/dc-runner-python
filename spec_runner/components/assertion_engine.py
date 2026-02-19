from __future__ import annotations

import os
import sys
from typing import Any, Callable

from spec_runner.assertion_health import (
    format_assertion_health_error,
    format_assertion_health_warning,
    lint_assert_tree,
    resolve_assert_health_mode,
)
from spec_runner.assertions import evaluate_internal_assert_tree
from spec_runner.components.contracts import HarnessExecutionContext
from spec_runner.components.hook_engine import (
    HookClauseContext,
    HookTotals,
    build_hook_event_envelope,
    execute_hook_list,
    parse_on_hooks,
)


def runtime_env(ctx) -> dict[str, str]:
    raw_env = getattr(ctx, "env", None)
    if raw_env is None:
        return dict(os.environ)
    return {str(k): str(v) for k, v in raw_env.items()}


def run_assertions_with_context(
    *,
    assert_tree,
    raw_assert_spec: list[Any] | None,
    raw_case: dict[str, Any],
    ctx,
    execution: HarnessExecutionContext,
    subject_for_key: Callable[[str], Any],
) -> None:
    mode = resolve_assert_health_mode(raw_case, env=runtime_env(ctx))
    diags = lint_assert_tree(raw_assert_spec or [])
    if diags and mode == "error":
        raise AssertionError(format_assertion_health_error(diags))
    if diags and mode == "warn":
        for d in diags:
            print(format_assertion_health_warning(d), file=sys.stderr)

    hooks = parse_on_hooks(raw_case=raw_case)
    fail_hook_ran = False

    def _run_event(event: str, *, clause: HookClauseContext, status: str, totals: HookTotals, failure: BaseException | None = None) -> None:
        exprs = hooks.get(event) or []
        if not exprs:
            return
        subject = build_hook_event_envelope(
            event=event,
            case_id=execution.case_id,
            case_type=execution.case_type,
            doc_path=execution.doc_path,
            clause=clause,
            status=status,
            totals=totals,
            profile_enabled=bool(getattr(ctx, "profile_enabled", False)),
            failure=failure,
        )
        execute_hook_list(
            event=event,
            hook_exprs=exprs,
            subject=subject,
            limits=execution.limits,
            symbols=execution.symbols,
            imports=execution.imports,
            capabilities=execution.capabilities,
        )

    def _to_clause(payload: dict[str, Any]) -> HookClauseContext:
        return HookClauseContext(
            index=int(payload.get("index", 0)),
            id=payload.get("id"),
            class_name=str(payload.get("class", "MUST")),
            assert_path=str(payload.get("assert_path", "contract")),
            target=payload.get("target"),
        )

    def _to_totals(payload: dict[str, int]) -> HookTotals:
        return HookTotals(
            passed_clauses=int(payload.get("passed_clauses", 0)),
            failed_clauses=int(payload.get("failed_clauses", 0)),
            must_passed=int(payload.get("MUST_passed", 0)),
            may_passed=int(payload.get("MAY_passed", 0)),
            must_not_passed=int(payload.get("MUST_NOT_passed", 0)),
        )

    def _on_clause_pass(clause: dict[str, Any], totals: dict[str, int]) -> None:
        cls = str(clause.get("class", "")).strip()
        event_map = {"MUST": "must", "MAY": "may", "MUST_NOT": "must_not"}
        event = event_map.get(cls)
        if event is not None:
            _run_event(
                event,
                clause=_to_clause(clause),
                status="pass",
                totals=_to_totals(totals),
            )

    def _on_clause_fail(clause: dict[str, Any], exc: BaseException, totals: dict[str, int]) -> None:
        nonlocal fail_hook_ran
        if fail_hook_ran:
            return
        fail_hook_ran = True
        try:
            _run_event(
                "fail",
                clause=_to_clause(clause),
                status="fail",
                totals=_to_totals(totals),
                failure=exc,
            )
        except Exception as hook_exc:  # noqa: BLE001
            raise RuntimeError(f"runtime.on_hook.fail_handler_failed: {hook_exc}") from hook_exc

    def _on_complete(totals: dict[str, int]) -> None:
        _run_event(
            "complete",
            clause=HookClauseContext(
                index=max(int(totals.get("passed_clauses", 0)) - 1, 0),
                id=None,
                class_name="MUST",
                assert_path="contract",
                target=None,
            ),
            status="pass",
            totals=_to_totals(totals),
        )

    evaluate_internal_assert_tree(
        assert_tree,
        case_id=execution.case_id,
        subject_for_key=subject_for_key,
        limits=execution.limits,
        symbols=execution.symbols,
        imports=execution.imports,
        capabilities=execution.capabilities,
        on_clause_pass=_on_clause_pass,
        on_clause_fail=_on_clause_fail,
        on_complete=_on_complete,
    )
