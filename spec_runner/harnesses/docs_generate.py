from __future__ import annotations

from spec_runner.compiler import compile_external_case
from spec_runner.components.assertion_engine import run_assertions_with_context, runtime_env
from spec_runner.components.effects.docs_ops import resolve_docs_generate_harness_config, run_docs_generation_op
from spec_runner.components.execution_context import build_execution_context
from spec_runner.components.meta_subject import build_meta_subject
from spec_runner.components.subject_router import resolve_subject_for_target
from spec_runner.dispatcher import SpecRunContext
from spec_runner.virtual_paths import contract_root_for


def run(case, *, ctx: SpecRunContext) -> None:
    if hasattr(case, "test") and hasattr(case, "doc_path"):
        case = compile_external_case(case.test, doc_path=case.doc_path)

    cfg = resolve_docs_generate_harness_config(case.harness)
    root = contract_root_for(case.doc_path)
    op = run_docs_generation_op(
        root=root,
        cfg=cfg,
        runtime_env=runtime_env(ctx),
        profiler=getattr(ctx, "profiler", None),
    )

    result_envelope: dict[str, object] = {
        "status": "pass",
        "surface_id": op["surface_id"],
        "mode": op["mode"],
        "output_mode": op["output_mode"],
        "changed": bool(op["changed"]),
        "template_path": "/" + op["template_path"].relative_to(root).as_posix().lstrip("/"),
        "output_path": "/" + op["output_path"].relative_to(root).as_posix().lstrip("/"),
        "data_source_ids": op["data_source_ids"],
    }
    context_profile = {
        "profile_id": "docs.generate/v1",
        "profile_version": 1,
        "value": result_envelope,
        "meta": {
            "target": "docs.generate",
            "case_id": case.id,
            "surface_id": op["surface_id"],
        },
        "context": {
            "template_path": result_envelope["template_path"],
            "output_path": result_envelope["output_path"],
            "data_source_ids": result_envelope["data_source_ids"],
            "output_mode": op["output_mode"],
            "changed": bool(op["changed"]),
        },
    }
    case_key = f"{case.doc_path.resolve().as_posix()}::{case.id}"
    chain_imports = dict(ctx.get_case_chain_imports(case_key=case_key))
    chain_payload = dict(ctx.get_case_chain_payload(case_key=case_key))
    execution = build_execution_context(
        case_id=case.id,
        case_type=case.type,
        harness={**case.harness, "_chain_imports": chain_imports},
        doc_path=case.doc_path,
    )
    targets = {
        "result_json": result_envelope,
        "context_json": context_profile,
        "output_text": op["output_text"],
        "chain_json": chain_payload,
    }
    targets["meta_json"] = build_meta_subject(
        case=case,
        ctx=ctx,
        case_key=case_key,
        harness={**case.harness, "_chain_imports": chain_imports},
        artifacts=targets,
    )
    ctx.set_case_targets(case_key=case_key, targets=targets)
    run_assertions_with_context(
        assert_tree=case.assert_tree,
        raw_assert_spec=case.raw_case.get("contract", []) or [],
        raw_case=case.raw_case,
        ctx=ctx,
        execution=execution,
        subject_for_key=lambda k: resolve_subject_for_target(k, targets, type_name="docs.generate"),
    )
