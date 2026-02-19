from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

from spec_runner.codecs import load_external_cases
from spec_runner.contract_governance import contract_coverage_jsonable
from spec_runner.docs_quality import (
    DocsIssue,
    check_command_examples_verified,
    check_example_id_uniqueness,
    check_instructions_complete,
    check_token_dependency_resolved,
    check_token_ownership_unique,
    load_docs_meta_for_paths,
    load_reference_manifest,
    manifest_chapter_paths,
)
from spec_runner.schema_registry import compile_registry, write_compiled_registry_artifact
from spec_runner.script_entrypoints import (
    check_docs_freshness_main,
    ci_gate_summary_main,
    compare_conformance_parity_main,
    conformance_purpose_report_main,
    docs_generate_all_main,
    docs_generate_specs_main,
    impl_evaluate_migration_report_main,
    normalize_docs_layout_main,
    normalize_repo_main,
    objective_scorecard_report_main,
    python_conformance_runner_main,
    quality_metric_reports_main,
    run_governance_specs_main,
    perf_smoke_main,
    generate_library_symbol_catalog_main,
    generate_spec_case_catalog_main,
    generate_spec_case_templates_main,
    review_validate_main,
    spec_portability_report_main,
    split_library_cases_per_symbol_main,
)
from spec_runner.spec_lang import SpecLangLimits, eval_expr
from spec_runner.spec_lang_format import main as spec_lang_format_main
from spec_runner.spec_lang_lint import main as spec_lang_lint_main
from spec_runner.spec_lang_stdlib_profile import spec_lang_stdlib_report_jsonable
from spec_runner.spec_lang_yaml_ast import SpecLangYamlAstError, compile_yaml_expr_to_sexpr
from spec_runner.virtual_paths import VirtualPathError, resolve_contract_path


def validate_report_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a conformance JSON report payload.")
    ap.add_argument("report", help="Path to report JSON file")
    ns = ap.parse_args(argv)

    p = Path(ns.report)
    payload = json.loads(p.read_text(encoding="utf-8"))
    errs = _validate_report_payload_spec_lang(payload)
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"OK: valid conformance report ({p})")
    return 0


@lru_cache(maxsize=1)
def _load_conformance_export_functions() -> dict[str, list[object]]:
    repo_root = Path(__file__).resolve().parents[3]
    lib_path = repo_root / "specs/libraries/domain/conformance_core.spec.md"
    if not lib_path.exists():
        raise RuntimeError(f"missing spec library file: {lib_path}")
    out: dict[str, list[object]] = {}
    for _doc_path, raw_case in load_external_cases(lib_path, formats={"md"}):
        if str(raw_case.get("type", "")).strip() != "contract.export":
            continue
        harness = dict(raw_case.get("harness") or {})
        exports = harness.get("exports") or []
        if not isinstance(exports, list):
            continue
        for exp in exports:
            if not isinstance(exp, dict):
                continue
            symbol_name = str(exp.get("as", "")).strip()
            if not symbol_name:
                continue
            if str(exp.get("from", "")).strip() != "assert.function":
                raise RuntimeError(f"{symbol_name} must use from: assert.function")
            step_id = str(exp.get("path", "")).strip().lstrip("/")
            params = exp.get("params")
            if not isinstance(params, list) or not params or not all(isinstance(x, str) and x.strip() for x in params):
                raise RuntimeError(f"{symbol_name} must declare non-empty string params list")
            contract = raw_case.get("contract")
            if not isinstance(contract, dict):
                raise RuntimeError(f"{symbol_name} producer case must include contract mapping")
            assert_steps = contract.get("steps")
            if not isinstance(assert_steps, list):
                raise RuntimeError(f"{symbol_name} producer case contract.steps must be a list")
            found_step = False
            for step in assert_steps:
                if not isinstance(step, dict):
                    continue
                if str(step.get("id", "")).strip() != step_id:
                    continue
                found_step = True
                checks = step.get("assert")
                if isinstance(checks, dict):
                    checks = [checks]
                if not isinstance(checks, list) or len(checks) != 1 or not isinstance(checks[0], dict):
                    raise RuntimeError(f"{symbol_name} export step must have exactly one expression assert")
                try:
                    body_expr = compile_yaml_expr_to_sexpr(
                        checks[0],
                        field_path=f"{lib_path.as_posix()}#{step_id}.assert[0]",
                    )
                except SpecLangYamlAstError as exc:
                    raise RuntimeError(str(exc)) from exc
                out[symbol_name] = ["fn", [str(x).strip() for x in params], body_expr]
            if not found_step:
                raise RuntimeError(f"{symbol_name} export step id not found: {step_id}")
    if not out:
        raise RuntimeError(f"no conformance exports found in: {lib_path}")
    return out


def _validate_report_payload_spec_lang(payload: object) -> list[str]:
    symbols = _load_conformance_export_functions()
    fn_expr = symbols.get("domain.conformance.validate_report_errors")
    if not isinstance(fn_expr, list):
        raise RuntimeError("missing symbol: domain.conformance.validate_report_errors")
    result = eval_expr(
        ["call", fn_expr, ["var", "subject"]],
        subject=payload,
        limits=SpecLangLimits(),
        symbols=symbols,
        imports={},
    )
    if not isinstance(result, list):
        raise RuntimeError("spec-lang validate_report function must return list[str]")
    out: list[str] = []
    for item in result:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _spec_lang_stdlib_to_markdown(payload: dict[str, object]) -> str:
    summary = payload.get("summary") if isinstance(payload, dict) else {}
    if not isinstance(summary, dict):
        summary = {}
    lines = [
        "# Spec-Lang Stdlib Profile Report",
        "",
        f"- profile symbols: {int(summary.get('profile_symbol_count', 0))}",
        f"- python symbols: {int(summary.get('python_symbol_count', 0))}",
        f"- php symbols: {int(summary.get('php_symbol_count', 0))}",
        f"- missing in python: {int(summary.get('missing_in_python_count', 0))}",
        f"- missing in php: {int(summary.get('missing_in_php_count', 0))}",
        f"- arity mismatch: {int(summary.get('arity_mismatch_count', 0))}",
        f"- docs sync missing: {int(summary.get('docs_sync_missing_count', 0))}",
        "",
    ]
    for key in ("missing_in_python", "missing_in_php", "arity_mismatch", "docs_sync_missing", "errors"):
        vals = payload.get(key) if isinstance(payload, dict) else []
        if not isinstance(vals, list) or not vals:
            continue
        lines.append(f"## {key.replace('_', ' ').title()}")
        lines.append("")
        for item in vals:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def spec_lang_stdlib_report_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Emit spec-lang stdlib profile completeness/parity report."
    )
    ap.add_argument("--out", help="Optional output path.")
    ap.add_argument("--format", choices=("json", "md"), default="json")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = spec_lang_stdlib_report_jsonable(repo_root)
    raw = (
        _spec_lang_stdlib_to_markdown(payload)
        if ns.format == "md"
        else json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )

    if ns.out:
        out = Path(ns.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(raw, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(raw, end="")
    return 0


def contract_coverage_report_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Emit optional spec_runner contract coverage report as JSON "
            "(artifact/reporting helper; not a primary gate)."
        )
    )
    ap.add_argument("--out", help="Optional output path for JSON report.")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = contract_coverage_jsonable(repo_root)
    raw = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.out:
        out = Path(ns.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(raw, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(raw, end="")
    return 0


def _schema_registry_render_md(payload: dict[str, object]) -> str:
    summary = payload.get("summary") if isinstance(payload, dict) else {}
    if not isinstance(summary, dict):
        summary = {}
    lines = [
        "# Schema Registry Report",
        "",
        f"- profile_count: {int(summary.get('profile_count', 0))}",
        f"- top_level_field_count: {int(summary.get('top_level_field_count', 0))}",
        f"- type_profile_count: {int(summary.get('type_profile_count', 0))}",
        f"- errors: {int(summary.get('error_count', 0))}",
        "",
    ]
    errors = payload.get("errors") if isinstance(payload, dict) else []
    if isinstance(errors, list) and errors:
        lines.extend(["## Errors", ""])
        for err in errors:
            lines.append(f"- {err}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def schema_registry_report_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Emit schema registry compiled report.")
    ap.add_argument("--out", default=".artifacts/schema_registry_report.md")
    ap.add_argument("--format", choices=("json", "md"), default="md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    compiled, errs = compile_registry(repo_root)
    payload: dict[str, object] = {
        "version": 1,
        "summary": {
            "profile_count": int(compiled.get("profile_count", 0)) if compiled else 0,
            "top_level_field_count": len((compiled or {}).get("top_level_fields") or {}),
            "type_profile_count": len((compiled or {}).get("type_profiles") or {}),
            "error_count": len(errs),
        },
        "errors": errs,
    }
    if compiled:
        payload["compiled"] = compiled

    if compiled:
        write_compiled_registry_artifact(repo_root, compiled)
    raw = (
        _schema_registry_render_md(payload)
        if ns.format == "md"
        else json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    out = Path(str(ns.out))
    out.parent.mkdir(parents=True, exist_ok=True)
    if ns.check:
        if not out.exists():
            print(f"{out}: missing report artifact")
            return 1
        if out.read_text(encoding="utf-8") != raw:
            print(f"{out}: stale report artifact")
            return 1
        print("OK: schema registry report is up to date")
        return 0
    out.write_text(raw, encoding="utf-8")
    print(f"wrote {out}")
    return 0 if not errs else 1


def _render_docs_issues(issues: list[DocsIssue]) -> None:
    for issue in issues:
        print(issue.render())


def docs_lint_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lint docs quality contract rules.")
    ap.add_argument("--manifest", default="docs/book/reference_manifest.yaml")
    ns = ap.parse_args(argv)

    root = Path.cwd()
    manifest, manifest_issues = load_reference_manifest(root, str(ns.manifest))
    issues: list[DocsIssue] = []
    issues.extend(manifest_issues)
    if manifest_issues:
        _render_docs_issues(issues)
        return 1

    docs = manifest_chapter_paths(manifest)
    metas, meta_issues, _meta_lines = load_docs_meta_for_paths(root, docs)
    issues.extend(meta_issues)

    for rel in docs:
        if rel in metas:
            try:
                doc_path = resolve_contract_path(root, str(rel), field="reference_manifest.chapters.path")
            except VirtualPathError as exc:
                issues.append(DocsIssue(path=str(rel), line=1, message=str(exc)))
                continue
            metas[rel]["__text__"] = doc_path.read_text(encoding="utf-8")

    issues.extend(check_token_ownership_unique(metas))
    issues.extend(check_token_dependency_resolved(metas))
    issues.extend(check_instructions_complete(root, metas))
    issues.extend(check_command_examples_verified(root, docs))
    issues.extend(check_example_id_uniqueness(metas))

    if issues:
        _render_docs_issues(issues)
        return 1
    print("OK: docs lint passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    normalized_argv = list(sys.argv[1:] if argv is None else argv)
    if normalized_argv and normalized_argv[0] == "evaluate-style":
        normalized_argv[0] = "spec-lang-format"
    ap = argparse.ArgumentParser(description="Spec-lang backed command entrypoints.")
    ap.add_argument(
        "command",
        choices=(
            "validate-report",
            "spec-lang-stdlib-report",
            "contract-coverage-report",
            "schema-registry-report",
            "spec-lang-format",
            "spec-lang-lint",
            "docs-lint",
            "check-docs-freshness",
            "ci-gate-summary",
            "compare-conformance-parity",
            "conformance-purpose-report",
            "docs-generate-all",
            "docs-generate-specs",
            "impl-evaluate-migration-report",
            "normalize-docs-layout",
            "normalize-repo",
            "objective-scorecard-report",
            "python-conformance-runner",
            "quality-metric-reports",
            "run-governance-specs",
            "perf-smoke",
            "generate-library-symbol-catalog",
            "generate-spec-case-catalog",
            "generate-spec-case-templates",
            "review-validate",
            "spec-portability-report",
            "split-library-cases-per-symbol",
        ),
        help="Command to run.",
    )
    ap.add_argument("args", nargs=argparse.REMAINDER)
    ns = ap.parse_args(normalized_argv)
    forwarded = list(ns.args or [])
    if ns.command == "validate-report":
        return validate_report_main(forwarded)
    if ns.command == "spec-lang-stdlib-report":
        return spec_lang_stdlib_report_main(forwarded)
    if ns.command == "contract-coverage-report":
        return contract_coverage_report_main(forwarded)
    if ns.command == "schema-registry-report":
        return schema_registry_report_main(forwarded)
    if ns.command == "spec-lang-format":
        return spec_lang_format_main(forwarded)
    if ns.command == "spec-lang-lint":
        return spec_lang_lint_main(forwarded)
    if ns.command == "docs-lint":
        return docs_lint_main(forwarded)
    if ns.command == "check-docs-freshness":
        return check_docs_freshness_main(forwarded)
    if ns.command == "ci-gate-summary":
        return ci_gate_summary_main(forwarded)
    if ns.command == "compare-conformance-parity":
        return compare_conformance_parity_main(forwarded)
    if ns.command == "conformance-purpose-report":
        return conformance_purpose_report_main(forwarded)
    if ns.command == "docs-generate-all":
        return docs_generate_all_main(forwarded)
    if ns.command == "docs-generate-specs":
        return docs_generate_specs_main(forwarded)
    if ns.command == "impl-evaluate-migration-report":
        return impl_evaluate_migration_report_main(forwarded)
    if ns.command == "normalize-docs-layout":
        return normalize_docs_layout_main(forwarded)
    if ns.command == "normalize-repo":
        return normalize_repo_main(forwarded)
    if ns.command == "objective-scorecard-report":
        return objective_scorecard_report_main(forwarded)
    if ns.command == "python-conformance-runner":
        return python_conformance_runner_main(forwarded)
    if ns.command == "quality-metric-reports":
        return quality_metric_reports_main(forwarded)
    if ns.command == "run-governance-specs":
        return run_governance_specs_main(forwarded)
    if ns.command == "perf-smoke":
        return perf_smoke_main(forwarded)
    if ns.command == "generate-library-symbol-catalog":
        return generate_library_symbol_catalog_main(forwarded)
    if ns.command == "generate-spec-case-catalog":
        return generate_spec_case_catalog_main(forwarded)
    if ns.command == "generate-spec-case-templates":
        return generate_spec_case_templates_main(forwarded)
    if ns.command == "review-validate":
        return review_validate_main(forwarded)
    if ns.command == "spec-portability-report":
        return spec_portability_report_main(forwarded)
    if ns.command == "split-library-cases-per-symbol":
        return split_library_cases_per_symbol_main(forwarded)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
