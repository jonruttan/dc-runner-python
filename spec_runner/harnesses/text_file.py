from spec_runner.compiler import compile_external_case
from spec_runner.components.assertion_engine import run_assertions_with_context
from spec_runner.components.execution_context import build_execution_context
from spec_runner.components.meta_subject import build_meta_subject
from spec_runner.components.subject_router import resolve_subject_for_target
from spec_runner.virtual_paths import contract_root_for, resolve_contract_path


def run(case, *, ctx) -> None:
    if hasattr(case, "test") and hasattr(case, "doc_path"):
        case = compile_external_case(case.test, doc_path=case.doc_path)
    t = case.raw_case
    case_id = case.id
    # By default, assert against the spec doc that contains the contract-spec.
    # If `path` is provided, assert against that file (relative to the spec doc).
    p = case.doc_path
    rel = t.get("path")
    if rel is not None:
        try:
            p = resolve_contract_path(
                contract_root_for(case.doc_path), str(rel), field="text.file path"
            )
        except ValueError as e:
            raise ValueError(str(e)) from e
    doc_path = case.doc_path.resolve()
    root = contract_root_for(doc_path)
    text = p.read_text(encoding="utf-8")
    text_subject_profile = {
        "profile_id": "text.file/v1",
        "profile_version": 1,
        "value": text,
        "meta": {
            "target": "text",
            "path": "/" + p.resolve().relative_to(root).as_posix().lstrip("/"),
        },
        "context": {
            "source_doc": "/" + doc_path.relative_to(root).as_posix().lstrip("/"),
        },
    }
    case_key = f"{case.doc_path.resolve().as_posix()}::{case_id}"
    chain_imports = dict(ctx.get_case_chain_imports(case_key=case_key))
    chain_payload = dict(ctx.get_case_chain_payload(case_key=case_key))
    execution = build_execution_context(
        case_id=case_id,
        case_type=case.type,
        harness={**case.harness, "_chain_imports": chain_imports},
        doc_path=case.doc_path,
    )
    targets = {
        "text": text,
        "context_json": text_subject_profile,
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
        raw_assert_spec=t.get("contract", []) or [],
        raw_case=t,
        ctx=ctx,
        execution=execution,
        subject_for_key=lambda k: resolve_subject_for_target(k, targets, type_name="text.file"),
    )
