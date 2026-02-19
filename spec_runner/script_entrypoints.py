from __future__ import annotations

import sys

from spec_runner.conformance_purpose_report import main as _conformance_purpose_report_main
from spec_runner.contract_assertions_report import main as _contract_assertions_report_main
from spec_runner.docs_build_reference import main as _docs_build_reference_main
from spec_runner.docs_generate_specs import main as _docs_generate_specs_main
from spec_runner.docs_operability_report import main as _docs_operability_report_main
from spec_runner.generate_governance_check_catalog import main as _generate_governance_check_catalog_main
from spec_runner.generate_harness_type_catalog import main as _generate_harness_type_catalog_main
from spec_runner.generate_library_symbol_catalog import main as _generate_library_symbol_catalog_main
from spec_runner.generate_metrics_field_catalog import main as _generate_metrics_field_catalog_main
from spec_runner.generate_policy_rule_catalog import main as _generate_policy_rule_catalog_main
from spec_runner.generate_runner_api_catalog import main as _generate_runner_api_catalog_main
from spec_runner.generate_spec_case_templates import main as _generate_spec_case_templates_main
from spec_runner.generate_spec_case_catalog import main as _generate_spec_case_catalog_main
from spec_runner.generate_schema_docs import main as _generate_schema_docs_main
from spec_runner.generate_spec_lang_builtin_catalog import main as _generate_spec_lang_builtin_catalog_main
from spec_runner.generate_spec_schema_field_catalog import main as _generate_spec_schema_field_catalog_main
from spec_runner.generate_traceability_catalog import main as _generate_traceability_catalog_main
from spec_runner.normalize_docs_layout import main as _normalize_docs_layout_main
from spec_runner.normalize_repo_runtime import main as _normalize_repo_main
from spec_runner.objective_scorecard_report import main as _objective_scorecard_report_main
from spec_runner.python_conformance_runner import main as _python_conformance_runner_main
from spec_runner.python_dependency_report import main as _python_dependency_report_main
from spec_runner.report_impl_evaluate_migration import main as _report_impl_evaluate_migration_main
from spec_runner.runner_independence_report import main as _runner_independence_report_main
from spec_runner.script_runtime_commands import (
    check_docs_freshness_main as _check_docs_freshness_main,
    ci_gate_summary_main as _ci_gate_summary_main,
    compare_conformance_parity_main as _compare_conformance_parity_main,
)
from spec_runner.script_runtime_commands import docs_generate_all_main as _docs_generate_all_main
from spec_runner.script_runtime_commands import perf_smoke_main as _perf_smoke_main
from spec_runner.spec_lang_adoption_report import main as _spec_lang_adoption_report_main
from spec_runner.spec_lang_format import main as _spec_lang_format_main
from spec_runner.spec_portability_report import main as _spec_portability_report_main
from spec_runner.review_snapshot_validate import main as _review_snapshot_validate_main
from spec_runner.split_library_cases_per_symbol import main as _split_library_cases_per_symbol_main


def ci_gate_summary_main(argv: list[str] | None = None) -> int:
    return int(_ci_gate_summary_main(argv))


def check_docs_freshness_main(argv: list[str] | None = None) -> int:
    return int(_check_docs_freshness_main(argv))


def compare_conformance_parity_main(argv: list[str] | None = None) -> int:
    return int(_compare_conformance_parity_main(argv))


def conformance_purpose_report_main(argv: list[str] | None = None) -> int:
    return int(_conformance_purpose_report_main(argv))


def docs_generate_all_main(argv: list[str] | None = None) -> int:
    return int(_docs_generate_all_main(argv))


def docs_generate_specs_main(argv: list[str] | None = None) -> int:
    return int(_docs_generate_specs_main(argv))


def docs_build_reference_main(argv: list[str] | None = None) -> int:
    return int(_docs_build_reference_main(argv))


def evaluate_style_main(argv: list[str] | None = None) -> int:
    return int(_spec_lang_format_main(argv))


def impl_evaluate_migration_report_main(argv: list[str] | None = None) -> int:
    return int(_report_impl_evaluate_migration_main(argv))


def normalize_docs_layout_main(argv: list[str] | None = None) -> int:
    return int(_normalize_docs_layout_main(argv))


def normalize_repo_main(argv: list[str] | None = None) -> int:
    return int(_normalize_repo_main(argv))


def objective_scorecard_report_main(argv: list[str] | None = None) -> int:
    return int(_objective_scorecard_report_main(argv))


def python_conformance_runner_main(argv: list[str] | None = None) -> int:
    return int(_python_conformance_runner_main(argv))


def quality_metric_reports_main(argv: list[str] | None = None) -> int:
    forwarded = list(argv or [])
    if not forwarded:
        raise SystemExit(
            "quality_metric_reports_main requires first argument: "
            "spec-lang-adoption|runner-independence|python-dependency|docs-operability|contract-assertions"
        )
    report = str(forwarded.pop(0)).strip()
    report_to_main = {
        "spec-lang-adoption": _spec_lang_adoption_report_main,
        "runner-independence": _runner_independence_report_main,
        "python-dependency": _python_dependency_report_main,
        "docs-operability": _docs_operability_report_main,
        "contract-assertions": _contract_assertions_report_main,
    }
    entry = report_to_main.get(report)
    if entry is None:
        print(f"unsupported quality report: {report}", file=sys.stderr)
        return 1
    return int(entry(forwarded))


def schema_registry_scripts_main(argv: list[str] | None = None) -> int:
    return int(_generate_schema_docs_main(argv))


def spec_portability_report_main(argv: list[str] | None = None) -> int:
    return int(_spec_portability_report_main(argv))


def split_library_cases_per_symbol_main(argv: list[str] | None = None) -> int:
    return int(_split_library_cases_per_symbol_main(argv))


def generate_governance_check_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_governance_check_catalog_main(argv))


def generate_harness_type_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_harness_type_catalog_main(argv))


def generate_library_symbol_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_library_symbol_catalog_main(argv))


def generate_spec_case_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_spec_case_catalog_main(argv))


def generate_spec_case_templates_main(argv: list[str] | None = None) -> int:
    return int(_generate_spec_case_templates_main(argv))


def generate_metrics_field_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_metrics_field_catalog_main(argv))


def generate_policy_rule_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_policy_rule_catalog_main(argv))


def generate_runner_api_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_runner_api_catalog_main(argv))


def generate_spec_lang_builtin_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_spec_lang_builtin_catalog_main(argv))


def generate_spec_schema_field_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_spec_schema_field_catalog_main(argv))


def generate_traceability_catalog_main(argv: list[str] | None = None) -> int:
    return int(_generate_traceability_catalog_main(argv))


def perf_smoke_main(argv: list[str] | None = None) -> int:
    return int(_perf_smoke_main(argv))


def review_validate_main(argv: list[str] | None = None) -> int:
    return int(_review_snapshot_validate_main(argv))


def run_governance_specs_main(argv: list[str] | None = None) -> int:
    from spec_runner.governance_runtime import main as _main

    return int(_main(argv))
