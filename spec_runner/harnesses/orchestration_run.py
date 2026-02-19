from __future__ import annotations

from typing import Any

from spec_runner.compiler import compile_external_case
from spec_runner.components.assertion_engine import run_assertions_with_context
from spec_runner.components.effects.tool_ops import load_tools_registry, resolve_tool, run_tool_op
from spec_runner.components.execution_context import build_execution_context
from spec_runner.components.meta_subject import build_meta_subject
from spec_runner.components.subject_router import resolve_subject_for_target
from spec_runner.virtual_paths import contract_root_for

def run(case, *, ctx) -> None:
    if hasattr(case, "test") and hasattr(case, "doc_path"):
        case = compile_external_case(case.test, doc_path=case.doc_path)

    case_id = case.id
    harness = case.harness
    orch = dict(harness.get("orchestration") or {})
    if not orch:
        raise ValueError("orchestration.run requires harness.orchestration mapping")

    tool_id = str(orch.get("tool_id", "")).strip()
    if not tool_id:
        raise ValueError("harness.orchestration.tool_id must be a non-empty string")

    impl = str(orch.get("impl", "")).strip() or "python"
    if impl not in {"python", "rust"}:
        raise ValueError("harness.orchestration.impl must be rust|python when provided")

    args_raw = orch.get("args")
    forwarded: list[str] = []
    if args_raw is None:
        forwarded = []
    elif isinstance(args_raw, list):
        forwarded = [str(x) for x in args_raw]
    else:
        raise TypeError("harness.orchestration.args must be a list when provided")

    capabilities_raw = orch.get("capabilities") or []
    if not isinstance(capabilities_raw, list):
        raise TypeError("harness.orchestration.capabilities must be a list when provided")
    declared_caps = {str(x).strip() for x in capabilities_raw if str(x).strip()}

    root = contract_root_for(case.doc_path)
    tools = load_tools_registry(root, impl)
    tool = resolve_tool(tools, tool_id)
    capability_id = str(tool.get("capability_id", "")).strip()
    if capability_id and capability_id not in declared_caps:
        raise ValueError(
            f"harness.orchestration.capabilities missing required capability for tool {tool_id}: {capability_id}"
        )

    subcommand = str(tool.get("adapter_subcommand", "")).strip()
    if not subcommand:
        raise ValueError(f"tool {tool_id} missing adapter_subcommand")

    result_envelope: dict[str, Any] = {
        **run_tool_op(root=root, impl=impl, subcommand=subcommand, args=forwarded),
        "tool_id": tool_id,
        "impl": impl,
    }

    context_profile = {
        "profile_id": "orchestration.run/v1",
        "profile_version": 1,
        "value": result_envelope,
        "meta": {
            "target": "orchestration.run",
            "case_id": case_id,
            "tool_id": tool_id,
            "effect_symbol": str(tool.get("effect_symbol", "")),
        },
        "context": {
            "impl": impl,
            "subcommand": subcommand,
        },
    }

    case_key = f"{case.doc_path.resolve().as_posix()}::{case_id}"
    chain_imports = dict(ctx.get_case_chain_imports(case_key=case_key))
    chain_payload = dict(ctx.get_case_chain_payload(case_key=case_key))
    execution = build_execution_context(
        case_id=case.id,
        case_type=case.type,
        harness={**harness, "_chain_imports": chain_imports},
        doc_path=case.doc_path,
    )
    targets = {
        "result_json": result_envelope,
        "stdout": str(result_envelope["data"]["stdout"]),
        "stderr": str(result_envelope["data"]["stderr"]),
        "exit_code": int(result_envelope["data"]["exit_code"]),
        "context_json": context_profile,
        "chain_json": chain_payload,
    }
    targets["meta_json"] = build_meta_subject(
        case=case,
        ctx=ctx,
        case_key=case_key,
        harness={**harness, "_chain_imports": chain_imports},
        artifacts=targets,
    )
    ctx.set_case_targets(case_key=case_key, targets=targets)
    run_assertions_with_context(
        assert_tree=case.assert_tree,
        raw_assert_spec=case.raw_case.get("contract", []) or [],
        raw_case=case.raw_case,
        ctx=ctx,
        execution=execution,
        subject_for_key=lambda k: resolve_subject_for_target(k, targets, type_name="orchestration.run"),
    )
