#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import contextvars
import contextlib
import json
import inspect
import os
import shlex
import subprocess
import sys
import re
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, cast

import yaml
from spec_runner.assertions import evaluate_internal_assert_tree
from spec_runner.codecs import load_external_cases as _load_external_cases_uncached
from spec_runner.dispatcher import SpecRunContext, iter_cases as _iter_cases_uncached, run_case
from spec_runner.doc_parser import iter_spec_doc_tests
from spec_runner.purpose_lint import (
    load_purpose_lint_policy,
    purpose_quality_warnings,
    resolve_purpose_lint_config,
)
from spec_runner.runtime_context import MiniCapsys, MiniMonkeyPatch
from spec_runner.settings import SETTINGS, case_file_name, governed_config_literals
from spec_runner.spec_lang import (
    SpecLangLimits,
    _builtin_arity_table,
    capabilities_from_harness,
    compile_import_bindings,
    eval_predicate,
)
from spec_runner.spec_lang_stdlib_profile import spec_lang_stdlib_report_jsonable
from spec_runner.spec_lang_libraries import load_spec_lang_symbols_for_case
from spec_runner.spec_domain import normalize_case_domain, normalize_export_symbol
from spec_runner.review_snapshot_validate import validate_review_snapshot_text
from spec_runner.spec_lang_yaml_ast import SpecLangYamlAstError, compile_yaml_expr_to_sexpr
from spec_runner.compiler import compile_assert_tree
from spec_runner.schema_registry import compile_registry
from spec_runner.ops_namespace import validate_ops_symbol
from spec_runner.ops_namespace import is_legacy_underscore_form
from spec_runner.ops_namespace import validate_registry_entry as validate_ops_registry_entry
from spec_runner.conformance_purpose import PURPOSE_WARNING_CODES
from spec_runner.conformance_purpose import conformance_purpose_report_jsonable
from spec_runner.contract_governance import check_contract_governance
from spec_runner.contract_governance import contract_coverage_jsonable
from spec_runner.docs_quality import build_docs_graph
from spec_runner.docs_quality import check_command_examples_verified
from spec_runner.docs_quality import check_example_id_uniqueness
from spec_runner.docs_quality import check_instructions_complete
from spec_runner.docs_quality import check_token_dependency_resolved
from spec_runner.docs_quality import check_token_ownership_unique
from spec_runner.docs_quality import load_docs_meta_for_paths
from spec_runner.docs_quality import load_reference_manifest
from spec_runner.docs_quality import manifest_chapter_paths
from spec_runner.docs_quality import render_reference_coverage
from spec_runner.docs_quality import render_reference_index
from spec_runner.docs_generators import REGISTRY_PATH as DOCS_GENERATOR_REGISTRY_PATH
from spec_runner.docs_generators import load_docs_generator_registry
from spec_runner.docs_generators import parse_generated_block
from spec_runner.quality_metrics import compare_metric_non_regression
from spec_runner.quality_metrics import contract_assertions_report_jsonable
from spec_runner.quality_metrics import docs_operability_report_jsonable
from spec_runner.quality_metrics import objective_scorecard_report_jsonable
from spec_runner.quality_metrics import python_dependency_report_jsonable
from spec_runner.quality_metrics import runner_independence_report_jsonable
from spec_runner.quality_metrics import spec_lang_adoption_report_jsonable
from spec_runner.quality_metrics import validate_metric_baseline_notes
from spec_runner.quality_metrics import _load_baseline_json
from spec_runner.components.meta_subject import build_meta_subject
from spec_runner.spec_portability import spec_portability_report_jsonable
from spec_runner.virtual_paths import VirtualPathError, normalize_contract_path, parse_external_ref, resolve_contract_path
from spec_runner.components.profiler import RunProfiler, profile_config_from_args
from spec_runner.components.liveness import (
    LivenessConfig,
    LivenessError,
    config_from_env as liveness_config_from_env,
    run_subprocess_with_liveness,
)


def normalize_evaluate(raw: object, *, field: str) -> list[object]:
    if not isinstance(raw, list):
        raise ValueError(f"{field} must be a non-empty list of mapping-ast expressions")
    if not raw:
        raise ValueError(f"{field} must be a non-empty list of mapping-ast expressions")
    try:
        compiled = [compile_yaml_expr_to_sexpr(item, field_path=f"{field}[{idx}]") for idx, item in enumerate(raw)]
    except SpecLangYamlAstError as exc:
        raise ValueError(str(exc)) from exc
    if len(compiled) == 1:
        return compiled[0]
    return ["std.logic.and", *compiled]


_SECURITY_WARNING_DOCS = (
    "README.md",
    "docs/book/10_getting_started.md",
    "specs/schema/schema_v1.md",
)
_SECURITY_WARNING_TOKENS = (
    "not a sandbox",
    "trusted inputs",
    "untrusted spec",
)
_V1_SCOPE_DOC = "specs/contract/08_v1_scope.md"
_V1_SCOPE_REQUIRED_TOKENS = (
    "v1 in scope",
    "v1 non-goals",
    "compatibility commitments",
    "current-spec-only rule",
)
_PYTHON_RUNTIME_ROOTS = ("runners/python/spec_runner", "scripts/python")
_CONFORMANCE_CASE_ID_PATTERN = r"\bSRCONF-[A-Z0-9-]+\b"
_CONFORMANCE_MAX_BLOCK_LINES = 120
_REGEX_PROFILE_DOC = "specs/contract/03a_regex_portability_v1.md"
_ASSERTION_OPERATOR_DOC_SYNC_TOKENS = ("evaluate",)
_ASSERT_UNIVERSAL_DOC_FILES = (
    "specs/schema/schema_v1.md",
    "specs/contract/03_assertions.md",
    "specs/contract/09_internal_representation.md",
)
_CURRENT_SPEC_ONLY_DOCS = (
    "README.md",
    "docs/book/20_case_model.md",
    "specs/schema/schema_v1.md",
    "specs/contract/01_discovery.md",
    "specs/contract/02_case_shape.md",
    "specs/contract/03_assertions.md",
    "specs/contract/04_harness.md",
    "specs/contract/08_v1_scope.md",
)
_CURRENT_SPEC_ONLY_CODE_FILES = (
    "runners/python/spec_runner/doc_parser.py",
    "runners/php/spec_runner.php",
    "runners/php/conformance_runner.php",
)
_CURRENT_SPEC_FORBIDDEN_PATTERNS = (
    r"previous\s+spec",
    r"prior\s+spec",
)
_TYPE_CONTRACTS_DIR = "specs/contract/types"
_CORE_TYPES = {"text.file", "cli.run", "contract.check"}
_ORCHESTRATION_TOOLS_FILES = (
    "specs/governance/tools/python/tools_v1.yaml",
    "specs/governance/tools/rust/tools_v1.yaml",
)
_COMMON_CASE_TOP_LEVEL_KEYS = {
    "id",
    "type",
    "title",
    "purpose",
    "domain",
    "assert",
    "contract",
    "when",
    "expect",
    "requires",
    "assert_health",
    "harness",
}
_RUNNER_KEYS_MUST_BE_UNDER_HARNESS = {
    "entrypoint",
    "env",
    "stdin_isatty",
    "stdin_text",
    "block_imports",
    "stub_modules",
    "setup_files",
    "hook_before",
    "hook_after",
    "hook_kwargs",
    "tmp_path",
    "patcher",
    "capture",
}
_NORMALIZATION_PROFILE_PATH = "specs/schema/normalization_profile_v1.yaml"
_DOCS_LAYOUT_PROFILE_PATH = "specs/schema/docs_layout_profile_v1.yaml"
_TOP_LEVEL_DIR_ALLOWLIST = {
    ".artifacts",
    ".git",
    ".github",
    ".githooks",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "dist",
    "docs",
    "fixtures",
    "runners",
    "scripts",
    "specs",
    "tests",
}
_PATH_LIKE_KEYS = {
    "path",
    "cases_path",
    "baseline_path",
    "manifest_path",
    "index_out",
    "coverage_out",
    "graph_out",
    "required_paths",
    "adapter_path",
    "cli_main_path",
    "required_library_path",
    "reference_manifest",
    "roots",
}
_DOMAIN_TREE_ROOTS = (
    "specs/conformance/cases",
    "specs/governance/cases",
    "specs/libraries",
)
_EXECUTABLE_CASE_TREE_ROOTS = (
    "specs/conformance/cases",
    "specs/governance/cases",
    "specs/impl",
)
_EXECUTABLE_NON_MD_SPEC_GLOBS = ("*.spec.yaml", "*.spec.yml", "*.spec.json")
_DATA_ARTIFACT_GLOBS = (
    "specs/governance/metrics/*.json",
    "specs/governance/metrics/*.yaml",
    "docs/book/reference_manifest.yaml",
    "specs/schema/*.yaml",
)
_GOVERNANCE_CHECK_CATALOG_MAP = "specs/governance/check_catalog_map_v1.yaml"
_SUBJECT_PROFILE_CONTRACT_DOC = "specs/contract/20_subject_profiles_v1.md"
_SUBJECT_PROFILE_SCHEMA_DOC = "specs/schema/subject_profiles_v1.yaml"
_SUBJECT_PROFILE_TYPE_DOCS = (
    "specs/contract/types/python_profile.md",
    "specs/contract/types/php_profile.md",
    "specs/contract/types/http_profile.md",
    "specs/contract/types/markdown_profile.md",
    "specs/contract/types/makefile_profile.md",
)
_SUBJECT_PROFILE_DOMAIN_LIBS = (
    "specs/libraries/domain/python_core.spec.md",
    "specs/libraries/domain/php_core.spec.md",
    "specs/libraries/domain/http_core.spec.md",
    "specs/libraries/domain/markdown_core.spec.md",
    "specs/libraries/domain/make_core.spec.md",
)
_SCHEMA_REGISTRY_ROOT = "specs/schema/registry/v1"
_SCHEMA_REGISTRY_SCHEMA = "specs/schema/registry_schema_v1.yaml"
_SCHEMA_REGISTRY_CONTRACT_DOC = "specs/contract/21_schema_registry_contract.md"
_SCHEMA_REGISTRY_COMPILED_ARTIFACT = ".artifacts/schema_registry_compiled.json"
_DOCS_GENERATOR_REPORT = ".artifacts/docs-generator-report.json"
_DOCS_GENERATOR_SUMMARY = ".artifacts/docs-generator-summary.md"
_DOCGEN_QUALITY_MIN_SCORE = 0.60
_REVIEW_PROMPT_FILES = (
    "docs/reviews/prompts/adoption_7_personas.md",
    "docs/reviews/prompts/self_healing.md",
    "docs/reviews/prompts/final_boss_gatekeeper.md",
    "docs/reviews/prompts/discovery_fit_self_heal.md",
)
_REVIEW_DISCOVERY_PROMPT = "docs/reviews/prompts/discovery_fit_self_heal.md"
_REVIEW_SCHEMA_REF_TOKENS = (
    "/specs/schema/review_snapshot_schema_v1.yaml",
    "/specs/contract/26_review_output_contract.md",
)
_REVIEW_REQUIRED_SECTION_TOKENS = (
    "## Scope Notes",
    "## Command Execution Log",
    "## Findings",
    "## Synthesis",
    "## Spec Candidates (YAML)",
    "## Classification Labels",
    "## Reject / Defer List",
    "## Raw Output",
)
_REVIEW_DISCOVERY_ENTRYPOINT_TOKENS = (
    "/README.md",
    "/docs/book/index.md",
    "/docs/development.md",
    "/specs/current.md",
    "/specs/contract/index.md",
    "/specs/schema/schema_v1.md",
)
_REVIEW_DISCOVERY_SELF_HEAL_ALLOWED_TOKENS = (
    "Allowed auto-fixes",
    "docs wording/path drift",
    "command example drift",
    "governance map/index/catalog token sync",
    "missing or incorrect prompt/template refs",
    "strict-schema output contract drift",
    "low-risk parser/CLI wiring inconsistencies",
)
_REVIEW_DISCOVERY_SELF_HEAL_FORBIDDEN_TOKENS = (
    "Forbidden auto-fixes",
    "architecture redesign",
    "schema semantic changes",
    "risky runtime logic changes",
    "dependency additions",
)
_CHAIN_TEMPLATE_PATTERN = re.compile(r"\{\{\s*chain\.([A-Za-z0-9_.-]+)\s*\}\}")
_CHAIN_REF_CASE_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")
_MD_NAMESPACE_LEGACY_PATTERN = re.compile(r"\bmd\.[A-Za-z0-9_]+\b")
_RAW_OPS_FS_ALLOWED_CASE_FILES = {
    "specs/conformance/cases/core/spec_lang_stdlib.spec.md",
}
_RAW_HTTP_META_ALLOWED_CASE_FILES = {
    "specs/conformance/cases/core/api_http.spec.md",
}
_OPS_FS_SYMBOL_PATTERN = re.compile(r"\bops\.fs\.[a-z0-9_.]+\b")
_GOVERNANCE_TRACE = os.environ.get("SPEC_RUNNER_GOVERNANCE_TRACE", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
_ACTIVE_PROFILER: contextvars.ContextVar[RunProfiler | None] = contextvars.ContextVar(
    "active_governance_profiler",
    default=None,
)


def _effective_governance_liveness() -> LivenessConfig:
    cfg = liveness_config_from_env(default_level="off")
    hard_cap_ms = int(cfg.hard_cap_ms)
    raw_governance_timeout = str(os.environ.get("SPEC_RUNNER_GOVERNANCE_SUBPROCESS_TIMEOUT_SECONDS", "")).strip()
    if raw_governance_timeout:
        try:
            hard_cap_ms = int(float(raw_governance_timeout) * 1000.0)
        except ValueError:
            pass
    raw_adapter_timeout = str(os.environ.get("SPEC_RUNNER_TIMEOUT_GOVERNANCE_SECONDS", "")).strip()
    if raw_adapter_timeout:
        try:
            hard_cap_ms = int(float(raw_adapter_timeout) * 1000.0)
        except ValueError:
            pass
    return LivenessConfig(
        level=cfg.level,
        stall_ms=int(cfg.stall_ms),
        min_events=int(cfg.min_events),
        hard_cap_ms=max(int(hard_cap_ms), 1),
        kill_grace_ms=int(cfg.kill_grace_ms),
    )


def _profiled_subprocess_run(
    cmd: list[str],
    *,
    cwd: Path,
    phase: str,
    text: bool = True,
) -> subprocess.CompletedProcess[str]:
    del text
    profiler = _ACTIVE_PROFILER.get()
    cfg = _effective_governance_liveness()
    return run_subprocess_with_liveness(
        command=cmd,
        cwd=cwd,
        profiler=profiler,
        phase=phase,
        cfg=cfg,
    )
_HARNESS_FILES = (
    "runners/python/spec_runner/harnesses/text_file.py",
    "runners/python/spec_runner/harnesses/cli_run.py",
    "runners/python/spec_runner/harnesses/orchestration_run.py",
    "runners/python/spec_runner/harnesses/docs_generate.py",
    "runners/python/spec_runner/harnesses/api_http.py",
)
_UNIT_TEST_OPT_OUT_BASELINE_PATH = "specs/governance/metrics/unit_test_opt_out_baseline.json"
_UNIT_TEST_OPT_OUT_PREFIX = "# SPEC-OPT-OUT:"

_SCAN_CACHE_TOKEN = 0
_EXTERNAL_CASES_CACHE: dict[tuple[int, str, tuple[str, ...], str | None], list[tuple[Path, dict[str, Any]]]] = {}
_ITER_CASES_CACHE: dict[tuple[int, str, str | None, tuple[str, ...] | None], list[Any]] = {}
_ALL_SPEC_CASES_CACHE: dict[tuple[int, str], list[tuple[Path, dict[str, Any]]]] = {}
_CHAIN_CASES_CACHE: dict[tuple[int, str], list[tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]]] = {}
_CONFORMANCE_IDS_CACHE: dict[tuple[int, str], set[str]] = {}
_CHAIN_REF_CASES_CACHE: dict[
    tuple[int, str, str, str],
    tuple[list[tuple[Path, dict[str, Any]]], list[str]],
] = {}
_GLOBAL_SYMBOL_REFERENCES_CACHE: dict[tuple[int, str], set[str]] = {}
_NORMALIZE_CHECK_CACHE: dict[tuple[int, str, str], tuple[int, list[str]]] = {}
_RUNNER_CERTIFY_CACHE: dict[tuple[int, str, str], tuple[int, str]] = {}
_SCAN_CACHE_LOCK = threading.RLock()


def _reset_scan_caches() -> None:
    global _SCAN_CACHE_TOKEN
    with _SCAN_CACHE_LOCK:
        _SCAN_CACHE_TOKEN += 1
        _EXTERNAL_CASES_CACHE.clear()
        _ITER_CASES_CACHE.clear()
        _ALL_SPEC_CASES_CACHE.clear()
        _CHAIN_CASES_CACHE.clear()
        _CONFORMANCE_IDS_CACHE.clear()
        _CHAIN_REF_CASES_CACHE.clear()
        _GLOBAL_SYMBOL_REFERENCES_CACHE.clear()
        _NORMALIZE_CHECK_CACHE.clear()
        _RUNNER_CERTIFY_CACHE.clear()


def load_external_cases(path: Path, *, formats: set[str] | None = None, md_pattern: str | None = None):
    normalized_formats = tuple(sorted(str(x) for x in (formats or set())))
    with _SCAN_CACHE_LOCK:
        cache_key = (_SCAN_CACHE_TOKEN, str(Path(path).resolve()), normalized_formats, md_pattern)
        cached = _EXTERNAL_CASES_CACHE.get(cache_key)
        if cached is not None:
            return cached
    loaded = list(_load_external_cases_uncached(path, formats=formats, md_pattern=md_pattern))
    with _SCAN_CACHE_LOCK:
        _EXTERNAL_CASES_CACHE[cache_key] = loaded
    return loaded


def iter_cases(
    spec_dir: Path,
    *,
    file_pattern: str | None = None,
    formats: set[str] | None = None,
):
    normalized_formats: tuple[str, ...] | None = None
    if formats is not None:
        normalized_formats = tuple(sorted(str(x) for x in formats))
    with _SCAN_CACHE_LOCK:
        cache_key = (_SCAN_CACHE_TOKEN, str(spec_dir.resolve()), file_pattern, normalized_formats)
        cached = _ITER_CASES_CACHE.get(cache_key)
        if cached is not None:
            return cached
    cases = list(_iter_cases_uncached(spec_dir, file_pattern=file_pattern, formats=formats))
    with _SCAN_CACHE_LOCK:
        _ITER_CASES_CACHE[cache_key] = cases
    return cases


def _resolve_contract_config_path(root: Path, raw: str, *, field: str) -> Path:
    return resolve_contract_path(root, str(raw), field=field)


def _join_contract_path(root: Path, raw: object) -> Path:
    return root / str(raw).lstrip("/")


def _line_for(text: str, token: str) -> int:
    idx = text.find(token)
    if idx < 0:
        return 1
    return text[:idx].count("\n") + 1


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(cast(Any, value))
    except (TypeError, ValueError):
        return default


def _iter_path_fields(node: object, *, key_path: str = ""):
    if isinstance(node, dict):
        for k, v in node.items():
            key = str(k)
            current = f"{key_path}.{key}" if key_path else key
            if key in {"request", "setup_files"}:
                yield from _iter_path_fields(v, key_path=current)
                continue
            is_spec_lang_includes = key == "includes" and (
                key_path == "harness.spec_lang" or key_path.endswith(".harness.spec_lang")
            )
            if key in _PATH_LIKE_KEYS or is_spec_lang_includes:
                if isinstance(v, str):
                    yield current, v
                elif isinstance(v, list):
                    for idx, item in enumerate(v):
                        if isinstance(item, str):
                            yield f"{current}[{idx}]", item
                elif isinstance(v, dict):
                    for kk, vv in v.items():
                        if isinstance(vv, str):
                            yield f"{current}.{kk}", vv
            yield from _iter_path_fields(v, key_path=current)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            current = f"{key_path}[{idx}]" if key_path else f"[{idx}]"
            yield from _iter_path_fields(item, key_path=current)


def _iter_all_spec_cases(base: Path):
    if not base.exists():
        return
    with _SCAN_CACHE_LOCK:
        cache_key = (_SCAN_CACHE_TOKEN, str(base.resolve()))
        cached = _ALL_SPEC_CASES_CACHE.get(cache_key)
    if cached is None:
        cached = []
        for file_path in sorted(base.rglob(SETTINGS.case.default_file_pattern)):
            if not file_path.is_file():
                continue
            for doc_path, case in load_external_cases(file_path, formats={"md"}):
                cached.append((doc_path, case))
        with _SCAN_CACHE_LOCK:
            _ALL_SPEC_CASES_CACHE[cache_key] = cached
    yield from cached


def _scan_contract_governance_check(root: Path) -> list[str]:
    return list(check_contract_governance(root))


def _scan_pending_no_resolved_markers(root: Path) -> list[str]:
    pending_dir = root / "specs/pending"
    if not pending_dir.exists():
        return []
    violations: list[str] = []
    for p in sorted(pending_dir.glob("*.md")):
        lower = p.read_text(encoding="utf-8").lower()
        for tok in ("resolved:", "completed:"):
            if tok in lower:
                rel = p.relative_to(root)
                violations.append(f"{rel}: found '{tok}'")
    return violations


def _scan_security_warning_docs(root: Path) -> list[str]:
    violations: list[str] = []
    for rel in _SECURITY_WARNING_DOCS:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}: missing required doc")
            continue
        lower = p.read_text(encoding="utf-8").lower()
        missing = [tok for tok in _SECURITY_WARNING_TOKENS if tok not in lower]
        if missing:
            violations.append(f"{rel}: missing token(s): {', '.join(missing)}")
    return violations


def _scan_v1_scope_doc(root: Path) -> list[str]:
    p = root / _V1_SCOPE_DOC
    if not p.exists():
        return [f"{_V1_SCOPE_DOC}: missing required doc"]
    lower = p.read_text(encoding="utf-8").lower()
    missing = [tok for tok in _V1_SCOPE_REQUIRED_TOKENS if tok not in lower]
    if missing:
        return [f"{_V1_SCOPE_DOC}: missing token(s): {', '.join(missing)}"]
    return []


def _scan_runtime_config_literals(root: Path) -> list[str]:
    violations: list[str] = []
    governed = governed_config_literals()
    for rel_root in _PYTHON_RUNTIME_ROOTS:
        runtime_root = _join_contract_path(root, rel_root)
        if not runtime_root.exists():
            continue
        for p in sorted(runtime_root.rglob("*.py")):
            if p.name == "settings.py":
                continue
            raw = p.read_text(encoding="utf-8")
            rel = p.relative_to(root)
            for literal, const_path in governed.items():
                if f'"{literal}"' in raw or f"'{literal}'" in raw:
                    violations.append(
                        f"{rel}: literal {literal!r} duplicated; use {const_path}"
                    )
    return violations


def _scan_runtime_settings_import_policy(root: Path) -> list[str]:
    violations: list[str] = []
    for rel_root in _PYTHON_RUNTIME_ROOTS:
        runtime_root = _join_contract_path(root, rel_root)
        if not runtime_root.exists():
            continue
        for p in sorted(runtime_root.rglob("*.py")):
            if p.name == "settings.py":
                continue
            rel = p.relative_to(root)
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
                s = line.strip()
                if not s.startswith("from spec_runner.settings import "):
                    continue
                imported = s.split("import ", 1)[1]
                names = [x.strip() for x in imported.split(",")]
                bad = [n for n in names if n.isupper() and n.startswith(("DEFAULT_", "ENV_"))]
                if bad:
                    violations.append(f"{rel}:{i}: banned settings constant import(s): {', '.join(bad)}")
    return violations


def _scan_runtime_assertions_via_spec_lang(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("assert_engine")
    if not isinstance(cfg, dict):
        return ["runtime.assertions_via_spec_lang requires harness.assert_engine mapping in governance spec"]
    files = cfg.get("files")
    if not isinstance(files, list) or not files:
        return ["harness.assert_engine.files must be a non-empty list"]
    for entry in files:
        if not isinstance(entry, dict):
            violations.append("harness.assert_engine.files entries must be mappings")
            continue
        rel = str(entry.get("path", "")).strip()
        if not rel:
            violations.append("harness.assert_engine.files[].path must be non-empty")
            continue
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing runtime assertion file")
            continue
        raw = p.read_text(encoding="utf-8")
        required = entry.get("required_tokens", [])
        forbidden = entry.get("forbidden_tokens", [])
        if not isinstance(required, list) or any(not isinstance(x, str) or not x.strip() for x in required):
            violations.append(f"{rel}:1: required_tokens must be list of non-empty strings")
            continue
        if not isinstance(forbidden, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden):
            violations.append(f"{rel}:1: forbidden_tokens must be list of non-empty strings")
            continue
        for tok in required:
            if tok not in raw:
                violations.append(f"{rel}:1: missing required token for spec-lang assertion path: {tok}")
        for tok in forbidden:
            if tok in raw:
                violations.append(f"{rel}:1: forbidden direct assertion token present: {tok}")
    return violations


def _scan_spec_lang_pure_no_effect_builtins(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("spec_lang_purity")
    if not isinstance(cfg, dict):
        return ["runtime.spec_lang_pure_no_effect_builtins requires harness.spec_lang_purity mapping in governance spec"]

    files = cfg.get("files")
    forbidden_tokens = cfg.get("forbidden_tokens")
    if not isinstance(files, list) or not files or any(not isinstance(x, str) or not x.strip() for x in files):
        return ["harness.spec_lang_purity.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(forbidden_tokens, list)
        or not forbidden_tokens
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return ["harness.spec_lang_purity.forbidden_tokens must be a non-empty list of non-empty strings"]

    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing spec-lang implementation file")
            continue
        raw = p.read_text(encoding="utf-8")
        for tok in forbidden_tokens:
            if tok in raw:
                violations.append(f"{rel}:1: forbidden side-effect token in spec-lang core: {tok}")
    return violations


def _scan_runtime_orchestration_policy_via_spec_lang(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("orchestration_policy")
    if not isinstance(cfg, dict):
        return [
            "runtime.orchestration_policy_via_spec_lang requires harness.orchestration_policy mapping in governance spec"
        ]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not isinstance(files, list) or not files:
        return ["harness.orchestration_policy.files must be a non-empty list"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.orchestration_policy.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(
        not isinstance(x, str) or not x.strip() for x in forbidden_tokens
    ):
        return ["harness.orchestration_policy.forbidden_tokens must be a list of non-empty strings"]

    violations: list[str] = []
    for entry in files:
        file_required = required_tokens
        file_forbidden = forbidden_tokens
        if isinstance(entry, str) and entry.strip():
            rel = entry.strip()
        elif isinstance(entry, dict):
            rel = str(entry.get("path", "")).strip()
            if not rel:
                violations.append("harness.orchestration_policy.files[].path must be non-empty")
                continue
            raw_required = entry.get("required_tokens")
            if raw_required is not None:
                if not isinstance(raw_required, list) or any(
                    not isinstance(x, str) or not x.strip() for x in raw_required
                ):
                    violations.append(f"{rel}:1: files[].required_tokens must be list of non-empty strings")
                    continue
                file_required = raw_required
            raw_forbidden = entry.get("forbidden_tokens")
            if raw_forbidden is not None:
                if not isinstance(raw_forbidden, list) or any(
                    not isinstance(x, str) or not x.strip() for x in raw_forbidden
                ):
                    violations.append(f"{rel}:1: files[].forbidden_tokens must be list of non-empty strings")
                    continue
                file_forbidden = raw_forbidden
        else:
            violations.append("harness.orchestration_policy.files entries must be strings or mappings")
            continue
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing orchestration file")
            continue
        raw = p.read_text(encoding="utf-8")
        for tok in file_required:
            if tok not in raw:
                violations.append(f"{rel}:1: missing required orchestration spec-lang token: {tok}")
        for tok in file_forbidden:
            if tok in raw:
                violations.append(f"{rel}:1: forbidden hardcoded orchestration verdict token present: {tok}")
    return violations


def _collect_conformance_fixture_ids(root: Path) -> set[str]:
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return set()
    with _SCAN_CACHE_LOCK:
        cache_key = (_SCAN_CACHE_TOKEN, str(cases_dir.resolve()))
        cached = _CONFORMANCE_IDS_CACHE.get(cache_key)
    if cached is not None:
        return set(cached)
    ids: set[str] = set()
    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        rid = str(spec.test.get("id", "")).strip()
        if rid:
            ids.add(rid)
    with _SCAN_CACHE_LOCK:
        _CONFORMANCE_IDS_CACHE[cache_key] = set(ids)
    return ids


def _scan_conformance_case_index_sync(root: Path) -> list[str]:
    violations: list[str] = []
    cases_dir = root / "specs/conformance/cases"
    fixture_ids = _collect_conformance_fixture_ids(root)
    index_path = cases_dir / "index.md"
    if not fixture_ids and not index_path.exists():
        return violations
    if not index_path.exists():
        return [f"{index_path.relative_to(root)}: missing conformance case index"]

    raw = index_path.read_text(encoding="utf-8")
    indexed_ids = set(re.findall(_CONFORMANCE_CASE_ID_PATTERN, raw))
    for rid in sorted(fixture_ids - indexed_ids):
        violations.append(f"{index_path.relative_to(root)}: missing id {rid}")
    for rid in sorted(indexed_ids - fixture_ids):
        violations.append(f"{index_path.relative_to(root)}: stale id {rid}")
    return violations


def _scan_conformance_purpose_warning_codes_sync(root: Path) -> list[str]:
    p = root / "specs/conformance/purpose_warning_codes.md"
    if not p.exists():
        return [f"{p.relative_to(root)}: missing purpose warning code doc"]
    raw = p.read_text(encoding="utf-8")
    doc_codes = set(re.findall(r"\bPUR\d{3}\b", raw))
    impl_codes = set(PURPOSE_WARNING_CODES)
    violations: list[str] = []
    for c in sorted(impl_codes - doc_codes):
        violations.append(f"{p.relative_to(root)}: missing code {c}")
    for c in sorted(doc_codes - impl_codes):
        violations.append(f"{p.relative_to(root)}: stale code {c}")
    return violations


def _scan_conformance_purpose_quality_gate(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("purpose_quality")
    if not isinstance(cfg, dict):
        return ["conformance.purpose_quality_gate requires harness.purpose_quality mapping in governance spec"]
    cases_rel = str(cfg.get("cases", "specs/conformance/cases")).strip() or "specs/conformance/cases"
    cases_dir = _join_contract_path(root, cases_rel)
    if not cases_dir.exists():
        return [f"{cases_rel}:1: conformance cases path does not exist"]
    max_total_warnings = int(cfg.get("max_total_warnings", 0))
    fail_on_policy_errors = bool(cfg.get("fail_on_policy_errors", True))
    fail_on_severity = str(cfg.get("fail_on_severity", "")).strip().lower()
    if fail_on_severity and fail_on_severity not in {"warn", "error"}:
        return ["harness.purpose_quality.fail_on_severity must be one of: warn, error"]
    payload = conformance_purpose_report_jsonable(cases_dir, repo_root=root)
    summary = payload.get("summary") or {}
    total_warning_count = int(summary.get("total_warning_count", 0))
    policy_error_count = int(summary.get("policy_error_count", 0))
    severity_counts = summary.get("warning_severity_counts") or {}
    warn_count = int(severity_counts.get("warn", 0))
    error_count = int(severity_counts.get("error", 0))
    violations: list[str] = []
    if fail_on_policy_errors and policy_error_count > 0:
        violations.append(
            f"specs/conformance/purpose_lint_v1.yaml:1: policy error count {policy_error_count} > 0"
        )
    if total_warning_count > max_total_warnings:
        violations.append(
            f"{cases_rel}:1: total purpose warnings {total_warning_count} exceed max_total_warnings={max_total_warnings}"
        )
    if fail_on_severity:
        at_or_above = error_count if fail_on_severity == "error" else (warn_count + error_count)
        if at_or_above > 0:
            violations.append(
                f"{cases_rel}:1: warnings at or above severity '{fail_on_severity}' = {at_or_above}"
            )
    return violations


def _scan_contract_coverage_threshold(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("contract_coverage")
    if not isinstance(cfg, dict):
        return ["contract.coverage_threshold requires harness.contract_coverage mapping in governance spec"]
    require_all_must = bool(cfg.get("require_all_must_covered", True))
    min_coverage_ratio = float(cfg.get("min_coverage_ratio", 0.0))
    payload = contract_coverage_jsonable(root)
    summary = payload.get("summary") or {}
    must_rules = int(summary.get("must_rules", 0))
    must_covered = int(summary.get("must_covered", 0))
    coverage_ratio = float(summary.get("coverage_ratio", 0.0))
    violations: list[str] = []
    if require_all_must and must_covered != must_rules:
        violations.append(
            "specs/contract/traceability_v1.yaml:1: "
            f"must_covered={must_covered} does not equal must_rules={must_rules}"
        )
    if coverage_ratio < min_coverage_ratio:
        violations.append(
            "specs/contract/traceability_v1.yaml:1: "
            f"coverage_ratio={coverage_ratio:.4f} below min_coverage_ratio={min_coverage_ratio:.4f}"
        )
    return violations


def _scan_spec_portability_metric(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    h = harness or {}
    cfg = h.get("portability_metric")
    if not isinstance(cfg, dict):
        return ["spec.portability_metric requires harness.portability_metric mapping in governance spec"]
    evaluate = None
    if "evaluate" in cfg:
        try:
            evaluate = normalize_evaluate(
                cfg.get("evaluate"), field="harness.portability_metric.evaluate"
            )
        except ValueError as exc:
            return [str(exc)]
    payload = spec_portability_report_jsonable(root, config=cfg)
    errs = payload.get("errors") or []
    if not isinstance(errs, list):
        return ["spec.portability_metric report contains invalid errors shape"]
    violations = [str(e) for e in errs if str(e).strip()]
    return _policy_outcome(
        subject=payload,
        evaluate=evaluate,
        policy_path="harness.portability_metric.evaluate",
        violations=violations,
    )


def _lookup_number_field(payload: object, dotted: str) -> float | None:
    cur = payload
    for part in dotted.split("."):
        key = part.strip()
        if not key:
            return None
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    if isinstance(cur, (int, float)):
        return float(cur)
    return None


def _scan_spec_portability_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("portability_non_regression")
    if not isinstance(cfg, dict):
        return ["spec.portability_non_regression requires harness.portability_non_regression mapping in governance spec"]

    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.portability_non_regression.baseline_path must be a non-empty string"]
    summary_fields = cfg.get("summary_fields")
    if (
        not isinstance(summary_fields, list)
        or not summary_fields
        or any(not isinstance(x, str) or not x.strip() for x in summary_fields)
    ):
        return ["harness.portability_non_regression.summary_fields must be a non-empty list of non-empty strings"]
    segment_fields = cfg.get("segment_fields", {})
    if not isinstance(segment_fields, dict):
        return ["harness.portability_non_regression.segment_fields must be a mapping"]
    for seg, fields in segment_fields.items():
        if not isinstance(seg, str) or not seg.strip():
            return ["harness.portability_non_regression.segment_fields keys must be non-empty strings"]
        if not isinstance(fields, list) or not fields or any(not isinstance(x, str) or not x.strip() for x in fields):
            return [
                f"harness.portability_non_regression.segment_fields.{seg} must be a non-empty list of non-empty strings"
            ]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.portability_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.portability_non_regression.epsilon must be >= 0"]

    report_config = cfg.get("portability_metric")
    if report_config is not None and not isinstance(report_config, dict):
        return ["harness.portability_non_regression.portability_metric must be a mapping when provided"]
    current = spec_portability_report_jsonable(root, config=report_config)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current portability report has errors: {str(e)}" for e in current_errs if str(e).strip()]

    baseline_file = _join_contract_path(root, baseline_path)
    if not baseline_file.exists():
        return [f"{baseline_path}:1: missing baseline portability metrics file"]
    try:
        baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{baseline_path}:1: invalid JSON baseline: {exc.msg} at line {exc.lineno} column {exc.colno}"]
    if not isinstance(baseline, dict):
        return [f"{baseline_path}:1: baseline payload must be a JSON object"]

    violations: list[str] = []
    for field in summary_fields:
        cur_val = _lookup_number_field(current, f"summary.{field}")
        base_val = _lookup_number_field(baseline, f"summary.{field}")
        if cur_val is None:
            violations.append(f"summary.{field}: missing numeric current metric")
            continue
        if base_val is None:
            violations.append(f"{baseline_path}: summary.{field}: missing numeric baseline metric")
            continue
        if cur_val + epsilon < base_val:
            violations.append(
                f"summary.{field}: regressed from baseline {base_val:.12g} to {cur_val:.12g}"
            )

    for segment, fields in segment_fields.items():
        for field in fields:
            cur_val = _lookup_number_field(current, f"segments.{segment}.{field}")
            base_val = _lookup_number_field(baseline, f"segments.{segment}.{field}")
            if cur_val is None:
                violations.append(f"segments.{segment}.{field}: missing numeric current metric")
                continue
            if base_val is None:
                violations.append(f"{baseline_path}: segments.{segment}.{field}: missing numeric baseline metric")
                continue
            if cur_val + epsilon < base_val:
                violations.append(
                    f"segments.{segment}.{field}: regressed from baseline {base_val:.12g} to {cur_val:.12g}"
                )
    return violations


def _scan_spec_lang_adoption_metric(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    h = harness or {}
    cfg = h.get("spec_lang_adoption")
    if not isinstance(cfg, dict):
        return ["spec.spec_lang_adoption_metric requires harness.spec_lang_adoption mapping in governance spec"]
    evaluate = None
    if "evaluate" in cfg:
        try:
            evaluate = normalize_evaluate(
                cfg.get("evaluate"), field="harness.spec_lang_adoption.evaluate"
            )
        except ValueError as exc:
            return [str(exc)]
    payload = spec_lang_adoption_report_jsonable(root, config=cfg)
    errs = payload.get("errors") or []
    if not isinstance(errs, list):
        return ["spec.spec_lang_adoption_metric report contains invalid errors shape"]
    violations = [str(e) for e in errs if str(e).strip()]
    return _policy_outcome(
        subject=payload,
        evaluate=evaluate,
        policy_path="harness.spec_lang_adoption.evaluate",
        violations=violations,
    )


def _scan_spec_lang_adoption_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("spec_lang_adoption_non_regression")
    if not isinstance(cfg, dict):
        return [
            "spec.spec_lang_adoption_non_regression requires harness.spec_lang_adoption_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.spec_lang_adoption_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("spec_lang_adoption")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.spec_lang_adoption_non_regression.spec_lang_adoption must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.spec_lang_adoption_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.spec_lang_adoption_non_regression.epsilon must be >= 0"]

    current = spec_lang_adoption_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current spec-lang adoption report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get("summary_fields"),
        segment_fields=cfg.get("segment_fields", {}),
        epsilon=epsilon,
    )


def _scan_conformance_evaluate_first_ratio_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("conformance_evaluate_first_non_regression")
    if not isinstance(cfg, dict):
        return [
            "conformance.evaluate_first_ratio_non_regression requires harness.conformance_evaluate_first_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.conformance_evaluate_first_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("spec_lang_adoption")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.conformance_evaluate_first_non_regression.spec_lang_adoption must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.conformance_evaluate_first_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.conformance_evaluate_first_non_regression.epsilon must be >= 0"]

    current = spec_lang_adoption_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current spec-lang adoption report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get(
            "summary_fields",
            {"overall_logic_self_contained_ratio": "non_decrease"},
        ),
        segment_fields=cfg.get(
            "segment_fields",
            {"conformance": {"mean_logic_self_contained_ratio": "non_decrease"}},
        ),
        epsilon=epsilon,
    )


def _scan_policy_library_usage_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("policy_library_usage_non_regression")
    if not isinstance(cfg, dict):
        return [
            "governance.policy_library_usage_non_regression requires harness.policy_library_usage_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.policy_library_usage_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("spec_lang_adoption")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.policy_library_usage_non_regression.spec_lang_adoption must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.policy_library_usage_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.policy_library_usage_non_regression.epsilon must be >= 0"]

    current = spec_lang_adoption_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current spec-lang adoption report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get(
            "summary_fields",
            {"governance_library_backed_policy_ratio": "non_decrease"},
        ),
        segment_fields=cfg.get(
            "segment_fields",
            {"governance": {"library_backed_policy_ratio": "non_decrease"}},
        ),
        epsilon=epsilon,
    )


def _scan_runner_independence_metric(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    h = harness or {}
    cfg = h.get("runner_independence")
    if not isinstance(cfg, dict):
        return ["runtime.runner_independence_metric requires harness.runner_independence mapping in governance spec"]
    evaluate = None
    if "evaluate" in cfg:
        try:
            evaluate = normalize_evaluate(
                cfg.get("evaluate"), field="harness.runner_independence.evaluate"
            )
        except ValueError as exc:
            return [str(exc)]
    payload = runner_independence_report_jsonable(root, config=cfg)
    errs = payload.get("errors") or []
    if not isinstance(errs, list):
        return ["runtime.runner_independence_metric report contains invalid errors shape"]
    violations = [str(e) for e in errs if str(e).strip()]
    return _policy_outcome(
        subject=payload,
        evaluate=evaluate,
        policy_path="harness.runner_independence.evaluate",
        violations=violations,
    )


def _scan_runner_independence_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("runner_independence_non_regression")
    if not isinstance(cfg, dict):
        return [
            "runtime.runner_independence_non_regression requires harness.runner_independence_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.runner_independence_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("runner_independence")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.runner_independence_non_regression.runner_independence must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.runner_independence_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.runner_independence_non_regression.epsilon must be >= 0"]

    current = runner_independence_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current runner independence report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get("summary_fields"),
        segment_fields=cfg.get("segment_fields", {}),
        epsilon=epsilon,
    )


def _scan_python_dependency_metric(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    h = harness or {}
    cfg = h.get("python_dependency")
    if not isinstance(cfg, dict):
        return ["runtime.python_dependency_metric requires harness.python_dependency mapping in governance spec"]
    evaluate = None
    if "evaluate" in cfg:
        try:
            evaluate = normalize_evaluate(
                cfg.get("evaluate"), field="harness.python_dependency.evaluate"
            )
        except ValueError as exc:
            return [str(exc)]
    payload = python_dependency_report_jsonable(root, config=cfg)
    errs = payload.get("errors") or []
    if not isinstance(errs, list):
        return ["runtime.python_dependency_metric report contains invalid errors shape"]
    violations = [str(e) for e in errs if str(e).strip()]
    return _policy_outcome(
        subject=payload,
        evaluate=evaluate,
        policy_path="harness.python_dependency.evaluate",
        violations=violations,
    )


def _scan_python_dependency_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("python_dependency_non_regression")
    if not isinstance(cfg, dict):
        return [
            "runtime.python_dependency_non_regression requires harness.python_dependency_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.python_dependency_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("python_dependency")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.python_dependency_non_regression.python_dependency must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.python_dependency_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.python_dependency_non_regression.epsilon must be >= 0"]

    current = python_dependency_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current python dependency report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get("summary_fields"),
        segment_fields=cfg.get("segment_fields", {}),
        epsilon=epsilon,
    )


def _scan_docs_operability_metric(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    h = harness or {}
    cfg = h.get("docs_operability")
    if not isinstance(cfg, dict):
        return ["docs.operability_metric requires harness.docs_operability mapping in governance spec"]
    evaluate = None
    if "evaluate" in cfg:
        try:
            evaluate = normalize_evaluate(
                cfg.get("evaluate"), field="harness.docs_operability.evaluate"
            )
        except ValueError as exc:
            return [str(exc)]
    payload = docs_operability_report_jsonable(root, config=cfg)
    errs = payload.get("errors") or []
    if not isinstance(errs, list):
        return ["docs.operability_metric report contains invalid errors shape"]
    violations = [str(e) for e in errs if str(e).strip()]
    return _policy_outcome(
        subject=payload,
        evaluate=evaluate,
        policy_path="harness.docs_operability.evaluate",
        violations=violations,
    )


def _scan_docs_operability_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("docs_operability_non_regression")
    if not isinstance(cfg, dict):
        return ["docs.operability_non_regression requires harness.docs_operability_non_regression mapping in governance spec"]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.docs_operability_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("docs_operability")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.docs_operability_non_regression.docs_operability must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.docs_operability_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.docs_operability_non_regression.epsilon must be >= 0"]

    current = docs_operability_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current docs operability report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get("summary_fields"),
        segment_fields=cfg.get("segment_fields", {}),
        epsilon=epsilon,
    )


def _scan_contract_assertions_metric(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    h = harness or {}
    cfg = h.get("contract_assertions")
    if not isinstance(cfg, dict):
        return ["spec.contract_assertions_metric requires harness.contract_assertions mapping in governance spec"]
    evaluate = None
    if "evaluate" in cfg:
        try:
            evaluate = normalize_evaluate(
                cfg.get("evaluate"), field="harness.contract_assertions.evaluate"
            )
        except ValueError as exc:
            return [str(exc)]
    payload = contract_assertions_report_jsonable(root, config=cfg)
    errs = payload.get("errors") or []
    if not isinstance(errs, list):
        return ["spec.contract_assertions_metric report contains invalid errors shape"]
    violations = [str(e) for e in errs if str(e).strip()]
    return _policy_outcome(
        subject=payload,
        evaluate=evaluate,
        policy_path="harness.contract_assertions.evaluate",
        violations=violations,
    )


def _scan_contract_assertions_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("contract_assertions_non_regression")
    if not isinstance(cfg, dict):
        return [
            "spec.contract_assertions_non_regression requires harness.contract_assertions_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.contract_assertions_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("contract_assertions")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.contract_assertions_non_regression.contract_assertions must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.contract_assertions_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.contract_assertions_non_regression.epsilon must be >= 0"]

    current = contract_assertions_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current contract assertions report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get("summary_fields"),
        segment_fields=cfg.get("segment_fields", {}),
        epsilon=epsilon,
    )


def _scan_objective_scorecard_metric(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    h = harness or {}
    cfg = h.get("objective_scorecard")
    if not isinstance(cfg, dict):
        return ["objective.scorecard_metric requires harness.objective_scorecard mapping in governance spec"]
    evaluate = None
    if "evaluate" in cfg:
        try:
            evaluate = normalize_evaluate(
                cfg.get("evaluate"), field="harness.objective_scorecard.evaluate"
            )
        except ValueError as exc:
            return [str(exc)]
    payload = objective_scorecard_report_jsonable(root, config=cfg)
    errs = payload.get("errors") or []
    if not isinstance(errs, list):
        return ["objective.scorecard_metric report contains invalid errors shape"]
    violations = [str(e) for e in errs if str(e).strip()]
    return _policy_outcome(
        subject=payload,
        evaluate=evaluate,
        policy_path="harness.objective_scorecard.evaluate",
        violations=violations,
    )


def _scan_objective_scorecard_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("objective_scorecard_non_regression")
    if not isinstance(cfg, dict):
        return [
            "objective.scorecard_non_regression requires harness.objective_scorecard_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.objective_scorecard_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("objective_scorecard")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.objective_scorecard_non_regression.objective_scorecard must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.objective_scorecard_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.objective_scorecard_non_regression.epsilon must be >= 0"]

    current = objective_scorecard_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current objective scorecard report has errors: {str(e)}" for e in current_errs if str(e).strip()]

    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs

    note_cfg = cfg.get("baseline_notes")
    if isinstance(note_cfg, dict):
        notes_path = str(note_cfg.get("path", "")).strip()
        baseline_paths = note_cfg.get("baseline_paths")
        if not notes_path:
            return ["harness.objective_scorecard_non_regression.baseline_notes.path must be non-empty"]
        if (
            not isinstance(baseline_paths, list)
            or not baseline_paths
            or any(not isinstance(x, str) or not x.strip() for x in baseline_paths)
        ):
            return [
                "harness.objective_scorecard_non_regression.baseline_notes.baseline_paths must be a non-empty list"
            ]
        note_violations = validate_metric_baseline_notes(
            root,
            notes_path=notes_path,
            baseline_paths=[str(x).strip() for x in baseline_paths],
        )
        if note_violations:
            return note_violations

    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get("summary_fields"),
        segment_fields=cfg.get("segment_fields", {}),
        epsilon=epsilon,
    )


def _scan_objective_tripwires_clean(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("objective_tripwires")
    if not isinstance(cfg, dict):
        return ["objective.tripwires_clean requires harness.objective_tripwires mapping in governance spec"]
    manifest_path = str(cfg.get("manifest_path", "")).strip() or "specs/governance/metrics/objective_manifest.yaml"
    cases_path = str(cfg.get("cases_path", "")).strip() or "specs/governance/cases"
    case_file_pattern = str(cfg.get("case_file_pattern", "")).strip() or SETTINGS.case.default_file_pattern

    manifest_file = _join_contract_path(root, manifest_path)
    if not manifest_file.exists():
        return [f"{manifest_path}:1: missing objective manifest"]
    try:
        manifest = yaml.safe_load(manifest_file.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{manifest_path}:1: invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return [f"{manifest_path}:1: manifest must be a mapping"]

    objectives = manifest.get("objectives")
    if not isinstance(objectives, list):
        return [f"{manifest_path}:1: objectives must be a list"]

    check_ids: set[str] = set()
    for row in objectives:
        if not isinstance(row, dict):
            continue
        tripwires = row.get("tripwires")
        if not isinstance(tripwires, list):
            continue
        for tw in tripwires:
            if not isinstance(tw, dict):
                continue
            cid = str(tw.get("check_id", "")).strip()
            if cid:
                check_ids.add(cid)

    if not check_ids:
        return [f"{manifest_path}:1: no tripwire check_id entries found"]

    cases_dir = _join_contract_path(root, cases_path)
    if not cases_dir.exists() or not cases_dir.is_dir():
        return [f"{cases_path}:1: cases path does not exist"]

    check_to_cases: dict[str, list[dict]] = {}
    for spec in iter_cases(cases_dir, file_pattern=case_file_pattern):
        case = spec.test if isinstance(spec.test, dict) else {}
        case_check = str(case.get("check", "")).strip()
        if case_check:
            check_to_cases.setdefault(case_check, []).append(case)

    violations: list[str] = []
    for cid in sorted(check_ids):
        if cid in {
            "objective.tripwires_clean",
            "objective.scorecard_metric",
            "objective.scorecard_non_regression",
        }:
            continue
        fn = _CHECKS.get(cid)
        if fn is None:
            violations.append(f"{manifest_path}:1: tripwire references unknown check id {cid}")
            continue
        cases = check_to_cases.get(cid, [])
        if not cases:
            violations.append(f"{cases_path}:1: no governance case found for tripwire check {cid}")
            continue
        matched = False
        for case in cases:
            harness_case_raw = case.get("harness")
            local_harness = dict(harness_case_raw) if isinstance(harness_case_raw, dict) else {}
            local_harness["root"] = str(root)
            params = inspect.signature(fn).parameters
            outcome = fn(root, harness=local_harness) if "harness" in params else fn(root)
            if isinstance(outcome, dict):
                out_violations = outcome.get("violations")
                case_violations = [str(v) for v in out_violations if str(v).strip()] if isinstance(out_violations, list) else []
            else:
                case_violations = [str(v) for v in outcome if str(v).strip()]
            if not case_violations:
                matched = True
                break
        if not matched:
            violations.append(f"tripwire check {cid} is failing in all matching governance cases")
    return violations


def _is_spec_opening_fence(line: str) -> tuple[str, int] | None:
    stripped = line.lstrip(" \t")
    if not stripped:
        return None
    if stripped[0] not in ("`", "~"):
        return None
    ch = stripped[0]
    i = 0
    while i < len(stripped) and stripped[i] == ch:
        i += 1
    if i < 3:
        return None
    info = stripped[i:].strip().lower().split()
    if "contract-spec" not in info:
        return None
    if "yaml" not in info and "yml" not in info:
        return None
    return ch, i


def _is_closing_fence(line: str, *, ch: str, min_len: int) -> bool:
    stripped = line.lstrip(" \t").rstrip()
    if not stripped or stripped[0] != ch:
        return False
    i = 0
    while i < len(stripped) and stripped[i] == ch:
        i += 1
    return i >= min_len and i == len(stripped)


def _is_markdown_fence_opening(line: str) -> tuple[str, int, str] | None:
    stripped = line.lstrip(" \t")
    if not stripped:
        return None
    if stripped[0] not in ("`", "~"):
        return None
    ch = stripped[0]
    i = 0
    while i < len(stripped) and stripped[i] == ch:
        i += 1
    if i < 3:
        return None
    return ch, i, stripped[i:].strip()


def _scan_conformance_case_doc_style_guard(root: Path) -> list[str]:
    violations: list[str] = []
    policy, policy_errs, _ = load_purpose_lint_policy(root)
    violations.extend(policy_errs)
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return violations

    global_ids: set[str] = set()
    for p in sorted(cases_dir.glob(SETTINGS.case.default_file_pattern)):
        raw = p.read_text(encoding="utf-8")
        lines = raw.splitlines()
        i = 0
        ids_in_file: list[str] = []
        while i < len(lines):
            opening = _is_spec_opening_fence(lines[i])
            if not opening:
                i += 1
                continue
            ch, fence_len = opening
            start = i
            i += 1
            block_lines: list[str] = []
            while i < len(lines) and not _is_closing_fence(lines[i], ch=ch, min_len=fence_len):
                block_lines.append(lines[i])
                i += 1
            if len(block_lines) > _CONFORMANCE_MAX_BLOCK_LINES:
                violations.append(
                    f"{p.relative_to(root)}:{start + 1}: block exceeds {_CONFORMANCE_MAX_BLOCK_LINES} lines"
                )
            payload = yaml.safe_load("\n".join(block_lines)) if block_lines else None
            if isinstance(payload, list):
                violations.append(f"{p.relative_to(root)}:{start + 1}: one case per contract-spec block required")
            if isinstance(payload, dict):
                rid = str(payload.get("id", "")).strip()
                purpose = str(payload.get("purpose", "")).strip()
                cfg, cfg_errs = resolve_purpose_lint_config(payload, policy)
                for e in cfg_errs:
                    violations.append(f"{p.relative_to(root)}:{start + 1}: {e}")
                if not purpose:
                    violations.append(f"{p.relative_to(root)}:{start + 1}: case must include non-empty purpose")
                title = str(payload.get("title", "")).strip()
                for w in purpose_quality_warnings(title, purpose, cfg, honor_enabled=True):
                    if w == "purpose duplicates title":
                        violations.append(
                            f"{p.relative_to(root)}:{start + 1}: purpose must add context beyond title for case {rid or '<unknown>'}"
                        )
                    elif w.startswith("purpose word count "):
                        violations.append(
                            f"{p.relative_to(root)}:{start + 1}: case purpose must be at least {int(cfg.get('min_words', 8))} words for case {rid or '<unknown>'}"
                        )
                    elif w.startswith("purpose contains placeholder token(s): "):
                        violations.append(
                            f"{p.relative_to(root)}:{start + 1}: purpose contains placeholder token(s) {w.split(': ', 1)[1]} for case {rid or '<unknown>'}"
                        )
                if rid:
                    ids_in_file.append(rid)
                    if rid in global_ids:
                        violations.append(f"{p.relative_to(root)}:{start + 1}: duplicate conformance case id across files: {rid}")
                    global_ids.add(rid)
                    prev_idx = start - 1
                    while prev_idx >= 0 and not lines[prev_idx].strip():
                        prev_idx -= 1
                    expected_heading = f"## {rid}"
                    if prev_idx < 0 or lines[prev_idx].strip() != expected_heading:
                        violations.append(
                            f"{p.relative_to(root)}:{start + 1}: expected heading '{expected_heading}' immediately before block"
                        )
            i += 1
        if ids_in_file != sorted(ids_in_file):
            violations.append(f"{p.relative_to(root)}: case ids must be sorted within file")
    return violations


def _scan_regex_doc_sync(root: Path) -> list[str]:
    violations: list[str] = []
    assertions_doc = root / "specs/contract/03_assertions.md"
    schema_doc = root / "specs/schema/schema_v1.md"
    policy_doc = root / "specs/contract/policy_v1.yaml"
    if not assertions_doc.exists() or not schema_doc.exists() or not policy_doc.exists():
        return violations

    assertions_text = assertions_doc.read_text(encoding="utf-8")
    schema_text = schema_doc.read_text(encoding="utf-8")
    policy_text = policy_doc.read_text(encoding="utf-8")

    if _REGEX_PROFILE_DOC not in assertions_text:
        violations.append(
            "specs/contract/03_assertions.md: missing regex portability profile reference"
        )
    if _REGEX_PROFILE_DOC not in schema_text:
        violations.append(
            "specs/schema/schema_v1.md: missing regex portability profile reference"
        )
    if _REGEX_PROFILE_DOC not in policy_text:
        violations.append(
            "specs/contract/policy_v1.yaml: missing regex portability profile reference"
        )

    for tok in _ASSERTION_OPERATOR_DOC_SYNC_TOKENS:
        if tok not in assertions_text:
            violations.append(f"specs/contract/03_assertions.md: missing operator token {tok}")
        if tok not in schema_text:
            violations.append(f"specs/schema/schema_v1.md: missing operator token {tok}")
    return violations


def _scan_assert_universal_core_sync(root: Path) -> list[str]:
    violations: list[str] = []
    required_tokens_by_file: dict[str, tuple[object, ...]] = {
        "specs/schema/schema_v1.md": (
            "universal core",
            "evaluate",
            ("conformance/cases/*.spec.md", "conformance/cases/**/*.spec.md"),
            ("governance/cases/*.spec.md", "governance/cases/**/*.spec.md"),
            "must use",
        ),
        "specs/contract/03_assertions.md": (
            "universal core",
            "evaluate",
            ("conformance/cases/*.spec.md", "conformance/cases/**/*.spec.md"),
            ("governance/cases/*.spec.md", "governance/cases/**/*.spec.md"),
            "must use",
        ),
        "specs/contract/09_internal_representation.md": (
            "universal core",
            "evaluate",
            "evaluate-only",
            "conformance",
            "governance",
        ),
    }
    for rel in _ASSERT_UNIVERSAL_DOC_FILES:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing assertion universal-core doc")
            continue
        lower = p.read_text(encoding="utf-8").lower()
        for tok in required_tokens_by_file.get(rel, ()):
            if isinstance(tok, tuple):
                if not any(str(opt) in lower for opt in tok):
                    joined = " or ".join(repr(str(opt)) for opt in tok)
                    violations.append(f"{rel}:1: missing universal-core token ({joined})")
                continue
            if str(tok) not in lower:
                violations.append(f"{rel}:1: missing universal-core token {tok!r}")
    return violations


def _scan_assert_sugar_compile_only_sync(root: Path) -> list[str]:
    violations: list[str] = []
    compiler_path = root / "runners/python/spec_runner/compiler.py"
    assertions_path = root / "runners/python/spec_runner/assertions.py"
    if not compiler_path.exists():
        violations.append("runners/python/spec_runner/compiler.py:1: missing compiler implementation")
        return violations
    if not assertions_path.exists():
        violations.append("runners/python/spec_runner/assertions.py:1: missing assertions implementation")
        return violations

    compiler_raw = compiler_path.read_text(encoding="utf-8")
    assertions_raw = assertions_path.read_text(encoding="utf-8")

    compiler_required = (
        'supported = {"evaluate"}',
        'op == "evaluate"',
    )
    for tok in compiler_required:
        if tok not in compiler_raw:
            violations.append(
                f"runners/python/spec_runner/compiler.py:1: missing compile-only sugar mapping token {tok}"
            )

    compiler_forbidden = (
        "if type_name == ",
        "allowed = {",
        'op == "contain"',
        'op == "regex"',
        'op == "json_type"',
        'op == "exists"',
    )
    for tok in compiler_forbidden:
        if tok in compiler_raw:
            violations.append(
                f"runners/python/spec_runner/compiler.py:1: forbidden per-type operator allowlist token {tok}"
            )

    if "eval_predicate(" not in assertions_raw:
        violations.append(
            "runners/python/spec_runner/assertions.py:1: missing spec-lang predicate evaluation call"
        )
    return violations


def _scan_assert_type_contract_subject_semantics_sync(root: Path) -> list[str]:
    violations: list[str] = []
    files = (
        "specs/contract/04_harness.md",
        "specs/contract/types/text_file.md",
        "specs/contract/types/cli_run.md",
        "specs/contract/types/api_http.md",
    )
    required_tokens = {
        "specs/contract/04_harness.md": ("subject", "availability", "shape"),
        "specs/contract/types/text_file.md": ("subject semantics",),
        "specs/contract/types/cli_run.md": ("target semantics",),
        "specs/contract/types/api_http.md": ("target semantics",),
    }
    forbidden_tokens = {
        "specs/contract/types/cli_run.md": ("only supports `exists`",),
    }
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing type/harness contract doc")
            continue
        lower = p.read_text(encoding="utf-8").lower()
        for tok in required_tokens.get(rel, ()):
            if tok not in lower:
                violations.append(f"{rel}:1: missing required subject-semantics token {tok!r}")
        for tok in forbidden_tokens.get(rel, ()):
            if tok in lower:
                violations.append(f"{rel}:1: forbidden per-operator allowlist token {tok!r}")
    return violations


def _scan_assert_compiler_schema_matrix_sync(root: Path) -> list[str]:
    violations: list[str] = []
    compiler = root / "runners/python/spec_runner/compiler.py"
    schema = root / "specs/schema/schema_v1.md"
    assertions_doc = root / "specs/contract/03_assertions.md"
    if not compiler.exists() or not schema.exists() or not assertions_doc.exists():
        return ["assert.compiler_schema_matrix_sync requires compiler + schema + assertion contract docs"]
    compiler_raw = compiler.read_text(encoding="utf-8")
    schema_lower = schema.read_text(encoding="utf-8").lower()
    assertions_lower = assertions_doc.read_text(encoding="utf-8").lower()

    if "universal core operator" not in schema_lower:
        violations.append("specs/schema/schema_v1.md:1: missing universal core operator section")
    if "only universal assertion operator contract" not in assertions_lower:
        violations.append("specs/contract/03_assertions.md:1: missing universal evaluate-only contract text")
    if 'supported = {"evaluate"}' not in compiler_raw:
        violations.append("runners/python/spec_runner/compiler.py:1: compiler operator matrix does not match universal-core contract")
    if "if type_name == " in compiler_raw:
        violations.append("runners/python/spec_runner/compiler.py:1: forbidden per-type operator matrix branching present")
    return violations


def _scan_assert_spec_lang_builtin_surface_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("spec_lang_builtin_sync")
    if not isinstance(cfg, dict):
        return [
            "assert.spec_lang_builtin_surface_sync requires harness.spec_lang_builtin_sync mapping in governance spec"
        ]
    required_ops = cfg.get("required_ops")
    if (
        not isinstance(required_ops, list)
        or not required_ops
        or any(not isinstance(x, str) or not x.strip() for x in required_ops)
    ):
        return ["harness.spec_lang_builtin_sync.required_ops must be a non-empty list of non-empty strings"]
    required = {str(x).strip() for x in required_ops if str(x).strip()}

    stdlib_report = spec_lang_stdlib_report_jsonable(root)
    profile_symbols = {
        str(k).strip()
        for k in (stdlib_report.get("profile_symbols") or {}).keys()
        if str(k).strip()
    }
    if not profile_symbols:
        # Unit-test fallback: allow contract-only surface checks when stdlib profile
        # fixture is not present.
        contract = root / "specs/contract/03b_spec_lang_v1.md"
        if not contract.exists():
            return [
                "assert.spec_lang_builtin_surface_sync requires stdlib profile or contract docs with builtin symbols"
            ]
        contract_raw = contract.read_text(encoding="utf-8")
        profile_symbols = {
            str(x).strip()
            for x in re.findall(r"`([a-z0-9_.]+)`", contract_raw)
            if str(x).strip()
        }
        profile_symbols -= {"fn", "if", "let", "call", "var"}
    unknown = sorted(required - profile_symbols)
    for op in unknown:
        violations.append(
            f"specs/schema/spec_lang_stdlib_profile_v1.yaml:1: required_ops entry is not in stdlib profile: {op}"
        )
    required = {op for op in required if op in profile_symbols}
    if not required:
        return violations

    py_ops = set(_builtin_arity_table().keys())
    py_missing = sorted(required - py_ops)
    for op in py_missing:
        violations.append(f"runners/python/spec_runner/spec_lang.py:1: missing builtin documented in contract: {op}")
    php_ops = {
        str(x).strip()
        for x in (stdlib_report.get("php_symbols") or [])
        if str(x).strip()
    }
    if not php_ops:
        php_impl = root / "runners/php/spec_runner.php"
        if php_impl.exists():
            php_raw = php_impl.read_text(encoding="utf-8")
            php_ops = {op for op in required if f"'{op}'" in php_raw}
    php_missing = sorted(required - php_ops)
    for op in php_missing:
        violations.append(f"runners/php/spec_runner.php:1: missing builtin documented in contract: {op}")

    return violations


def _scan_spec_lang_stdlib_profile_complete(root: Path) -> list[str]:
    payload = spec_lang_stdlib_report_jsonable(root)
    violations: list[str] = []
    errors = payload.get("errors") or []
    for err in errors:
        s = str(err).strip()
        if s:
            violations.append(s)
    for item in payload.get("missing_in_python") or []:
        violations.append(f"spec_lang stdlib profile missing in python: {item}")
    for item in payload.get("missing_in_php") or []:
        violations.append(f"spec_lang stdlib profile missing in php: {item}")
    for item in payload.get("arity_mismatch") or []:
        violations.append(f"spec_lang stdlib profile arity mismatch: {item}")
    return violations


def _scan_spec_lang_stdlib_py_php_parity(root: Path) -> list[str]:
    payload = spec_lang_stdlib_report_jsonable(root)
    violations: list[str] = []
    for item in payload.get("missing_in_python") or []:
        violations.append(f"python missing stdlib symbol: {item}")
    for item in payload.get("missing_in_php") or []:
        violations.append(f"php missing stdlib symbol: {item}")
    return violations


def _scan_spec_lang_stdlib_docs_sync(root: Path) -> list[str]:
    payload = spec_lang_stdlib_report_jsonable(root)
    violations: list[str] = []
    for item in payload.get("docs_sync_missing") or []:
        violations.append(str(item))
    return violations


def _scan_spec_lang_stdlib_conformance_coverage(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("stdlib_conformance")
    if not isinstance(cfg, dict):
        return [
            "spec_lang.stdlib_conformance_coverage requires harness.stdlib_conformance mapping in governance spec"
        ]
    required_paths = cfg.get("required_paths")
    if (
        not isinstance(required_paths, list)
        or not required_paths
        or any(not isinstance(x, str) or not x.strip() for x in required_paths)
    ):
        return ["harness.stdlib_conformance.required_paths must be a non-empty list of paths"]
    violations: list[str] = []
    for raw in required_paths:
        rel = str(raw).strip()
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}: missing required conformance file")
    return violations


def _scan_assert_subject_profiles_declared(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    required_paths = (
        _SUBJECT_PROFILE_CONTRACT_DOC,
        _SUBJECT_PROFILE_SCHEMA_DOC,
        *_SUBJECT_PROFILE_TYPE_DOCS,
        "specs/libraries/domain/index.md",
        *_SUBJECT_PROFILE_DOMAIN_LIBS,
    )
    for rel in required_paths:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing required subject-profile artifact")
    return violations


def _scan_assert_subject_profiles_json_only(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    schema = _join_contract_path(root, _SUBJECT_PROFILE_SCHEMA_DOC)
    evaluator = _join_contract_path(root, "runners/python/spec_runner/spec_lang.py")
    if not schema.exists():
        return [f"{_SUBJECT_PROFILE_SCHEMA_DOC}:1: missing subject profile schema"]
    if not evaluator.exists():
        return ["runners/python/spec_runner/spec_lang.py:1: missing evaluator implementation"]
    schema_raw = schema.read_text(encoding="utf-8")
    eval_raw = evaluator.read_text(encoding="utf-8")
    required_schema_tokens = ("json_core_only: true", "non_json_native_values_must_be_projected: true")
    for tok in required_schema_tokens:
        if tok not in schema_raw:
            violations.append(f"{_SUBJECT_PROFILE_SCHEMA_DOC}:1: missing required JSON-core token {tok}")
    required_eval_tokens = (
        "def _is_json_value(",
        "spec_lang subject must be a JSON value",
    )
    for tok in required_eval_tokens:
        if tok not in eval_raw:
            violations.append(f"runners/python/spec_runner/spec_lang.py:1: missing JSON-core evaluator token {tok}")
    return violations


def _scan_assert_domain_profiles_docs_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    schema = _join_contract_path(root, _SUBJECT_PROFILE_SCHEMA_DOC)
    if not schema.exists():
        return [f"{_SUBJECT_PROFILE_SCHEMA_DOC}:1: missing subject profile schema"]
    schema_raw = schema.read_text(encoding="utf-8")
    required_profile_ids = {
        "python_profile.md": "python.generic/v1",
        "php_profile.md": "php.generic/v1",
        "http_profile.md": "api.http/v1",
        "markdown_profile.md": "markdown.generic/v1",
        "makefile_profile.md": "makefile.generic/v1",
    }
    for rel in _SUBJECT_PROFILE_TYPE_DOCS:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing profile contract doc")
            continue
        raw = p.read_text(encoding="utf-8")
        profile_id = required_profile_ids.get(Path(rel).name)
        if profile_id and profile_id not in raw:
            violations.append(f"{rel}:1: missing profile id token {profile_id}")
        if profile_id and profile_id not in schema_raw:
            violations.append(f"{_SUBJECT_PROFILE_SCHEMA_DOC}:1: missing profile id {profile_id}")
    return violations


def _scan_assert_domain_library_usage_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    cases_dir = root / "specs/conformance/cases/core"
    if not cases_dir.exists():
        return ["specs/conformance/cases/core:1: missing conformance core cases directory"]
    target_file = cases_dir / "domain_libraries.spec.md"
    if not target_file.exists():
        return [f"{target_file.relative_to(root)}:1: missing domain library conformance coverage case"]
    found = False
    for _doc_path, case in load_external_cases(target_file, formats={"md"}):
        if str(case.get("id", "")).strip().startswith("DCCONF-DOMAIN-LIB-"):
            found = True
            harness_map = case.get("harness")
            if not isinstance(harness_map, dict):
                violations.append(
                    f"{target_file.relative_to(root)}: case {case.get('id', '<unknown>')} missing harness mapping"
                )
                continue
            lib_paths = _collect_chain_library_refs(case)
            if not any("/specs/libraries/domain/" in str(x) for x in lib_paths):
                violations.append(
                    f"{target_file.relative_to(root)}: case {case.get('id', '<unknown>')} missing domain library path in harness.chain steps"
                )
    if not found:
        violations.append(f"{target_file.relative_to(root)}:1: expected DCCONF-DOMAIN-LIB-* cases")
    return violations


def _scan_assert_adapter_projection_contract_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    required = {
        "runners/python/spec_runner/harnesses/text_file.py": ("context_json", "profile_id", "profile_version"),
        "runners/python/spec_runner/harnesses/cli_run.py": ("context_json", "profile_id", "profile_version"),
        "runners/python/spec_runner/harnesses/api_http.py": ("context_json", "profile_id", "profile_version"),
    }
    for rel, tokens in required.items():
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing adapter for projection sync check")
            continue
        raw = p.read_text(encoding="utf-8")
        for tok in tokens:
            if tok not in raw:
                violations.append(f"{rel}:1: missing adapter projection token {tok}")
    return violations


def _scan_schema_registry_valid(root: Path) -> list[str]:
    violations: list[str] = []
    schema = _join_contract_path(root, _SCHEMA_REGISTRY_SCHEMA)
    registry_root = _join_contract_path(root, _SCHEMA_REGISTRY_ROOT)
    contract_doc = _join_contract_path(root, _SCHEMA_REGISTRY_CONTRACT_DOC)
    if not schema.exists():
        violations.append(f"{_SCHEMA_REGISTRY_SCHEMA}:1: missing registry schema")
    if not registry_root.exists():
        violations.append(f"{_SCHEMA_REGISTRY_ROOT}:1: missing registry root")
    if not contract_doc.exists():
        violations.append(f"{_SCHEMA_REGISTRY_CONTRACT_DOC}:1: missing registry contract doc")
    compiled, errs = compile_registry(root)
    for err in errs:
        violations.append(err)
    if compiled is None:
        return violations
    return violations


def _scan_schema_registry_compiled_sync(root: Path) -> list[str]:
    compiled, errs = compile_registry(root)
    if compiled is None:
        return errs
    artifact = _join_contract_path(root, _SCHEMA_REGISTRY_COMPILED_ARTIFACT)
    if not artifact.exists():
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(json.dumps(compiled, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return []
    try:
        existing = json.loads(artifact.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"{_SCHEMA_REGISTRY_COMPILED_ARTIFACT}:1: invalid JSON: {exc}"]
    if existing != compiled:
        return [f"{_SCHEMA_REGISTRY_COMPILED_ARTIFACT}:1: stale compiled registry artifact"]
    return []


def _scan_schema_registry_docs_sync(root: Path) -> list[str]:
    schema_doc = _join_contract_path(root, "specs/schema/schema_v1.md")
    if not schema_doc.exists():
        return ["specs/schema/schema_v1.md:1: missing schema doc"]
    raw = schema_doc.read_text(encoding="utf-8")
    required_tokens = (
        "BEGIN GENERATED: SCHEMA_REGISTRY_V1",
        "END GENERATED: SCHEMA_REGISTRY_V1",
        "Generated Registry Snapshot",
    )
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in raw:
            violations.append(f"specs/schema/schema_v1.md:1: missing token {tok}")
    if _SCHEMA_REGISTRY_ROOT not in raw:
        violations.append(f"specs/schema/schema_v1.md:1: missing registry root token {_SCHEMA_REGISTRY_ROOT}")
    return violations


def _scan_schema_no_prose_only_rules(root: Path) -> list[str]:
    violations: list[str] = []
    contract_doc = _join_contract_path(root, _SCHEMA_REGISTRY_CONTRACT_DOC)
    schema_doc = _join_contract_path(root, "specs/schema/schema_v1.md")
    for rel, p in (
        (_SCHEMA_REGISTRY_CONTRACT_DOC, contract_doc),
        ("specs/schema/schema_v1.md", schema_doc),
    ):
        if not p.exists():
            violations.append(f"{rel}:1: missing required doc")
            continue
        lower = p.read_text(encoding="utf-8").lower()
        if "source of truth" not in lower:
            violations.append(f"{rel}:1: missing source-of-truth wording")
        if "registry" not in lower:
            violations.append(f"{rel}:1: missing registry wording")
    return violations


def _scan_schema_type_profiles_complete(root: Path) -> list[str]:
    compiled, errs = compile_registry(root)
    if compiled is None:
        return errs
    type_profiles = compiled.get("type_profiles") or {}
    required = {
        "cli.run",
        "text.file",
        "governance.check",
        "spec.export",
        "orchestration.run",
    }
    violations: list[str] = []
    for ctype in sorted(required):
        if ctype not in type_profiles:
            violations.append(f"{_SCHEMA_REGISTRY_ROOT}:1: missing required type profile for {ctype}")
    return violations


def _iter_orchestration_cases(root: Path):
    base = _join_contract_path(root, "specs")
    if not base.exists():
        return
    for spec in iter_spec_doc_tests(base):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() == "orchestration.run":
            yield spec.doc_path, case


def _load_tool_registry(root: Path, rel: str) -> tuple[list[dict], list[str]]:
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [], [f"{rel}:1: missing tools registry"]
    payload = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return [], [f"{rel}:1: tools registry must be a mapping"]
    tools = payload.get("tools")
    if not isinstance(tools, list):
        return [], [f"{rel}:1: tools must be a list"]
    out: list[dict] = []
    violations: list[str] = []
    for i, item in enumerate(tools):
        if not isinstance(item, dict):
            violations.append(f"{rel}:1: tools[{i}] must be a mapping")
            continue
        out.append(item)
    return out, violations


def _scan_orchestration_ops_symbol_grammar(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    for rel in _ORCHESTRATION_TOOLS_FILES:
        tools, errs = _load_tool_registry(root, rel)
        violations.extend(errs)
        for idx, tool in enumerate(tools):
            symbol = str(tool.get("effect_symbol", "")).strip()
            if not symbol:
                continue
            for diag in validate_ops_symbol(symbol, context=f"{rel}:tools[{idx}]"):
                violations.append(f"{rel}:1: {diag.code}: {diag.message}")
    return violations


def _scan_orchestration_ops_legacy_underscore_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    for rel in _ORCHESTRATION_TOOLS_FILES:
        tools, errs = _load_tool_registry(root, rel)
        violations.extend(errs)
        for idx, tool in enumerate(tools):
            symbol = str(tool.get("effect_symbol", "")).strip()
            if symbol and is_legacy_underscore_form(symbol):
                violations.append(
                    f"{rel}:1: ORCHESTRATION_OPS_UNDERSCORE_LEGACY_FORBIDDEN: tools[{idx}] uses forbidden symbol {symbol}"
                )
    return violations


def _scan_orchestration_ops_registry_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    tool_ids: set[str] = set()
    for rel in _ORCHESTRATION_TOOLS_FILES:
        tools, errs = _load_tool_registry(root, rel)
        violations.extend(errs)
        for idx, tool in enumerate(tools):
            for diag in validate_ops_registry_entry(tool, where=f"{rel}:tools[{idx}]"):
                violations.append(f"{rel}:1: {diag.code}: {diag.message}")
            tool_id = str(tool.get("tool_id", "")).strip()
            if not tool_id:
                violations.append(f"{rel}:1: ORCHESTRATION_OPS_REGISTRY_DECLARED_REQUIRED: tools[{idx}] missing tool_id")
                continue
            tool_ids.add(tool_id)
            for key in ("input_schema_ref", "output_schema_ref", "stability", "since"):
                if not str(tool.get(key, "")).strip():
                    violations.append(f"{rel}:1: ORCHESTRATION_OPS_REGISTRY_DECLARED_REQUIRED: tool {tool_id} missing {key}")
    # Any orchestration.run case should reference a known tool_id.
    for doc_path, case in _iter_orchestration_cases(root):
        orch = dict((case.get("harness") or {}).get("orchestration") or {})
        tool_id = str(orch.get("tool_id", "")).strip()
        if tool_id and tool_id not in tool_ids:
            rel = doc_path.relative_to(root).as_posix()
            violations.append(f"{rel}:1: ORCHESTRATION_OPS_REGISTRY_DECLARED_REQUIRED: unknown tool_id {tool_id}")
    return violations


def _scan_orchestration_ops_capability_bindings(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    capability_by_tool: dict[str, str] = {}
    for rel in _ORCHESTRATION_TOOLS_FILES:
        tools, errs = _load_tool_registry(root, rel)
        violations.extend(errs)
        for tool in tools:
            tool_id = str(tool.get("tool_id", "")).strip()
            cap = str(tool.get("capability_id", "")).strip()
            if tool_id and cap:
                capability_by_tool[tool_id] = cap
    for doc_path, case in _iter_orchestration_cases(root):
        orch = dict((case.get("harness") or {}).get("orchestration") or {})
        tool_id = str(orch.get("tool_id", "")).strip()
        if not tool_id:
            continue
        required_cap = capability_by_tool.get(tool_id, "")
        caps = orch.get("capabilities") or []
        if not isinstance(caps, list):
            rel = doc_path.relative_to(root).as_posix()
            violations.append(f"{rel}:1: ORCHESTRATION_OPS_CAPABILITY_BINDING_REQUIRED: harness.orchestration.capabilities must be a list")
            continue
        cap_set = {str(x).strip() for x in caps if str(x).strip()}
        if required_cap and required_cap not in cap_set:
            rel = doc_path.relative_to(root).as_posix()
            violations.append(
                f"{rel}:1: ORCHESTRATION_OPS_CAPABILITY_BINDING_REQUIRED: tool {tool_id} requires capability {required_cap}"
            )
    return violations


def _scan_current_spec_only_contract(root: Path) -> list[str]:
    violations: list[str] = []
    patterns = [re.compile(p, re.IGNORECASE) for p in _CURRENT_SPEC_FORBIDDEN_PATTERNS]
    for rel in (*_CURRENT_SPEC_ONLY_DOCS, *_CURRENT_SPEC_ONLY_CODE_FILES):
        p = _join_contract_path(root, rel)
        if not p.exists():
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
            for pat in patterns:
                if pat.search(line):
                    violations.append(
                        f"{rel}:{i}: forbidden pre-current-spec reference matched /{pat.pattern}/"
                    )
                    break
    return violations


def _iter_mapping_key_paths(value: object, *, path: str = ""):
    if isinstance(value, dict):
        for k, v in value.items():
            key = str(k)
            next_path = f"{path}.{key}" if path else key
            yield next_path, key
            yield from _iter_mapping_key_paths(v, path=next_path)
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            next_path = f"{path}[{idx}]" if path else f"[{idx}]"
            yield from _iter_mapping_key_paths(item, path=next_path)


def _scan_current_spec_policy_key_names(root: Path) -> list[str]:
    violations: list[str] = []
    specs_root = root / "specs"
    if not specs_root.exists():
        return violations
    for p in sorted(specs_root.rglob(SETTINGS.case.default_file_pattern)):
        try:
            tests = list(iter_spec_doc_tests(p.parent, file_pattern=p.name))
        except Exception as exc:  # noqa: BLE001
            rel = p.relative_to(root)
            violations.append(f"{rel}:1: unable to parse contract-spec blocks: {exc}")
            continue
        for spec in tests:
            case_id = str(spec.test.get("id", "<unknown>")).strip() or "<unknown>"
            for key_path, key in _iter_mapping_key_paths(spec.test):
                if key.endswith("_expr"):
                    rel = p.relative_to(root)
                    violations.append(
                        f"{rel}: case {case_id} uses unsupported policy-expression key at {key_path}; "
                        "use 'evaluate'"
                    )
    return violations


def _scan_governance_evaluate_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("policy_requirements") or h.get("policy_forbidden")
    if not isinstance(cfg, dict):
        return ["runtime.evaluate_forbidden requires harness.policy_forbidden mapping in governance spec"]
    cases_rel = str(cfg.get("cases_path", "specs/governance/cases")).strip() or "specs/governance/cases"
    case_pattern = str(cfg.get("case_file_pattern", SETTINGS.case.default_file_pattern)).strip() or SETTINGS.case.default_file_pattern
    ignore_checks_raw = cfg.get("ignore_checks", [])
    if not isinstance(ignore_checks_raw, list) or any(not isinstance(x, str) for x in ignore_checks_raw):
        return ["harness.policy_requirements.ignore_checks must be a list of strings"]
    ignore_checks = {x.strip() for x in ignore_checks_raw if x.strip()}

    cases_dir = _join_contract_path(root, cases_rel)
    if not cases_dir.exists():
        return [f"{cases_rel}:1: governance cases path does not exist"]

    violations: list[str] = []
    for spec in iter_cases(cases_dir, file_pattern=case_pattern):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "governance.check":
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        check_id = str(case.get("check", "")).strip()
        if check_id in ignore_checks:
            continue
        harness_map = case.get("harness")
        if not isinstance(harness_map, dict):
            violations.append(f"{spec.doc_path.relative_to(root)}: case {case_id} missing harness mapping")
            continue
        if "evaluate" in harness_map:
            violations.append(
                f"{spec.doc_path.relative_to(root)}: case {case_id} check {check_id} uses forbidden harness.evaluate"
            )
    return violations


def _scan_governance_policy_library_usage_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del root, harness
    return []


def _scan_conformance_library_policy_usage_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del root, harness
    return []


def _scan_governance_extractor_only_no_verdict_branching(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("extractor_policy")
    if not isinstance(cfg, dict):
        return ["governance.extractor_only_no_verdict_branching requires harness.extractor_policy mapping in governance spec"]
    rel = str(cfg.get("path", "runners/python/spec_runner/governance_runtime.py")).strip() or "runners/python/spec_runner/governance_runtime.py"
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing governance runtime module"]
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(forbidden_tokens, list)
        or not forbidden_tokens
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return ["harness.extractor_policy.forbidden_tokens must be a non-empty list of non-empty strings"]
    raw = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in forbidden_tokens:
        if tok in raw:
            violations.append(f"{rel}:1: forbidden check-level verdict token present: {tok}")
    return violations


def _scan_governance_structured_assertions_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("structured_assertions")
    if not isinstance(cfg, dict):
        return ["governance.structured_assertions_required requires harness.structured_assertions mapping in governance spec"]
    cases_rel = str(cfg.get("cases_path", "specs/governance/cases")).strip() or "specs/governance/cases"
    case_pattern = str(cfg.get("case_file_pattern", SETTINGS.case.default_file_pattern)).strip() or SETTINGS.case.default_file_pattern
    ignore_checks_raw = cfg.get("ignore_checks", [])
    if not isinstance(ignore_checks_raw, list) or any(not isinstance(x, str) for x in ignore_checks_raw):
        return ["harness.structured_assertions.ignore_checks must be a list of strings"]
    ignore_checks = {x.strip() for x in ignore_checks_raw if x.strip()}

    cases_dir = _join_contract_path(root, cases_rel)
    if not cases_dir.exists():
        return [f"{cases_rel}:1: governance cases path does not exist"]

    violations: list[str] = []
    for spec in iter_cases(cases_dir, file_pattern=case_pattern):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "governance.check":
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        check_id = str(case.get("check", "")).strip()
        if check_id in ignore_checks:
            continue
        assert_tree = case.get("contract", []) or []
        has_structured_target = False
        text_pass_only = True

        leaf_rows: list[tuple[str, str, object, bool]] = []

        def _collect_leaf(leaf: dict, *, inherited_target: str | None = None, assert_path: str = "assert") -> None:
            del assert_path  # scanner only needs leaf tuples
            for row in iter_leaf_assertions(leaf, target_override=inherited_target):
                leaf_rows.append(row)

        try:
            eval_assert_tree(assert_tree, eval_leaf=_collect_leaf)
        except Exception as exc:  # noqa: BLE001
            violations.append(
                f"{spec.doc_path.relative_to(root)}: case {case_id} check {check_id} has invalid assert tree ({exc})"
            )
            continue
        for target, op, value, _ in leaf_rows:
            if target in {"summary_json", "violation_count"} and op == "evaluate":
                has_structured_target = True
            if not (target == "text" and op == "contain" and str(value).strip().startswith("PASS: ")):
                text_pass_only = False
        if not has_structured_target:
            violations.append(
                f"{spec.doc_path.relative_to(root)}: case {case_id} check {check_id} missing structured evaluate assertions"
            )
        elif text_pass_only:
            violations.append(
                f"{spec.doc_path.relative_to(root)}: case {case_id} check {check_id} relies solely on PASS text assertions"
            )
    return violations


def _scan_runtime_rust_adapter_no_python_exec(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("rust_no_python_exec")
    if not isinstance(cfg, dict):
        return ["runtime.rust_adapter_no_python_exec requires harness.rust_no_python_exec mapping in governance spec"]
    rel = str(cfg.get("path", "runners/rust/spec_runner_cli/src/main.rs")).strip() or "runners/rust/spec_runner_cli/src/main.rs"
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing rust runner interface implementation"]
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(forbidden_tokens, list)
        or not forbidden_tokens
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return ["harness.rust_no_python_exec.forbidden_tokens must be a non-empty list of non-empty strings"]
    raw = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in forbidden_tokens:
        if tok in raw:
            violations.append(f"{rel}:1: forbidden python-coupling token present: {tok}")
    return violations


def _scan_runtime_non_python_lane_no_python_exec(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("python_dependency")
    if not isinstance(cfg, dict):
        return [
            "runtime.non_python_lane_no_python_exec requires harness.python_dependency mapping in governance spec"
        ]
    payload = python_dependency_report_jsonable(root, config=cfg)
    errors = payload.get("errors") or []
    if isinstance(errors, list) and any(str(e).strip() for e in errors):
        return [str(e) for e in errors if str(e).strip()]
    summary = payload.get("summary") if isinstance(payload, dict) else {}
    if not isinstance(summary, dict):
        return ["python dependency payload missing summary mapping"]
    count = int(summary.get("non_python_lane_python_exec_count", 0))
    violations: list[str] = []
    if count > 0:
        violations.append(
            f".artifacts/python-dependency.json:1: non_python_lane_python_exec_count={count} (expected 0)"
        )
    return violations


def _scan_runtime_rust_adapter_transitive_no_python(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("rust_transitive_no_python")
    if not isinstance(cfg, dict):
        return [
            "runtime.rust_adapter_transitive_no_python requires harness.rust_transitive_no_python mapping in governance spec"
        ]
    files = cfg.get("files")
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.rust_transitive_no_python.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(forbidden_tokens, list)
        or not forbidden_tokens
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return [
            "harness.rust_transitive_no_python.forbidden_tokens must be a non-empty list of non-empty strings"
        ]
    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing rust adapter file for transitive no-python check")
            continue
        raw = p.read_text(encoding="utf-8")
        for tok in forbidden_tokens:
            if tok in raw:
                violations.append(f"{rel}:1: forbidden rust transitive python token present: {tok}")
    return violations


def _scan_runtime_public_runner_entrypoint_single(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("public_runner_entrypoint")
    if not isinstance(cfg, dict):
        return [
            "runtime.public_runner_entrypoint_single requires harness.public_runner_entrypoint mapping in governance spec"
        ]
    required_entrypoint = str(cfg.get("required_entrypoint", "")).strip()
    gate_files = cfg.get("gate_files")
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    forbidden_paths = cfg.get("forbidden_paths", [])
    if not required_entrypoint:
        return ["harness.public_runner_entrypoint.required_entrypoint must be a non-empty string"]
    if (
        not isinstance(gate_files, list)
        or not gate_files
        or any(not isinstance(x, str) or not x.strip() for x in gate_files)
    ):
        return ["harness.public_runner_entrypoint.gate_files must be a non-empty list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.public_runner_entrypoint.forbidden_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_paths, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_paths):
        return ["harness.public_runner_entrypoint.forbidden_paths must be a list of non-empty strings"]

    violations: list[str] = []
    for rel in gate_files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing gate file")
            continue
        text = p.read_text(encoding="utf-8")
        if required_entrypoint not in text:
            violations.append(f"{rel}:1: missing required public runner entrypoint token {required_entrypoint}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden direct runner token {tok}")

    for rel in forbidden_paths:
        p = _join_contract_path(root, rel)
        if p.exists():
            violations.append(f"{rel}:1: forbidden legacy wrapper path exists")
    return violations


def _scan_runtime_public_runner_default_rust(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("public_runner_default")
    if not isinstance(cfg, dict):
        return ["runtime.public_runner_default_rust requires harness.public_runner_default mapping in governance spec"]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not path:
        return ["harness.public_runner_default.path must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.public_runner_default.required_tokens must be a non-empty list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.public_runner_default.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing public runner adapter script"]
    text = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing required rust-default token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{path}:1: forbidden default token {tok}")
    return violations


def _scan_runtime_python_lane_explicit_opt_in(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("python_lane_opt_in")
    if not isinstance(cfg, dict):
        return ["runtime.python_lane_explicit_opt_in requires harness.python_lane_opt_in mapping in governance spec"]
    files = cfg.get("files")
    required_opt_in_tokens = cfg.get("required_opt_in_tokens", [])
    forbidden_default_tokens = cfg.get("forbidden_default_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.python_lane_opt_in.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_opt_in_tokens, list)
        or not required_opt_in_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_opt_in_tokens)
    ):
        return ["harness.python_lane_opt_in.required_opt_in_tokens must be a non-empty list of non-empty strings"]
    if not isinstance(forbidden_default_tokens, list) or any(
        not isinstance(x, str) or not x.strip() for x in forbidden_default_tokens
    ):
        return ["harness.python_lane_opt_in.forbidden_default_tokens must be a list of non-empty strings"]
    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing file for python lane opt-in policy check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in forbidden_default_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden implicit python-lane token {tok}")
        if not any(tok in text for tok in required_opt_in_tokens):
            violations.append(f"{rel}:1: missing explicit python opt-in token")
    return violations


def _scan_runtime_no_public_direct_rust_adapter_docs(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("public_docs")
    if not isinstance(cfg, dict):
        return ["runtime.no_public_direct_rust_adapter_docs requires harness.public_docs mapping in governance spec"]
    files = cfg.get("files")
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    allowlist = cfg.get("allowlist", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.public_docs.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(forbidden_tokens, list)
        or not forbidden_tokens
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return ["harness.public_docs.forbidden_tokens must be a non-empty list of non-empty strings"]
    if not isinstance(allowlist, list) or any(not isinstance(x, str) or not x.strip() for x in allowlist):
        return ["harness.public_docs.allowlist must be a list of non-empty strings"]
    allow = {str(x).lstrip("/") for x in allowlist}
    violations: list[str] = []
    for rel in files:
        normalized = str(rel).lstrip("/")
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing public doc for rust-adapter invocation check")
            continue
        if normalized in allow:
            continue
        text = p.read_text(encoding="utf-8")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden direct rust-adapter public doc token {tok}")
    return violations


def _type_contract_doc_rel_for(case_type: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", case_type.lower()).strip("_")
    return f"{_TYPE_CONTRACTS_DIR}/{slug}.md"


def _scan_conformance_type_contract_docs(root: Path) -> list[str]:
    violations: list[str] = []
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return violations

    seen_types: set[str] = set()
    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case_type = str(spec.test.get("type", "")).strip()
        if not case_type:
            continue
        seen_types.add(case_type)

    for case_type in sorted(seen_types):
        rel = _type_contract_doc_rel_for(case_type)
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"missing type contract doc for '{case_type}': {rel}")
            continue
        raw = p.read_text(encoding="utf-8")
        heading = f"# Type Contract: {case_type}"
        if heading not in raw:
            violations.append(f"{rel}: missing heading '{heading}'")
    return violations


def _collect_assert_targets(node: object) -> list[str]:
    targets: list[str] = []
    if isinstance(node, list):
        for child in node:
            targets.extend(_collect_assert_targets(child))
        return targets
    if not isinstance(node, dict):
        return targets
    target = node.get("target")
    if isinstance(target, str) and target.strip():
        targets.append(target.strip())
    for key in ("MUST", "MAY", "MUST_NOT"):
        child = node.get(key)
        if child is not None:
            targets.extend(_collect_assert_targets(child))
    return targets


def _is_live_network_url(raw: str) -> bool:
    value = str(raw).strip().lower()
    return value.startswith("http://") or value.startswith("https://")


def _scan_conformance_api_http_portable_shape(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("api_http")
    if not isinstance(cfg, dict):
        return ["conformance.api_http_portable_shape requires harness.api_http mapping in governance spec"]
    raw_allowed_keys = cfg.get("allowed_top_level_keys")
    if not isinstance(raw_allowed_keys, list) or not raw_allowed_keys or any(not isinstance(x, str) for x in raw_allowed_keys):
        return ["harness.api_http.allowed_top_level_keys must be a non-empty list of strings"]
    allowed_top_level_keys = {x.strip() for x in raw_allowed_keys if x.strip()}
    if not allowed_top_level_keys:
        return ["harness.api_http.allowed_top_level_keys must include at least one non-empty key"]
    raw_allowed_targets = cfg.get("allowed_assert_targets")
    if not isinstance(raw_allowed_targets, list) or not raw_allowed_targets or any(not isinstance(x, str) for x in raw_allowed_targets):
        return ["harness.api_http.allowed_assert_targets must be a non-empty list of strings"]
    allowed_assert_targets = {x.strip() for x in raw_allowed_targets if x.strip()}
    if not allowed_assert_targets:
        return ["harness.api_http.allowed_assert_targets must include at least one non-empty target"]
    raw_required_request_fields = cfg.get("required_request_fields", ["method", "url"])
    if (
        not isinstance(raw_required_request_fields, list)
        or not raw_required_request_fields
        or any(not isinstance(x, str) for x in raw_required_request_fields)
    ):
        return ["harness.api_http.required_request_fields must be a non-empty list of strings"]
    required_request_fields = {x.strip() for x in raw_required_request_fields if x.strip()}
    if not required_request_fields:
        return ["harness.api_http.required_request_fields must include at least one non-empty field"]
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return violations

    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case = spec.test
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        case_type = str(case.get("type", "")).strip()
        if case_type != "api.http":
            continue
        expect = case.get("expect")
        schema_failure_fixture = False
        if isinstance(expect, dict):
            portable = expect.get("portable")
            if isinstance(portable, dict):
                status = str(portable.get("status", "")).strip().lower()
                category_raw = portable.get("category")
                category = None if category_raw is None else str(category_raw).strip().lower()
                schema_failure_fixture = status == "fail" and category == "schema"

        extra_top = sorted(k for k in case.keys() if str(k) not in allowed_top_level_keys)
        if extra_top:
            violations.append(
                f"{case_id}: unsupported top-level key(s) for api.http portable case: {', '.join(extra_top)}"
            )

        request = case.get("request")
        requests = case.get("requests")
        if request is not None and requests is not None:
            violations.append(f"{case_id}: api.http request and requests are mutually exclusive")
        elif request is None and requests is None:
            violations.append(f"{case_id}: api.http requires request mapping or requests list")
        elif isinstance(request, dict):
            if not schema_failure_fixture:
                for field in sorted(required_request_fields):
                    value = str(request.get(field, "")).strip()
                    if not value:
                        violations.append(f"{case_id}: api.http request.{field} is required")
        elif isinstance(requests, list):
            if not requests:
                violations.append(f"{case_id}: api.http requests must be a non-empty list")
            for idx, step in enumerate(requests):
                if not isinstance(step, dict):
                    violations.append(f"{case_id}: api.http requests[{idx}] must be a mapping")
                    continue
                for field in sorted(required_request_fields):
                    value = str(step.get(field, "")).strip()
                    if not value:
                        violations.append(f"{case_id}: api.http requests[{idx}].{field} is required")
                step_id = str(step.get("id", "")).strip()
                if not step_id:
                    violations.append(f"{case_id}: api.http requests[{idx}].id is required")
        else:
            violations.append(f"{case_id}: api.http requires request mapping or requests list")

        targets = _collect_assert_targets(case.get("contract", []))
        for t in targets:
            if t not in allowed_assert_targets:
                violations.append(
                    f"{case_id}: unsupported api.http assert target '{t}' "
                    f"(allowed: {', '.join(sorted(allowed_assert_targets))})"
                )
    return violations


def _iter_api_http_cases(root: Path):
    for rel_root in ("specs/conformance/cases", "specs/impl", "specs/governance/cases"):
        base = root / rel_root
        if not base.exists():
            continue
        for spec in iter_cases(base, file_pattern=SETTINGS.case.default_file_pattern):
            case = spec.test
            case_type = str(case.get("type", "")).strip()
            if case_type == "api.http":
                pass
            elif case_type == "contract.check":
                harness = case.get("harness")
                if not isinstance(harness, dict):
                    continue
                check = harness.get("check")
                if not isinstance(check, dict):
                    continue
                if str(check.get("profile", "")).strip() != "api.http":
                    continue
                cfg = check.get("config")
                if isinstance(cfg, dict):
                    merged = {k: v for k, v in case.items()}
                    for key in ("request", "requests"):
                        if key in cfg and key not in merged:
                            merged[key] = cfg[key]
                    case = merged
            else:
                continue
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            yield case_id, case


def _oauth_block(case: dict[str, object]) -> dict[str, object] | None:
    harness = case.get("harness")
    if not isinstance(harness, dict):
        return None
    api_http = harness.get("api_http")
    if not isinstance(api_http, dict):
        return None
    auth = api_http.get("auth")
    if not isinstance(auth, dict):
        return None
    oauth = auth.get("oauth")
    if not isinstance(oauth, dict):
        return None
    return oauth


def _scan_runtime_api_http_oauth_env_only(root: Path) -> list[str]:
    violations: list[str] = []
    for case_id, case in _iter_api_http_cases(root):
        oauth = _oauth_block(case)
        if oauth is None:
            continue
        client_id_env = str(oauth.get("client_id_env", "")).strip()
        client_secret_env = str(oauth.get("client_secret_env", "")).strip()
        if not client_id_env:
            violations.append(f"{case_id}: oauth client_id_env is required")
        if not client_secret_env:
            violations.append(f"{case_id}: oauth client_secret_env is required")
        if "client_id" in oauth:
            violations.append(f"{case_id}: oauth inline client_id is forbidden")
        if "client_secret" in oauth:
            violations.append(f"{case_id}: oauth inline client_secret is forbidden")
    return violations


def _scan_runtime_api_http_oauth_no_secret_literals(root: Path) -> list[str]:
    violations: list[str] = []
    forbidden_keys = {"client_id", "client_secret", "access_token", "refresh_token", "password"}
    for case_id, case in _iter_api_http_cases(root):
        oauth = _oauth_block(case)
        if oauth is not None:
            for key in sorted(forbidden_keys):
                if key in oauth:
                    violations.append(f"{case_id}: oauth secret literal field is forbidden: {key}")
        request_nodes: list[dict] = []
        request = case.get("request")
        if isinstance(request, dict):
            request_nodes.append(request)
        requests = case.get("requests")
        if isinstance(requests, list):
            for step in requests:
                if isinstance(step, dict):
                    request_nodes.append(step)
        for req in request_nodes:
            headers = req.get("headers")
            if not isinstance(headers, dict):
                continue
            for raw_key, raw_value in headers.items():
                key = str(raw_key).strip().lower()
                value = str(raw_value).strip()
                if key == "authorization" and value.lower().startswith("bearer "):
                    violations.append(f"{case_id}: inline bearer Authorization header is forbidden")
    return violations


def _scan_runtime_api_http_live_mode_explicit(root: Path) -> list[str]:
    violations: list[str] = []
    for case_id, case in _iter_api_http_cases(root):
        harness = case.get("harness")
        mode = "deterministic"
        if isinstance(harness, dict):
            api_http = harness.get("api_http")
            if isinstance(api_http, dict):
                mode = str(api_http.get("mode", "deterministic")).strip().lower() or "deterministic"
        request = case.get("request")
        request_urls: list[str] = []
        if isinstance(request, dict):
            request_urls.append(str(request.get("url", "")).strip())
        requests = case.get("requests")
        if isinstance(requests, list):
            for step in requests:
                if isinstance(step, dict):
                    request_urls.append(str(step.get("url", "")).strip())
        oauth = _oauth_block(case)
        token_url = "" if oauth is None else str(oauth.get("token_url", "")).strip()
        if any(_is_live_network_url(u) for u in request_urls) and mode != "live":
            violations.append(f"{case_id}: network request url requires harness.api_http.mode=live")
        if _is_live_network_url(token_url) and mode != "live":
            violations.append(f"{case_id}: network oauth token_url requires harness.api_http.mode=live")
    return violations


def _scan_runtime_api_http_oauth_docs_sync(root: Path) -> list[str]:
    required: dict[str, tuple[str, ...]] = {
        "specs/schema/schema_v1.md": (
            "harness.api_http.auth.oauth",
            "client_id_env",
            "client_secret_env",
            "deterministic",
            "live",
        ),
        "specs/contract/04_harness.md": (
            "harness.api_http.auth.oauth",
            "client_id_env",
            "client_secret_env",
            "Authorization: Bearer",
        ),
        "specs/contract/types/api_http.md": (
            "auth.oauth",
            "client_credentials",
            "client_id_env",
            "client_secret_env",
            "mode",
        ),
        "specs/contract/types/http_profile.md": (
            "meta.auth_mode",
            "meta.oauth_token_source",
            "context.oauth",
        ),
    }
    violations: list[str] = []
    for rel, tokens in required.items():
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}: missing required doc for api.http oauth contract")
            continue
        raw = p.read_text(encoding="utf-8")
        for token in tokens:
            if token not in raw:
                violations.append(f"{rel}: missing oauth sync token '{token}'")
    return violations


def _scan_runtime_api_http_verb_suite(root: Path) -> list[str]:
    supported = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
    seen: set[str] = set()
    violations: list[str] = []
    for case_id, case in _iter_api_http_cases(root):
        request = case.get("request")
        requests = case.get("requests")
        request_nodes: list[tuple[str, dict[str, object]]] = []
        if isinstance(request, dict):
            request_nodes.append((case_id, request))
        if isinstance(requests, list):
            for idx, raw in enumerate(requests):
                if isinstance(raw, dict):
                    request_nodes.append((f"{case_id}.requests[{idx}]", raw))
        for node_id, req in request_nodes:
            expect = case.get("expect")
            schema_fixture = False
            if isinstance(expect, dict):
                portable = expect.get("portable")
                if isinstance(portable, dict):
                    status = str(portable.get("status", "")).strip().lower()
                    category = str(portable.get("category", "")).strip().lower()
                    schema_fixture = status == "fail" and category == "schema"
            method = str(req.get("method", "")).strip().upper()
            if not method:
                violations.append(f"{node_id}: api.http request.method is required")
                continue
            if method not in supported:
                if not schema_fixture:
                    violations.append(f"{node_id}: unsupported method '{method}'")
                continue
            seen.add(method)
    missing = sorted(supported - seen)
    if missing:
        violations.append(f"api.http conformance coverage missing methods: {', '.join(missing)}")
    return violations


def _scan_runtime_api_http_cors_support(root: Path) -> list[str]:
    required_tokens: dict[str, tuple[str, ...]] = {
        "runners/python/spec_runner/harnesses/api_http.py": (
            "request.cors",
            "preflight",
            "Access-Control-Request-Method",
            "cors_json",
        ),
        "specs/contract/types/api_http.md": (
            "request.cors",
            "preflight",
            "cors_json",
        ),
        "specs/contract/types/http_profile.md": (
            "value.cors",
            "allow_origin",
            "allow_methods",
        ),
        "specs/libraries/domain/http_core.spec.md": (
            "domain.http.cors_allow_origin",
            "domain.http.cors_allows_method",
            "domain.http.cors_allows_header",
        ),
        "specs/conformance/cases/core/api_http.spec.md": (
            "request.cors",
            "preflight",
        ),
    }
    violations: list[str] = []
    for rel, tokens in required_tokens.items():
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}: missing required api.http CORS surface")
            continue
        raw = p.read_text(encoding="utf-8")
        for token in tokens:
            if token not in raw:
                violations.append(f"{rel}: missing CORS token '{token}'")
    return violations


def _scan_runtime_api_http_scenario_roundtrip(root: Path) -> list[str]:
    violations: list[str] = []
    has_requests_case = False
    for case_id, case in _iter_api_http_cases(root):
        requests = case.get("requests")
        if not isinstance(requests, list) or not requests:
            continue
        has_requests_case = True
        ids: set[str] = set()
        for idx, step in enumerate(requests):
            if not isinstance(step, dict):
                violations.append(f"{case_id}.requests[{idx}]: step must be a mapping")
                continue
            step_id = str(step.get("id", "")).strip()
            if not step_id:
                violations.append(f"{case_id}.requests[{idx}]: id is required")
                continue
            if step_id in ids:
                violations.append(f"{case_id}: duplicate requests step id '{step_id}'")
            ids.add(step_id)
    if not has_requests_case:
        violations.append("api.http roundtrip conformance requires at least one case using requests list")
    for rel, tokens in {
        "runners/python/spec_runner/harnesses/api_http.py": ("harness.api_http.scenario", "steps_json", "steps."),
        "specs/contract/types/api_http.md": ("harness.api_http.scenario", "requests", "steps_json"),
        "specs/conformance/cases/core/api_http.spec.md": ("requests:", "{{steps.", "steps_json"),
    }.items():
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}: missing required api.http scenario surface")
            continue
        raw = p.read_text(encoding="utf-8")
        for token in tokens:
            if token not in raw:
                violations.append(f"{rel}: missing scenario token '{token}'")
    return violations


def _scan_runtime_api_http_parity_contract_sync(root: Path) -> list[str]:
    violations: list[str] = []
    checks: dict[str, tuple[str, ...]] = {
        "runners/python/spec_runner/harnesses/api_http.py": ("_SUPPORTED_METHODS", "cors_json", "steps_json"),
        "runners/php/conformance_runner.php": ("api.http", "request.method", "context_json"),
        "specs/contract/types/api_http.md": ("GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS", "steps_json", "cors_json"),
    }
    for rel, tokens in checks.items():
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}: missing parity sync surface")
            continue
        raw = p.read_text(encoding="utf-8")
        for token in tokens:
            if token not in raw:
                violations.append(f"{rel}: missing parity sync token '{token}'")
    return violations


def _scan_docs_api_http_tutorial_sync(root: Path) -> list[str]:
    required_tokens: dict[str, tuple[str, ...]] = {
        "docs/book/60_runner_and_gates.md": (
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
            "CORS",
            "round-trip",
            "api.http",
        ),
        "docs/book/80_troubleshooting.md": (
            "api.http",
            "CORS",
            "preflight",
            "requests",
            "steps_json",
        ),
    }
    violations: list[str] = []
    for rel, tokens in required_tokens.items():
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}: missing api.http tutorial document")
            continue
        raw = p.read_text(encoding="utf-8")
        lowered = raw.lower()
        for token in tokens:
            if token.lower() not in lowered:
                violations.append(f"{rel}: missing tutorial token '{token}'")
    return violations


def _iter_cases_with_chain(root: Path):
    with _SCAN_CACHE_LOCK:
        cache_key = (_SCAN_CACHE_TOKEN, str(root.resolve()))
        cached = _CHAIN_CASES_CACHE.get(cache_key)
    if cached is None:
        cached = []
        for doc_path, case in _iter_all_spec_cases(root):
            harness = case.get("harness")
            if not isinstance(harness, dict):
                continue
            chain = harness.get("chain")
            if isinstance(chain, dict):
                cached.append((doc_path, case, harness, chain))
        with _SCAN_CACHE_LOCK:
            _CHAIN_CASES_CACHE[cache_key] = cached
    yield from cached


def _rel_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _expand_chain_step_exports(raw_exports: object, *, domain: str | None = None) -> tuple[dict[str, dict], list[str]]:
    if raw_exports is None:
        return {}, []
    if not isinstance(raw_exports, list):
        return {}, ["exports must be list (canonical form)"]

    errors: list[str] = []
    expanded: dict[str, dict] = {}
    for idx, raw_entry in enumerate(raw_exports):
        if not isinstance(raw_entry, dict):
            errors.append(f"exports[{idx}] must be mapping")
            continue

        allowed = {"as", "from", "path", "params", "required"}
        unknown = sorted(str(k) for k in raw_entry.keys() if str(k) not in allowed)
        if unknown:
            errors.append(f"exports[{idx}] entry has unsupported keys: {', '.join(unknown)}")
        raw_export_name = str(raw_entry.get("as", "")).strip()
        if not raw_export_name:
            errors.append(f"exports[{idx}] entry requires non-empty as")
            continue
        export_name = normalize_export_symbol(domain, raw_export_name)
        if export_name in expanded:
            raw_domain = domain if domain is not None else "<none>"
            errors.append(
                "exports duplicate key after domain prefix "
                f"(raw_as={raw_export_name}, domain={raw_domain}, canonical={export_name})"
            )
            continue
        from_source = str(raw_entry.get("from", "")).strip()
        if not from_source:
            errors.append(f"exports[{idx}] entry requires non-empty from")
        elif from_source != "assert.function":
            errors.append(f"exports[{idx}] from must be assert.function")
        export_path = raw_entry.get("path")
        if export_path is not None and not isinstance(export_path, str):
            errors.append(f"exports[{idx}] path must be string when provided")
        params = raw_entry.get("params")
        if params is not None:
            if not isinstance(params, list) or not params:
                errors.append(f"exports[{idx}] params must be non-empty list when provided")
            elif any(not isinstance(x, str) or not str(x).strip() for x in params):
                errors.append(f"exports[{idx}] params entries must be non-empty strings")
        raw_required = raw_entry.get("required", True)
        if not isinstance(raw_required, bool):
            errors.append(f"exports[{idx}] required must be bool")
        expanded[export_name] = {
            "from": from_source,
            "path": export_path,
            "params": params,
            "required": raw_required,
        }
    return expanded, errors


def _producer_step_exports(
    root: Path,
    *,
    consumer_doc_path: Path,
    step: dict,
) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    names: set[str] = set()
    loaded, resolve_errors = _resolve_chain_step_cases(
        root,
        consumer_doc_path=consumer_doc_path,
        raw_ref=step.get("ref"),
    )
    if resolve_errors:
        return set(), resolve_errors

    for _source_doc, source_case in loaded:
        try:
            source_domain = normalize_case_domain(source_case.get("domain"))
        except (TypeError, ValueError) as exc:
            errors.append(f"producer domain invalid ({exc})")
            source_domain = None
        source_harness = source_case.get("harness")
        if not isinstance(source_harness, dict):
            source_harness = {}
        if "exports" in source_harness:
            expanded, parse_errors = _expand_chain_step_exports(
                source_harness.get("exports"),
                domain=source_domain,
            )
            if parse_errors:
                for err in parse_errors:
                    errors.append(f"producer harness.exports {err}")
                continue
            names.update(str(name).strip() for name in expanded.keys() if str(name).strip())

        # Implicit producer export model for spec_lang.export: defines.public keys.
        if str(source_case.get("type", "")).strip() == "spec_lang.export":
            raw_defines = source_case.get("defines")
            if isinstance(raw_defines, dict):
                raw_public = raw_defines.get("public")
                if isinstance(raw_public, dict):
                    for raw_name in raw_public.keys():
                        name = str(raw_name).strip()
                        if name:
                            names.add(name)
    return names, errors


def _collect_chain_library_refs(case: dict) -> list[str]:
    out: list[str] = []
    harness = case.get("harness")
    if not isinstance(harness, dict):
        return out
    chain = harness.get("chain")
    if not isinstance(chain, dict):
        return out
    steps = chain.get("steps")
    if not isinstance(steps, list):
        return out
    imports = chain.get("imports")
    import_from_ids: set[str] = set()
    if isinstance(imports, list):
        for item in imports:
            if not isinstance(item, dict):
                continue
            from_id = str(item.get("from", "")).strip()
            if from_id:
                import_from_ids.add(from_id)

    for step in steps:
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("id", "")).strip()
        if step_id and import_from_ids and step_id not in import_from_ids:
            continue
        try:
            ref_path, _ref_case_id = _parse_chain_ref_value(step.get("ref"))
        except ValueError:
            continue
        if ref_path:
            out.append(ref_path)
    return out


def _load_chain_imported_symbol_bindings(
    root: Path, *, doc_path: Path, case: dict, limits: SpecLangLimits
) -> dict[str, object]:
    del limits
    out: dict[str, object] = {}
    harness = case.get("harness")
    if not isinstance(harness, dict):
        return out
    chain = harness.get("chain")
    if not isinstance(chain, dict):
        return out
    steps = chain.get("steps")
    if not isinstance(steps, list):
        return out

    step_exports: dict[str, dict[str, object]] = {}
    for step in steps:
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("id", "")).strip()
        if not step_id:
            continue
        export_names, _errors = _producer_step_exports(
            root,
            consumer_doc_path=doc_path,
            step=step,
        )
        if export_names:
            step_exports[step_id] = {name: {"__chain_export__": True} for name in export_names}

    imports = chain.get("imports")
    if not isinstance(imports, list):
        return out
    for item in imports:
        if not isinstance(item, dict):
            continue
        from_id = str(item.get("from", "")).strip()
        if not from_id or from_id not in step_exports:
            continue
        names = item.get("names")
        if not isinstance(names, list):
            continue
        alias_map_raw = item.get("as")
        alias_map = alias_map_raw if isinstance(alias_map_raw, dict) else {}
        for raw_name in names:
            name = str(raw_name).strip()
            if not name:
                continue
            if name not in step_exports[from_id]:
                continue
            local = str(alias_map.get(name, name)).strip()
            if not local:
                continue
            out[local] = step_exports[from_id][name]
    return out


def _scan_runtime_chain_step_class_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        steps = chain.get("steps")
        if not isinstance(steps, list):
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip() or f"<step[{idx}]>"
            class_name = str(step.get("class", "")).strip()
            if class_name not in {"MUST", "MAY", "MUST_NOT"}:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} step {step_id} class must be one of: MUST, MAY, MUST_NOT"
                )
    return violations


def _scan_runtime_chain_import_alias_collision_forbidden(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    reserved = {"subject", "if", "let", "fn", "call", "var"}
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        steps = chain.get("steps")
        if not isinstance(steps, list):
            continue
        step_ids: set[str] = set()
        step_exports: dict[str, set[str]] = {}
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            sid = str(step.get("id", "")).strip() or f"<step[{idx}]>"
            step_ids.add(sid)
            export_names, errors = _producer_step_exports(
                root,
                consumer_doc_path=doc_path,
                step=step,
            )
            if errors:
                step_exports[sid] = set()
            else:
                step_exports[sid] = {str(x).strip() for x in export_names if str(x).strip()}

        imports = chain.get("imports", [])
        if imports is None:
            imports = []
        if not isinstance(imports, list):
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports must be list")
            continue
        local_seen: set[str] = set()
        for idx, imp in enumerate(imports):
            if not isinstance(imp, dict):
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}] must be mapping"
                )
                continue
            from_id = str(imp.get("from", "")).strip()
            if not from_id:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}].from must be non-empty"
                )
                continue
            if from_id not in step_ids:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}].from unknown step id {from_id}"
                )
                continue
            names = imp.get("names")
            if not isinstance(names, list) or not names:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}].names must be non-empty list"
                )
                continue
            parsed_names: list[str] = []
            for j, raw_name in enumerate(names):
                name = str(raw_name).strip()
                if not name:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}].names[{j}] must be non-empty"
                    )
                    continue
                if name not in step_exports.get(from_id, set()):
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}].names[{j}] unknown export {name} from step {from_id}"
                    )
                parsed_names.append(name)
            aliases = imp.get("as", {})
            if aliases is None:
                aliases = {}
            if not isinstance(aliases, dict):
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}].as must be mapping when provided"
                )
                continue
            for raw_from, raw_to in aliases.items():
                from_name = str(raw_from).strip()
                to_name = str(raw_to).strip()
                if not from_name or not to_name:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}].as keys and values must be non-empty strings"
                    )
                    continue
                if from_name not in parsed_names:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}].as unknown name {from_name}"
                    )
            for name in parsed_names:
                local = str(aliases.get(name, name)).strip()
                if not local:
                    continue
                if local in reserved:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}] local name {local} collides with reserved symbol"
                    )
                    continue
                if local in local_seen:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} harness.chain.imports[{idx}] local name collision: {local}"
                    )
                    continue
                local_seen.add(local)
    return violations


def _scan_runtime_chain_contract_single_location(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_all_spec_cases(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        if "chain" in case:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} top-level chain is forbidden; use harness.chain"
            )
        harness_map = case.get("harness")
        if not isinstance(harness_map, dict):
            continue
        for h_key, h_value in harness_map.items():
            k = str(h_key).strip()
            if k == "chain":
                continue
            if isinstance(h_value, dict) and "chain" in h_value:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} type-specific {k}.chain is forbidden; use harness.chain"
                )
    return violations


def _scan_runtime_universal_chain_support_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    rel = "runners/python/spec_runner/dispatcher.py"
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing dispatcher module"]
    text = p.read_text(encoding="utf-8")
    required_tokens = (
        "execute_case_chain(",
        "\"api.http\":",
        "\"cli.run\":",
        "\"docs.generate\":",
        "\"orchestration.run\":",
        "\"text.file\":",
    )
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{rel}:1: missing universal chain support token {tok}")
    return violations


def _scan_runtime_chain_shared_context_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    rel = "runners/python/spec_runner/dispatcher.py"
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing dispatcher module"]
    text = p.read_text(encoding="utf-8")
    required_tokens = (
        "chain_state:",
        "chain_trace:",
        "set_case_chain_imports(",
        "get_case_chain_imports(",
        "set_case_chain_payload(",
        "get_case_chain_payload(",
    )
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{rel}:1: missing chain shared-context token {tok}")
    return violations


def _parse_chain_ref_value(raw: object) -> tuple[str | None, str | None]:
    if isinstance(raw, dict):
        raise ValueError("legacy mapping format for step.ref is not supported; use string [path][#case_id]")
    if not isinstance(raw, str):
        raise ValueError("step.ref must be a string")
    ref = str(raw).strip()
    if not ref:
        raise ValueError("step.ref must be a non-empty string")
    if "#" in ref:
        path_part, case_part = ref.split("#", 1)
        path = path_part.strip() or None
        case_id = case_part.strip()
        if not case_id:
            raise ValueError("step.ref fragment case_id must be non-empty when '#' is present")
        if not _CHAIN_REF_CASE_ID_PATTERN.match(case_id):
            raise ValueError("step.ref fragment case_id must match [A-Za-z0-9._:-]+")
        return path, case_id
    return ref, None


def _resolve_chain_ref_doc(root: Path, doc_path: Path, ref_path: str) -> Path:
    if ref_path.startswith("/"):
        return resolve_contract_path(root, ref_path, field="harness.chain.steps.ref")
    candidate = (doc_path.resolve().parent / ref_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise VirtualPathError("harness.chain.steps.ref escapes contract root") from exc
    return candidate


def _resolve_chain_step_cases(
    root: Path,
    *,
    consumer_doc_path: Path,
    raw_ref: object,
) -> tuple[list[tuple[Path, dict[str, Any]]], list[str]]:
    if not isinstance(raw_ref, str):
        return [], ["step.ref must be a string"]
    ref_text = str(raw_ref).strip()
    if not ref_text:
        return [], ["step.ref must be a non-empty string"]
    with _SCAN_CACHE_LOCK:
        cache_key = (_SCAN_CACHE_TOKEN, str(root.resolve()), consumer_doc_path.resolve().as_posix(), ref_text)
        cached = _CHAIN_REF_CASES_CACHE.get(cache_key)
    if cached is not None:
        return cached

    try:
        ref_path, ref_case_id = _parse_chain_ref_value(ref_text)
    except ValueError as exc:
        result: tuple[list[tuple[Path, dict[str, Any]]], list[str]] = ([], [str(exc)])
        with _SCAN_CACHE_LOCK:
            _CHAIN_REF_CASES_CACHE[cache_key] = result
        return result

    if ref_path:
        try:
            resolved_doc = _resolve_chain_ref_doc(root, consumer_doc_path, ref_path)
        except VirtualPathError as exc:
            result = ([], [f"invalid ref ({exc})"])
            with _SCAN_CACHE_LOCK:
                _CHAIN_REF_CASES_CACHE[cache_key] = result
            return result
        if not resolved_doc.exists() or not resolved_doc.is_file():
            result = ([], [f"missing ref path {ref_path}"])
            with _SCAN_CACHE_LOCK:
                _CHAIN_REF_CASES_CACHE[cache_key] = result
            return result
    else:
        resolved_doc = consumer_doc_path

    try:
        loaded = list(load_external_cases(resolved_doc, formats={"md"}))
    except Exception as exc:  # noqa: BLE001
        result = ([], [f"unable to load producer cases ({exc})"])
        with _SCAN_CACHE_LOCK:
            _CHAIN_REF_CASES_CACHE[cache_key] = result
        return result

    if ref_case_id:
        filtered = [item for item in loaded if str(item[1].get("id", "")).strip() == ref_case_id]
        if len(filtered) != 1:
            target = ref_path or _rel_path(root, consumer_doc_path)
            result = ([], [f"unresolved case fragment {ref_case_id} in {target}"])
            with _SCAN_CACHE_LOCK:
                _CHAIN_REF_CASES_CACHE[cache_key] = result
            return result
        loaded = filtered

    result = (loaded, [])
    with _SCAN_CACHE_LOCK:
        _CHAIN_REF_CASES_CACHE[cache_key] = result
    return result


def _scan_runtime_chain_reference_resolution(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        steps = chain.get("steps")
        has_exports = "exports" in chain
        if not isinstance(steps, list):
            if has_exports:
                continue
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} harness.chain.steps must be list")
            continue
        if not steps and has_exports:
            continue
        if not steps:
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} harness.chain.steps must be non-empty list")
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                violations.append(f"{doc_path.relative_to(root)}: case {case_id} step[{idx}] must be mapping")
                continue
            step_id = str(step.get("id", "")).strip() or f"<step[{idx}]>"
            _loaded, errors = _resolve_chain_step_cases(
                root,
                consumer_doc_path=doc_path,
                raw_ref=step.get("ref"),
            )
            for err in errors:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} step {step_id} {err}"
                )
    return violations


def _scan_runtime_chain_cycle_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    docs = {(doc_path.resolve().as_posix(), str(case.get("id", "")).strip()): (doc_path, case) for doc_path, case in _iter_all_spec_cases(root)}
    graph: dict[str, set[str]] = {}
    violations: list[str] = []
    for (doc_key, case_id), (doc_path, case) in docs.items():
        if not case_id:
            continue
        node = f"{doc_key}::{case_id}"
        graph.setdefault(node, set())
        harness_map = case.get("harness")
        if not isinstance(harness_map, dict):
            continue
        chain = harness_map.get("chain")
        if not isinstance(chain, dict):
            continue
        steps = chain.get("steps")
        if not isinstance(steps, list):
            continue
        for step in steps:
            if not isinstance(step, dict):
                continue
            found, _errors = _resolve_chain_step_cases(
                root,
                consumer_doc_path=doc_path,
                raw_ref=step.get("ref"),
            )
            targets = [
                f"{d.resolve().as_posix()}::{str(t.get('id', '')).strip()}"
                for d, t in found
                if str(t.get("id", "")).strip()
            ]
            for target in targets:
                if target:
                    graph[node].add(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    def _dfs(node: str, stack: list[str]) -> None:
        if node in visiting:
            cycle = stack[stack.index(node):] + [node] if node in stack else stack + [node]
            violations.append(f"chain cycle detected: {' -> '.join(cycle)}")
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for nxt in sorted(graph.get(node, set())):
            _dfs(nxt, stack)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph.keys()):
        _dfs(node, [])
    return violations


def _scan_runtime_chain_exports_target_derived_only(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        steps = chain.get("steps")
        if not isinstance(steps, list):
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip() or f"<step[{idx}]>"
            try:
                _ref_path, ref_case_id = _parse_chain_ref_value(step.get("ref"))
            except ValueError:
                ref_case_id = None
            exports, errors = _expand_chain_step_exports(step.get("imports"))
            if errors:
                for err in errors:
                    violations.append(f"{doc_path.relative_to(root)}: case {case_id} step {step_id} {err}")
                continue
            has_library_symbol = False
            for export_name, export_raw in exports.items():
                if not isinstance(export_raw, dict):
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} step {step_id} export {export_name} must be mapping"
                    )
                    continue
                for key in export_raw.keys():
                    if str(key) not in {"from", "path", "required"}:
                        violations.append(
                            f"{doc_path.relative_to(root)}: case {case_id} step {step_id} export {export_name} has unsupported key {key}"
                        )
                from_source = str(export_raw.get("from", "")).strip()
                if not from_source:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} step {step_id} export {export_name} missing from"
                    )
                    continue
                if from_source == "assert.function":
                    has_library_symbol = True
                    if not str(export_raw.get("path", "")).strip():
                        violations.append(
                            f"{doc_path.relative_to(root)}: case {case_id} step {step_id} export {export_name} from={from_source} requires path"
                        )
            if exports and not ref_case_id and not has_library_symbol:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} step {step_id} exports require ref with #case_id fragment"
                )
    return violations


def _scan_runtime_chain_exports_from_key_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        steps = chain.get("steps")
        if not isinstance(steps, list):
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip() or f"<step[{idx}]>"
            exports, errors = _expand_chain_step_exports(step.get("imports"))
            if errors:
                continue
            for export_name, export_raw in exports.items():
                if not isinstance(export_raw, dict):
                    continue
                if "from" not in export_raw:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} step {step_id} export {export_name} missing required from key"
                    )
    return violations


def _scan_runtime_chain_exports_list_only_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        steps = chain.get("steps")
        if not isinstance(steps, list):
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip() or f"<step[{idx}]>"
            raw_exports = step.get("imports")
            if raw_exports is not None and not isinstance(raw_exports, list):
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} step {step_id} exports must be list (canonical form)"
                )
    return violations


def _scan_runtime_harness_exports_location_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, harness_map, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        case_type = str(case.get("type", "")).strip()
        if "exports" in chain:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} harness.chain.exports is forbidden; use harness.exports"
            )
        if case_type == "spec.export" and "exports" not in harness_map:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} spec.export requires harness.exports"
            )
    return violations


def _scan_runtime_chain_exports_legacy_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    return _scan_runtime_harness_exports_location_required(root, harness=harness)


def _scan_runtime_harness_exports_schema_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, harness_map, _chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        try:
            case_domain = normalize_case_domain(case.get("domain"))
        except (TypeError, ValueError) as exc:
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} invalid domain ({exc})")
            case_domain = None
        raw_exports = harness_map.get("exports")
        if raw_exports is None:
            continue
        _expanded, errors = _expand_chain_step_exports(raw_exports, domain=case_domain)
        for err in errors:
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} harness.exports {err}")
    return violations


def _scan_runtime_chain_imports_consumer_surface_unchanged(root: Path, *, harness: dict | None = None) -> list[str]:
    return _scan_runtime_chain_import_alias_collision_forbidden(root, harness=harness)


def _scan_runtime_chain_library_symbol_exports_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        steps = chain.get("steps")
        if not isinstance(steps, list):
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip() or f"<step[{idx}]>"
            exports, errors = _expand_chain_step_exports(step.get("imports"))
            if errors:
                continue
            for export_name, export_raw in exports.items():
                if not isinstance(export_raw, dict):
                    continue
                from_source = str(export_raw.get("from", "")).strip()
                if from_source != "assert.function":
                    continue
                symbol_name = str(export_raw.get("path", "")).strip().lstrip("/")
                if not symbol_name:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} step {step_id} export {export_name} from={from_source} requires non-empty path"
                    )
    return violations


def _scan_runtime_chain_legacy_from_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        steps = chain.get("steps")
        if not isinstance(steps, list):
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip() or f"<step[{idx}]>"
            exports, errors = _expand_chain_step_exports(step.get("imports"))
            if errors:
                continue
            raw_imports = step.get("imports")
            if not isinstance(raw_imports, list):
                continue
            for export_name, export_raw in exports.items():
                if not isinstance(export_raw, dict):
                    continue
                if any(
                    isinstance(item, dict)
                    and str(item.get("as", "")).strip() == str(export_name).strip()
                    and "from_target" in item
                    for item in raw_imports
                ):
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} step {step_id} export {export_name} uses legacy from_target key"
                    )
    return violations


def _scan_runtime_executable_spec_lang_includes_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_all_spec_cases(root):
        case_type = str(case.get("type", "")).strip()
        if case_type == "spec_lang.export":
            continue
        h = case.get("harness")
        if not isinstance(h, dict):
            continue
        spec_lang = h.get("spec_lang")
        if not isinstance(spec_lang, dict):
            continue
        includes = spec_lang.get("includes")
        if isinstance(includes, list) and includes:
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} harness.spec_lang.includes is forbidden for executable cases; use harness.chain"
            )
    return violations


def _collect_operator_keys(node: object, out: set[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str):
                op = key.strip()
                if op:
                    out.add(op)
            _collect_operator_keys(value, out)
        return
    if isinstance(node, list):
        for value in node:
            _collect_operator_keys(value, out)


def _scan_runtime_domain_library_preferred_for_fs_ops(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    violations: list[str] = []
    scan_roots = (
        root / "specs/conformance/cases",
        root / "specs/governance/cases",
        root / "specs/impl",
    )
    for base in scan_roots:
        if not base.exists():
            continue
        for doc_path, case in _iter_all_spec_cases(base):
            rel_doc = _rel_path(root, doc_path)
            if rel_doc in _RAW_OPS_FS_ALLOWED_CASE_FILES:
                continue
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            ops: set[str] = set()
            _collect_operator_keys(case, ops)
            raw_fs_ops = sorted(op for op in ops if op.startswith("ops.fs."))
            if not raw_fs_ops:
                continue
            violations.append(
                f"{rel_doc}: case {case_id} uses raw ops.fs symbols ({', '.join(raw_fs_ops)}); "
                "prefer domain.path.* / domain.fs.* helpers in executable specs"
            )
    return violations


def _expr_contains_http_meta_projection(expr: object) -> bool:
    text = json.dumps(expr, sort_keys=True, ensure_ascii=True)
    return "std.object.get" in text and (
        "\"auth_mode\"" in text or "\"oauth_token_source\"" in text
    )


def _expr_uses_domain_http_meta_helpers(expr: object) -> bool:
    wanted = {"domain.http.auth_is_oauth", "domain.http.oauth_token_source_is"}

    def _walk(node: object) -> bool:
        if isinstance(node, dict):
            for key, value in node.items():
                op = str(key).strip()
                if op in wanted:
                    return True
                if op == "var" and str(value).strip() in wanted:
                    return True
                if _walk(value):
                    return True
            return False
        if isinstance(node, list):
            return any(_walk(x) for x in node)
        return False

    return _walk(expr)


def _scan_runtime_domain_library_preferred_for_http_helpers(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    violations: list[str] = []
    scan_roots = (
        root / "specs/conformance/cases",
        root / "specs/governance/cases",
        root / "specs/impl",
    )
    for base in scan_roots:
        if not base.exists():
            continue
        for doc_path, case in _iter_all_spec_cases(base):
            if str(case.get("type", "")).strip() != "api.http":
                continue
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            rel_doc = _rel_path(root, doc_path)
            if rel_doc in _RAW_HTTP_META_ALLOWED_CASE_FILES:
                continue
            assert_tree = case.get("contract", []) or []
            leaf_rows: list[tuple[str, str, object, bool]] = []
            def _collect_leaf(leaf: dict, *, inherited_target: str | None = None, assert_path: str = "assert") -> None:
                del assert_path
                for row in iter_leaf_assertions(leaf, target_override=inherited_target):
                    leaf_rows.append(row)
            try:
                eval_assert_tree(assert_tree, eval_leaf=_collect_leaf)
            except Exception:
                continue
            for target, op, value, _ in leaf_rows:
                if target != "context_json" or op != "evaluate":
                    continue
                if not _expr_contains_http_meta_projection(value):
                    continue
                if _expr_uses_domain_http_meta_helpers(value):
                    continue
                violations.append(
                    f"{rel_doc}: case {case_id} projects oauth http meta fields with raw std.object.get; "
                    "prefer domain.http.auth_is_oauth/domain.http.oauth_token_source_is"
                )
                break
    return violations


def _scan_runtime_spec_lang_export_type_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    scan_roots = [
        root / "specs/conformance/cases",
        root / "specs/governance/cases",
        root / "specs/impl",
        root / "specs/libraries",
    ]
    for base in scan_roots:
        if not base.exists():
            continue
        for doc_path, case in _iter_all_spec_cases(base):
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            if str(case.get("type", "")).strip() == "spec_lang.export":
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} uses forbidden type spec_lang.export; use spec.export"
                )
    return violations


def _scan_docs_markdown_namespace_legacy_alias_forbidden(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    violations: list[str] = []
    for rel in ("specs", "docs/book"):
        base = root / rel
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            text = p.read_text(encoding="utf-8")
            if _MD_NAMESPACE_LEGACY_PATTERN.search(text):
                violations.append(
                    f"{p.relative_to(root)}: legacy markdown alias namespace md.* is forbidden; use domain.markdown.*"
                )
    return violations


def _scan_library_single_public_symbol_per_case(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return []
    violations: list[str] = []
    for lib_file in sorted(libs_root.rglob(SETTINGS.case.default_file_pattern)):
        if not lib_file.is_file():
            continue
        try:
            loaded = load_external_cases(lib_file, formats={"md"})
        except Exception as exc:  # noqa: BLE001
            violations.append(f"{lib_file.relative_to(root)}: unable to parse library file ({exc})")
            continue
        for _doc_path, case in loaded:
            if str(case.get("type", "")).strip() != "spec_lang.export":
                continue
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            defines = case.get("defines")
            if not isinstance(defines, dict):
                continue
            public = defines.get("public")
            n = len(public) if isinstance(public, dict) else 0
            if n != 1:
                violations.append(
                    f"{lib_file.relative_to(root)}: case {case_id} must define exactly one defines.public symbol (found {n})"
                )
    return violations


def _scan_library_colocated_symbol_tests_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return []
    violations: list[str] = []
    exported_by_file: dict[Path, set[str]] = {}
    referenced: set[str] = set()
    for lib_file in sorted(libs_root.rglob(SETTINGS.case.default_file_pattern)):
        if not lib_file.is_file():
            continue
        try:
            loaded = list(load_external_cases(lib_file, formats={"md"}))
        except Exception as exc:  # noqa: BLE001
            violations.append(f"{lib_file.relative_to(root)}: unable to parse library file ({exc})")
            continue
        has_executable_test_case = False
        file_exports: set[str] = set()
        for _doc_path, case in loaded:
            case_type = str(case.get("type", "")).strip()
            if case_type and case_type != "spec_lang.export":
                has_executable_test_case = True
            if case_type == "spec_lang.export":
                defines = case.get("defines")
                if isinstance(defines, dict):
                    public = defines.get("public")
                    if isinstance(public, dict):
                        file_exports.update(str(x).strip() for x in public.keys() if str(x).strip())
        exported_by_file[lib_file] = file_exports
        if has_executable_test_case:
            continue

    referenced.update(_collect_global_symbol_references(root))

    for lib_file, file_exports in exported_by_file.items():
        if file_exports and not any(sym in referenced for sym in file_exports):
            violations.append(
                f"{lib_file.relative_to(root)}: library file must include colocated executable tests or referenced exports in executable specs"
            )
    return violations


def _scan_runtime_chain_fail_fast_default(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case, _harness, chain in _iter_cases_with_chain(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        if "fail_fast" in chain and not isinstance(chain.get("fail_fast"), bool):
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} harness.chain.fail_fast must be bool")
        steps = chain.get("steps")
        if isinstance(steps, list):
            for idx, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                if "allow_continue" in step and not isinstance(step.get("allow_continue"), bool):
                    step_id = str(step.get("id", "")).strip() or f"<step[{idx}]>"
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} step {step_id} allow_continue must be bool"
                    )
    return violations


def _scan_runtime_chain_state_template_resolution(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_all_spec_cases(root):
        if str(case.get("type", "")).strip() != "api.http":
            continue
        chain_map = (((case.get("harness") or {}) if isinstance(case.get("harness"), dict) else {}).get("chain"))
        exported: set[tuple[str, str]] = set()
        if isinstance(chain_map, dict) and isinstance(chain_map.get("steps"), list):
            for step in chain_map.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                sid = str(step.get("id", "")).strip()
                if not sid:
                    continue
                export_names, _errors = _producer_step_exports(
                    root,
                    consumer_doc_path=doc_path,
                    step=step,
                )
                for name in export_names:
                    exported.add((sid, str(name)))
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"

        def _scan_text(raw: str, where: str) -> None:
            for m in _CHAIN_TEMPLATE_PATTERN.finditer(str(raw)):
                dotted = m.group(1)
                parts = [p for p in dotted.split(".") if p]
                if len(parts) < 2:
                    violations.append(f"{doc_path.relative_to(root)}: case {case_id} {where} invalid chain template {m.group(0)}")
                    continue
                if (parts[0], parts[1]) not in exported:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} {where} unresolved chain reference {parts[0]}.{parts[1]}"
                    )

        request = case.get("request")
        if isinstance(request, dict):
            if isinstance(request.get("url"), str):
                _scan_text(str(request.get("url")), "request.url")
            headers = request.get("headers")
            if isinstance(headers, dict):
                for k, v in headers.items():
                    if isinstance(v, str):
                        _scan_text(v, f"request.headers.{k}")
            if isinstance(request.get("body_text"), str):
                _scan_text(str(request.get("body_text")), "request.body_text")
        requests = case.get("requests")
        if isinstance(requests, list):
            for idx, step in enumerate(requests):
                if not isinstance(step, dict):
                    continue
                if isinstance(step.get("url"), str):
                    _scan_text(str(step.get("url")), f"requests[{idx}].url")
                headers = step.get("headers")
                if isinstance(headers, dict):
                    for k, v in headers.items():
                        if isinstance(v, str):
                            _scan_text(v, f"requests[{idx}].headers.{k}")
                if isinstance(step.get("body_text"), str):
                    _scan_text(str(step.get("body_text")), f"requests[{idx}].body_text")
    return violations


def _iter_string_values(node: object):
    if isinstance(node, dict):
        for v in node.values():
            yield from _iter_string_values(v)
        return
    if isinstance(node, list):
        for v in node:
            yield from _iter_string_values(v)
        return
    if isinstance(node, str):
        yield node


def _any_pattern_matches(text: str, patterns: list[re.Pattern[str]]) -> bool:
    for pat in patterns:
        if pat.search(text):
            return True
    return False


def _scan_conformance_no_runner_logic_outside_harness(root: Path) -> list[str]:
    violations: list[str] = []
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return violations

    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case = spec.test
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        bad = sorted(k for k in case.keys() if str(k) in _RUNNER_KEYS_MUST_BE_UNDER_HARNESS)
        if bad:
            violations.append(
                f"{case_id}: runner/setup key(s) must be under harness: {', '.join(bad)}"
            )
    return violations


def _scan_conformance_portable_determinism_guard(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    violations: list[str] = []
    h = harness or {}
    determinism = h.get("determinism")
    if not isinstance(determinism, dict):
        return ["conformance.portable_determinism_guard requires harness.determinism mapping in governance spec"]
    try:
        evaluate = normalize_evaluate(
            determinism.get("evaluate"), field="harness.determinism.evaluate"
        )
    except ValueError as exc:
        return [str(exc)]
    raw_patterns = determinism.get("patterns")
    if not isinstance(raw_patterns, list) or not raw_patterns:
        return ["conformance.portable_determinism_guard requires non-empty harness.determinism.patterns list"]
    compiled_patterns: list[re.Pattern[str]] = []
    for raw in raw_patterns:
        if not isinstance(raw, str) or not raw.strip():
            violations.append("harness.determinism.patterns entries must be non-empty strings")
            continue
        try:
            compiled_patterns.append(re.compile(raw, re.IGNORECASE))
        except re.error as e:
            violations.append(f"invalid regex in harness.determinism.patterns: {raw!r} ({e})")
    raw_exclude = determinism.get("exclude_case_keys", ["id", "title", "purpose", "expect", "requires", "assert_health"])
    if not isinstance(raw_exclude, list) or any(not isinstance(x, str) for x in raw_exclude):
        violations.append("harness.determinism.exclude_case_keys must be a list of strings")
        return violations
    exclude_case_keys = {x for x in raw_exclude if x}
    if not compiled_patterns:
        return violations
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return violations

    rows: list[dict[str, object]] = []
    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case = spec.test
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        scoped = {
            k: v
            for k, v in case.items()
            if str(k) not in exclude_case_keys
        }
        rows.append(
            {
                "id": case_id,
                "strings": list(_iter_string_values(scoped)),
            }
        )

    pattern_values = [p.pattern for p in compiled_patterns]
    for row in rows:
        case_id = str(row.get("id", "<unknown>")).strip() or "<unknown>"
        strings = row.get("strings")
        if not isinstance(strings, list):
            continue
        if any(_any_pattern_matches(str(s), compiled_patterns) for s in strings):
            violations.append(
                f"{case_id}: non-deterministic token matched configured pattern in case content"
            )
    return _policy_outcome(
        subject={"rows": rows, "violations": list(violations)},
        evaluate=evaluate,
        policy_path="harness.determinism.evaluate",
        symbols={"patterns": pattern_values},
        violations=violations,
    )


def _scan_conformance_no_ambient_assumptions(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    violations: list[str] = []
    h = harness or {}
    ambient = h.get("ambient_assumptions")
    if not isinstance(ambient, dict):
        return ["conformance.no_ambient_assumptions requires harness.ambient_assumptions mapping in governance spec"]
    try:
        evaluate = normalize_evaluate(
            ambient.get("evaluate"), field="harness.ambient_assumptions.evaluate"
        )
    except ValueError as exc:
        return [str(exc)]
    raw_patterns = ambient.get("patterns")
    if not isinstance(raw_patterns, list) or not raw_patterns:
        return ["conformance.no_ambient_assumptions requires non-empty harness.ambient_assumptions.patterns list"]
    compiled_patterns: list[re.Pattern[str]] = []
    for raw in raw_patterns:
        if not isinstance(raw, str) or not raw.strip():
            violations.append("harness.ambient_assumptions.patterns entries must be non-empty strings")
            continue
        try:
            compiled_patterns.append(re.compile(raw, re.IGNORECASE))
        except re.error as e:
            violations.append(f"invalid regex in harness.ambient_assumptions.patterns: {raw!r} ({e})")
    raw_exclude = ambient.get("exclude_case_keys", ["id", "title", "purpose", "expect", "requires", "assert_health"])
    if not isinstance(raw_exclude, list) or any(not isinstance(x, str) for x in raw_exclude):
        violations.append("harness.ambient_assumptions.exclude_case_keys must be a list of strings")
        return violations
    exclude_case_keys = {x for x in raw_exclude if x}
    if not compiled_patterns:
        return violations
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return violations

    rows: list[dict[str, object]] = []
    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case = spec.test
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        scoped = {k: v for k, v in case.items() if str(k) not in exclude_case_keys}
        rows.append(
            {
                "id": case_id,
                "strings": list(_iter_string_values(scoped)),
            }
        )

    pattern_values = [p.pattern for p in compiled_patterns]
    for row in rows:
        case_id = str(row.get("id", "<unknown>")).strip() or "<unknown>"
        strings = row.get("strings")
        if not isinstance(strings, list):
            continue
        if any(_any_pattern_matches(str(s), compiled_patterns) for s in strings):
            violations.append(
                f"{case_id}: ambient-assumption token matched configured pattern in case content"
            )
    return _policy_outcome(
        subject={"rows": rows, "violations": violations},
        evaluate=evaluate,
        policy_path="harness.ambient_assumptions.evaluate",
        symbols={"patterns": pattern_values},
        violations=violations,
    )


def _scan_conformance_extension_requires_capabilities(root: Path) -> list[str]:
    violations: list[str] = []
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return violations

    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case = spec.test
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        case_type = str(case.get("type", "")).strip()
        if not case_type or case_type in _CORE_TYPES:
            continue

        requires = case.get("requires")
        if not isinstance(requires, dict):
            violations.append(f"{case_id}: extension type '{case_type}' requires mapping 'requires'")
            continue
        capabilities = requires.get("capabilities")
        if not isinstance(capabilities, list):
            violations.append(f"{case_id}: extension type '{case_type}' requires list requires.capabilities")
            continue
        cap_values = {str(v).strip() for v in capabilities if str(v).strip()}
        if case_type not in cap_values:
            violations.append(
                f"{case_id}: requires.capabilities must include extension type '{case_type}'"
            )
    return violations


def _load_type_contract_top_level_fields(root: Path, case_type: str) -> set[str]:
    rel = _type_contract_doc_rel_for(case_type)
    p = _join_contract_path(root, rel)
    if not p.exists():
        return set()
    fields: set[str] = set()
    in_fields_section = False
    current_section = ""
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            current_section = line[3:].strip().lower()
            in_fields_section = current_section in {"required fields", "optional fields"}
            continue
        if not in_fields_section or not line.startswith("- "):
            continue
        m = re.search(r"`([^`]+)`", line)
        if not m:
            continue
        token = m.group(1).strip()
        if not token:
            continue
        fields.add(token.split(".", 1)[0])
    return fields


def _scan_conformance_type_contract_field_sync(root: Path) -> list[str]:
    violations: list[str] = []
    cases_dir = root / "specs/conformance/cases"
    if not cases_dir.exists():
        return violations

    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case = spec.test
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        case_type = str(case.get("type", "")).strip()
        if not case_type:
            continue
        type_fields = _load_type_contract_top_level_fields(root, case_type)
        if not type_fields:
            # Missing type doc is handled by conformance.type_contract_docs.
            continue
        allowed = _COMMON_CASE_TOP_LEVEL_KEYS | type_fields
        bad = sorted(k for k in case.keys() if str(k) not in allowed)
        if bad:
            violations.append(
                f"{case_id}: key(s) not declared in type contract for {case_type}: {', '.join(bad)}"
            )
    return violations


def _scan_conformance_spec_lang_preferred(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("spec_lang_preferred")
    if not isinstance(cfg, dict):
        return ["conformance.spec_lang_preferred requires harness.spec_lang_preferred mapping in governance spec"]
    roots = cfg.get("roots")
    if (
        not isinstance(roots, list)
        or not roots
        or any(not isinstance(x, str) or not x.strip() for x in roots)
    ):
        return ["harness.spec_lang_preferred.roots must be a non-empty list of non-empty strings"]
    if "allow_sugar_files" in cfg:
        return ["harness.spec_lang_preferred.allow_sugar_files is not supported; assertions are evaluate-only in this surface"]
    try:
        evaluate = normalize_evaluate(
            cfg.get("evaluate"), field="harness.spec_lang_preferred.evaluate"
        )
    except ValueError as exc:
        return [str(exc)]

    all_rows: list[dict[str, object]] = []
    for rel_root in roots:
        base = _join_contract_path(root, rel_root)
        if not base.exists():
            violations.append(f"{rel_root}:1: missing conformance root for spec-lang preference scan")
            continue
        for spec in iter_cases(base, file_pattern=SETTINGS.case.default_file_pattern):
            try:
                rel = str(spec.doc_path.resolve().relative_to(root))
            except ValueError:
                rel = str(spec.doc_path)
            non_evaluate_ops: set[str] = set()

            def _collect_ops(node: object, *, inherited_target: str | None = None) -> None:
                if node is None:
                    return
                if isinstance(node, list):
                    for child in node:
                        _collect_ops(child, inherited_target=inherited_target)
                    return
                if not isinstance(node, dict):
                    return
                step_class = str(node.get("class", "")).strip() if "class" in node else ""
                if step_class in {"MUST", "MAY", "MUST_NOT"} and "asserts" in node:
                    node_target = str(node.get("target", "")).strip() or inherited_target
                    raw_checks = node.get("asserts")
                    if isinstance(raw_checks, list):
                        for child in raw_checks:
                            _collect_ops(child, inherited_target=node_target)
                    return
                present_groups = [k for k in ("MUST", "MAY", "MUST_NOT") if k in node]
                if present_groups:
                    node_target = str(node.get("target", "")).strip() or inherited_target
                    for key in present_groups:
                        children = node.get(key, [])
                        if isinstance(children, list):
                            for child in children:
                                _collect_ops(child, inherited_target=node_target)
                    return
                if "target" in node:
                    return
                if "evaluate" in node:
                    non_evaluate_ops.add("evaluate")
                    return
                # Expression-mapping leaf; canonical evaluate form.
                return
                for key in node.keys():
                    op = str(key).strip()
                    if not op or op in {"target", "MUST", "MAY", "MUST_NOT"}:
                        continue
                    if op != "evaluate":
                        non_evaluate_ops.add(op)

            _collect_ops(spec.test.get("contract", []) or [])
            case_id = str(spec.test.get("id", "<unknown>")).strip() or "<unknown>"
            all_rows.append(
                {
                    "id": case_id,
                    "file": rel,
                    "non_evaluate_ops": sorted(non_evaluate_ops),
                }
            )

    for row in all_rows:
        ops = row.get("non_evaluate_ops")
        if not isinstance(ops, list) or not ops:
            continue
        case_id = str(row.get("id", "<unknown>")).strip() or "<unknown>"
        rel = str(row.get("file", "<unknown>"))
        found = ", ".join(str(x) for x in ops)
        violations.append(
            f"{rel}: case {case_id} uses unsupported sugar ops ({found}); "
            "use evaluate-only assertions for conformance/governance surfaces"
        )
    return _policy_outcome(
        subject=all_rows,
        evaluate=evaluate,
        policy_path="harness.spec_lang_preferred.evaluate",
        violations=violations,
    )


def _scan_impl_evaluate_first_required(root: Path, *, harness: dict | None = None) -> GovernanceCheckOutcome:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("impl_evaluate_first")
    if not isinstance(cfg, dict):
        return ["impl.evaluate_first_required requires harness.impl_evaluate_first mapping in governance spec"]
    roots = cfg.get("roots")
    if (
        not isinstance(roots, list)
        or not roots
        or any(not isinstance(x, str) or not x.strip() for x in roots)
    ):
        return ["harness.impl_evaluate_first.roots must be a non-empty list of non-empty strings"]
    allow_case_ids_raw = cfg.get("allow_sugar_case_ids", [])
    if not isinstance(allow_case_ids_raw, list) or any(
        not isinstance(x, str) for x in allow_case_ids_raw
    ):
        return ["harness.impl_evaluate_first.allow_sugar_case_ids must be a list of strings"]
    allow_case_ids = {x.strip() for x in allow_case_ids_raw if x.strip()}
    try:
        evaluate = normalize_evaluate(
            cfg.get("evaluate"), field="harness.impl_evaluate_first.evaluate"
        )
    except ValueError as exc:
        return [str(exc)]

    def _collect_non_eval_ops(node: object, out: set[str]) -> None:
        if node is None:
            return
        if isinstance(node, list):
            for child in node:
                _collect_non_eval_ops(child, out)
            return
        if not isinstance(node, dict):
            return
        step_class = str(node.get("class", "")).strip() if "class" in node else ""
        if step_class in {"MUST", "MAY", "MUST_NOT"} and "asserts" in node:
            raw_checks = node.get("asserts")
            if isinstance(raw_checks, list):
                for child in raw_checks:
                    _collect_non_eval_ops(child, out)
            return
        present_groups = [k for k in ("MUST", "MAY", "MUST_NOT") if k in node]
        if present_groups:
            for key in present_groups:
                children = node.get(key, [])
                if isinstance(children, list):
                    for child in children:
                        _collect_non_eval_ops(child, out)
            return
        if "target" in node:
            return
        if "evaluate" in node:
            out.add("evaluate")
            return
        # Expression-mapping leaf; canonical evaluate form.
        return
        for key in node.keys():
            op = str(key).strip()
            if not op or op in {"target", "MUST", "MAY", "MUST_NOT"}:
                continue
            if op != "evaluate":
                out.add(op)

    all_rows: list[dict[str, object]] = []
    for rel_root in roots:
        base = _join_contract_path(root, rel_root)
        if not base.exists():
            violations.append(f"{rel_root}:1: missing impl root for evaluate-first scan")
            continue
        for spec_file in sorted(base.rglob(SETTINGS.case.default_file_pattern)):
            if not spec_file.is_file():
                continue
            for spec in iter_spec_doc_tests(spec_file.parent, file_pattern=spec_file.name):
                try:
                    rel = str(spec.doc_path.resolve().relative_to(root))
                except ValueError:
                    rel = str(spec.doc_path)
                non_evaluate_ops: set[str] = set()
                _collect_non_eval_ops(spec.test.get("contract", []) or [], non_evaluate_ops)
                case_id = str(spec.test.get("id", "<unknown>")).strip() or "<unknown>"
                is_allowlisted = case_id in allow_case_ids
                all_rows.append(
                    {
                        "id": case_id,
                        "file": rel,
                        "type": str(spec.test.get("type", "")).strip(),
                        "non_evaluate_ops": sorted(non_evaluate_ops),
                        "allowlisted": is_allowlisted,
                    }
                )
                if non_evaluate_ops and not is_allowlisted:
                    found = ", ".join(sorted(non_evaluate_ops))
                    violations.append(
                        f"{rel}: case {case_id} uses unsupported sugar ops ({found}); "
                        "use evaluate-first assertions for impl surface or add explicit allow_sugar_case_ids entry"
                    )

    return _policy_outcome(
        subject=all_rows,
        evaluate=evaluate,
        policy_path="harness.impl_evaluate_first.evaluate",
        violations=violations,
    )


def _scan_impl_evaluate_ratio_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("impl_evaluate_first_non_regression")
    if not isinstance(cfg, dict):
        return [
            "impl.evaluate_ratio_non_regression requires harness.impl_evaluate_first_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.impl_evaluate_first_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("spec_lang_adoption")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.impl_evaluate_first_non_regression.spec_lang_adoption must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.impl_evaluate_first_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.impl_evaluate_first_non_regression.epsilon must be >= 0"]

    current = spec_lang_adoption_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current spec-lang adoption report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get(
            "summary_fields",
            {"overall_logic_self_contained_ratio": "non_decrease"},
        ),
        segment_fields=cfg.get(
            "segment_fields",
            {"impl": {"mean_logic_self_contained_ratio": "non_decrease"}},
        ),
        epsilon=epsilon,
    )


def _scan_impl_library_usage_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("impl_library_usage_non_regression")
    if not isinstance(cfg, dict):
        return [
            "impl.library_usage_non_regression requires harness.impl_library_usage_non_regression mapping in governance spec"
        ]
    baseline_path = str(cfg.get("baseline_path", "")).strip()
    if not baseline_path:
        return ["harness.impl_library_usage_non_regression.baseline_path must be a non-empty string"]
    report_cfg = cfg.get("spec_lang_adoption")
    if report_cfg is not None and not isinstance(report_cfg, dict):
        return ["harness.impl_library_usage_non_regression.spec_lang_adoption must be a mapping when provided"]
    epsilon_raw = cfg.get("epsilon", 1e-12)
    try:
        epsilon = float(epsilon_raw)
    except (TypeError, ValueError):
        return ["harness.impl_library_usage_non_regression.epsilon must be numeric"]
    if epsilon < 0:
        return ["harness.impl_library_usage_non_regression.epsilon must be >= 0"]

    current = spec_lang_adoption_report_jsonable(root, config=report_cfg)
    current_errs = current.get("errors") or []
    if isinstance(current_errs, list) and any(str(e).strip() for e in current_errs):
        return [f"current spec-lang adoption report has errors: {str(e)}" for e in current_errs if str(e).strip()]
    baseline, baseline_errs = _load_baseline_json(root, baseline_path)
    if baseline is None:
        return baseline_errs
    return compare_metric_non_regression(
        current=current,
        baseline=baseline,
        summary_fields=cfg.get(
            "summary_fields",
            {"impl_library_backed_case_ratio": "non_decrease"},
        ),
        segment_fields=cfg.get(
            "segment_fields",
            {"impl": {"library_backed_case_ratio": "non_decrease"}},
        ),
        epsilon=epsilon,
    )


def _scan_conformance_spec_lang_fixture_library_usage(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("spec_lang_fixture_library_usage")
    if not isinstance(cfg, dict):
        return ["conformance.spec_lang_fixture_library_usage requires harness.spec_lang_fixture_library_usage mapping in governance spec"]
    rel = str(cfg.get("path", "specs/conformance/cases/core/spec_lang.spec.md")).strip() or "specs/conformance/cases/core/spec_lang.spec.md"
    required_library_path = str(cfg.get("required_library_path", "")).strip()
    if not required_library_path:
        return ["harness.spec_lang_fixture_library_usage.required_library_path must be a non-empty string"]
    required_call_prefix = str(cfg.get("required_call_prefix", "conf.")).strip() or "conf."
    min_call_count = cfg.get("min_call_count", 1)
    if not isinstance(min_call_count, int) or min_call_count < 1:
        return ["harness.spec_lang_fixture_library_usage.min_call_count must be a positive int"]
    required_case_ids_raw = cfg.get("required_case_ids", [])
    if not isinstance(required_case_ids_raw, list) or any(not isinstance(x, str) or not x.strip() for x in required_case_ids_raw):
        return ["harness.spec_lang_fixture_library_usage.required_case_ids must be a list of non-empty strings"]
    required_case_ids = {str(x).strip() for x in required_case_ids_raw if str(x).strip()}

    fixture = _join_contract_path(root, rel)
    if not fixture.exists():
        return [f"{rel}:1: missing conformance fixture file"]

    def _count_helper_calls(node: object) -> int:
        if isinstance(node, list):
            return sum(_count_helper_calls(x) for x in node)
        if not isinstance(node, dict):
            return 0
        count = 0
        call_node = node.get("call")
        if isinstance(call_node, list) and call_node:
            fn_node = call_node[0]
            if (
                isinstance(fn_node, dict)
                and len(fn_node) == 1
                and "var" in fn_node
                and isinstance(fn_node.get("var"), str)
                and str(fn_node.get("var", "")).startswith(required_call_prefix)
            ):
                count += 1
        for v in node.values():
            count += _count_helper_calls(v)
        return count

    total_calls = 0
    seen_required: set[str] = set()
    violations: list[str] = []
    for spec in iter_spec_doc_tests(fixture.parent, file_pattern=fixture.name):
        case = spec.test if isinstance(spec.test, dict) else {}
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        if str(case.get("type", "")).strip() not in {"text.file", "contract.check"}:
            continue
        lib_ok = any(str(x).strip() == required_library_path for x in _collect_chain_library_refs(case))
        calls = _count_helper_calls(case.get("contract"))
        total_calls += calls
        if case_id in required_case_ids:
            seen_required.add(case_id)
            if not lib_ok:
                violations.append(f"{rel}: case {case_id} missing chain library ref {required_library_path}")
            if calls < 1:
                violations.append(f"{rel}: case {case_id} missing helper call with prefix {required_call_prefix!r}")

    missing_ids = sorted(required_case_ids - seen_required)
    for case_id in missing_ids:
        violations.append(f"{rel}: required_case_ids entry not found: {case_id}")
    if total_calls < min_call_count:
        violations.append(
            f"{rel}: helper call count {total_calls} is below min_call_count {min_call_count} for prefix {required_call_prefix!r}"
        )
    return violations


def _scan_conformance_library_contract_cases_present(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    h = harness or {}
    cfg = h.get("conformance_library_contract_cases_present")
    if not isinstance(cfg, dict):
        return [
            "conformance.library_contract_cases_present requires harness.conformance_library_contract_cases_present mapping in governance spec"
        ]
    rel = str(cfg.get("path", "")).strip()
    if not rel:
        return [
            "harness.conformance_library_contract_cases_present.path must be a non-empty string"
        ]
    required_case_ids_raw = cfg.get("required_case_ids")
    if (
        not isinstance(required_case_ids_raw, list)
        or not required_case_ids_raw
        or any(not isinstance(x, str) or not x.strip() for x in required_case_ids_raw)
    ):
        return [
            "harness.conformance_library_contract_cases_present.required_case_ids must be a non-empty list of non-empty strings"
        ]
    required_case_ids = {str(x).strip() for x in required_case_ids_raw}

    fixture = _join_contract_path(root, rel)
    if not fixture.exists():
        return [f"{rel}:1: missing conformance fixture file"]

    found_case_ids: set[str] = set()
    evaluate_case_ids: set[str] = set()
    for spec in iter_spec_doc_tests(fixture.parent, file_pattern=fixture.name):
        case = spec.test if isinstance(spec.test, dict) else {}
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        found_case_ids.add(case_id)
        raw_assert = case.get("contract")
        if isinstance(raw_assert, list) and any(True for _ in _iter_evaluate_expr_nodes(raw_assert)):
            evaluate_case_ids.add(case_id)

    violations: list[str] = []
    for case_id in sorted(required_case_ids):
        if case_id not in found_case_ids:
            violations.append(f"{rel}: missing required conformance case id {case_id}")
            continue
        if case_id not in evaluate_case_ids:
            violations.append(f"{rel}: required case {case_id} must include evaluate assertions")
    return violations


def _scan_docs_reference_surface_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("docs_reference_surface")
    if not isinstance(cfg, dict):
        return ["docs.reference_surface_complete requires harness.docs_reference_surface mapping in governance spec"]

    required_files = cfg.get("required_files")
    if (
        not isinstance(required_files, list)
        or not required_files
        or any(not isinstance(x, str) or not x.strip() for x in required_files)
    ):
        return ["harness.docs_reference_surface.required_files must be a non-empty list of non-empty strings"]

    required_globs = cfg.get("required_globs", [])
    if not isinstance(required_globs, list) or any(not isinstance(x, str) or not x.strip() for x in required_globs):
        return ["harness.docs_reference_surface.required_globs must be a list of non-empty strings"]

    for rel in required_files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing required reference file")

    for pattern in required_globs:
        matches = sorted(root.glob(pattern))
        if not matches:
            violations.append(f"{pattern}:1: glob matched no files")
    return violations


def _extract_backtick_paths(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"`([^`]+)`", text) if m.group(1).strip()]


def _scan_docs_reference_index_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("reference_index")
    if not isinstance(cfg, dict):
        return ["docs.reference_index_sync requires harness.reference_index mapping in governance spec"]

    index_rel = str(cfg.get("path", "")).strip()
    include_glob = str(cfg.get("include_glob", "")).strip()
    if not index_rel:
        return ["harness.reference_index.path must be a non-empty string"]
    if not include_glob:
        return ["harness.reference_index.include_glob must be a non-empty string"]

    exclude_files = cfg.get("exclude_files", [])
    if not isinstance(exclude_files, list) or any(not isinstance(x, str) for x in exclude_files):
        return ["harness.reference_index.exclude_files must be a list of strings"]
    exclude = {x.strip() for x in exclude_files if x.strip()}

    index_path = _join_contract_path(root, index_rel)
    if not index_path.exists():
        return [f"{index_rel}:1: missing reference index file"]

    include_norm = include_glob.lstrip("/")
    expected = []
    for p in sorted(root.glob(include_norm)):
        relp = str(p.relative_to(root)).replace("\\", "/")
        if relp in exclude or ("/" + relp) in exclude:
            continue
        expected.append(relp)
    raw = index_path.read_text(encoding="utf-8")
    listed = [
        p.lstrip("/")
        for p in _extract_backtick_paths(raw)
        if p.lstrip("/").startswith("docs/book/") and p.lstrip("/").endswith(".md")
    ]
    seen: set[str] = set()
    deduped_listed: list[str] = []
    for rel in listed:
        if rel in seen:
            violations.append(f"{index_rel}:1: duplicate entry {rel}")
            continue
        seen.add(rel)
        deduped_listed.append(rel)

    for rel in expected:
        if rel not in seen:
            violations.append(f"{index_rel}:1: missing entry {rel}")
    for rel in deduped_listed:
        if rel not in expected:
            violations.append(f"{index_rel}:1: stale entry {rel}")
    if deduped_listed and expected and deduped_listed != expected:
        violations.append(
            f"{index_rel}:1: entries are out of sync or out of order with {include_glob}"
        )
    return violations


def _scan_docs_book_chapter_order_canonical(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    manifest, issues = load_reference_manifest(root, "docs/book/reference_manifest.yaml")
    if issues:
        return [x.render() for x in issues]
    chapters = manifest.get("chapters") if isinstance(manifest, dict) else None
    if not isinstance(chapters, list):
        return ["docs/book/reference_manifest.yaml:1: chapters must be a non-empty list"]
    actual = []
    for row in chapters:
        if isinstance(row, dict):
            actual.append(str(row.get("path", "")).strip())
    expected = [
        "/docs/book/10_getting_started.md",
        "/docs/book/20_case_model.md",
        "/docs/book/30_assertion_model.md",
        "/docs/book/40_spec_lang_authoring.md",
        "/docs/book/50_library_authoring.md",
        "/docs/book/60_runner_and_gates.md",
        "/docs/book/70_governance_and_quality.md",
        "/docs/book/80_troubleshooting.md",
        "/docs/book/90_reference_guide.md",
        "/docs/book/91_appendix_runner_api_reference.md",
        "/docs/book/92_appendix_harness_type_reference.md",
        "/docs/book/93_appendix_spec_lang_builtin_catalog.md",
        "/docs/book/93a_std_core.md",
        "/docs/book/93b_std_logic.md",
        "/docs/book/93c_std_math.md",
        "/docs/book/93d_std_string.md",
        "/docs/book/93e_std_collection.md",
        "/docs/book/93f_std_object.md",
        "/docs/book/93g_std_type.md",
        "/docs/book/93h_std_set.md",
        "/docs/book/93i_std_json_schema_fn_null.md",
        "/docs/book/93j_library_symbol_reference.md",
        "/docs/book/93k_library_symbol_index.md",
        "/docs/book/93l_spec_case_reference.md",
        "/docs/book/93m_spec_case_index.md",
        "/docs/book/93n_spec_case_templates_reference.md",
        "/docs/book/94_appendix_contract_policy_reference.md",
        "/docs/book/95_appendix_traceability_reference.md",
        "/docs/book/96_appendix_governance_checks_reference.md",
        "/docs/book/97_appendix_metrics_reference.md",
        "/docs/book/98_appendix_spec_case_shape_reference.md",
        "/docs/book/99_generated_reference_index.md",
    ]
    if actual != expected:
        return [
            "docs/book/reference_manifest.yaml:1: canonical chapter order mismatch for docs.book_chapter_order_canonical"
        ]
    return []


def _load_docs_quality_context(root: Path, harness: dict | None = None) -> tuple[dict, list[str], dict[str, dict], list[str]]:
    h = harness or {}
    cfg = h.get("docs_quality")
    if not isinstance(cfg, dict):
        return {}, [], {}, ["docs_quality config required in harness.docs_quality"]
    manifest_rel = str(cfg.get("manifest", "")).strip()
    if not manifest_rel:
        return {}, [], {}, ["harness.docs_quality.manifest must be a non-empty string"]
    manifest, manifest_issues = load_reference_manifest(root, manifest_rel)
    if manifest_issues:
        return {}, [], {}, [x.render() for x in manifest_issues]
    docs = manifest_chapter_paths(manifest)
    metas, meta_issues, _meta_lines = load_docs_meta_for_paths(root, docs)
    meta_msgs = [x.render() for x in meta_issues]
    for rel in docs:
        if rel in metas:
            metas[rel]["__text__"] = (_join_contract_path(root, rel)).read_text(encoding="utf-8")
    return manifest, docs, metas, meta_msgs


def _scan_docs_meta_schema_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    _manifest, _docs, _metas, meta_msgs = _load_docs_quality_context(root, harness)
    if meta_msgs:
        return meta_msgs
    return []


def _scan_docs_reference_manifest_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("docs_quality")
    if not isinstance(cfg, dict):
        return ["docs.reference_manifest_sync requires harness.docs_quality mapping in governance spec"]
    manifest, _docs, _metas, msgs = _load_docs_quality_context(root, harness)
    if msgs:
        return msgs
    index_rel = str(cfg.get("index_out", "docs/book/reference_index.md")).strip()
    index_path = _join_contract_path(root, index_rel)
    expected = render_reference_index(manifest)
    if not index_path.exists():
        return [f"{index_rel}:1: missing generated reference index"]
    if index_path.read_text(encoding="utf-8") != expected:
        return [f"{index_rel}:1: out of sync with docs_quality manifest"]
    return []


def _scan_docs_token_ownership_unique(root: Path, *, harness: dict | None = None) -> list[str]:
    _manifest, _docs, metas, msgs = _load_docs_quality_context(root, harness)
    if msgs:
        return msgs
    return [x.render() for x in check_token_ownership_unique(metas)]


def _scan_docs_token_dependency_resolved(root: Path, *, harness: dict | None = None) -> list[str]:
    _manifest, _docs, metas, msgs = _load_docs_quality_context(root, harness)
    if msgs:
        return msgs
    return [x.render() for x in check_token_dependency_resolved(metas)]


def _scan_docs_instructions_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    _manifest, _docs, metas, msgs = _load_docs_quality_context(root, harness)
    if msgs:
        return msgs
    return [x.render() for x in check_instructions_complete(root, metas)]


def _scan_docs_command_examples_verified(root: Path, *, harness: dict | None = None) -> list[str]:
    _manifest, docs, _metas, msgs = _load_docs_quality_context(root, harness)
    if msgs:
        return msgs
    return [x.render() for x in check_command_examples_verified(root, docs)]


def _scan_docs_example_id_uniqueness(root: Path, *, harness: dict | None = None) -> list[str]:
    _manifest, _docs, metas, msgs = _load_docs_quality_context(root, harness)
    if msgs:
        return msgs
    return [x.render() for x in check_example_id_uniqueness(metas)]


def _scan_docs_generated_files_clean(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("docs_quality")
    if not isinstance(cfg, dict):
        return ["docs.generated_files_clean requires harness.docs_quality mapping in governance spec"]
    manifest, _docs, metas, msgs = _load_docs_quality_context(root, harness)
    if msgs:
        return msgs

    index_rel = str(cfg.get("index_out", "docs/book/reference_index.md")).strip()
    coverage_rel = str(cfg.get("coverage_out", "docs/book/reference_coverage.md")).strip()
    graph_rel = str(cfg.get("graph_out", "docs/book/docs_graph.json")).strip()
    index_path = _join_contract_path(root, index_rel)
    coverage_path = _join_contract_path(root, coverage_rel)
    graph_path = _join_contract_path(root, graph_rel)

    out: list[str] = []
    expected_index = render_reference_index(manifest)
    expected_coverage = render_reference_coverage(root, metas)
    expected_graph = json.dumps(build_docs_graph(root, metas), indent=2, sort_keys=True) + "\n"

    def _append_mismatch(rel: str, path: Path, expected: str) -> None:
        if not path.exists():
            out.append(f"{rel}:1: generated file missing")
            return
        actual = path.read_text(encoding="utf-8")
        if actual == expected:
            return
        exp_lines = expected.splitlines()
        act_lines = actual.splitlines()
        max_len = max(len(exp_lines), len(act_lines))
        line_no = 1
        for i in range(max_len):
            e = exp_lines[i] if i < len(exp_lines) else "<EOF>"
            a = act_lines[i] if i < len(act_lines) else "<EOF>"
            if e != a:
                line_no = i + 1
                out.append(
                    f"{rel}:{line_no}: generated file out of date "
                    f"(expected={e!r} actual={a!r})"
                )
                return
        out.append(f"{rel}:1: generated file out of date")

    _append_mismatch(index_rel, index_path, expected_index)
    _append_mismatch(coverage_rel, coverage_path, expected_coverage)
    _append_mismatch(graph_rel, graph_path, expected_graph)
    return out


def _run_python_script_check(root: Path, args: list[str]) -> list[str]:
    py = root / ".venv/bin/python"
    cmd = [str(py if py.exists() else Path("python3")), *args]
    try:
        cp = _profiled_subprocess_run(
            cmd,
            cwd=root,
            phase="governance.python_script_check",
        )
    except LivenessError as exc:
        return [
            f"{' '.join(args)} failed liveness watchdog: {exc.reason_token}"
        ]
    if cp.returncode == 0:
        return []
    lines = [x.strip() for x in ((cp.stdout or "") + "\n" + (cp.stderr or "")).splitlines() if x.strip()]
    if not lines:
        return [f"{' '.join(args)} failed with exit code {cp.returncode}"]
    return lines


def _run_python_module_check(root: Path, module: str, args: list[str]) -> list[str]:
    py = root / ".venv/bin/python"
    cmd = [str(py if py.exists() else Path("python3")), "-m", module, *args]
    try:
        cp = _profiled_subprocess_run(
            cmd,
            cwd=root,
            phase="governance.python_module_check",
        )
    except LivenessError as exc:
        return [
            f"-m {module} {' '.join(args)} failed liveness watchdog: {exc.reason_token}"
        ]
    if cp.returncode == 0:
        return []
    lines = [x.strip() for x in ((cp.stdout or "") + "\n" + (cp.stderr or "")).splitlines() if x.strip()]
    if not lines:
        return [f"-m {module} {' '.join(args)} failed with exit code {cp.returncode}"]
    return lines


def _scan_docs_generator_registry_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    registry, issues = load_docs_generator_registry(root)
    out = [x.render() for x in issues]
    if registry is None:
        return out
    required_surfaces = {
        "reference_book",
        "schema_docs",
        "docs_graph",
        "runner_api_catalog",
        "harness_type_catalog",
        "spec_lang_builtin_catalog",
        "spec_lang_namespace_core",
        "spec_lang_namespace_logic",
        "spec_lang_namespace_math",
        "spec_lang_namespace_string",
        "spec_lang_namespace_collection",
        "spec_lang_namespace_object",
        "spec_lang_namespace_type",
        "spec_lang_namespace_set",
        "spec_lang_namespace_json_schema_fn_null",
        "spec_case_reference",
        "policy_rule_catalog",
        "traceability_catalog",
        "governance_check_catalog",
        "metrics_field_catalog",
        "spec_schema_field_catalog",
    }
    seen = {
        str(x.get("surface_id", "")).strip()
        for x in (registry.get("surfaces") or [])
        if isinstance(x, dict)
    }
    missing = sorted(required_surfaces - seen)
    for sid in missing:
        out.append(f"{DOCS_GENERATOR_REGISTRY_PATH.as_posix()}: missing required surface_id {sid}")
    return out


def _scan_docs_generator_outputs_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(
        root,
        "spec_runner.spec_lang_commands",
        ["docs-generate-all", "--check"],
    )


def _iter_library_export_entries(root: Path) -> list[tuple[str, str, int, dict[str, Any]]]:
    out: list[tuple[str, str, int, dict[str, Any]]] = []
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return out
    for spec in iter_spec_doc_tests(libs_root, file_pattern=case_file_name("*")):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "contract.export":
            continue
        case_id = str(case.get("id", "")).strip() or "<unknown>"
        harness_map = case.get("harness")
        exports = harness_map.get("exports") if isinstance(harness_map, dict) else None
        if not isinstance(exports, list):
            continue
        rel = spec.doc_path.relative_to(root).as_posix()
        for idx, exp in enumerate(exports):
            if not isinstance(exp, dict):
                continue
            out.append((rel, case_id, idx, exp))
    return out


def _iter_spec_cases(root: Path) -> list[tuple[str, str, dict[str, Any]]]:
    out: list[tuple[str, str, dict[str, Any]]] = []
    specs_root = root / "specs"
    if not specs_root.exists():
        return out
    for spec in iter_spec_doc_tests(specs_root, file_pattern=case_file_name("*")):
        case = spec.test if isinstance(spec.test, dict) else {}
        case_id = str(case.get("id", "")).strip() or "<unknown>"
        rel = spec.doc_path.relative_to(root).as_posix()
        out.append((rel, case_id, case))
    return out


def _scan_docs_library_symbol_metadata_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    out: list[str] = []
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return ["specs/libraries:1: missing library spec root"]
    for spec in iter_spec_doc_tests(libs_root, file_pattern=case_file_name("*")):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "contract.export":
            continue
        case_id = str(case.get("id", "")).strip() or "<unknown>"
        rel = spec.doc_path.relative_to(root).as_posix()
        library = case.get("library")
        if not isinstance(library, dict):
            out.append(f"{rel}:{case_id}: missing required library metadata mapping")
            continue
        for key in ("id", "module", "stability", "owner"):
            if not str(library.get(key, "")).strip():
                out.append(f"{rel}:{case_id}: library.{key} must be non-empty")
        stability = str(library.get("stability", "")).strip()
        if stability not in {"alpha", "beta", "stable", "internal"}:
            out.append(
                f"{rel}:{case_id}: library.stability must be alpha|beta|stable|internal"
            )

    allowed_doc_keys = {
        "summary",
        "description",
        "params",
        "returns",
        "errors",
        "examples",
        "portability",
        "see_also",
        "since",
        "deprecated",
    }
    for rel, case_id, idx, exp in _iter_library_export_entries(root):
        doc = exp.get("doc")
        if not isinstance(doc, dict):
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc must be mapping")
            continue
        unknown = sorted(str(k) for k in doc.keys() if str(k) not in allowed_doc_keys)
        if unknown:
            out.append(
                f"{rel}:{case_id}: harness.exports[{idx}].doc has unsupported keys: {', '.join(unknown)}"
            )
        if not str(doc.get("summary", "")).strip():
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc.summary must be non-empty")
        if not str(doc.get("description", "")).strip():
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc.description must be non-empty")
        returns = doc.get("returns")
        if not isinstance(returns, dict):
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc.returns must be mapping")
        else:
            if not str(returns.get("type", "")).strip():
                out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc.returns.type must be non-empty")
            if not str(returns.get("description", "")).strip():
                out.append(
                    f"{rel}:{case_id}: harness.exports[{idx}].doc.returns.description must be non-empty"
                )
        errors = doc.get("errors")
        if not isinstance(errors, list) or not errors:
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc.errors must be non-empty list")
        portability = doc.get("portability")
        if not isinstance(portability, dict):
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc.portability must be mapping")
        else:
            for runtime in ("python", "php", "rust"):
                if not isinstance(portability.get(runtime), bool):
                    out.append(
                        f"{rel}:{case_id}: harness.exports[{idx}].doc.portability.{runtime} must be bool"
                    )
    return out


def _scan_docs_library_symbol_params_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    out: list[str] = []
    for rel, case_id, idx, exp in _iter_library_export_entries(root):
        params = exp.get("params")
        if not isinstance(params, list):
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].params must be list")
            continue
        param_names = [str(x).strip() for x in params]
        if any(not name for name in param_names):
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].params must be non-empty strings")
            continue
        doc = exp.get("doc")
        if not isinstance(doc, dict):
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc must be mapping")
            continue
        doc_params = doc.get("params")
        if not isinstance(doc_params, list):
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc.params must be list")
            continue
        doc_names = [str(item.get("name", "")).strip() for item in doc_params if isinstance(item, dict)]
        if doc_names != param_names:
            out.append(
                f"{rel}:{case_id}: harness.exports[{idx}].doc.params names must match params exactly"
            )
    return out


def _scan_docs_library_symbol_examples_present(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    out: list[str] = []
    for rel, case_id, idx, exp in _iter_library_export_entries(root):
        doc = exp.get("doc")
        if not isinstance(doc, dict):
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc must be mapping")
            continue
        examples = doc.get("examples")
        if not isinstance(examples, list) or not examples:
            out.append(f"{rel}:{case_id}: harness.exports[{idx}].doc.examples must be non-empty list")
            continue
        for ex_idx, example in enumerate(examples):
            if not isinstance(example, dict):
                out.append(
                    f"{rel}:{case_id}: harness.exports[{idx}].doc.examples[{ex_idx}] must be mapping"
                )
                continue
            if not str(example.get("title", "")).strip():
                out.append(
                    f"{rel}:{case_id}: harness.exports[{idx}].doc.examples[{ex_idx}].title must be non-empty"
                )
            if example.get("input") is None:
                out.append(
                    f"{rel}:{case_id}: harness.exports[{idx}].doc.examples[{ex_idx}].input is required"
                )
            if example.get("expected") is None:
                out.append(
                    f"{rel}:{case_id}: harness.exports[{idx}].doc.examples[{ex_idx}].expected is required"
                )
    return out


def _scan_docs_library_symbol_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(
        root,
        "spec_runner.spec_lang_commands",
        ["generate-library-symbol-catalog", "--check"],
    )


def _scan_docs_spec_case_doc_metadata_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    out: list[str] = []
    allowed = {"summary", "description", "audience", "since", "tags", "see_also", "deprecated"}
    for rel, case_id, case in _iter_spec_cases(root):
        if str(case.get("type", "")).strip() != "contract.export":
            continue
        where = f"{rel}:{case_id}"
        raw_doc = case.get("doc")
        if not isinstance(raw_doc, dict):
            out.append(f"{where}: contract.export requires root doc mapping")
            continue
        unknown = sorted(str(k) for k in raw_doc.keys() if str(k) not in allowed)
        if unknown:
            out.append(f"{where}: unsupported doc keys: {', '.join(unknown)}")
        for key in ("summary", "description", "audience", "since"):
            if not str(raw_doc.get(key, "")).strip():
                out.append(f"{where}: doc.{key} must be non-empty")
        tags = raw_doc.get("tags")
        if tags is not None and (
            not isinstance(tags, list) or any(not isinstance(x, str) or not str(x).strip() for x in tags)
        ):
            out.append(f"{where}: doc.tags must be list of non-empty strings when provided")
        see_also = raw_doc.get("see_also")
        if see_also is not None and (
            not isinstance(see_also, list)
            or any(not isinstance(x, str) or not str(x).strip() for x in see_also)
        ):
            out.append(f"{where}: doc.see_also must be list of non-empty strings when provided")
        deprecated = raw_doc.get("deprecated")
        if deprecated is not None:
            if not isinstance(deprecated, dict):
                out.append(f"{where}: doc.deprecated must be mapping when provided")
            else:
                if not str(deprecated.get("replacement", "")).strip():
                    out.append(f"{where}: doc.deprecated.replacement must be non-empty")
                if not str(deprecated.get("reason", "")).strip():
                    out.append(f"{where}: doc.deprecated.reason must be non-empty")
    return out


def _scan_docs_spec_case_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(
        root,
        "spec_runner.spec_lang_commands",
        ["generate-spec-case-catalog", "--check"],
    )


def _scan_docs_spec_domain_grouping_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    check_errors = _run_python_module_check(
        root,
        "spec_runner.spec_lang_commands",
        ["generate-spec-case-catalog", "--check"],
    )
    if check_errors:
        return check_errors
    catalog_path = root / ".artifacts/spec-case-catalog.json"
    if not catalog_path.exists():
        return [".artifacts/spec-case-catalog.json: missing generated artifact for domain grouping"]
    try:
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f".artifacts/spec-case-catalog.json:{exc.lineno}: invalid JSON ({exc.msg})"]
    if not isinstance(raw, dict):
        return [".artifacts/spec-case-catalog.json: expected object root"]
    domains = raw.get("domains")
    if not isinstance(domains, list):
        return [".artifacts/spec-case-catalog.json: missing domains summary list"]
    rows = raw.get("cases")
    if not isinstance(rows, list):
        return [".artifacts/spec-case-catalog.json: missing cases list"]
    violations: list[str] = []
    seen_domain_rows: dict[str, int] = {}
    prior_key: tuple[str, str, str] | None = None
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append(f".artifacts/spec-case-catalog.json: cases[{idx}] must be object")
            continue
        domain = str(row.get("domain", "")).strip()
        if not domain:
            violations.append(f".artifacts/spec-case-catalog.json: cases[{idx}].domain must be non-empty")
            continue
        case_type = str(row.get("type", "")).strip()
        case_id = str(row.get("case_id", "")).strip()
        key = (domain, case_type, case_id)
        if prior_key is not None and key < prior_key:
            violations.append(
                ".artifacts/spec-case-catalog.json: cases are not sorted by (domain, type, case_id)"
            )
            break
        prior_key = key
        seen_domain_rows[domain] = seen_domain_rows.get(domain, 0) + 1
    prior_domain = ""
    for idx, item in enumerate(domains):
        if not isinstance(item, dict):
            violations.append(f".artifacts/spec-case-catalog.json: domains[{idx}] must be object")
            continue
        domain = str(item.get("domain", "")).strip()
        if not domain:
            violations.append(f".artifacts/spec-case-catalog.json: domains[{idx}].domain must be non-empty")
            continue
        if prior_domain and domain < prior_domain:
            violations.append(".artifacts/spec-case-catalog.json: domains summary must be sorted by domain")
            break
        prior_domain = domain
        expected_count = seen_domain_rows.get(domain, 0)
        case_count = item.get("case_count")
        if not isinstance(case_count, int) or case_count != expected_count:
            violations.append(
                f".artifacts/spec-case-catalog.json: domains[{idx}] case_count mismatch for domain {domain}"
            )
    return violations


def _scan_docs_generation_spec_cases_present(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    cases_root = root / "specs/impl/docs_generate/cases"
    if not cases_root.exists():
        return ["specs/impl/docs_generate/cases:1: missing docs.generate case tree"]
    hits: list[str] = []
    for spec in iter_spec_doc_tests(cases_root, file_pattern=case_file_name("*")):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "docs.generate":
            continue
        docs_generate = (((case.get("harness") or {}) if isinstance(case.get("harness"), dict) else {}).get("docs_generate"))
        if isinstance(docs_generate, dict) and str(docs_generate.get("surface_id", "")).strip():
            hits.append(str(docs_generate.get("surface_id", "")).strip())
    if not hits:
        return ["specs/impl/docs_generate/cases:1: missing executable docs.generate surface cases"]
    return []


def _scan_docs_generation_registry_surface_case_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    registry, issues = load_docs_generator_registry(root)
    if registry is None:
        return [x.render() for x in issues]
    expected = {
        str(s.get("surface_id", "")).strip()
        for s in (registry.get("surfaces") or [])
        if isinstance(s, dict) and str(s.get("surface_id", "")).strip()
    }
    seen: set[str] = set()
    cases_root = root / "specs/impl/docs_generate/cases"
    if not cases_root.exists():
        return ["specs/impl/docs_generate/cases:1: missing docs.generate case tree"]
    for spec in iter_spec_doc_tests(cases_root, file_pattern=case_file_name("*")):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "docs.generate":
            continue
        harness_map = case.get("harness")
        if not isinstance(harness_map, dict):
            continue
        docs_generate = harness_map.get("docs_generate")
        if not isinstance(docs_generate, dict):
            continue
        sid = str(docs_generate.get("surface_id", "")).strip()
        if sid:
            seen.add(sid)
    missing = sorted(expected - seen)
    return [f"specs/impl/docs_generate/cases: missing docs.generate case for surface_id {sid}" for sid in missing]


def _scan_docs_template_paths_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    registry, issues = load_docs_generator_registry(root)
    if registry is None:
        return [x.render() for x in issues]
    out: list[str] = []
    for surface in (registry.get("surfaces") or []):
        if not isinstance(surface, dict):
            continue
        sid = str(surface.get("surface_id", "")).strip() or "<unknown>"
        template_path = str(surface.get("template_path", "")).strip()
        if not template_path:
            out.append(f"{DOCS_GENERATOR_REGISTRY_PATH.as_posix()}: surface {sid} missing template_path")
            continue
        p = _join_contract_path(root, template_path)
        if not p.exists():
            out.append(f"{template_path}:1: template path missing for surface {sid}")
    return out


def _scan_docs_template_data_sources_declared(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    registry, issues = load_docs_generator_registry(root)
    if registry is None:
        return [x.render() for x in issues]
    out: list[str] = []
    for surface in (registry.get("surfaces") or []):
        if not isinstance(surface, dict):
            continue
        sid = str(surface.get("surface_id", "")).strip() or "<unknown>"
        data_sources = surface.get("data_sources")
        if not isinstance(data_sources, list) or not data_sources:
            out.append(f"{DOCS_GENERATOR_REGISTRY_PATH.as_posix()}: surface {sid} must declare non-empty data_sources")
            continue
        for idx, src in enumerate(data_sources):
            if not isinstance(src, dict):
                out.append(
                    f"{DOCS_GENERATOR_REGISTRY_PATH.as_posix()}: surface {sid} data_sources[{idx}] must be a mapping"
                )
                continue
            source_type = str(src.get("source_type", "")).strip()
            if source_type in {"json_file", "yaml_file", "generated_artifact"}:
                raw_path = str(src.get("path", "")).strip()
                if not raw_path:
                    out.append(
                        f"{DOCS_GENERATOR_REGISTRY_PATH.as_posix()}: surface {sid} data_sources[{idx}] missing path"
                    )
    return out


def _scan_docs_output_mode_contract_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    registry, issues = load_docs_generator_registry(root)
    if registry is None:
        return [x.render() for x in issues]
    out: list[str] = []
    for surface in (registry.get("surfaces") or []):
        if not isinstance(surface, dict):
            continue
        sid = str(surface.get("surface_id", "")).strip() or "<unknown>"
        output_mode = str(surface.get("output_mode", "")).strip()
        if output_mode not in {"markers", "full_file"}:
            out.append(f"{DOCS_GENERATOR_REGISTRY_PATH.as_posix()}: surface {sid} invalid output_mode {output_mode!r}")
            continue
        if output_mode == "markers" and not str(surface.get("marker_surface_id", "")).strip():
            out.append(f"{DOCS_GENERATOR_REGISTRY_PATH.as_posix()}: surface {sid} requires marker_surface_id")
    return out


def _scan_docs_generate_check_passes(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(
        root,
        "spec_runner.spec_lang_commands",
        ["docs-generate-specs", "--check"],
    )


def _scan_docs_generated_sections_read_only(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    registry, issues = load_docs_generator_registry(root)
    if registry is None:
        return [x.render() for x in issues]
    out: list[str] = []
    surfaces = [x for x in (registry.get("surfaces") or []) if isinstance(x, dict)]
    for surface in surfaces:
        sid = str(surface.get("surface_id", "")).strip() or "<unknown>"
        for raw in surface.get("read_only_sections") or []:
            p = _join_contract_path(root, str(raw))
            rel = p.relative_to(root).as_posix() if p.exists() else str(raw)
            if not p.exists():
                out.append(f"{rel}:1: missing read_only_sections file for {sid}")
                continue
            text = p.read_text(encoding="utf-8")
            try:
                parse_generated_block(text, surface_id=sid)
            except Exception as exc:  # noqa: BLE001
                out.append(f"{rel}:1: invalid generated section markers for {sid} ({exc})")
    return out


def _scan_docs_runner_api_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(root, "spec_runner.generate_runner_api_catalog", ["--check"])


def _scan_docs_harness_type_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(root, "spec_runner.generate_harness_type_catalog", ["--check"])


def _scan_docs_spec_lang_builtin_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(root, "spec_runner.generate_spec_lang_builtin_catalog", ["--check"])


def _scan_docs_policy_rule_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(root, "spec_runner.generate_policy_rule_catalog", ["--check"])


def _scan_docs_traceability_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(root, "spec_runner.generate_traceability_catalog", ["--check"])


def _scan_docs_governance_check_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(root, "spec_runner.generate_governance_check_catalog", ["--check"])


def _scan_docs_metrics_field_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(root, "spec_runner.generate_metrics_field_catalog", ["--check"])


def _scan_docs_spec_schema_field_catalog_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    return _run_python_module_check(root, "spec_runner.generate_spec_schema_field_catalog", ["--check"])


def _read_json_artifact(root: Path, rel: str) -> tuple[dict[str, Any] | None, list[str]]:
    path = _join_contract_path(root, rel)
    if not path.exists():
        return None, [f"{rel}:1: missing generated artifact"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, [f"{rel}:1: invalid json ({exc})"]
    if not isinstance(payload, dict):
        return None, [f"{rel}:1: expected top-level mapping"]
    return payload, []


def _scan_docs_stdlib_symbol_docs_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    payload, errs = _read_json_artifact(root, ".artifacts/spec-lang-builtin-catalog.json")
    if errs:
        return errs
    if payload is None:
        return [".artifacts/spec-lang-builtin-catalog.json:1: missing generated artifact payload"]
    violations: list[str] = []
    for row in payload.get("builtins") or []:
        if not isinstance(row, dict):
            continue
        sym = str(row.get("symbol", "<unknown>"))
        if not str(row.get("summary", "")).strip():
            violations.append(f"{sym}: missing summary")
        params = row.get("params")
        if not isinstance(params, list):
            violations.append(f"{sym}: missing params")
        elif row.get("arity") != 0 and not params:
            violations.append(f"{sym}: missing params")
        if not isinstance(row.get("returns"), dict) or not str((row.get("returns") or {}).get("description", "")).strip():
            violations.append(f"{sym}: missing returns")
        if not isinstance(row.get("errors"), list) or not row.get("errors"):
            violations.append(f"{sym}: missing errors")
        if not isinstance(row.get("examples"), list) or not row.get("examples"):
            violations.append(f"{sym}: missing examples")
    return violations


def _scan_docs_stdlib_examples_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    payload, errs = _read_json_artifact(root, ".artifacts/spec-lang-builtin-catalog.json")
    if errs:
        return errs
    if payload is None:
        return [".artifacts/spec-lang-builtin-catalog.json:1: missing generated artifact payload"]
    violations: list[str] = []
    for row in payload.get("builtins") or []:
        if not isinstance(row, dict):
            continue
        sym = str(row.get("symbol", "<unknown>"))
        examples = row.get("examples")
        if not isinstance(examples, list) or not examples:
            violations.append(f"{sym}: missing examples")
            continue
        first = examples[0] if isinstance(examples[0], dict) else {}
        if not str(first.get("expr", "")).strip() or not str(first.get("result", "")).strip():
            violations.append(f"{sym}: first example missing expr/result")
    return violations


def _scan_docs_harness_reference_semantics_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    payload, errs = _read_json_artifact(root, ".artifacts/harness-type-catalog.json")
    if errs:
        return errs
    if payload is None:
        return [".artifacts/harness-type-catalog.json:1: missing generated artifact payload"]
    violations: list[str] = []
    for row in payload.get("type_profiles") or []:
        if not isinstance(row, dict):
            continue
        case_type = str(row.get("case_type", "<unknown>"))
        if not str(row.get("summary", "")).strip():
            violations.append(f"{case_type}: missing summary")
        if not isinstance(row.get("defaults"), list):
            violations.append(f"{case_type}: missing defaults")
        if not isinstance(row.get("failure_modes"), list):
            violations.append(f"{case_type}: missing failure_modes")
        if not isinstance(row.get("examples"), list) or not row.get("examples"):
            violations.append(f"{case_type}: missing examples")
    return violations


def _scan_docs_runner_reference_semantics_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    payload, errs = _read_json_artifact(root, ".artifacts/runner-api-catalog.json")
    if errs:
        return errs
    if payload is None:
        return [".artifacts/runner-api-catalog.json:1: missing generated artifact payload"]
    violations: list[str] = []
    for row in payload.get("commands") or []:
        if not isinstance(row, dict):
            continue
        cmd = str(row.get("command", "<unknown>"))
        if not str(row.get("summary", "")).strip():
            violations.append(f"{cmd}: missing summary")
        if not isinstance(row.get("defaults"), list):
            violations.append(f"{cmd}: missing defaults")
        if not isinstance(row.get("failure_modes"), list):
            violations.append(f"{cmd}: missing failure_modes")
        if not isinstance(row.get("examples"), list) or not row.get("examples"):
            violations.append(f"{cmd}: missing examples")
    return violations


def _scan_docs_reference_namespace_chapters_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    required = [
        "docs/book/93a_std_core.md",
        "docs/book/93b_std_logic.md",
        "docs/book/93c_std_math.md",
        "docs/book/93d_std_string.md",
        "docs/book/93e_std_collection.md",
        "docs/book/93f_std_object.md",
        "docs/book/93g_std_type.md",
        "docs/book/93h_std_set.md",
        "docs/book/93i_std_json_schema_fn_null.md",
    ]
    out: list[str] = []
    for rel in required:
        if not _join_contract_path(root, rel).exists():
            out.append(f"{rel}:1: missing namespace chapter")
    manifest, issues = load_reference_manifest(root, "docs/book/reference_manifest.yaml")
    if issues:
        out.extend(x.render() for x in issues)
        return out
    chapter_paths = [str(x.get("path", "")).strip() for x in (manifest.get("chapters") or []) if isinstance(x, dict)]
    for rel in required:
        prefixed = "/" + rel.lstrip("/")
        if prefixed not in chapter_paths:
            out.append(f"docs/book/reference_manifest.yaml: missing chapter {prefixed}")
    return out


def _scan_docs_docgen_quality_score_threshold(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    checks = [
        ("spec_runner.generate_spec_lang_builtin_catalog", ".artifacts/spec-lang-builtin-catalog.json"),
        ("spec_runner.generate_runner_api_catalog", ".artifacts/runner-api-catalog.json"),
        ("spec_runner.generate_harness_type_catalog", ".artifacts/harness-type-catalog.json"),
    ]
    out: list[str] = []
    py = root / ".venv/bin/python"
    for module_name, rel in checks:
        # Ensure artifacts exist and are fresh even in cleanroom check-only runs.
        try:
            cp = _profiled_subprocess_run(
                [str(py if py.exists() else Path("python3")), "-m", module_name],
                cwd=root,
                phase="governance.docgen_quality",
            )
        except LivenessError as exc:
            out.append(
                f"-m {module_name}: liveness watchdog triggered ({exc.reason_token})"
            )
            continue
        if cp.returncode != 0:
            lines = [x.strip() for x in ((cp.stdout or "") + "\n" + (cp.stderr or "")).splitlines() if x.strip()]
            out.extend(lines or [f"-m {module_name}: generation failed"])
            continue
        payload, errs = _read_json_artifact(root, rel)
        if errs:
            out.extend(errs)
            continue
        quality = payload.get("quality") if isinstance(payload, dict) else None
        score = float((quality or {}).get("score", 0.0))
        if score < _DOCGEN_QUALITY_MIN_SCORE:
            out.append(
                f"{rel}: quality.score {score:.4f} below required {_DOCGEN_QUALITY_MIN_SCORE:.2f}"
            )
    return out


def _scan_docs_required_sections(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("required_sections")
    if not isinstance(cfg, dict) or not cfg:
        return ["docs.required_sections requires non-empty harness.required_sections mapping in governance spec"]

    for rel, tokens in cfg.items():
        if not isinstance(rel, str) or not rel.strip():
            violations.append("harness.required_sections keys must be non-empty file paths")
            continue
        if not isinstance(tokens, list) or not tokens or any(not isinstance(x, str) or not x.strip() for x in tokens):
            violations.append(f"harness.required_sections[{rel!r}] must be a non-empty list of non-empty strings")
            continue
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing required section-checked file")
            continue
        lower = p.read_text(encoding="utf-8").lower()
        missing = [tok for tok in tokens if tok.lower() not in lower]
        if missing:
            violations.append(f"{rel}:1: missing required token(s): {', '.join(missing)}")
    return violations


def _scan_docs_markdown_structured_assertions_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    cases_dir = root / "specs/governance/cases/core"
    if not cases_dir.exists():
        return [f"{cases_dir.relative_to(root)}: missing governance cases directory"]

    markdown_library_path = "/specs/libraries/domain/markdown_core.spec.md"
    violations: list[str] = []

    def _expr_contains_plain_contains(expr: object) -> bool:
        if isinstance(expr, dict):
            for key, value in expr.items():
                op = str(key).strip()
                if op in {"std.string.contains", "contains"}:
                    return True
                if _expr_contains_plain_contains(value):
                    return True
            return False
        if isinstance(expr, list):
            return any(_expr_contains_plain_contains(item) for item in expr)
        return False

    def _expr_uses_markdown_helper(expr: object) -> bool:
        if isinstance(expr, dict):
            for key, value in expr.items():
                op = str(key).strip()
                if op.startswith("domain.markdown.") or op.startswith("md."):
                    return True
                if op == "var":
                    sym = str(value).strip()
                    if sym.startswith("domain.markdown.") or sym.startswith("md."):
                        return True
                if _expr_uses_markdown_helper(value):
                    return True
            return False
        if isinstance(expr, list):
            return any(_expr_uses_markdown_helper(item) for item in expr)
        return False

    for spec in iter_cases(cases_dir):
        case = spec.test if isinstance(spec.test, dict) else {}
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        if str(case.get("type", "")).strip() != "text.file":
            continue
        raw_path = str(case.get("path", "")).strip()
        if not raw_path.endswith(".md"):
            continue
        harness_value = case.get("harness")
        harness_map: dict[str, Any] = harness_value if isinstance(harness_value, dict) else {}
        spec_lang_raw = harness_map.get("spec_lang")
        spec_lang_cfg: dict[str, Any] = spec_lang_raw if isinstance(spec_lang_raw, dict) else {}
        includes_raw = spec_lang_cfg.get("includes")
        includes: list[Any] = includes_raw if isinstance(includes_raw, list) else []
        has_markdown_include = any(
            isinstance(item, str) and item.strip().endswith(markdown_library_path)
            for item in includes
        )

        leaf_rows: list[tuple[str, str, object, bool]] = []

        def _collect_leaf(leaf: dict, *, inherited_target: str | None = None, assert_path: str = "assert") -> None:
            del assert_path
            for row in iter_leaf_assertions(leaf, target_override=inherited_target):
                leaf_rows.append(row)

        assert_tree = case.get("contract", []) or []
        try:
            eval_assert_tree(assert_tree, eval_leaf=_collect_leaf)
        except Exception as exc:  # noqa: BLE001
            violations.append(
                f"{spec.doc_path.relative_to(root)}: case {case_id} has invalid assert tree ({exc})"
            )
            continue

        for target, op, value, _ in leaf_rows:
            if target != "text" or op != "evaluate":
                continue
            has_plain_contains = _expr_contains_plain_contains(value)
            if not has_plain_contains:
                continue
            if _expr_uses_markdown_helper(value):
                continue
            if not has_markdown_include:
                violations.append(
                    f"{spec.doc_path.relative_to(root)}: case {case_id} text evaluate uses plain contains without markdown library include"
                )
            else:
                violations.append(
                    f"{spec.doc_path.relative_to(root)}: case {case_id} text evaluate uses plain contains where markdown helper should be used"
                )
            break
    return violations


def _has_docs_example_opt_out(lines: list[str], start: int, end: int) -> bool:
    lo = max(0, start - 3)
    hi = min(len(lines), end + 4)
    marker = re.compile(r"DOCS-EXAMPLE-OPT-OUT:\s*(.+)")
    for idx in range(lo, hi):
        m = marker.search(lines[idx])
        if m and m.group(1).strip():
            return True
    return False


def _validate_shell_block(block_lines: list[str]) -> str | None:
    pending = ""
    pending_start = 0
    for i, raw in enumerate(block_lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if pending:
            line = f"{pending} {line}"
            pending = ""
        else:
            pending_start = i
        if line.startswith("$"):
            return f"shell line {i}: leading '$' prompt markers are not allowed"
        if line.endswith("\\"):
            pending = line[:-1].rstrip()
            continue
        try:
            parts = shlex.split(line)
        except ValueError as e:
            return f"shell line {i}: {e}"
        if not parts:
            continue
    if pending:
        return f"shell line {pending_start}: trailing line-continuation without command tail"
    return None


def _validate_python_block(block_lines: list[str]) -> str | None:
    src = "\n".join(block_lines)
    try:
        compile(src, "<docs-python-example>", "exec")
    except SyntaxError as e:
        return f"python syntax error: line {e.lineno}: {e.msg}"
    return None


def _scan_docs_examples_prefer_domain_fs_helpers(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("examples_prefer_domain_fs_helpers")
    if not isinstance(cfg, dict):
        return [
            "docs.examples_prefer_domain_fs_helpers requires harness.examples_prefer_domain_fs_helpers mapping in governance spec"
        ]
    raw_files = cfg.get("files")
    if (
        not isinstance(raw_files, list)
        or not raw_files
        or any(not isinstance(x, str) or not x.strip() for x in raw_files)
    ):
        return ["harness.examples_prefer_domain_fs_helpers.files must be a non-empty list of non-empty strings"]

    for rel in raw_files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing docs file for fs helper preference scan")
            continue
        lines = p.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            opening = _is_markdown_fence_opening(lines[i])
            if not opening:
                i += 1
                continue
            ch, min_len, language_raw = opening
            language = str(language_raw).strip().lower()
            block_start = i + 1
            i += 1
            block: list[str] = []
            while i < len(lines) and not _is_closing_fence(lines[i], ch=ch, min_len=min_len):
                block.append(lines[i])
                i += 1
            if language.startswith("yaml"):
                block_text = "\n".join(block)
                symbols = sorted(set(_OPS_FS_SYMBOL_PATTERN.findall(block_text)))
                if symbols:
                    violations.append(
                        f"{rel}:{block_start}: yaml example uses raw ops.fs symbols ({', '.join(symbols)}); "
                        "prefer domain.path.* / domain.fs.* helpers"
                    )
            if i < len(lines):
                i += 1
    return violations


def _scan_docs_examples_runnable(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("docs_examples")
    if not isinstance(cfg, dict):
        return ["docs.examples_runnable requires harness.docs_examples mapping in governance spec"]
    docs = cfg.get("files")
    if not isinstance(docs, list) or not docs or any(not isinstance(x, str) or not x.strip() for x in docs):
        return ["harness.docs_examples.files must be a non-empty list of non-empty strings"]

    for rel in docs:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}: missing docs file for example scan")
            continue
        lines = p.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            opening = _is_markdown_fence_opening(lines[i])
            if not opening:
                i += 1
                continue
            ch, fence_len, info = opening
            start = i
            info_tokens = info.lower().split()
            i += 1
            block_lines: list[str] = []
            while i < len(lines) and not _is_closing_fence(lines[i], ch=ch, min_len=fence_len):
                block_lines.append(lines[i])
                i += 1
            end = i
            err: str | None = None
            if "contract-spec" in info_tokens and ("yaml" in info_tokens or "yml" in info_tokens):
                try:
                    payload = yaml.safe_load("\n".join(block_lines))
                    if payload is None:
                        err = "empty contract-spec block"
                except Exception as e:  # noqa: BLE001
                    err = f"yaml parse error: {e}"
            elif info_tokens and info_tokens[0] in {"sh", "bash", "shell", "zsh"}:
                err = _validate_shell_block(block_lines)
            elif info_tokens and info_tokens[0] == "python":
                err = _validate_python_block(block_lines)
            if err and not _has_docs_example_opt_out(lines, start, end):
                violations.append(f"{rel}:{start + 1}: invalid example block ({err})")
            i += 1
    return violations


def _extract_python_script_flags(path: Path) -> set[str]:
    raw = path.read_text(encoding="utf-8")
    return set(re.findall(r"add_argument\(\s*['\"](--[a-z0-9-]+)['\"]", raw))


def _extract_php_script_flags(path: Path) -> set[str]:
    raw = path.read_text(encoding="utf-8")
    return set(re.findall(r"\$arg\s*===\s*['\"](--[a-z0-9-]+)['\"]", raw))


def _scan_docs_cli_flags_documented(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("cli_docs")
    if not isinstance(cfg, dict):
        return ["docs.cli_flags_documented requires harness.cli_docs mapping in governance spec"]

    python_scripts = cfg.get("python_scripts", [])
    php_scripts = cfg.get("php_scripts", [])
    python_docs = cfg.get("python_docs", [])
    php_docs = cfg.get("php_docs", [])
    for name, value in (
        ("python_scripts", python_scripts),
        ("php_scripts", php_scripts),
        ("python_docs", python_docs),
        ("php_docs", php_docs),
    ):
        if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
            return [f"harness.cli_docs.{name} must be a list of non-empty strings"]

    python_flags: dict[str, set[str]] = {}
    for rel in python_scripts:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing python script for CLI docs scan")
            continue
        python_flags[rel] = _extract_python_script_flags(p)

    php_flags: dict[str, set[str]] = {}
    for rel in php_scripts:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing php script for CLI docs scan")
            continue
        php_flags[rel] = _extract_php_script_flags(p)

    doc_cache: dict[str, str] = {}
    for rel in [*python_docs, *php_docs]:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing documentation file for CLI docs scan")
            continue
        doc_cache[rel] = p.read_text(encoding="utf-8")

    for script_rel, flags in sorted(python_flags.items()):
        for flag in sorted(flags):
            for doc_rel in python_docs:
                text = doc_cache.get(doc_rel)
                if text is None:
                    continue
                if flag not in text:
                    violations.append(
                        f"{doc_rel}:1: missing CLI flag {flag} documented from {script_rel}"
                    )

    for script_rel, flags in sorted(php_flags.items()):
        for flag in sorted(flags):
            for doc_rel in php_docs:
                text = doc_cache.get(doc_rel)
                if text is None:
                    continue
                if flag not in text:
                    violations.append(
                        f"{doc_rel}:1: missing CLI flag {flag} documented from {script_rel}"
                    )
    return violations


def _scan_docs_contract_schema_book_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("doc_sync")
    if not isinstance(cfg, dict):
        return ["docs.contract_schema_book_sync requires harness.doc_sync mapping in governance spec"]
    files = cfg.get("files")
    tokens = cfg.get("tokens")
    if not isinstance(files, list) or len(files) < 2 or any(not isinstance(x, str) or not x.strip() for x in files):
        return ["harness.doc_sync.files must be a list of at least two non-empty strings"]
    if not isinstance(tokens, list) or not tokens or any(not isinstance(x, str) or not x.strip() for x in tokens):
        return ["harness.doc_sync.tokens must be a non-empty list of non-empty strings"]

    loaded: dict[str, str] = {}
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing doc_sync file")
            continue
        loaded[rel] = p.read_text(encoding="utf-8").lower()
    if len(loaded) < 2:
        return violations

    for tok in tokens:
        want = tok.lower()
        for rel, text in loaded.items():
            if want not in text:
                violations.append(f"{rel}:1: missing sync token {tok}")
    return violations


def _scan_docs_make_commands_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("make_commands")
    if not isinstance(cfg, dict):
        return ["docs.make_commands_sync requires harness.make_commands mapping in governance spec"]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.make_commands.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.make_commands.required_tokens must be a non-empty list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.make_commands.forbidden_tokens must be a list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing docs file for make command sync check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required make command token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden make command token present {tok}")
    return violations


def _scan_docs_adoption_profiles_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("adoption_profiles")
    if not isinstance(cfg, dict):
        return ["docs.adoption_profiles_sync requires harness.adoption_profiles mapping in governance spec"]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.adoption_profiles.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.adoption_profiles.required_tokens must be a non-empty list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing docs file for adoption profile sync check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required adoption-profile token {tok}")
    return violations


def _scan_docs_release_contract_automation_policy(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("release_contract")
    if not isinstance(cfg, dict):
        return ["docs.release_contract_automation_policy requires harness.release_contract mapping in governance spec"]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    forbidden_patterns = cfg.get("forbidden_patterns", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.release_contract.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.release_contract.required_tokens must be a non-empty list of non-empty strings"]
    if not isinstance(forbidden_patterns, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_patterns):
        return ["harness.release_contract.forbidden_patterns must be a list of non-empty strings"]

    compiled: list[re.Pattern[str]] = []
    for pat in forbidden_patterns:
        try:
            compiled.append(re.compile(str(pat), re.MULTILINE))
        except re.error as exc:
            return [f"harness.release_contract.forbidden_patterns invalid regex {pat!r}: {exc}"]

    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing release contract doc")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required release-contract token {tok}")
        for pat in compiled:
            if pat.search(text):
                violations.append(
                    f"{rel}:1: forbidden manual-choreography pattern matched /{pat.pattern}/"
                )
    return violations


def _load_docs_layout_profile(root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    p = root / _DOCS_LAYOUT_PROFILE_PATH
    if not p.exists():
        return None, [f"{_DOCS_LAYOUT_PROFILE_PATH}:1: missing docs layout profile"]
    try:
        payload = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [f"{_DOCS_LAYOUT_PROFILE_PATH}:1: invalid yaml ({exc})"]
    if not isinstance(payload, dict):
        return None, [f"{_DOCS_LAYOUT_PROFILE_PATH}:1: profile must be a mapping"]
    return payload, []


def _scan_docs_layout_canonical_trees(root: Path, *, harness: dict | None = None) -> list[str]:
    profile, errs = _load_docs_layout_profile(root)
    if errs:
        return errs
    assert profile is not None
    violations: list[str] = []
    canonical_roots = profile.get("canonical_roots")
    roots = canonical_roots if isinstance(canonical_roots, list) else []
    for raw in roots:
        rel = str(raw).strip()
        if not rel:
            continue
        p = _join_contract_path(root, rel)
        if not p.exists() or not p.is_dir():
            violations.append(f"{rel.lstrip('/')}:1: missing canonical docs root")
    for child in sorted(p for p in root.iterdir() if p.is_dir()):
        name = child.name
        if name in _TOP_LEVEL_DIR_ALLOWLIST:
            continue
        violations.append(
            f"{name}:1: forbidden top-level directory (allowed: {', '.join(sorted(_TOP_LEVEL_DIR_ALLOWLIST))})"
        )
    return violations


def _scan_docs_index_filename_policy(root: Path, *, harness: dict | None = None) -> list[str]:
    profile, errs = _load_docs_layout_profile(root)
    if errs:
        return errs
    assert profile is not None
    violations: list[str] = []
    index_name = str(profile.get("index_filename", "index.md")).strip() or "index.md"
    required_index_dirs = profile.get("required_index_dirs")
    dirs = required_index_dirs if isinstance(required_index_dirs, list) else []
    for raw in dirs:
        rel = str(raw).strip()
        if not rel:
            continue
        d = _join_contract_path(root, rel)
        if not d.exists() or not d.is_dir():
            violations.append(f"{rel.lstrip('/')}:1: missing index directory")
            continue
        idx = d / index_name
        if not idx.exists():
            violations.append(f"{idx.relative_to(root)}: missing required {index_name}")

    docs_root = root / "docs"
    if docs_root.exists():
        for p in sorted(docs_root.rglob("README.md")):
            if p.is_file():
                violations.append(f"{p.relative_to(root)}: forbidden filename README.md under docs/")
    return violations


def _scan_docs_filename_policy(root: Path, *, harness: dict | None = None) -> list[str]:
    docs_root = root / "docs"
    if not docs_root.exists():
        return ["docs:1: missing docs root"]
    violations: list[str] = []
    for p in sorted(x for x in docs_root.rglob("*") if x.is_file()):
        rel = p.relative_to(root).as_posix()
        if any(ch.isupper() for ch in rel):
            violations.append(f"{rel}: uppercase characters are forbidden")
        if " " in rel:
            violations.append(f"{rel}: spaces are forbidden")
        if not re.fullmatch(r"[a-z0-9_./-]+", rel):
            violations.append(f"{rel}: unsupported characters for docs filename policy")
    return violations


def _scan_docs_reviews_namespace_active(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    active_root = root / "docs/reviews"
    history_root = root / "docs/history/reviews"
    if not active_root.exists() or not active_root.is_dir():
        violations.append("docs/reviews: missing canonical active review root")
        return violations
    if not history_root.exists() or not history_root.is_dir():
        violations.append("docs/history/reviews: missing historical review archive root")
    roots_to_scan: list[Path] = [
        root / "docs",
        root / "specs",
        root / "scripts",
        root / "README.md",
    ]
    needle = "docs/history/reviews"
    for base in roots_to_scan:
        if not base.exists():
            continue
        files: list[Path] = []
        if base.is_file():
            files = [base]
        else:
            files = [p for p in base.rglob("*") if p.is_file()]
        for p in sorted(files):
            rel = p.relative_to(root).as_posix()
            if rel.startswith("docs/history/"):
                continue
            if rel.startswith(".artifacts/"):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if needle in text:
                violations.append(
                    f"{rel}:1: active surfaces must not reference historical review namespace `{needle}`"
                )
    return violations


def _scan_docs_reviews_prompt_schema_contract_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for rel in _REVIEW_PROMPT_FILES:
        path = root / rel
        if not path.exists():
            violations.append(f"{rel}:1: missing prompt file")
            continue
        text = path.read_text(encoding="utf-8")
        for token in _REVIEW_SCHEMA_REF_TOKENS:
            if token not in text:
                violations.append(f"{rel}:1: missing required review contract reference {token}")
        for token in _REVIEW_REQUIRED_SECTION_TOKENS:
            if token not in text:
                violations.append(f"{rel}:1: missing required output section token {token}")
    return violations


def _scan_docs_review_snapshot_template_contract_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    rel = "docs/reviews/templates/review_snapshot.md"
    path = root / rel
    if not path.exists():
        return [f"{rel}:1: missing canonical review snapshot template"]
    text = path.read_text(encoding="utf-8")
    return validate_review_snapshot_text(text, source=rel)


def _scan_docs_review_tooling_contract_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    snapshot_script = root / "runners/python/spec_runner/new_review_snapshot.py"
    pending_script = root / "runners/python/spec_runner/review_to_pending.py"

    if not snapshot_script.exists():
        violations.append("runners/python/spec_runner/new_review_snapshot.py:1: missing snapshot scaffold tool")
    else:
        text = snapshot_script.read_text(encoding="utf-8")
        for token in _REVIEW_REQUIRED_SECTION_TOKENS:
            if token not in text:
                violations.append(
                    f"runners/python/spec_runner/new_review_snapshot.py:1: scaffold missing section token {token}"
                )
        if "review_snapshot_schema_v1.yaml" not in text:
            violations.append(
                "runners/python/spec_runner/new_review_snapshot.py:1: scaffold missing schema baseline reference"
            )

    if not pending_script.exists():
        violations.append("runners/python/spec_runner/review_to_pending.py:1: missing pending conversion tool")
    else:
        text = pending_script.read_text(encoding="utf-8")
        if "parse_spec_candidates" not in text or "validate_review_snapshot" not in text:
            violations.append(
                "runners/python/spec_runner/review_to_pending.py:1: parser must use review snapshot validator helpers"
            )
        legacy_tokens = ("'where'", "\"where\"", "'statement'", "\"statement\"", "'rationale'", "\"rationale\"", "'verification'", "\"verification\"")
        for token in legacy_tokens:
            if token in text:
                violations.append(
                    f"runners/python/spec_runner/review_to_pending.py:1: legacy candidate key token forbidden ({token})"
                )
    return violations


def _scan_docs_review_snapshots_schema_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    snapshots_dir = root / "docs/reviews/snapshots"
    if not snapshots_dir.exists() or not snapshots_dir.is_dir():
        return ["docs/reviews/snapshots:1: missing snapshots directory"]

    violations: list[str] = []
    snapshot_files = sorted(p for p in snapshots_dir.glob("*.md") if p.is_file())
    if not snapshot_files:
        violations.append("docs/reviews/snapshots:1: at least one canonical snapshot is required")
        return violations
    for path in snapshot_files:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        violations.extend(validate_review_snapshot_text(text, source=rel))
    return violations


def _scan_docs_reviews_discovery_prompt_present(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    path = root / _REVIEW_DISCOVERY_PROMPT
    if not path.exists() or not path.is_file():
        return [f"{_REVIEW_DISCOVERY_PROMPT}:1: missing discovery prompt"]
    return []


def _scan_docs_reviews_discovery_prompt_contract_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    path = root / _REVIEW_DISCOVERY_PROMPT
    if not path.exists() or not path.is_file():
        return [f"{_REVIEW_DISCOVERY_PROMPT}:1: missing discovery prompt"]
    text = path.read_text(encoding="utf-8")
    violations: list[str] = []
    for token in _REVIEW_SCHEMA_REF_TOKENS:
        if token not in text:
            violations.append(f"{_REVIEW_DISCOVERY_PROMPT}:1: missing required review contract reference {token}")
    for token in _REVIEW_REQUIRED_SECTION_TOKENS:
        if token not in text:
            violations.append(f"{_REVIEW_DISCOVERY_PROMPT}:1: missing required output section token {token}")
    for token in _REVIEW_DISCOVERY_ENTRYPOINT_TOKENS:
        if token not in text:
            violations.append(f"{_REVIEW_DISCOVERY_PROMPT}:1: missing discovery entrypoint token {token}")
    for token in _REVIEW_DISCOVERY_SELF_HEAL_ALLOWED_TOKENS:
        if token not in text:
            violations.append(f"{_REVIEW_DISCOVERY_PROMPT}:1: missing allowed self-heal policy token {token}")
    for token in _REVIEW_DISCOVERY_SELF_HEAL_FORBIDDEN_TOKENS:
        if token not in text:
            violations.append(f"{_REVIEW_DISCOVERY_PROMPT}:1: missing forbidden self-heal policy token {token}")
    if "Start at:" not in text:
        violations.append(f"{_REVIEW_DISCOVERY_PROMPT}:1: missing explicit discovery start directive")
    if "If missing or insufficient, continue in this exact fallback order:" not in text:
        violations.append(f"{_REVIEW_DISCOVERY_PROMPT}:1: missing fallback order directive")
    return violations


def _scan_docs_reviews_discovery_workflow_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    rel = "docs/reviews/README.md"
    path = root / rel
    if not path.exists() or not path.is_file():
        return [f"{rel}:1: missing docs/reviews README"]
    text = path.read_text(encoding="utf-8")
    violations: list[str] = []
    required_tokens = (
        "docs/reviews/prompts/discovery_fit_self_heal.md",
        "python -m spec_runner.new_review_snapshot --prompt docs/reviews/prompts/discovery_fit_self_heal.md",
        "python -m spec_runner.spec_lang_commands review-validate --snapshot",
        "python -m spec_runner.review_to_pending",
        "specs/governance/pending/<snapshot>-pending.md",
    )
    for token in required_tokens:
        if token not in text:
            violations.append(f"{rel}:1: missing discovery workflow token {token}")
    return violations


def _scan_docs_no_os_artifact_files(root: Path, *, harness: dict | None = None) -> list[str]:
    docs_root = root / "docs"
    if not docs_root.exists():
        return []
    violations: list[str] = []
    for p in sorted(docs_root.rglob(".DS_Store")):
        if p.is_file():
            violations.append(f"{p.relative_to(root)}: OS artifact files are forbidden")
    return violations


def _scan_runtime_scope_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("runtime_scope")
    if not isinstance(cfg, dict):
        return ["runtime.scope_sync requires harness.runtime_scope mapping in governance spec"]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.runtime_scope.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.runtime_scope.required_tokens must be a non-empty list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.runtime_scope.forbidden_tokens must be a list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing runtime-scope doc")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required runtime-scope token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden runtime-scope token present {tok}")
    return violations


def _scan_runtime_profiling_contract_artifacts(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    required = [
        "specs/schema/run_trace_v1.yaml",
        "specs/contract/24_runtime_profiling_contract.md",
    ]
    violations: list[str] = []
    for rel in required:
        p = root / rel
        if not p.exists():
            violations.append(f"{rel}:1: missing profiling contract artifact")
    current = root / "specs/current.md"
    if current.exists():
        text = current.read_text(encoding="utf-8")
        if "run_trace_v1" not in text:
            violations.append("specs/current.md:1: missing run_trace_v1 snapshot note")
    return violations


def _scan_runtime_profiling_redaction_policy(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("profiling_redaction")
    if not isinstance(cfg, dict):
        return ["runtime.profiling_redaction_policy requires harness.profiling_redaction mapping in governance spec"]
    trace_rel = str(cfg.get("trace_path", ".artifacts/run-trace.json")).strip()
    trace_path = _join_contract_path(root, trace_rel)
    if not trace_path.exists():
        return [f"{trace_rel}:1: profiling trace file missing for redaction policy check"]
    try:
        payload = json.loads(trace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{trace_rel}:1: invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}"]
    violations: list[str] = []
    env_profile = payload.get("env_profile")
    if not isinstance(env_profile, dict):
        violations.append(f"{trace_rel}:1: env_profile must be a mapping")
    else:
        for key, meta in env_profile.items():
            if not isinstance(meta, dict):
                violations.append(f"{trace_rel}:1: env_profile[{key!r}] must be a mapping")
                continue
            if "value" in meta:
                violations.append(f"{trace_rel}:1: env_profile[{key!r}] must not include raw value")
    text = trace_path.read_text(encoding="utf-8")
    for token in ("Bearer ", "sk-", "Authorization:"):
        if token in text:
            violations.append(f"{trace_rel}:1: forbidden secret-like token present in trace artifact: {token!r}")
    return violations


def _scan_runtime_profiling_span_taxonomy(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("profiling_span_taxonomy")
    if not isinstance(cfg, dict):
        return ["runtime.profiling_span_taxonomy requires harness.profiling_span_taxonomy mapping in governance spec"]
    trace_rel = str(cfg.get("trace_path", ".artifacts/run-trace.json")).strip()
    trace_path = _join_contract_path(root, trace_rel)
    if not trace_path.exists():
        return [f"{trace_rel}:1: profiling trace file missing for span taxonomy check"]
    try:
        payload = json.loads(trace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{trace_rel}:1: invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}"]
    required_spans = cfg.get(
        "required_spans",
        [
            "run.total",
            "runner.dispatch",
            "case.run",
            "case.chain",
            "case.harness",
            "check.execute",
            "subprocess.exec",
            "subprocess.wait",
        ],
    )
    if not isinstance(required_spans, list) or any(not isinstance(x, str) or not x.strip() for x in required_spans):
        return ["harness.profiling_span_taxonomy.required_spans must be a non-empty list of strings"]
    spans = payload.get("spans")
    if not isinstance(spans, list):
        return [f"{trace_rel}:1: spans must be a list"]
    names = {str(x.get("name", "")).strip() for x in spans if isinstance(x, dict)}
    missing = [x for x in required_spans if str(x).strip() not in names]
    violations: list[str] = []
    if missing:
        violations.append(f"{trace_rel}:1: missing required span names: {', '.join(missing)}")
    return violations


def _scan_runtime_liveness_watchdog_contract_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    required_docs = (
        (
            "specs/contract/24_runtime_profiling_contract.md",
            (
                "SPEC_RUNNER_LIVENESS_LEVEL",
                "SPEC_RUNNER_LIVENESS_STALL_MS",
                "SPEC_RUNNER_LIVENESS_MIN_EVENTS",
                "SPEC_RUNNER_LIVENESS_HARD_CAP_MS",
                "SPEC_RUNNER_LIVENESS_KILL_GRACE_MS",
            ),
        ),
        (
            "specs/schema/run_trace_v1.yaml",
            (
                "stall.runner.no_progress",
                "stall.subprocess.no_output_no_event",
                "timeout.hard_cap.emergency",
                "watchdog.kill.term",
                "watchdog.kill.killed",
            ),
        ),
    )
    for rel, tokens in required_docs:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing liveness contract artifact")
            continue
        text = p.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                violations.append(f"{rel}:1: missing liveness token {token}")
    return violations


def _scan_runtime_liveness_stall_token_emitted(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("liveness_trace_tokens")
    if not isinstance(cfg, dict):
        return ["runtime.liveness_stall_token_emitted requires harness.liveness_trace_tokens mapping in governance spec"]
    trace_rel = str(cfg.get("trace_path", ".artifacts/run-trace.json")).strip()
    trace_path = _join_contract_path(root, trace_rel)
    if not trace_path.exists():
        return [f"{trace_rel}:1: missing run trace for liveness token check"]
    try:
        payload = json.loads(trace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{trace_rel}:1: invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}"]
    required = cfg.get("required_tokens", ["stall.runner.no_progress", "stall.subprocess.no_output_no_event"])
    if not isinstance(required, list) or any(not isinstance(x, str) or not x.strip() for x in required):
        return ["harness.liveness_trace_tokens.required_tokens must be a non-empty list of strings"]
    events = payload.get("events")
    if not isinstance(events, list):
        return [f"{trace_rel}:1: events must be a list"]
    seen: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            continue
        attrs = event.get("attrs")
        if isinstance(attrs, dict):
            tok = str(attrs.get("reason_token", "")).strip()
            if tok:
                seen.add(tok)
    missing = [tok for tok in required if tok not in seen]
    return [f"{trace_rel}:1: missing required liveness reason tokens: {', '.join(missing)}"] if missing else []


def _scan_runtime_liveness_hard_cap_token_emitted(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("liveness_trace_tokens")
    if not isinstance(cfg, dict):
        return ["runtime.liveness_hard_cap_token_emitted requires harness.liveness_trace_tokens mapping in governance spec"]
    trace_rel = str(cfg.get("trace_path", ".artifacts/run-trace.json")).strip()
    trace_path = _join_contract_path(root, trace_rel)
    if not trace_path.exists():
        return [f"{trace_rel}:1: missing run trace for liveness hard-cap token check"]
    try:
        payload = json.loads(trace_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{trace_rel}:1: invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}"]
    events = payload.get("events")
    if not isinstance(events, list):
        return [f"{trace_rel}:1: events must be a list"]
    tokens = {
        str((event.get("attrs") or {}).get("reason_token", "")).strip()
        for event in events
        if isinstance(event, dict) and isinstance(event.get("attrs"), dict)
    }
    required_any = {"timeout.hard_cap.emergency", "watchdog.kill.term", "watchdog.kill.killed"}
    if not (tokens & required_any):
        return [f"{trace_rel}:1: expected at least one hard-cap/kill liveness token ({', '.join(sorted(required_any))})"]
    return []


def _scan_runtime_gate_fail_fast_behavior_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("gate_fail_fast")
    if not isinstance(cfg, dict):
        return ["runtime.gate_fail_fast_behavior_required requires harness.gate_fail_fast mapping in governance spec"]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.gate_fail_fast.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.gate_fail_fast.required_tokens must be a non-empty list of non-empty strings"]
    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing gate fail-fast file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing fail-fast token {tok}")
    return violations


def _scan_runtime_gate_skipped_steps_contract_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("gate_skipped_contract")
    if not isinstance(cfg, dict):
        return [
            "runtime.gate_skipped_steps_contract_required requires harness.gate_skipped_contract mapping in governance spec"
        ]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.gate_skipped_contract.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.gate_skipped_contract.required_tokens must be a non-empty list of non-empty strings"]
    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing skipped-steps contract file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing skipped-steps token {tok}")
    return violations


def _scan_runtime_profile_artifacts_on_fail_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("profile_on_fail")
    if not isinstance(cfg, dict):
        return ["runtime.profile_artifacts_on_fail_required requires harness.profile_on_fail mapping in governance spec"]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.profile_on_fail.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.profile_on_fail.required_tokens must be a non-empty list of non-empty strings"]
    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing profile-on-fail file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing profile-on-fail token {tok}")
    return violations


def _scan_runtime_gate_evaluates_with_skipped_rows(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("gate_policy_skipped_rows")
    if not isinstance(cfg, dict):
        return [
            "runtime.gate_evaluates_with_skipped_rows requires harness.gate_policy_skipped_rows mapping in governance spec"
        ]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.gate_policy_skipped_rows.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.gate_policy_skipped_rows.required_tokens must be a non-empty list of non-empty strings"]
    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing gate policy file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing skipped-rows policy token {tok}")
    return violations


def _scan_runtime_evaluate_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("policy_forbidden")
    if not isinstance(cfg, dict):
        return ["runtime.evaluate_forbidden requires harness.policy_forbidden mapping in governance spec"]
    cases_rel = str(cfg.get("cases_path", "specs/governance/cases")).strip() or "specs/governance/cases"
    case_pattern = str(cfg.get("case_file_pattern", SETTINGS.case.default_file_pattern)).strip() or SETTINGS.case.default_file_pattern
    cases_dir = _join_contract_path(root, cases_rel)
    if not cases_dir.exists():
        return [f"{cases_rel}:1: governance cases path does not exist"]
    violations: list[str] = []
    for spec in iter_cases(cases_dir, file_pattern=case_pattern):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "governance.check":
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        check_id = str(case.get("check", "")).strip() or "<unknown>"
        harness_map = case.get("harness")
        if not isinstance(harness_map, dict):
            continue
        if "evaluate" in harness_map:
            violations.append(
                f"{spec.doc_path.relative_to(root)}: case {case_id} check {check_id} uses forbidden harness.evaluate"
            )
        orchestration = harness_map.get("orchestration_policy")
        if isinstance(orchestration, dict) and "evaluate" in orchestration:
            violations.append(
                f"{spec.doc_path.relative_to(root)}: case {case_id} check {check_id} uses forbidden harness.orchestration_policy.evaluate"
            )
    return violations


def _scan_runtime_assert_block_decision_authority_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("assert_decision_authority")
    if not isinstance(cfg, dict):
        return [
            "runtime.assert_block_decision_authority_required requires harness.assert_decision_authority mapping in governance spec"
        ]
    rel = str(cfg.get("path", "runners/python/spec_runner/governance_runtime.py")).strip() or "runners/python/spec_runner/governance_runtime.py"
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.assert_decision_authority.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.assert_decision_authority.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing runtime module for assert decision authority check"]
    raw = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in raw:
            violations.append(f"{rel}:1: missing required assert decision token: {tok}")
    for tok in forbidden_tokens:
        if tok in raw:
            violations.append(f"{rel}:1: forbidden policy decision token present: {tok}")
    return violations


def _scan_runtime_meta_json_target_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("meta_json_targets")
    if not isinstance(cfg, dict):
        return ["runtime.meta_json_target_required requires harness.meta_json_targets mapping in governance spec"]
    files = cfg.get("files")
    if not isinstance(files, list) or not files or any(not isinstance(x, str) or not x.strip() for x in files):
        return ["harness.meta_json_targets.files must be a non-empty list of non-empty strings"]
    required_tokens = cfg.get("required_tokens", ["meta_json"])
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.meta_json_targets.required_tokens must be a list of non-empty strings"]
    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing file for meta_json target check")
            continue
        raw = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in raw:
                violations.append(f"{rel}:1: missing required meta_json token: {tok}")
    return violations


def _scan_schema_contract_target_on_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    for doc_path, case in _iter_all_spec_cases(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        contract = case.get("contract")
        if not isinstance(contract, dict):
            continue
        defaults = contract.get("defaults")
        if isinstance(defaults, dict):
            if "target" in defaults:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} contract.defaults.target is forbidden; use contract.imports"
                )
            if "on" in defaults:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} contract.defaults.on is forbidden; use contract.imports"
                )
        steps = contract.get("steps")
        if not isinstance(steps, list):
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            if "target" in step:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} contract.steps[{idx}].target is forbidden; use imports"
                )
            if "on" in step:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} contract.steps[{idx}].on is forbidden; use imports"
                )
    return violations


def _scan_schema_contract_imports_explicit_required(root: Path, *, harness: dict | None = None) -> list[str]:
    def _collect_imported_locals(raw_imports: object, *, where: str, violations: list[str]) -> set[str]:
        locals_out: set[str] = set()
        if raw_imports is None:
            return locals_out
        if isinstance(raw_imports, dict):
            violations.append(f"{where} imports must use list form with from/names/as")
            return locals_out
        if not isinstance(raw_imports, list):
            violations.append(f"{where} imports must be a list when provided")
            return locals_out
        for idx, raw_item in enumerate(raw_imports):
            if not isinstance(raw_item, dict):
                violations.append(f"{where}.imports[{idx}] must be mapping")
                continue
            src = str(raw_item.get("from", "")).strip()
            if src != "artifact":
                violations.append(f"{where}.imports[{idx}].from must be artifact")
                continue
            raw_names = raw_item.get("names")
            if not isinstance(raw_names, list) or not raw_names:
                violations.append(f"{where}.imports[{idx}].names must be non-empty list")
                continue
            raw_as = raw_item.get("as")
            alias_map: dict[str, str] = {}
            if raw_as is not None:
                if not isinstance(raw_as, dict):
                    violations.append(f"{where}.imports[{idx}].as must be mapping when provided")
                    continue
                for raw_key, raw_val in raw_as.items():
                    source_name = str(raw_key).strip()
                    local_name = str(raw_val).strip()
                    if not source_name or not local_name:
                        violations.append(
                            f"{where}.imports[{idx}].as keys and values must be non-empty strings"
                        )
                        continue
                    alias_map[source_name] = local_name
            source_set: set[str] = set()
            for name_idx, raw_name in enumerate(raw_names):
                source_name = str(raw_name).strip()
                if not source_name:
                    violations.append(
                        f"{where}.imports[{idx}].names[{name_idx}] must be non-empty string"
                    )
                    continue
                source_set.add(source_name)
                locals_out.add(alias_map.get(source_name, source_name))
            for alias_key in sorted(alias_map.keys()):
                if alias_key not in source_set:
                    violations.append(
                        f"{where}.imports[{idx}].as key {alias_key!r} is not present in names"
                    )
        return locals_out

    def _contains_var_subject(node: object) -> bool:
        if isinstance(node, dict):
            if set(node.keys()) == {"var"} and str(node.get("var", "")).strip() == "subject":
                return True
            return any(_contains_var_subject(v) for v in node.values())
        if isinstance(node, list):
            return any(_contains_var_subject(v) for v in node)
        return False

    violations: list[str] = []
    for doc_path, case in _iter_all_spec_cases(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        contract = case.get("contract")
        if not isinstance(contract, dict):
            continue
        defaults = contract.get("defaults")
        if isinstance(defaults, dict) and "imports" in defaults:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} contract.defaults.imports is forbidden; use contract.imports"
            )
        contract_imports_raw = contract.get("imports")
        if isinstance(contract_imports_raw, dict):
            if "defaults" in contract_imports_raw:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} contract.imports.defaults is forbidden; use contract.imports directly"
                )
            if "steps" in contract_imports_raw:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} contract.imports.steps is forbidden; use contract.steps[].imports"
                )
        contract_where = f"{doc_path.relative_to(root)}: case {case_id} contract"
        default_imports = _collect_imported_locals(contract_imports_raw, where=contract_where, violations=violations)
        steps = contract.get("steps")
        if not isinstance(steps, list):
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            raw_assert = step.get("assert")
            if raw_assert is None or not _contains_var_subject(raw_assert):
                continue
            merged_names: set[str] = set(default_imports)
            step_where = f"{doc_path.relative_to(root)}: case {case_id} contract.steps[{idx}]"
            merged_names.update(
                _collect_imported_locals(step.get("imports"), where=step_where, violations=violations)
            )
            if "subject" not in merged_names:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} contract.steps[{idx}] uses var subject without imports.subject"
                )
    return violations


def _scan_runtime_implicit_subject_binding_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    rel = "runners/python/spec_runner/spec_lang.py"
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing spec_lang evaluator file"]
    text = p.read_text(encoding="utf-8")
    if 'root_symbols["subject"]' in text:
        return [f"{rel}:1: implicit subject injection is forbidden; use explicit imports"]
    return []


def _scan_runtime_ops_os_capability_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("ops_os_capability")
    if not isinstance(cfg, dict):
        return ["runtime.ops_os_capability_required requires harness.ops_os_capability mapping in governance spec"]
    rel = str(cfg.get("path", "runners/python/spec_runner/spec_lang.py")).strip() or "runners/python/spec_runner/spec_lang.py"
    required_tokens = cfg.get("required_tokens", [])
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.ops_os_capability.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing spec_lang implementation file"]
    raw = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in raw:
            violations.append(f"{rel}:1: missing required ops.os capability token: {tok}")
    return violations


def _scan_runtime_ops_os_stdlib_surface_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("ops_os_stdlib_surface")
    if not isinstance(cfg, dict):
        return ["runtime.ops_os_stdlib_surface_sync requires harness.ops_os_stdlib_surface mapping in governance spec"]
    files = cfg.get("files")
    symbols = cfg.get("required_symbols")
    if not isinstance(files, list) or not files or any(not isinstance(x, str) or not x.strip() for x in files):
        return ["harness.ops_os_stdlib_surface.files must be a non-empty list of non-empty strings"]
    if not isinstance(symbols, list) or not symbols or any(not isinstance(x, str) or not x.strip() for x in symbols):
        return ["harness.ops_os_stdlib_surface.required_symbols must be a non-empty list of non-empty strings"]
    violations: list[str] = []
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing stdlib surface file")
            continue
        raw = p.read_text(encoding="utf-8")
        for symbol in symbols:
            if symbol not in raw:
                violations.append(f"{rel}:1: missing required ops.os symbol token: {symbol}")
    return violations


def _iter_docs_spec_cases(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    out: list[tuple[Path, dict[str, Any]]] = []
    cases_root = _join_contract_path(root, "specs")
    if not cases_root.exists():
        return out
    for spec in iter_cases(cases_root, file_pattern="**/*.spec.md"):
        if isinstance(spec.test, dict):
            out.append((spec.doc_path, spec.test))
    return out


def _scan_runtime_contract_spec_fence_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    cases_root = _join_contract_path(root, "specs")
    if not cases_root.exists():
        return ["specs:1: missing specs tree"]
    for p in sorted(cases_root.rglob(SETTINGS.case.default_file_pattern)):
        if not p.is_file():
            continue
        raw = p.read_text(encoding="utf-8")
        if "```yaml contract-spec" not in raw:
            violations.append(f"{p.relative_to(root)}:1: missing required executable fence token ```yaml contract-spec")
    return violations


def _scan_runtime_legacy_spec_test_fence_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    cases_root = _join_contract_path(root, "specs")
    if not cases_root.exists():
        return ["specs:1: missing specs tree"]
    for p in sorted(cases_root.rglob(SETTINGS.case.default_file_pattern)):
        if not p.is_file():
            continue
        raw = p.read_text(encoding="utf-8")
        if "spec-test" in raw:
            violations.append(f"{p.relative_to(root)}:1: legacy spec-test token is forbidden")
    return violations


def _scan_runtime_case_contract_block_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_docs_spec_cases(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        if "contract" not in case:
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} missing required contract block")
    return violations


def _scan_runtime_legacy_assert_block_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_docs_spec_cases(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        if "assert" in case:
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} legacy assert block is forbidden")
    return violations


def _scan_runtime_contract_step_asserts_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []

    def _walk(node: Any, *, rel: str, case_id: str, path: str) -> None:
        if isinstance(node, list):
            for i, child in enumerate(node):
                _walk(child, rel=rel, case_id=case_id, path=f"{path}[{i}]")
            return
        if not isinstance(node, dict):
            return
        step_class = str(node.get("class", "")).strip() if "class" in node else ""
        if step_class in {"MUST", "MAY", "MUST_NOT"}:
            if "asserts" not in node:
                violations.append(f"{rel}: case {case_id} {path} step requires asserts list")
            raw_asserts = node.get("asserts")
            if not isinstance(raw_asserts, list) or not raw_asserts:
                violations.append(f"{rel}: case {case_id} {path}.asserts must be non-empty list")
            else:
                for i, child in enumerate(raw_asserts):
                    _walk(child, rel=rel, case_id=case_id, path=f"{path}.asserts[{i}]")
            return
        for key in ("MUST", "MAY", "MUST_NOT"):
            raw_children = node.get(key)
            if isinstance(raw_children, list):
                for i, child in enumerate(raw_children):
                    _walk(child, rel=rel, case_id=case_id, path=f"{path}.{key}[{i}]")

    for doc_path, case in _iter_docs_spec_cases(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        _walk(case.get("contract"), rel=doc_path.relative_to(root).as_posix(), case_id=case_id, path="contract")
    return violations


def _scan_runtime_legacy_checks_key_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []

    def _walk(node: Any, *, rel: str, case_id: str, path: str) -> None:
        if isinstance(node, list):
            for i, child in enumerate(node):
                _walk(child, rel=rel, case_id=case_id, path=f"{path}[{i}]")
            return
        if not isinstance(node, dict):
            return
        if "checks" in node:
            violations.append(f"{rel}: case {case_id} {path} uses forbidden legacy key checks")
        for key, value in node.items():
            _walk(value, rel=rel, case_id=case_id, path=f"{path}.{key}")

    for doc_path, case in _iter_docs_spec_cases(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        _walk(case.get("contract"), rel=doc_path.relative_to(root).as_posix(), case_id=case_id, path="contract")
    return violations


def _scan_runtime_contract_job_dispatch_in_contract_required(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_docs_spec_cases(root):
        if str(case.get("type", "")).strip() != "contract.job":
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        raw = yaml.safe_dump(case.get("contract"), sort_keys=False)
        if "ops.job.dispatch" not in raw:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} contract.job must dispatch via contract ops.job.dispatch"
            )
    return violations


def _scan_runtime_harness_jobs_metadata_map_required(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_docs_spec_cases(root):
        if str(case.get("type", "")).strip() != "contract.job":
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        harness_map = case.get("harness")
        if not isinstance(harness_map, dict):
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} harness must be mapping")
            continue
        jobs = harness_map.get("jobs")
        if not isinstance(jobs, dict) or not jobs:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} harness.jobs must be non-empty mapping"
            )
            continue
        for name, entry in jobs.items():
            if not isinstance(entry, dict):
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} harness.jobs.{name} must be mapping"
                )
                continue
            helper = str(entry.get("helper", "")).strip()
            if not helper:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} harness.jobs.{name}.helper is required"
                )
    return violations


def _scan_runtime_harness_job_legacy_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_docs_spec_cases(root):
        if str(case.get("type", "")).strip() != "contract.job":
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        harness_map = case.get("harness")
        if isinstance(harness_map, dict) and "job" in harness_map:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} legacy harness.job is forbidden"
            )
        jobs = harness_map.get("jobs") if isinstance(harness_map, dict) else None
        if isinstance(jobs, dict):
            for name, entry in jobs.items():
                if isinstance(entry, dict) and "ref" in entry:
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} harness.jobs.{name}.ref is forbidden"
                    )
    return violations


def _scan_runtime_ops_job_capability_required(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for doc_path, case in _iter_docs_spec_cases(root):
        contract = case.get("contract")
        raw = yaml.safe_dump(contract, sort_keys=False)
        if "ops.job.dispatch" not in raw:
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        harness_map = case.get("harness")
        spec_lang = harness_map.get("spec_lang") if isinstance(harness_map, dict) else None
        caps = spec_lang.get("capabilities") if isinstance(spec_lang, dict) else None
        if not isinstance(caps, list) or "ops.job" not in caps:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} ops.job.dispatch requires harness.spec_lang.capabilities to include ops.job"
            )
    return violations


def _scan_runtime_ops_job_nested_dispatch_forbidden(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    h = harness or {}
    cfg = h.get("ops_job_nested_dispatch")
    if not isinstance(cfg, dict):
        return ["runtime.ops_job_nested_dispatch_forbidden requires harness.ops_job_nested_dispatch mapping in governance spec"]
    rel = str(cfg.get("path", "runners/rust/spec_runner_cli/src/spec_lang.rs")).strip()
    required_tokens = cfg.get("required_tokens", ["runtime.dispatch.nested_forbidden"])
    if not rel:
        return ["harness.ops_job_nested_dispatch.path must be non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.ops_job_nested_dispatch.required_tokens must be list of non-empty strings"]
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing file for ops.job nested dispatch check"]
    raw = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in raw:
            violations.append(f"{rel}:1: missing required nested-dispatch token: {tok}")
    return violations


def _scan_runtime_when_hooks_schema_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    allowed = {"must", "may", "must_not", "fail", "complete"}
    for doc_path, case in _iter_docs_spec_cases(root):
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        harness_map = case.get("harness")
        if harness_map is None:
            continue
        if not isinstance(harness_map, dict):
            continue
        if "on" in harness_map:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} harness.on is forbidden; use when"
            )
        if "when" in harness_map:
            violations.append(
                f"{doc_path.relative_to(root)}: case {case_id} harness.when is forbidden; use when"
            )
        hooks = case.get("when")
        if hooks is None:
            continue
        if not isinstance(hooks, dict):
            violations.append(f"{doc_path.relative_to(root)}: case {case_id} when must be mapping")
            continue
        for key, exprs in hooks.items():
            key_name = str(key).strip()
            if key_name not in allowed:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} when contains unknown key {key_name}"
                )
                continue
            if not isinstance(exprs, list) or not exprs:
                violations.append(
                    f"{doc_path.relative_to(root)}: case {case_id} when.{key_name} must be non-empty list"
                )
                continue
            for idx, expr in enumerate(exprs):
                if not isinstance(expr, dict):
                    violations.append(
                        f"{doc_path.relative_to(root)}: case {case_id} when.{key_name}[{idx}] must be mapping expression"
                    )
    return violations


def _scan_runtime_when_ordering_contract_required(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    h = harness or {}
    cfg = h.get("when_ordering")
    if not isinstance(cfg, dict):
        return ["runtime.when_ordering_contract_required requires harness.when_ordering mapping in governance spec"]
    rel = str(cfg.get("path", "runners/python/spec_runner/components/assertion_engine.py")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not rel:
        return ["harness.when_ordering.path must be non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.when_ordering.required_tokens must be list of non-empty strings"]
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing file for when ordering check"]
    raw = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in raw:
            violations.append(f"{rel}:1: missing required when ordering token: {tok}")
    return violations


def _scan_runtime_when_fail_hook_required_behavior(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    h = harness or {}
    cfg = h.get("when_fail")
    if not isinstance(cfg, dict):
        return ["runtime.when_fail_hook_required_behavior requires harness.when_fail mapping in governance spec"]
    rel = str(cfg.get("path", "runners/python/spec_runner/components/assertion_engine.py")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not rel:
        return ["harness.when_fail.path must be non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.when_fail.required_tokens must be list of non-empty strings"]
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing file for when fail hook check"]
    raw = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in raw:
            violations.append(f"{rel}:1: missing required when fail token: {tok}")
    return violations


def _scan_runtime_when_complete_hook_required_behavior(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    h = harness or {}
    cfg = h.get("when_complete")
    if not isinstance(cfg, dict):
        return ["runtime.when_complete_hook_required_behavior requires harness.when_complete mapping in governance spec"]
    rel = str(cfg.get("path", "runners/python/spec_runner/components/assertion_engine.py")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not rel:
        return ["harness.when_complete.path must be non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.when_complete.required_tokens must be list of non-empty strings"]
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing file for when complete hook check"]
    raw = p.read_text(encoding="utf-8")
    violations: list[str] = []
    for tok in required_tokens:
        if tok not in raw:
            violations.append(f"{rel}:1: missing required when complete token: {tok}")
    return violations


def _scan_runtime_contract_job_hooks_refactor_applied(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    target_files = (
        "specs/impl/rust/jobs/script_jobs.spec.md",
        "specs/impl/rust/jobs/report_jobs.spec.md",
    )
    target_set = {p.as_posix() for p in (_join_contract_path(root, rel) for rel in target_files)}
    violations: list[str] = []
    for doc_path, case in _iter_docs_spec_cases(root):
        if doc_path.as_posix() not in target_set:
            continue
        if str(case.get("type", "")).strip() != "contract.job":
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        rel = doc_path.relative_to(root).as_posix()

        harness_map = case.get("harness")
        if not isinstance(harness_map, dict):
            violations.append(f"{rel}: case {case_id} harness must be mapping")
            continue
        jobs = harness_map.get("jobs")
        if not isinstance(jobs, dict):
            violations.append(f"{rel}: case {case_id} harness.jobs must be mapping")
            continue
        for hook_job in ("on_fail", "on_complete"):
            entry = jobs.get(hook_job)
            if not isinstance(entry, dict):
                violations.append(f"{rel}: case {case_id} missing harness.jobs.{hook_job}")

        on_hooks = case.get("when")
        if not isinstance(on_hooks, dict):
            violations.append(f"{rel}: case {case_id} missing when mapping")
            continue
        fail_hook = on_hooks.get("fail")
        complete_hook = on_hooks.get("complete")
        if not _has_dispatch_for_job(fail_hook, "on_fail"):
            violations.append(f"{rel}: case {case_id} when.fail must dispatch on_fail")
        if not _has_dispatch_for_job(complete_hook, "on_complete"):
            violations.append(f"{rel}: case {case_id} when.complete must dispatch on_complete")

        contract = case.get("contract")
        if not _contract_dispatches_main(contract):
            violations.append(f"{rel}: case {case_id} contract must retain ops.job.dispatch main assertion")
    return violations


def _has_dispatch_for_job(exprs: Any, job_name: str) -> bool:
    if not isinstance(exprs, list):
        return False
    for expr in exprs:
        if not isinstance(expr, dict):
            continue
        dispatch = expr.get("ops.job.dispatch")
        if isinstance(dispatch, list) and dispatch and str(dispatch[0]).strip() == job_name:
            return True
    return False


def _contract_dispatches_main(contract: Any) -> bool:
    def _walk(node: Any) -> bool:
        if isinstance(node, dict):
            dispatch = node.get("ops.job.dispatch")
            if isinstance(dispatch, list) and dispatch and str(dispatch[0]).strip() == "main":
                return True
            for value in node.values():
                if _walk(value):
                    return True
            return False
        if isinstance(node, list):
            for value in node:
                if _walk(value):
                    return True
        return False

    return _walk(contract)


def _scan_architecture_harness_workflow_components_required(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    required_tokens = (
        "from spec_runner.components.execution_context import build_execution_context",
        "from spec_runner.components.assertion_engine import run_assertions_with_context",
        "from spec_runner.components.subject_router import resolve_subject_for_target",
    )
    violations: list[str] = []
    for rel in _HARNESS_FILES:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing harness file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required component workflow token {tok}")
    return violations


def _scan_architecture_harness_local_workflow_duplication_forbidden(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    forbidden_tokens = (
        "compile_import_bindings(",
        "limits_from_harness(",
        "load_spec_lang_symbols_for_case(",
        "evaluate_internal_assert_tree(",
    )
    violations: list[str] = []
    for rel in _HARNESS_FILES:
        p = _join_contract_path(root, rel)
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for tok in forbidden_tokens:
            if tok in text:
                line = _line_for(text, tok)
                violations.append(f"{rel}:{line}: forbidden legacy harness-workflow token present: {tok}")
    return violations


def _scan_schema_harness_type_overlay_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    required = {
        "specs/schema/registry/v1/types/orchestration_run.yaml": (
            "required_top_level",
            "allowed_top_level_extra",
            "fields",
        ),
        "specs/schema/registry/v1/types/docs_generate.yaml": (
            "required_top_level",
            "allowed_top_level_extra",
            "fields",
        ),
    }
    violations: list[str] = []
    for rel, keys in required.items():
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing required type overlay")
            continue
        payload = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            violations.append(f"{rel}:1: type overlay must be a mapping")
            continue
        for key in keys:
            if key not in payload:
                violations.append(f"{rel}:1: missing key {key}")
        fields = payload.get("fields")
        if not isinstance(fields, dict) or not fields:
            violations.append(f"{rel}:1: fields must be a non-empty mapping")
    return violations


def _scan_schema_harness_contract_overlay_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    contract = _join_contract_path(root, "specs/contract/04_harness.md")
    current = _join_contract_path(root, "specs/current.md")
    overlays = (
        _join_contract_path(root, "specs/schema/registry/v1/types/orchestration_run.yaml"),
        _join_contract_path(root, "specs/schema/registry/v1/types/docs_generate.yaml"),
    )
    violations: list[str] = []
    if not contract.exists():
        violations.append("specs/contract/04_harness.md:1: missing harness contract doc")
        return violations
    if not current.exists():
        violations.append("specs/current.md:1: missing current spec doc")
        return violations
    contract_text = contract.read_text(encoding="utf-8").lower()
    current_text = current.read_text(encoding="utf-8").lower()
    required_tokens = ("orchestration.run", "docs.generate", "components")
    for tok in required_tokens:
        if tok not in contract_text:
            violations.append(f"specs/contract/04_harness.md:1: missing token {tok}")
        if tok not in current_text:
            violations.append(f"specs/current.md:1: missing token {tok}")
    for p in overlays:
        if not p.exists():
            continue
        payload = yaml.safe_load(p.read_text(encoding="utf-8"))
        case_type = str((payload or {}).get("case_type", "")).strip()
        if case_type and case_type not in contract_text:
            violations.append(f"specs/contract/04_harness.md:1: missing overlay case_type token {case_type}")
    return violations


def _scan_runtime_harness_subject_target_map_declared(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    violations: list[str] = []
    for rel in _HARNESS_FILES:
        p = _join_contract_path(root, rel)
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        if "targets = {" not in text:
            violations.append(f"{rel}:1: missing declared target mapping (targets = {{...}})")
    return violations


def _scan_runtime_python_bin_resolver_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("python_bin_resolver")
    if not isinstance(cfg, dict):
        return [
            "runtime.python_bin_resolver_sync requires harness.python_bin_resolver mapping in governance spec"
        ]
    files = cfg.get("files")
    helper = str(cfg.get("helper", "")).strip()
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    required_tokens = cfg.get("required_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.python_bin_resolver.files must be a non-empty list of non-empty strings"]
    if not helper:
        return ["harness.python_bin_resolver.helper must be a non-empty string"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.python_bin_resolver.forbidden_tokens must be a list of non-empty strings"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.python_bin_resolver.required_tokens must be a list of non-empty strings"]

    helper_path = _join_contract_path(root, helper)
    if not helper_path.exists():
        violations.append(f"{helper}:1: missing shared python-bin resolver helper")

    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing script for python-bin resolver sync check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required python-bin resolver token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden inline python-bin resolver token {tok}")
    return violations


def _scan_runtime_runner_interface_gate_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("runner_interface")
    if not isinstance(cfg, dict):
        return [
            "runtime.runner_interface_gate_sync requires harness.runner_interface mapping in governance spec"
        ]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    required_paths = cfg.get("required_paths", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.runner_interface.files must be a non-empty list of non-empty strings"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.runner_interface.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.runner_interface.forbidden_tokens must be a list of non-empty strings"]
    if not isinstance(required_paths, list) or any(not isinstance(x, str) or not x.strip() for x in required_paths):
        return ["harness.runner_interface.required_paths must be a list of non-empty strings"]

    for rel in required_paths:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing required runner interface path")

    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing gate file for runner interface sync check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required runner-interface token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden direct runtime token {tok}")
    return violations


def _scan_runtime_runner_interface_subcommands(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("runner_interface_subcommands")
    if not isinstance(cfg, dict):
        return [
            "runtime.runner_interface_subcommands requires harness.runner_interface_subcommands mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_subcommands = cfg.get("required_subcommands")
    if not path:
        return ["harness.runner_interface_subcommands.path must be a non-empty string"]
    if (
        not isinstance(required_subcommands, list)
        or not required_subcommands
        or any(not isinstance(x, str) or not x.strip() for x in required_subcommands)
    ):
        return [
            "harness.runner_interface_subcommands.required_subcommands must be a non-empty list of non-empty strings"
        ]

    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing runner adapter script"]
    text = p.read_text(encoding="utf-8")
    declared: set[str] = set()
    for block in re.split(r'case\s+"\$\{subcommand\}"\s+in', text):
        if "esac" not in block:
            continue
        body = block.split("esac", 1)[0]
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped.endswith(")"):
                continue
            label = stripped[:-1].strip()
            if not label or label == "*":
                continue
            for candidate in label.split("|"):
                cmd = candidate.strip()
                if not cmd or cmd.startswith("-") or cmd == "*":
                    continue
                if re.fullmatch(r"[a-z0-9_-]+", cmd):
                    declared.add(cmd)
    for cmd in required_subcommands:
        if cmd not in declared:
            violations.append(f"{path}:1: missing runner-interface subcommand case label: {cmd}")
    return violations


def _scan_runtime_runner_interface_ci_lane(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("runner_interface_ci_lane")
    if not isinstance(cfg, dict):
        return [
            "runtime.runner_interface_ci_lane requires harness.runner_interface_ci_lane mapping in governance spec"
        ]
    workflow = str(cfg.get("workflow", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not workflow:
        return ["harness.runner_interface_ci_lane.workflow must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.runner_interface_ci_lane.required_tokens must be a non-empty list of non-empty strings"]
    p = _join_contract_path(root, workflow)
    if not p.exists():
        return [f"{workflow}:1: missing workflow file for runner interface CI lane check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{workflow}:1: missing required CI lane token {tok}")
    return violations


def _scan_runtime_runner_adapter_python_impl_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("runner_adapter_python_impl")
    if not isinstance(cfg, dict):
        return [
            "runtime.runner_adapter_python_impl_forbidden requires harness.runner_adapter_python_impl mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not path:
        return ["harness.runner_adapter_python_impl.path must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.runner_adapter_python_impl.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.runner_adapter_python_impl.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing runner adapter script"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing runner adapter token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{path}:1: forbidden python impl token present {tok}")
    return violations


def _scan_runtime_local_ci_parity_python_lane_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("local_ci_parity_python_lane")
    if not isinstance(cfg, dict):
        return [
            "runtime.local_ci_parity_python_lane_forbidden requires harness.local_ci_parity_python_lane mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not path:
        return ["harness.local_ci_parity_python_lane.path must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.local_ci_parity_python_lane.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.local_ci_parity_python_lane.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing local ci parity script"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing rust-only parity token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{path}:1: forbidden python lane token present {tok}")
    return violations


def _scan_runtime_make_python_parity_targets_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("make_python_parity")
    if not isinstance(cfg, dict):
        return [
            "runtime.make_python_parity_targets_forbidden requires harness.make_python_parity mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not path:
        return ["harness.make_python_parity.path must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.make_python_parity.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.make_python_parity.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing Makefile"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing Makefile token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{path}:1: forbidden python Make target token present {tok}")
    return violations


def _scan_runtime_ci_python_lane_non_blocking_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("ci_python_lane_non_blocking")
    if not isinstance(cfg, dict):
        return [
            "runtime.ci_python_lane_non_blocking_required requires harness.ci_python_lane_non_blocking mapping in governance spec"
        ]
    workflow = str(cfg.get("workflow", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not workflow:
        return ["harness.ci_python_lane_non_blocking.workflow must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.ci_python_lane_non_blocking.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.ci_python_lane_non_blocking.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, workflow)
    if not p.exists():
        return [f"{workflow}:1: missing CI workflow file"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{workflow}:1: missing python lane non-blocking token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{workflow}:1: forbidden blocking token present {tok}")
    return violations


def _scan_runtime_required_rust_lane_blocking_status(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("required_rust_lane")
    if not isinstance(cfg, dict):
        return [
            "runtime.required_rust_lane_blocking_status requires harness.required_rust_lane mapping in governance spec"
        ]
    workflow = str(cfg.get("workflow", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not workflow:
        return ["harness.required_rust_lane.workflow must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.required_rust_lane.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.required_rust_lane.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, workflow)
    if not p.exists():
        return [f"{workflow}:1: missing CI workflow file"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{workflow}:1: missing required rust-lane blocking token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{workflow}:1: forbidden non-blocking rust-lane token present {tok}")
    return violations


def _scan_runtime_compatibility_lanes_non_blocking_status(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("compatibility_lanes")
    if not isinstance(cfg, dict):
        return [
            "runtime.compatibility_lanes_non_blocking_status requires harness.compatibility_lanes mapping in governance spec"
        ]
    workflow = str(cfg.get("workflow", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not workflow:
        return ["harness.compatibility_lanes.workflow must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.compatibility_lanes.required_tokens must be a non-empty list of non-empty strings"]
    p = _join_contract_path(root, workflow)
    if not p.exists():
        return [f"{workflow}:1: missing CI workflow file"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{workflow}:1: missing compatibility non-blocking token {tok}")
    return violations


def _scan_runtime_compatibility_matrix_registration_required(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("compatibility_matrix")
    if not isinstance(cfg, dict):
        return [
            "runtime.compatibility_matrix_registration_required requires harness.compatibility_matrix mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.compatibility_matrix.path must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.compatibility_matrix.required_tokens must be a non-empty list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing compatibility matrix contract file"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing compatibility matrix token {tok}")
    return violations


def _run_runner_certify_cached(root: Path, runner_id: str) -> tuple[int, str]:
    key = (_SCAN_CACHE_TOKEN, str(root), runner_id)
    with _SCAN_CACHE_LOCK:
        cached = _RUNNER_CERTIFY_CACHE.get(key)
    if cached is not None:
        return cached
    cmd = [
        "./runners/public/runner_adapter.sh",
        "--impl",
        "rust",
        "runner-certify",
        "--runner",
        runner_id,
    ]
    try:
        cp = _profiled_subprocess_run(
            cmd,
            cwd=root,
            phase="governance.runner_certify",
        )
    except LivenessError as exc:
        result = (124, f"runner-certify --runner {runner_id} failed liveness watchdog: {exc.reason_token}")
        with _SCAN_CACHE_LOCK:
            _RUNNER_CERTIFY_CACHE[key] = result
        return result
    output = ((cp.stdout or "") + "\n" + (cp.stderr or "")).strip()
    result = (int(cp.returncode), output)
    with _SCAN_CACHE_LOCK:
        _RUNNER_CERTIFY_CACHE[key] = result
    return result


def _scan_runtime_runner_certification_registry_valid(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("runner_certification")
    if not isinstance(cfg, dict):
        return [
            "runtime.runner_certification_registry_valid requires harness.runner_certification mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_runner_ids = cfg.get("required_runner_ids", [])
    if not path:
        return ["harness.runner_certification.path must be a non-empty string"]
    if (
        not isinstance(required_runner_ids, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_runner_ids)
    ):
        return ["harness.runner_certification.required_runner_ids must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing runner certification registry file"]
    try:
        payload = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{path}:1: invalid YAML ({exc})"]
    if not isinstance(payload, dict):
        return [f"{path}:1: expected mapping root"]
    runners = payload.get("runners")
    if not isinstance(runners, list) or not runners:
        return [f"{path}:1: runners must be a non-empty list"]
    seen: set[str] = set()
    valid_classes = {"required", "compatibility_non_blocking"}
    valid_status = {"active", "planned", "retired"}
    for idx, item in enumerate(runners, start=1):
        if not isinstance(item, dict):
            violations.append(f"{path}:1: runners[{idx}] must be a mapping")
            continue
        rid = str(item.get("runner_id", "")).strip()
        if not rid:
            violations.append(f"{path}:1: runners[{idx}].runner_id required")
            continue
        if rid in seen:
            violations.append(f"{path}:1: duplicate runner_id `{rid}`")
        seen.add(rid)
        clazz = str(item.get("class", "")).strip()
        if clazz not in valid_classes:
            violations.append(
                f"{path}:1: runners[{idx}].class must be one of required|compatibility_non_blocking"
            )
        status = str(item.get("status", "")).strip()
        if status not in valid_status:
            violations.append(f"{path}:1: runners[{idx}].status must be one of active|planned|retired")
        entrypoints = item.get("entrypoints")
        if not isinstance(entrypoints, dict):
            violations.append(f"{path}:1: runners[{idx}].entrypoints must be a mapping")
        command_subset = item.get("command_contract_subset", [])
        if not isinstance(command_subset, list):
            violations.append(f"{path}:1: runners[{idx}].command_contract_subset must be a list")
        artifact_contract = item.get("artifact_contract")
        if not isinstance(artifact_contract, dict):
            violations.append(f"{path}:1: runners[{idx}].artifact_contract must be a mapping")
        else:
            if not str(artifact_contract.get("json_out", "")).strip():
                violations.append(f"{path}:1: runners[{idx}].artifact_contract.json_out required")
            if not str(artifact_contract.get("md_out", "")).strip():
                violations.append(f"{path}:1: runners[{idx}].artifact_contract.md_out required")
    for rid in required_runner_ids:
        if rid not in seen:
            violations.append(f"{path}:1: missing required runner registry entry `{rid}`")
    return violations


def _scan_runtime_runner_certification_surfaces_sync(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("runner_certification_surfaces")
    if not isinstance(cfg, dict):
        return [
            "runtime.runner_certification_surfaces_sync requires harness.runner_certification_surfaces mapping in governance spec"
        ]
    files = cfg.get("files", [])
    required_tokens = cfg.get("required_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.runner_certification_surfaces.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return [
            "harness.runner_certification_surfaces.required_tokens must be a non-empty list of non-empty strings"
        ]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing runner certification surface file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing runner certification token {tok}")
    return violations


def _scan_runtime_runner_certification_artifacts_contract_sync(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    code, output = _run_runner_certify_cached(root, "rust")
    if code != 0:
        msg = output or "runner-certify --runner rust failed"
        return [msg]
    json_path = root / ".artifacts/runner-certification-rust.json"
    md_path = root / ".artifacts/runner-certification-rust.md"
    violations: list[str] = []
    if not json_path.exists():
        violations.append(".artifacts/runner-certification-rust.json:1: certification JSON artifact missing")
    else:
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            violations.append(
                f".artifacts/runner-certification-rust.json:{exc.lineno}: invalid JSON artifact"
            )
        else:
            if not isinstance(payload, dict):
                violations.append(".artifacts/runner-certification-rust.json:1: artifact must be JSON object")
            else:
                for key in ("runner", "summary", "checks"):
                    if key not in payload:
                        violations.append(
                            f".artifacts/runner-certification-rust.json:1: missing artifact key `{key}`"
                        )
    if not md_path.exists():
        violations.append(".artifacts/runner-certification-rust.md:1: certification markdown artifact missing")
    return violations


def _scan_runtime_runner_certification_required_lane_passes(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    code, output = _run_runner_certify_cached(root, "rust")
    if code != 0:
        return [output or "runner-certify --runner rust failed"]
    json_path = root / ".artifacts/runner-certification-rust.json"
    if not json_path.exists():
        return [".artifacts/runner-certification-rust.json:1: certification artifact missing"]
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f".artifacts/runner-certification-rust.json:{exc.lineno}: invalid JSON artifact"]
    runner = payload.get("runner") if isinstance(payload, dict) else None
    summary = payload.get("summary") if isinstance(payload, dict) else None
    violations: list[str] = []
    if not isinstance(runner, dict) or runner.get("runner_id") != "rust":
        violations.append(".artifacts/runner-certification-rust.json:1: runner_id must be rust")
    if isinstance(runner, dict) and runner.get("blocking") is not True:
        violations.append(".artifacts/runner-certification-rust.json:1: required rust lane must be blocking")
    if not isinstance(summary, dict) or summary.get("status") != "pass":
        violations.append(".artifacts/runner-certification-rust.json:1: required rust lane certification must pass")
    return violations


def _scan_runtime_runner_certification_compat_lanes_non_blocking(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    del harness
    lanes = ("python", "php", "node", "c")
    violations: list[str] = []
    for lane in lanes:
        code, output = _run_runner_certify_cached(root, lane)
        if code not in (0, 1):
            violations.append(output or f"runner-certify --runner {lane} failed with exit code {code}")
            continue
        json_path = root / f".artifacts/runner-certification-{lane}.json"
        if not json_path.exists():
            violations.append(f".artifacts/runner-certification-{lane}.json:1: certification artifact missing")
            continue
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            violations.append(f".artifacts/runner-certification-{lane}.json:{exc.lineno}: invalid JSON artifact")
            continue
        runner = payload.get("runner") if isinstance(payload, dict) else None
        if not isinstance(runner, dict):
            violations.append(f".artifacts/runner-certification-{lane}.json:1: missing runner metadata")
            continue
        if runner.get("class") != "compatibility_non_blocking":
            violations.append(
                f".artifacts/runner-certification-{lane}.json:1: runner class must be compatibility_non_blocking"
            )
        if runner.get("blocking") is True:
            violations.append(f".artifacts/runner-certification-{lane}.json:1: compatibility lane must be non-blocking")
    return violations


def _scan_docs_compatibility_examples_labeled(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("compatibility_docs")
    if not isinstance(cfg, dict):
        return [
            "docs.compatibility_examples_labeled requires harness.compatibility_docs mapping in governance spec"
        ]
    files = cfg.get("files", [])
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.compatibility_docs.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.compatibility_docs.required_tokens must be a list of non-empty strings"]
    if (
        not isinstance(forbidden_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return ["harness.compatibility_docs.forbidden_tokens must be a list of non-empty strings"]

    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing compatibility docs file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing compatibility docs token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden unlabeled python-first token {tok}")
    return violations


def _scan_docs_readme_rust_first_coherence(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("readme_coherence")
    if not isinstance(cfg, dict):
        return [
            "docs.readme_rust_first_coherence requires harness.readme_coherence mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    required_paths = cfg.get("required_paths", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not path:
        return ["harness.readme_coherence.path must be a non-empty string"]
    if (
        not isinstance(required_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.readme_coherence.required_tokens must be a list of non-empty strings"]
    if (
        not isinstance(required_paths, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_paths)
    ):
        return ["harness.readme_coherence.required_paths must be a list of non-empty strings"]
    if (
        not isinstance(forbidden_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return ["harness.readme_coherence.forbidden_tokens must be a list of non-empty strings"]

    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing README coherence file"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing required README token {tok}")
    for rel in required_paths:
        if rel not in text:
            violations.append(f"{path}:1: missing required README path {rel}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{path}:1: forbidden legacy token present {tok}")
    return violations


def _scan_docs_generated_command_meta_no_python_exec(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("generated_command_meta")
    if not isinstance(cfg, dict):
        return [
            "docs.generated_command_meta_no_python_exec requires harness.generated_command_meta mapping in governance spec"
        ]
    files = cfg.get("files", [])
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.generated_command_meta.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.generated_command_meta.required_tokens must be a list of non-empty strings"]
    if (
        not isinstance(forbidden_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return ["harness.generated_command_meta.forbidden_tokens must be a list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing generated docs file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required generated command token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden python command token present {tok}")
    return violations


def _scan_runtime_rust_only_prepush_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("rust_only_prepush")
    if not isinstance(cfg, dict):
        return ["runtime.rust_only_prepush_required requires harness.rust_only_prepush mapping in governance spec"]
    file_token_sets = cfg.get("file_token_sets", [])
    if (
        not isinstance(file_token_sets, list)
        or not file_token_sets
        or any(not isinstance(x, dict) for x in file_token_sets)
    ):
        return [
            "harness.rust_only_prepush.file_token_sets must be a non-empty list of mappings with path, required_tokens, and forbidden_tokens"
        ]
    for item in file_token_sets:
        rel = str(item.get("path", "")).strip()
        required_tokens = item.get("required_tokens", [])
        forbidden_tokens = item.get("forbidden_tokens", [])
        if not rel:
            return ["harness.rust_only_prepush.file_token_sets[*].path must be non-empty"]
        if (
            not isinstance(required_tokens, list)
            or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
        ):
            return [
                "harness.rust_only_prepush.file_token_sets[*].required_tokens must be a list of non-empty strings"
            ]
        if (
            not isinstance(forbidden_tokens, list)
            or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
        ):
            return [
                "harness.rust_only_prepush.file_token_sets[*].forbidden_tokens must be a list of non-empty strings"
            ]
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing file for rust-only prepush check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing rust-only prepush token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden non-rust prepush token present {tok}")
    return violations


def _scan_runtime_prepush_parity_default_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("prepush_parity_default")
    if not isinstance(cfg, dict):
        return ["runtime.prepush_parity_default_required requires harness.prepush_parity_default mapping in governance spec"]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.prepush_parity_default.files must be a non-empty list of non-empty strings"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.prepush_parity_default.required_tokens must be a list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing prepush parity file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing prepush parity default token {tok}")
    return violations


def _scan_runtime_prepush_python_parity_not_optional_by_default(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("prepush_python_parity")
    if not isinstance(cfg, dict):
        return [
            "runtime.prepush_python_parity_not_optional_by_default requires harness.prepush_python_parity mapping in governance spec"
        ]
    file_rel = str(cfg.get("path", "")).strip()
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    required_tokens = cfg.get("required_tokens", [])
    if not file_rel:
        return ["harness.prepush_python_parity.path must be a non-empty string"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.prepush_python_parity.forbidden_tokens must be a list of non-empty strings"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.prepush_python_parity.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, file_rel)
    if not p.exists():
        return [f"{file_rel}:1: missing prepush script"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{file_rel}:1: missing required python parity token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{file_rel}:1: forbidden optional parity token present {tok}")
    return violations


def _scan_runtime_git_hook_prepush_enforced(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("git_hook_prepush")
    if not isinstance(cfg, dict):
        return ["runtime.git_hook_prepush_enforced requires harness.git_hook_prepush mapping in governance spec"]
    hook_path = str(cfg.get("hook_path", "")).strip()
    install_script = str(cfg.get("install_script", "")).strip()
    makefile_path = str(cfg.get("makefile_path", "Makefile")).strip() or "Makefile"
    if not hook_path or not install_script:
        return ["harness.git_hook_prepush.hook_path and install_script must be non-empty strings"]
    hook = _join_contract_path(root, hook_path)
    installer = _join_contract_path(root, install_script)
    makefile = _join_contract_path(root, makefile_path)
    if not hook.exists():
        violations.append(f"{hook_path}:1: missing managed pre-push hook")
    else:
        text = hook.read_text(encoding="utf-8")
        for tok in ("SPEC_PREPUSH_BYPASS", "make prepush"):
            if tok not in text:
                violations.append(f"{hook_path}:1: missing pre-push hook token {tok}")
    if not installer.exists():
        violations.append(f"{install_script}:1: missing git-hook installer script")
    else:
        text = installer.read_text(encoding="utf-8")
        if "core.hooksPath .githooks" not in text:
            violations.append(f"{install_script}:1: missing core.hooksPath installation token")
    if not makefile.exists():
        violations.append(f"{makefile_path}:1: missing Makefile for hook target")
    else:
        text = makefile.read_text(encoding="utf-8")
        if "hooks-install:" not in text:
            violations.append(f"{makefile_path}:1: missing hooks-install target")
    return violations


def _scan_runtime_fast_path_consistency_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("fast_path_consistency")
    if not isinstance(cfg, dict):
        return [
            "runtime.fast_path_consistency_required requires harness.fast_path_consistency mapping in governance spec"
        ]
    file_token_sets = cfg.get("file_token_sets", [])
    if (
        not isinstance(file_token_sets, list)
        or not file_token_sets
        or any(not isinstance(x, dict) for x in file_token_sets)
    ):
        return [
            "harness.fast_path_consistency.file_token_sets must be a non-empty list of mappings with path and required_tokens"
        ]
    for item in file_token_sets:
        rel = str(item.get("path", "")).strip()
        required_tokens = item.get("required_tokens", [])
        if not rel:
            return ["harness.fast_path_consistency.file_token_sets[*].path must be non-empty"]
        if (
            not isinstance(required_tokens, list)
            or not required_tokens
            or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
        ):
            return [
                "harness.fast_path_consistency.file_token_sets[*].required_tokens must be a non-empty list of non-empty strings"
            ]
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing fast-path consistency file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing fast-path consistency token {tok}")
    return violations


def _scan_runtime_rust_adapter_target_fallback_defined(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("rust_target_fallback")
    if not isinstance(cfg, dict):
        return [
            "runtime.rust_adapter_target_fallback_defined requires harness.rust_target_fallback mapping in governance spec"
        ]
    rel = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not rel:
        return ["harness.rust_target_fallback.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.rust_target_fallback.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, rel)
    if not p.exists():
        return [f"{rel}:1: missing rust adapter script"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{rel}:1: missing rust target fallback token {tok}")
    return violations


def _scan_runtime_local_ci_parity_entrypoint_documented(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("local_ci_parity_docs")
    if not isinstance(cfg, dict):
        return [
            "runtime.local_ci_parity_entrypoint_documented requires harness.local_ci_parity_docs mapping in governance spec"
        ]
    files = cfg.get("files")
    required_tokens = cfg.get("required_tokens")
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.local_ci_parity_docs.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.local_ci_parity_docs.required_tokens must be a non-empty list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing local-ci parity doc file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing local-ci parity doc token {tok}")
    return violations


def _scan_runtime_governance_triage_entrypoint_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("governance_triage")
    if not isinstance(cfg, dict):
        return ["runtime.governance_triage_entrypoint_required requires harness.governance_triage mapping in governance spec"]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.governance_triage.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.governance_triage.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing governance triage entrypoint script"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing governance triage token {tok}")
    return violations


def _scan_runtime_prepush_uses_governance_triage_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("prepush_governance_triage")
    if not isinstance(cfg, dict):
        return [
            "runtime.prepush_uses_governance_triage_required requires harness.prepush_governance_triage mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not path:
        return ["harness.prepush_governance_triage.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.prepush_governance_triage.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.prepush_governance_triage.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing prepush parity script for governance triage check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing prepush governance triage token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{path}:1: forbidden prepush token present {tok}")
    return violations


def _scan_runtime_cigate_uses_governance_triage_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("cigate_governance_triage")
    if not isinstance(cfg, dict):
        return [
            "runtime.cigate_uses_governance_triage_required requires harness.cigate_governance_triage mapping in governance spec"
        ]
    files = cfg.get("files", [])
    required_tokens = cfg.get("required_tokens", [])
    if not isinstance(files, list) or any(not isinstance(x, str) or not x.strip() for x in files):
        return ["harness.cigate_governance_triage.files must be a non-empty list of non-empty strings"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.cigate_governance_triage.required_tokens must be a list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing ci-gate governance triage file")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing ci-gate governance triage token {tok}")
    return violations


def _scan_runtime_triage_artifacts_emitted_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("triage_artifacts")
    if not isinstance(cfg, dict):
        return ["runtime.triage_artifacts_emitted_required requires harness.triage_artifacts mapping in governance spec"]
    files = cfg.get("files", [])
    required_tokens = cfg.get("required_tokens", [])
    if not isinstance(files, list) or any(not isinstance(x, str) or not x.strip() for x in files):
        return ["harness.triage_artifacts.files must be a non-empty list of non-empty strings"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.triage_artifacts.required_tokens must be a list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing file for triage artifact check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing triage artifact token {tok}")
    return violations


def _scan_runtime_triage_failure_id_parsing_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("triage_failure_parser")
    if not isinstance(cfg, dict):
        return [
            "runtime.triage_failure_id_parsing_required requires harness.triage_failure_parser mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.triage_failure_parser.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.triage_failure_parser.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing governance triage parser script"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing triage failure-parser token {tok}")
    return violations


def _scan_runtime_triage_bypass_logged_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("triage_bypass_logging")
    if not isinstance(cfg, dict):
        return ["runtime.triage_bypass_logged_required requires harness.triage_bypass_logging mapping in governance spec"]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.triage_bypass_logging.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.triage_bypass_logging.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing pre-push hook for bypass logging check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing triage bypass logging token {tok}")
    return violations


def _scan_runtime_triage_stall_fallback_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("triage_stall_fallback")
    if not isinstance(cfg, dict):
        return ["runtime.triage_stall_fallback_required requires harness.triage_stall_fallback mapping in governance spec"]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.triage_stall_fallback.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.triage_stall_fallback.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing governance triage script for stall fallback check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing triage stall fallback token {tok}")
    return violations


def _scan_runtime_governance_triage_targeted_first_required(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("triage_targeted_first")
    if not isinstance(cfg, dict):
        return [
            "runtime.governance_triage_targeted_first_required requires harness.triage_targeted_first mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.triage_targeted_first.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.triage_targeted_first.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing governance triage script for targeted-first check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing targeted-first token {tok}")
    return violations


def _scan_runtime_local_prepush_broad_governance_forbidden(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("local_prepush_broad_forbidden")
    if not isinstance(cfg, dict):
        return [
            "runtime.local_prepush_broad_governance_forbidden requires harness.local_prepush_broad_forbidden mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not path:
        return ["harness.local_prepush_broad_forbidden.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.local_prepush_broad_forbidden.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.local_prepush_broad_forbidden.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing local prepush script for broad-governance check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing local prepush token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{path}:1: forbidden local prepush token present {tok}")
    return violations


def _scan_runtime_ci_gate_ownership_contract_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("ci_gate_ownership_contract")
    if not isinstance(cfg, dict):
        return [
            "runtime.ci_gate_ownership_contract_required requires harness.ci_gate_ownership_contract mapping in governance spec"
        ]

    gate_path = str(cfg.get("gate_path", "")).strip()
    gate_required_tokens = cfg.get("gate_required_tokens", [])
    gate_ordered_tokens = cfg.get("gate_ordered_tokens", [])
    summary_files = cfg.get("summary_files", [])
    summary_required_tokens = cfg.get("summary_required_tokens", [])
    summary_forbidden_tokens = cfg.get("summary_forbidden_tokens", [])

    if (
        not gate_path
        or not isinstance(gate_required_tokens, list)
        or not gate_required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in gate_required_tokens)
        or not isinstance(gate_ordered_tokens, list)
        or len(gate_ordered_tokens) < 2
        or any(not isinstance(x, str) or not x.strip() for x in gate_ordered_tokens)
    ):
        return [
            "harness.ci_gate_ownership_contract gate_path/gate_required_tokens/gate_ordered_tokens are required with non-empty string tokens"
        ]
    if (
        not isinstance(summary_files, list)
        or not summary_files
        or any(not isinstance(x, str) or not x.strip() for x in summary_files)
        or not isinstance(summary_required_tokens, list)
        or not summary_required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in summary_required_tokens)
        or not isinstance(summary_forbidden_tokens, list)
        or any(not isinstance(x, str) or not x.strip() for x in summary_forbidden_tokens)
    ):
        return [
            "harness.ci_gate_ownership_contract summary_files/summary_required_tokens/summary_forbidden_tokens must be valid token lists"
        ]

    gate_file = _join_contract_path(root, gate_path)
    if not gate_file.exists():
        violations.append(f"{gate_path}:1: missing ci gate script for ownership-contract check")
    else:
        gate_text = gate_file.read_text(encoding="utf-8")
        for tok in gate_required_tokens:
            if tok not in gate_text:
                violations.append(f"{gate_path}:1: missing required ci gate ownership token {tok}")
        last_idx = -1
        for tok in gate_ordered_tokens:
            idx = gate_text.find(tok)
            if idx < 0:
                violations.append(f"{gate_path}:1: missing ordered ci gate ownership token {tok}")
                break
            if idx < last_idx:
                violations.append(f"{gate_path}:1: ordered token violation for ci gate ownership sequence")
                break
            last_idx = idx

    for rel in summary_files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing ci-gate-summary file for ownership-contract check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in summary_required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required ci-gate-summary ownership token {tok}")
        for tok in summary_forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden ci-gate-summary ownership token present {tok}")
    return violations


def _scan_runtime_governance_prefix_selection_from_changed_paths(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("triage_prefix_selection")
    if not isinstance(cfg, dict):
        return [
            "runtime.governance_prefix_selection_from_changed_paths requires harness.triage_prefix_selection mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.triage_prefix_selection.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.triage_prefix_selection.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing governance triage script for changed-path selection check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing changed-path selection token {tok}")
    return violations


def _scan_runtime_governance_triage_artifact_contains_selection_metadata(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("triage_artifact_selection_metadata")
    if not isinstance(cfg, dict):
        return [
            "runtime.governance_triage_artifact_contains_selection_metadata requires harness.triage_artifact_selection_metadata mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.triage_artifact_selection_metadata.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.triage_artifact_selection_metadata.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing governance triage script for artifact metadata check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing triage artifact metadata token {tok}")
    return violations


def _scan_runtime_ci_artifact_upload_paths_valid(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("ci_artifact_upload")
    if not isinstance(cfg, dict):
        return ["runtime.ci_artifact_upload_paths_valid requires harness.ci_artifact_upload mapping in governance spec"]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.ci_artifact_upload.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.ci_artifact_upload.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing workflow file for artifact upload path check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing artifact upload token {tok}")
    return violations


def _scan_runtime_ci_workflow_critical_gate_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("ci_workflow_critical_gate")
    if not isinstance(cfg, dict):
        return [
            "runtime.ci_workflow_critical_gate_required requires harness.ci_workflow_critical_gate mapping in governance spec"
        ]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    if not path:
        return ["harness.ci_workflow_critical_gate.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.ci_workflow_critical_gate.required_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing workflow file for rust critical gate check"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing rust critical gate workflow token {tok}")
    return violations


def _scan_runtime_ci_gate_default_no_python_governance_required(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("ci_gate_default_no_python_governance")
    if not isinstance(cfg, dict):
        return [
            "runtime.ci_gate_default_no_python_governance_required requires harness.ci_gate_default_no_python_governance mapping in governance spec"
        ]
    files = cfg.get("files", [])
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.ci_gate_default_no_python_governance.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(required_tokens, list)
        or not required_tokens
        or any(not isinstance(x, str) or not x.strip() for x in required_tokens)
    ):
        return ["harness.ci_gate_default_no_python_governance.required_tokens must be a non-empty list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.ci_gate_default_no_python_governance.forbidden_tokens must be a list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing file for CI gate no-python-governance check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                violations.append(f"{rel}:1: missing required no-python-governance token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden default-governance token present {tok}")
    return violations


def _scan_runtime_ci_gate_default_report_commands_forbidden(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("ci_gate_default_reports_forbidden")
    if not isinstance(cfg, dict):
        return [
            "runtime.ci_gate_default_report_commands_forbidden requires harness.ci_gate_default_reports_forbidden mapping in governance spec"
        ]
    files = cfg.get("files", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if (
        not isinstance(files, list)
        or not files
        or any(not isinstance(x, str) or not x.strip() for x in files)
    ):
        return ["harness.ci_gate_default_reports_forbidden.files must be a non-empty list of non-empty strings"]
    if (
        not isinstance(forbidden_tokens, list)
        or not forbidden_tokens
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens)
    ):
        return ["harness.ci_gate_default_reports_forbidden.forbidden_tokens must be a non-empty list of non-empty strings"]
    for rel in files:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing file for default report-command check")
            continue
        text = p.read_text(encoding="utf-8")
        for tok in forbidden_tokens:
            if tok in text:
                violations.append(f"{rel}:1: forbidden default report-command token present {tok}")
    return violations


def _scan_runtime_rust_adapter_no_delegate(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("rust_adapter")
    if not isinstance(cfg, dict):
        return ["runtime.rust_adapter_no_delegate requires harness.rust_adapter mapping in governance spec"]
    path = str(cfg.get("path", "")).strip()
    required_tokens = cfg.get("required_tokens", [])
    forbidden_tokens = cfg.get("forbidden_tokens", [])
    if not path:
        return ["harness.rust_adapter.path must be a non-empty string"]
    if not isinstance(required_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in required_tokens):
        return ["harness.rust_adapter.required_tokens must be a list of non-empty strings"]
    if not isinstance(forbidden_tokens, list) or any(not isinstance(x, str) or not x.strip() for x in forbidden_tokens):
        return ["harness.rust_adapter.forbidden_tokens must be a list of non-empty strings"]
    p = _join_contract_path(root, path)
    if not p.exists():
        return [f"{path}:1: missing rust adapter script"]
    text = p.read_text(encoding="utf-8")
    for tok in required_tokens:
        if tok not in text:
            violations.append(f"{path}:1: missing required rust-adapter token {tok}")
    for tok in forbidden_tokens:
        if tok in text:
            violations.append(f"{path}:1: forbidden rust-adapter delegation token {tok}")
    return violations


def _scan_runtime_rust_adapter_exec_smoke(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("rust_adapter_exec_smoke")
    if not isinstance(cfg, dict):
        return ["runtime.rust_adapter_exec_smoke requires harness.rust_adapter_exec_smoke mapping in governance spec"]

    raw_command = cfg.get("command")
    command: list[str]
    if isinstance(raw_command, str):
        command = shlex.split(raw_command)
    elif isinstance(raw_command, list) and raw_command:
        if any(not isinstance(x, str) or not x.strip() for x in raw_command):
            return ["harness.rust_adapter_exec_smoke.command list must contain only non-empty strings"]
        command = [x.strip() for x in raw_command]
    else:
        return ["harness.rust_adapter_exec_smoke.command must be a non-empty string or list of strings"]
    if not command:
        return ["harness.rust_adapter_exec_smoke.command must not be empty"]

    expected_exit_codes = cfg.get("expected_exit_codes", [0])
    if (
        not isinstance(expected_exit_codes, list)
        or not expected_exit_codes
        or any(not isinstance(x, int) for x in expected_exit_codes)
    ):
        return ["harness.rust_adapter_exec_smoke.expected_exit_codes must be a non-empty list of integers"]

    required_output_tokens = cfg.get("required_output_tokens", [])
    if not isinstance(required_output_tokens, list) or any(
        not isinstance(x, str) or not x.strip() for x in required_output_tokens
    ):
        return ["harness.rust_adapter_exec_smoke.required_output_tokens must be a list of non-empty strings"]

    forbidden_output_tokens = cfg.get("forbidden_output_tokens", [])
    if not isinstance(forbidden_output_tokens, list) or any(
        not isinstance(x, str) or not x.strip() for x in forbidden_output_tokens
    ):
        return ["harness.rust_adapter_exec_smoke.forbidden_output_tokens must be a list of non-empty strings"]

    timeout_seconds = cfg.get("timeout_seconds", 120)
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        return ["harness.rust_adapter_exec_smoke.timeout_seconds must be a positive number"]

    display_cmd = shlex.join(command)
    try:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=float(timeout_seconds),
            check=False,
        )
    except FileNotFoundError:
        return [f"{display_cmd}:1: command not found for rust adapter exec smoke"]
    except PermissionError:
        return [f"{display_cmd}:1: permission denied for rust adapter exec smoke command"]
    except subprocess.TimeoutExpired:
        return [f"{display_cmd}:1: rust adapter exec smoke command timed out after {timeout_seconds}s"]

    violations: list[str] = []
    if result.returncode not in expected_exit_codes:
        violations.append(
            f"{display_cmd}:1: unexpected exit code {result.returncode} "
            f"(expected one of: {expected_exit_codes})"
        )

    combined_output = f"{result.stdout}\n{result.stderr}"
    for tok in required_output_tokens:
        if tok not in combined_output:
            violations.append(f"{display_cmd}:1: missing required output token {tok!r}")
    for tok in forbidden_output_tokens:
        if tok in combined_output:
            violations.append(f"{display_cmd}:1: forbidden output token present {tok!r}")

    return violations


def _scan_runtime_rust_adapter_subcommand_parity(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("rust_subcommand_parity")
    if not isinstance(cfg, dict):
        return [
            "runtime.rust_adapter_subcommand_parity requires harness.rust_subcommand_parity mapping in governance spec"
        ]

    adapter_path = str(cfg.get("adapter_path", "")).strip()
    cli_main_path = str(cfg.get("cli_main_path", "")).strip()
    if not adapter_path:
        return ["harness.rust_subcommand_parity.adapter_path must be a non-empty string"]
    if not cli_main_path:
        return ["harness.rust_subcommand_parity.cli_main_path must be a non-empty string"]

    adapter_file = _join_contract_path(root, adapter_path)
    cli_main_file = _join_contract_path(root, cli_main_path)
    if not adapter_file.exists():
        return [f"{adapter_path}:1: missing rust adapter script for subcommand parity check"]
    if not cli_main_file.exists():
        return [f"{cli_main_path}:1: missing rust cli main source for subcommand parity check"]

    adapter_text = adapter_file.read_text(encoding="utf-8")
    cli_text = cli_main_file.read_text(encoding="utf-8")

    def _extract_case_blocks(text: str, marker: str) -> list[str]:
        blocks: list[str] = []
        start = 0
        while True:
            idx = text.find(marker, start)
            if idx < 0:
                break
            body = text[idx + len(marker) :]
            end = body.find("esac")
            if end < 0:
                break
            blocks.append(body[:end])
            start = idx + len(marker) + end + len("esac")
        return blocks

    adapter_subcommands: set[str] = set()
    for block in _extract_case_blocks(adapter_text, 'case "${subcommand}" in'):
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped.endswith(")"):
                continue
            label = stripped[:-1].strip()
            if not label or label == "*":
                continue
            for candidate in label.split("|"):
                cmd = candidate.strip()
                if not cmd or cmd == "*" or cmd.startswith("-"):
                    continue
                if re.fullmatch(r"[a-z0-9_-]+", cmd):
                    adapter_subcommands.add(cmd)

    cli_subcommands: set[str] = set()
    match_marker = 'let code = match subcommand.as_str() {'
    start_idx = cli_text.find(match_marker)
    if start_idx >= 0:
        match_body = cli_text[start_idx + len(match_marker) :]
        end_idx = match_body.find("\n    };")
        if end_idx >= 0:
            match_body = match_body[:end_idx]
    else:
        match_body = cli_text
    for arm in re.finditer(r'((?:"[a-z0-9_-]+"\s*(?:\|\s*)?)+)\s*=>', match_body, flags=re.MULTILINE):
        for lit in re.finditer(r'"([a-z0-9_-]+)"', arm.group(1)):
            cli_subcommands.add(lit.group(1))

    if not adapter_subcommands:
        return [f"{adapter_path}:1: no adapter subcommand labels found"]
    if not cli_subcommands:
        return [f"{cli_main_path}:1: no rust cli subcommand match arms found"]

    violations: list[str] = []
    for cmd in sorted(adapter_subcommands - cli_subcommands):
        violations.append(
            f"{cli_main_path}:1: missing rust cli subcommand handler for adapter-exposed command {cmd}"
        )
    for cmd in sorted(cli_subcommands - adapter_subcommands):
        violations.append(
            f"{adapter_path}:1: missing adapter subcommand label for rust cli-exposed command {cmd}"
        )
    return violations


def _scan_naming_filename_policy(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    h = harness or {}
    cfg = h.get("filename_policy")
    if not isinstance(cfg, dict):
        return ["naming.filename_policy requires harness.filename_policy mapping in governance spec"]

    paths = cfg.get("paths")
    if not isinstance(paths, list) or not paths or any(not isinstance(x, str) or not x.strip() for x in paths):
        return ["harness.filename_policy.paths must be a non-empty list of non-empty strings"]

    include_exts = cfg.get("include_extensions", [])
    if not isinstance(include_exts, list) or any(not isinstance(x, str) or not x.strip() for x in include_exts):
        return ["harness.filename_policy.include_extensions must be a list of non-empty strings"]
    include_exts_set = {x.strip().lower() for x in include_exts}

    allow_exact = cfg.get("allow_exact", [])
    if not isinstance(allow_exact, list) or any(not isinstance(x, str) or not x.strip() for x in allow_exact):
        return ["harness.filename_policy.allow_exact must be a list of non-empty strings"]
    allow_exact_set = {x.strip() for x in allow_exact}

    allowed_name_regex = str(
        cfg.get("allowed_name_regex", r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
    ).strip()
    if not allowed_name_regex:
        return ["harness.filename_policy.allowed_name_regex must be non-empty"]
    try:
        allowed_re = re.compile(allowed_name_regex)
    except re.error as exc:
        return [f"harness.filename_policy.allowed_name_regex invalid: {exc}"]

    for rel_root in paths:
        base = _join_contract_path(root, rel_root)
        if not base.exists():
            violations.append(f"{rel_root}:1: missing path for filename policy scan")
            continue
        if not base.is_dir():
            violations.append(f"{rel_root}:1: expected directory for filename policy scan")
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            if include_exts_set and p.suffix.lower() not in include_exts_set:
                continue
            name = p.name
            if name in allow_exact_set:
                continue
            if not allowed_re.fullmatch(name):
                rel = p.relative_to(root)
                violations.append(
                    f"{rel}: filename {name!r} must match {allowed_name_regex} "
                    "(lowercase words with '_' for spaces and '-' for section separators)"
                )
    return violations


def _scan_normalization_virtual_root_paths_only(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    scope = [
        root / "specs/conformance/cases",
        root / "specs/governance/cases",
        root / "specs/libraries",
    ]
    for base in scope:
        if not base.exists():
            continue
        for doc_path, case in _iter_all_spec_cases(base):
            rel = doc_path.relative_to(root)
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            for field, raw in _iter_path_fields(case):
                s = str(raw).strip()
                if not s or s.startswith("external://"):
                    continue
                try:
                    normalized = normalize_contract_path(s, field=f"{case_id}.{field}")
                except VirtualPathError:
                    violations.append(f"{rel}: case {case_id} has invalid virtual path at {field}: {s}")
                    continue
                if s != normalized:
                    violations.append(
                        f"{rel}: case {case_id} non-canonical path at {field}: {s!r} -> {normalized!r}"
                    )
    return violations


def _scan_reference_contract_paths_exist(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    scope = [
        root / "specs/conformance/cases",
        root / "specs/governance/cases",
        root / "specs/libraries",
    ]
    must_exist_keys = {
        "path",
        "includes",
        "cases_path",
        "baseline_path",
        "manifest_path",
        "required_paths",
        "adapter_path",
        "cli_main_path",
        "required_library_path",
        "reference_manifest",
    }
    for base in scope:
        if not base.exists():
            continue
        for doc_path, case in _iter_all_spec_cases(base):
            rel = doc_path.relative_to(root)
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            for field, raw in _iter_path_fields(case):
                if field.split(".")[-1].split("[", 1)[0] not in must_exist_keys:
                    continue
                if (
                    (".exports." in field or ".exports[" in field or ".imports." in field or ".imports[" in field)
                    and field.endswith(".path")
                ):
                    continue
                s = str(raw).strip()
                if not s or s.startswith("external://"):
                    continue
                try:
                    p = _resolve_contract_config_path(root, s, field=field)
                except VirtualPathError:
                    violations.append(f"{rel}: case {case_id} has invalid path at {field}: {s}")
                    continue
                if not p.exists():
                    violations.append(f"{rel}: case {case_id} references missing path at {field}: {s}")
    return violations


def _scan_reference_check_ids_exist(root: Path, *, harness: dict | None = None) -> list[str]:
    cases_dir = root / "specs/governance/cases"
    if not cases_dir.exists():
        return []
    violations: list[str] = []
    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case_id = str(spec.test.get("id", "<unknown>")).strip() or "<unknown>"
        check_id = str(spec.test.get("check", "")).strip()
        try:
            rel_doc = spec.doc_path.relative_to(root)
        except ValueError:
            rel_doc = Path(spec.doc_path)
        if not check_id:
            violations.append(f"{rel_doc}: case {case_id} missing check id")
            continue
        if check_id not in _CHECKS:
            violations.append(f"{rel_doc}: case {case_id} unknown check id: {check_id}")
    return violations


def _scan_reference_symbols_exist(root: Path, *, harness: dict | None = None) -> list[str]:
    cases_dir = root / "specs/governance/cases"
    if not cases_dir.exists():
        return []
    violations: list[str] = []
    limits = SpecLangLimits()
    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        harness_map = spec.test.get("harness")
        if not isinstance(harness_map, dict):
            continue
        spec_lang_cfg = harness_map.get("spec_lang")
        if not isinstance(spec_lang_cfg, dict):
            continue
        if not spec_lang_cfg.get("includes"):
            continue
        try:
            load_spec_lang_symbols_for_case(
                doc_path=spec.doc_path,
                harness=harness_map,
                limits=limits,
            )
        except Exception as exc:  # noqa: BLE001
            case_id = str(spec.test.get("id", "<unknown>")).strip() or "<unknown>"
            violations.append(
                f"{spec.doc_path.relative_to(root)}: case {case_id} library symbol/path reference error ({exc})"
            )
    return violations


def _collect_var_symbols(expr: object) -> set[str]:
    out: set[str] = set()
    if isinstance(expr, dict):
        raw_var = expr.get("var")
        if isinstance(raw_var, str):
            sym = raw_var.strip()
            if sym:
                out.add(sym)
        for value in expr.values():
            out.update(_collect_var_symbols(value))
        return out
    if isinstance(expr, list):
        for value in expr:
            out.update(_collect_var_symbols(value))
    return out


def _iter_evaluate_expr_nodes(assert_node: object) -> list[object]:
    out: list[object] = []
    if isinstance(assert_node, list):
        for child in assert_node:
            out.extend(_iter_evaluate_expr_nodes(child))
        return out
    if not isinstance(assert_node, dict):
        return out
    step_class = str(assert_node.get("class", "")).strip() if "class" in assert_node else ""
    if step_class in {"MUST", "MAY", "MUST_NOT"} and "asserts" in assert_node:
        raw_checks = assert_node.get("asserts")
        if isinstance(raw_checks, list):
            for child in raw_checks:
                out.extend(_iter_evaluate_expr_nodes(child))
        return out
    for key in ("MUST", "MAY", "MUST_NOT"):
        raw_children = assert_node.get(key)
        if isinstance(raw_children, list):
            for child in raw_children:
                out.extend(_iter_evaluate_expr_nodes(child))
    raw_eval = assert_node.get("evaluate")
    if isinstance(raw_eval, list):
        out.extend(raw_eval)
        return out
    if "target" in assert_node:
        return out
    if assert_node:
        out.append(assert_node)
    return out


def _collect_global_symbol_references(root: Path) -> set[str]:
    with _SCAN_CACHE_LOCK:
        cache_key = (_SCAN_CACHE_TOKEN, str(root.resolve()))
        cached = _GLOBAL_SYMBOL_REFERENCES_CACHE.get(cache_key)
    if cached is not None:
        return set(cached)

    referenced: set[str] = set()
    scan_roots = [
        root / "specs/conformance/cases",
        root / "specs/governance/cases",
        root / "specs/impl",
        root / "specs/libraries",
    ]
    for base in scan_roots:
        if not base.exists():
            continue
        for _doc_path, case in _iter_all_spec_cases(base):
            h = case.get("harness")
            if isinstance(h, dict):
                spec_lang = h.get("spec_lang")
                if isinstance(spec_lang, dict):
                    raw_exports = spec_lang.get("exports")
                    if isinstance(raw_exports, list):
                        for raw in raw_exports:
                            sym = str(raw).strip()
                            if sym and "." in sym:
                                referenced.add(sym)
                chain = h.get("chain")
                if isinstance(chain, dict):
                    raw_imports = chain.get("imports")
                    if isinstance(raw_imports, list):
                        for item in raw_imports:
                            if not isinstance(item, dict):
                                continue
                            names = item.get("names")
                            if isinstance(names, list):
                                for raw_name in names:
                                    sym = str(raw_name).strip()
                                    if sym and "." in sym:
                                        referenced.add(sym)
                            aliases = item.get("as")
                            if isinstance(aliases, dict):
                                for raw_alias in aliases.values():
                                    sym = str(raw_alias).strip()
                                    if sym and "." in sym:
                                        referenced.add(sym)
                policy = h.get("evaluate")
                if isinstance(policy, list):
                    referenced.update(sym for sym in _collect_var_symbols(policy) if "." in sym)
            raw_assert = case.get("contract")
            if isinstance(raw_assert, list):
                for expr in _iter_evaluate_expr_nodes(raw_assert):
                    referenced.update(sym for sym in _collect_var_symbols(expr) if "." in sym)
            if str(case.get("type", "")).strip() == "spec_lang.export":
                raw_defines = case.get("defines")
                if isinstance(raw_defines, dict):
                    for scope in ("public", "private"):
                        scoped = raw_defines.get(scope)
                        if isinstance(scoped, dict):
                            for expr in scoped.values():
                                referenced.update(sym for sym in _collect_var_symbols(expr) if "." in sym)
    with _SCAN_CACHE_LOCK:
        _GLOBAL_SYMBOL_REFERENCES_CACHE[cache_key] = set(referenced)
    return referenced


def _scan_reference_policy_symbols_resolve(root: Path, *, harness: dict | None = None) -> list[str]:
    cases_dir = root / "specs/governance/cases"
    if not cases_dir.exists():
        return []
    limits = SpecLangLimits()
    violations: list[str] = []
    for spec in iter_cases(cases_dir, file_pattern=SETTINGS.case.default_file_pattern):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "governance.check":
            continue
        case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
        harness_map = case.get("harness")
        if not isinstance(harness_map, dict):
            continue
        policy = harness_map.get("evaluate")
        if not isinstance(policy, list) or not policy:
            continue
        policy_refs = {sym for sym in _collect_var_symbols(policy) if "." in sym}
        if not policy_refs:
            continue
        symbols: dict[str, object] = {}
        try:
            symbols.update(
                load_spec_lang_symbols_for_case(
                    doc_path=spec.doc_path,
                    harness=harness_map,
                    limits=limits,
                )
            )
        except Exception as exc:  # noqa: BLE001
            violations.append(
                f"{_rel_path(root, spec.doc_path)}: case {case_id} unable to load policy symbols ({exc})"
            )
            continue
        try:
            symbols.update(
                _load_chain_imported_symbol_bindings(
                    root,
                    doc_path=spec.doc_path,
                    case=case,
                    limits=limits,
                )
            )
        except Exception as exc:  # noqa: BLE001
            violations.append(
                f"{_rel_path(root, spec.doc_path)}: case {case_id} unable to load chain-imported symbols ({exc})"
            )
            continue
        unresolved = sorted(sym for sym in policy_refs if sym not in symbols)
        if unresolved:
            violations.append(
                f"{_rel_path(root, spec.doc_path)}: case {case_id} unresolved policy symbols: "
                + ", ".join(unresolved)
            )
    return violations


def _scan_reference_library_exports_used(root: Path, *, harness: dict | None = None) -> list[str]:
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return []
    exported: dict[str, Path] = {}
    violations: list[str] = []
    for lib_file in sorted(libs_root.rglob(SETTINGS.case.default_file_pattern)):
        if not lib_file.is_file():
            continue
        try:
            loaded = load_external_cases(lib_file, formats={"md"})
        except Exception as exc:  # noqa: BLE001
            violations.append(f"{lib_file.relative_to(root)}: unable to parse library file ({exc})")
            continue
        for _doc_path, case in loaded:
            if str(case.get("type", "")).strip() != "spec_lang.export":
                continue
            raw_defines = case.get("defines")
            if not isinstance(raw_defines, dict):
                continue
            raw_public = raw_defines.get("public")
            if not isinstance(raw_public, dict):
                continue
            for raw in raw_public.keys():
                sym = str(raw).strip()
                if not sym:
                    continue
                prior = exported.get(sym)
                if prior is not None and prior != lib_file:
                    violations.append(
                        f"{lib_file.relative_to(root)}: duplicate export symbol '{sym}' also exported by {prior.relative_to(root)}"
                    )
                    continue
                exported[sym] = lib_file
    if violations:
        return violations

    referenced = _collect_global_symbol_references(root)

    for sym, src in sorted(exported.items(), key=lambda item: item[0]):
        if sym not in referenced:
            violations.append(
                f"{src.relative_to(root)}: exported symbol '{sym}' is not referenced by any case policy/expression or harness.spec_lang.exports"
            )
    return violations


def _scan_library_public_surface_model(root: Path, *, harness: dict | None = None) -> list[str]:
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return []
    violations: list[str] = []
    for lib_file in sorted(libs_root.rglob(SETTINGS.case.default_file_pattern)):
        if not lib_file.is_file():
            continue
        try:
            loaded = load_external_cases(lib_file, formats={"md"})
        except Exception as exc:  # noqa: BLE001
            violations.append(f"{lib_file.relative_to(root)}: unable to parse library file ({exc})")
            continue
        for _doc_path, case in loaded:
            if str(case.get("type", "")).strip() != "spec_lang.export":
                continue
            raw_defines = case.get("defines")
            if not isinstance(raw_defines, dict):
                violations.append(
                    f"{lib_file.relative_to(root)}: spec_lang.export requires defines mapping"
                )
                continue
            raw_public = raw_defines.get("public")
            raw_private = raw_defines.get("private")
            if not isinstance(raw_public, dict) and not isinstance(raw_private, dict):
                violations.append(
                    f"{lib_file.relative_to(root)}: spec_lang.export requires defines.public or defines.private mapping"
                )
                continue
            public_symbols: set[str] = set()
            private_symbols: set[str] = set()
            if isinstance(raw_public, dict):
                public_symbols.update(str(k).strip() for k in raw_public)
            if isinstance(raw_private, dict):
                private_symbols.update(str(k).strip() for k in raw_private)
            if public_symbols and private_symbols:
                overlap = sorted(public_symbols.intersection(private_symbols))
                overlap = [s for s in overlap if s]
                if overlap:
                    violations.append(
                        f"{lib_file.relative_to(root)}: duplicate symbol across defines.public/defines.private: "
                        + ", ".join(overlap)
                    )
    return violations


def _scan_library_legacy_definitions_key_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return []
    violations: list[str] = []
    for lib_file in sorted(libs_root.rglob(SETTINGS.case.default_file_pattern)):
        if not lib_file.is_file():
            continue
        try:
            loaded = load_external_cases(lib_file, formats={"md"})
        except Exception as exc:  # noqa: BLE001
            violations.append(f"{lib_file.relative_to(root)}: unable to parse library file ({exc})")
            continue
        for _doc_path, case in loaded:
            if str(case.get("type", "")).strip() != "spec_lang.export":
                continue
            if "definitions" in case:
                violations.append(
                    f"{lib_file.relative_to(root)}: spec_lang.export legacy key 'definitions' is forbidden; use 'defines'"
                )
    return violations


def _scan_library_verb_first_schema_keys_required(root: Path, *, harness: dict | None = None) -> list[str]:
    violations = _scan_library_public_surface_model(root, harness=harness)
    violations.extend(_scan_library_legacy_definitions_key_forbidden(root, harness=harness))
    return violations


def _scan_schema_verb_first_contract_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    del harness
    checks: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
        (
            "specs/contract/14_spec_lang_libraries.md",
            ("type: spec.export", "harness.exports", "from: assert.function"),
            ("type: spec_lang.export", "defines.public", "defines.private", "definitions.public", "definitions.private"),
        ),
        (
            "specs/schema/schema_v1.md",
            ("`spec.export`", "`harness.exports`", "`assert.function`"),
            ("`spec_lang.export`", "`defines`", "`definitions`", "definitions.public", "definitions.private"),
        ),
        (
            "specs/current.md",
            ("spec.export", "harness.exports"),
            ("spec_lang.export", "defines.public", "defines.private", "definitions.public", "definitions.private"),
        ),
    )
    violations: list[str] = []
    for rel, required_tokens, forbidden_tokens in checks:
        p = root / rel
        if not p.exists():
            violations.append(f"{rel}:1: missing file")
            continue
        raw = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in raw:
                violations.append(f"{rel}:1: missing required token {tok!r}")
        for tok in forbidden_tokens:
            if tok in raw:
                line = raw[: raw.find(tok)].count("\n") + 1
                violations.append(f"{rel}:{line}: forbidden legacy token present: {tok!r}")
    return violations


def _scan_reference_private_symbols_forbidden(root: Path, *, harness: dict | None = None) -> list[str]:
    libs_root = root / "specs/libraries"
    private_symbols: set[str] = set()
    if libs_root.exists():
        for lib_file in sorted(libs_root.rglob(SETTINGS.case.default_file_pattern)):
            if not lib_file.is_file():
                continue
            try:
                loaded = load_external_cases(lib_file, formats={"md"})
            except Exception:
                continue
            for _doc_path, case in loaded:
                if str(case.get("type", "")).strip() != "spec_lang.export":
                    continue
                raw_defines = case.get("defines")
                if not isinstance(raw_defines, dict):
                    continue
                raw_private = raw_defines.get("private")
                if not isinstance(raw_private, dict):
                    continue
                for sym in raw_private.keys():
                    s = str(sym).strip()
                    if s:
                        private_symbols.add(s)
    if not private_symbols:
        return []

    violations: list[str] = []
    scan_roots = [
        root / "specs/conformance/cases",
        root / "specs/governance/cases",
        root / "specs/impl",
    ]
    for base in scan_roots:
        if not base.exists():
            continue
        for doc_path, case in _iter_all_spec_cases(base):
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            rel = doc_path.relative_to(root)
            refs: set[str] = set()
            h = case.get("harness")
            if isinstance(h, dict):
                policy = h.get("evaluate")
                if isinstance(policy, list):
                    refs.update(sym for sym in _collect_var_symbols(policy) if "." in sym)
                spec_lang = h.get("spec_lang")
                if isinstance(spec_lang, dict):
                    raw_exports = spec_lang.get("exports")
                    if isinstance(raw_exports, list):
                        for raw in raw_exports:
                            sym = str(raw).strip()
                            if sym and "." in sym:
                                refs.add(sym)
            raw_assert = case.get("contract")
            if isinstance(raw_assert, list):
                for expr in _iter_evaluate_expr_nodes(raw_assert):
                    refs.update(sym for sym in _collect_var_symbols(expr) if "." in sym)
            bad = sorted(sym for sym in refs if sym in private_symbols)
            if bad:
                violations.append(
                    f"{rel}: case {case_id} references private library symbols: " + ", ".join(bad)
                )
    return violations


def _scan_reference_external_refs_policy(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    scope = [
        root / "specs/conformance/cases",
        root / "specs/governance/cases",
        root / "specs/libraries",
    ]
    for base in scope:
        if not base.exists():
            continue
        for doc_path, case in _iter_all_spec_cases(base):
            rel = doc_path.relative_to(root)
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            requires = dict(case.get("requires") or {})
            caps = set(str(x).strip() for x in (requires.get("capabilities") or []) if str(x).strip())
            h = dict(case.get("harness") or {})
            spec_lang_cfg = dict(h.get("spec_lang") or {})
            ext_cfg = dict(spec_lang_cfg.get("references") or {})
            mode = str(ext_cfg.get("mode", "deny")).strip().lower() or "deny"
            providers = set(
                str(x).strip() for x in (ext_cfg.get("providers") or []) if str(x).strip()
            )
            for field, raw in _iter_path_fields(case):
                ext = parse_external_ref(str(raw).strip())
                if ext is None:
                    continue
                if "external.ref.v1" not in caps:
                    violations.append(
                        f"{rel}: case {case_id} external ref at {field} requires capabilities including external.ref.v1"
                    )
                if mode != "allow":
                    violations.append(
                        f"{rel}: case {case_id} external ref at {field} requires harness.spec_lang.references.mode=allow"
                    )
                if ext.provider not in providers:
                    violations.append(
                        f"{rel}: case {case_id} external provider {ext.provider} not allowlisted at {field}"
                    )
    return violations


def _scan_reference_token_anchors_exist(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("token_anchors")
    if cfg is None:
        return []
    if not isinstance(cfg, dict):
        return ["reference.token_anchors_exist requires harness.token_anchors mapping in governance spec"]
    files = cfg.get("files")
    if not isinstance(files, list):
        return ["harness.token_anchors.files must be a list"]
    violations: list[str] = []
    for idx, entry in enumerate(files):
        if not isinstance(entry, dict):
            violations.append(f"harness.token_anchors.files[{idx}] must be a mapping")
            continue
        rel = str(entry.get("path", "")).strip()
        tokens = entry.get("tokens")
        if not rel:
            violations.append(f"harness.token_anchors.files[{idx}].path must be non-empty")
            continue
        if not isinstance(tokens, list) or any(not isinstance(t, str) or not t.strip() for t in tokens):
            violations.append(f"harness.token_anchors.files[{idx}].tokens must be a list of non-empty strings")
            continue
        try:
            p = _resolve_contract_config_path(root, rel, field=f"token_anchors.files[{idx}].path")
        except VirtualPathError as exc:
            violations.append(str(exc))
            continue
        if not p.exists():
            violations.append(f"{rel}:1: token anchor file does not exist")
            continue
        text = p.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                violations.append(f"{rel}:1: missing token anchor {token!r}")
    return violations


def _scan_spec_layout_domain_trees(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    for rel_root in _DOMAIN_TREE_ROOTS:
        base = _join_contract_path(root, rel_root)
        if not base.exists():
            violations.append(f"{rel_root}:1: missing required domain root")
            continue
        if not base.is_dir():
            violations.append(f"{rel_root}:1: expected directory")
            continue
        direct_cases = sorted(p for p in base.glob(SETTINGS.case.default_file_pattern) if p.is_file())
        for p in direct_cases:
            violations.append(
                f"{p.relative_to(root)}: spec files must live under domain subdirectories (for example {rel_root}/core/)"
            )
        domain_dirs = sorted(
            p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")
        )
        if not domain_dirs:
            violations.append(f"{rel_root}:1: expected at least one domain subdirectory")
            continue
        for domain_dir in domain_dirs:
            has_specs = any(domain_dir.rglob(SETTINGS.case.default_file_pattern))
            if not has_specs:
                continue
            index_path = domain_dir / "index.md"
            if not index_path.exists():
                violations.append(
                    f"{index_path.relative_to(root)}: missing required domain index.md"
                )
    return violations


def _scan_spec_taxonomy_hard_cut_required(root: Path, *, harness: dict | None = None) -> list[str]:
    h = harness or {}
    cfg = h.get("taxonomy_layout")
    if not isinstance(cfg, dict):
        return ["spec.taxonomy_hard_cut_required requires harness.taxonomy_layout mapping in governance spec"]
    required_paths = cfg.get("required_paths", [])
    forbidden_paths = cfg.get("forbidden_paths", [])
    if (
        not isinstance(required_paths, list)
        or any(not isinstance(x, str) or not x.strip() for x in required_paths)
    ):
        return ["harness.taxonomy_layout.required_paths must be a list of non-empty strings"]
    if (
        not isinstance(forbidden_paths, list)
        or any(not isinstance(x, str) or not x.strip() for x in forbidden_paths)
    ):
        return ["harness.taxonomy_layout.forbidden_paths must be a list of non-empty strings"]
    violations: list[str] = []
    for rel in required_paths:
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: missing required canonical taxonomy path")
    for rel in forbidden_paths:
        p = _join_contract_path(root, rel)
        if p.exists():
            violations.append(f"{rel}:1: forbidden legacy taxonomy path exists")
    return violations


def _scan_spec_domain_index_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    for rel_root in _DOMAIN_TREE_ROOTS:
        base = _join_contract_path(root, rel_root)
        if not base.exists() or not base.is_dir():
            continue
        domain_dirs = sorted(
            p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")
        )
        for domain_dir in domain_dirs:
            spec_files = sorted(p for p in domain_dir.glob(SETTINGS.case.default_file_pattern) if p.is_file())
            if not spec_files:
                continue
            index_path = domain_dir / "index.md"
            if not index_path.exists():
                continue
            raw = index_path.read_text(encoding="utf-8")
            for p in spec_files:
                rel = "/" + p.relative_to(root).as_posix()
                if rel not in raw:
                    violations.append(
                        f"{index_path.relative_to(root)}: missing indexed path: {rel}"
                    )
            # Ensure stale entries are not retained.
            for m in re.finditer(r"`(/specs/[^`]+\.spec\.md)`", raw):
                rel = m.group(1)
                target = _join_contract_path(root, rel)
                if not target.exists():
                    line = raw[: m.start()].count("\n") + 1
                    violations.append(
                        f"{index_path.relative_to(root)}:{line}: stale indexed path missing from tree: {rel}"
                    )
    return violations


def _scan_library_domain_ownership(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    # Conformance cases: conformance libraries only.
    conformance_root = root / "specs/conformance/cases"
    if conformance_root.exists():
        for doc_path, case in _iter_all_spec_cases(conformance_root):
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            h = case.get("harness")
            if not isinstance(h, dict):
                continue
            libs = _collect_chain_library_refs(case)
            for idx, raw in enumerate(libs):
                s = str(raw).strip()
                if not s or s.startswith("external://"):
                    continue
                try:
                    normalized = normalize_contract_path(
                        s, field=f"{case_id}.harness.chain.steps[{idx}].ref"
                    )
                except VirtualPathError:
                    continue
                if not (
                    normalized.startswith("/specs/libraries/conformance/")
                    or normalized.startswith("/specs/libraries/domain/")
                ):
                    rel = doc_path.relative_to(root)
                    violations.append(
                        f"{rel}: case {case_id} includes[{idx}] must be under "
                        "/specs/libraries/conformance/ or /specs/libraries/domain/"
                    )

    # Governance cases: policy/path libraries only.
    governance_root = root / "specs/governance/cases"
    if governance_root.exists():
        for doc_path, case in _iter_all_spec_cases(governance_root):
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            h = case.get("harness")
            if not isinstance(h, dict):
                continue
            libs = _collect_chain_library_refs(case)
            for idx, raw in enumerate(libs):
                s = str(raw).strip()
                if not s or s.startswith("external://"):
                    continue
                try:
                    normalized = normalize_contract_path(
                        s, field=f"{case_id}.harness.chain.steps[{idx}].ref"
                    )
                except VirtualPathError:
                    continue
                allowed = (
                    normalized.startswith("/specs/libraries/policy/")
                    or normalized.startswith("/specs/libraries/path/")
                )
                if not allowed:
                    rel = doc_path.relative_to(root)
                    violations.append(
                        f"{rel}: case {case_id} includes[{idx}] must be under "
                        "/specs/libraries/policy/ or /specs/libraries/path/"
                    )
    return violations


def _scan_library_domain_index_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return ["specs/libraries:1: missing libraries root"]

    for domain_dir in sorted(p for p in libs_root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        spec_files = sorted(p for p in domain_dir.glob(SETTINGS.case.default_file_pattern) if p.is_file())
        if not spec_files:
            continue
        index_path = domain_dir / "index.md"
        if not index_path.exists():
            violations.append(f"{index_path.relative_to(root)}: missing required domain index.md")
            continue
        raw = index_path.read_text(encoding="utf-8")
        if "## Exported Symbols" not in raw:
            violations.append(f"{index_path.relative_to(root)}: missing '## Exported Symbols' section")
        for p in spec_files:
            rel = "/" + p.relative_to(root).as_posix()
            if rel not in raw:
                violations.append(f"{index_path.relative_to(root)}: missing indexed path: {rel}")
            try:
                loaded = load_external_cases(p, formats={"md"})
            except Exception as exc:  # noqa: BLE001
                violations.append(f"{p.relative_to(root)}: unable to parse library file ({exc})")
                continue
            exports: list[str] = []
            for _doc_path, case in loaded:
                if str(case.get("type", "")).strip() != "spec_lang.export":
                    continue
                raw_defines = case.get("defines")
                if not isinstance(raw_defines, dict):
                    continue
                raw_public = raw_defines.get("public")
                if not isinstance(raw_public, dict):
                    continue
                for item in raw_public.keys():
                    sym = str(item).strip()
                    if sym:
                        exports.append(sym)
            for sym in sorted(dict.fromkeys(exports)):
                token = f"`{sym}` ({rel})"
                if token not in raw:
                    violations.append(
                        f"{index_path.relative_to(root)}: missing exported symbol entry {token}"
                    )
        for m in re.finditer(r"`(/specs/libraries/[^`]+\.spec\.md)`", raw):
            rel = m.group(1)
            target = _join_contract_path(root, rel)
            if not target.exists():
                line = raw[: m.start()].count("\n") + 1
                violations.append(
                    f"{index_path.relative_to(root)}:{line}: stale indexed path missing from tree: {rel}"
                )
    return violations


def _load_normalization_profile(root: Path) -> tuple[dict[str, object] | None, list[str]]:
    p = root / _NORMALIZATION_PROFILE_PATH
    if not p.exists():
        return None, [f"{_NORMALIZATION_PROFILE_PATH}:1: missing normalization profile"]
    try:
        payload = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [f"{_NORMALIZATION_PROFILE_PATH}:1: invalid yaml ({exc})"]
    if not isinstance(payload, dict):
        return None, [f"{_NORMALIZATION_PROFILE_PATH}:1: profile must be a mapping"]
    return payload, []


def _scan_normalization_profile_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    profile, errs = _load_normalization_profile(root)
    if errs:
        return errs
    assert profile is not None
    violations: list[str] = []
    required_top = ("version", "paths", "docs_layout", "expression", "spec_style", "docs_token_sync")
    for key in required_top:
        if key not in profile:
            violations.append(f"{_NORMALIZATION_PROFILE_PATH}:1: missing required key: {key}")
    paths = profile.get("paths")
    if not isinstance(paths, dict):
        violations.append(f"{_NORMALIZATION_PROFILE_PATH}:1: paths must be a mapping")
    else:
        for key in ("specs", "contracts", "tests"):
            vals = paths.get(key)
            if not isinstance(vals, list) or not vals or any(not isinstance(x, str) or not x.strip() for x in vals):
                violations.append(f"{_NORMALIZATION_PROFILE_PATH}:1: paths.{key} must be a non-empty list of strings")
    docs_layout = profile.get("docs_layout")
    if not isinstance(docs_layout, dict):
        violations.append(f"{_NORMALIZATION_PROFILE_PATH}:1: docs_layout must be a mapping")
    else:
        for key in ("profile_path", "canonical_roots", "forbidden_roots", "index_filename", "required_index_dirs", "forbidden_filenames"):
            if key not in docs_layout:
                violations.append(f"{_NORMALIZATION_PROFILE_PATH}:1: docs_layout missing required key: {key}")
    expr = profile.get("expression")
    if not isinstance(expr, dict):
        violations.append(f"{_NORMALIZATION_PROFILE_PATH}:1: expression must be a mapping")
    else:
        fields = expr.get("expression_fields")
        if not isinstance(fields, list) or "evaluate" not in fields or "evaluate" not in fields:
            violations.append(
                f"{_NORMALIZATION_PROFILE_PATH}:1: expression.expression_fields must include evaluate and evaluate"
            )
    return violations


def _run_normalize_check_cached(root: Path, *, scope: str) -> tuple[int, list[str]]:
    with _SCAN_CACHE_LOCK:
        cache_key = (_SCAN_CACHE_TOKEN, str(root.resolve()), scope)
        cached = _NORMALIZE_CHECK_CACHE.get(cache_key)
    if cached is not None:
        return cached
    cmd = [sys.executable, "-m", "spec_runner.spec_lang_commands", "normalize-repo", "--check", "--scope", scope]
    try:
        proc = _profiled_subprocess_run(
            cmd,
            cwd=root,
            phase="governance.normalize_check",
        )
        out = (proc.stdout or "").splitlines() + (proc.stderr or "").splitlines()
        violations = [line.strip() for line in out if line.strip()]
        result = (int(proc.returncode), violations)
    except LivenessError as exc:
        result = (
            124,
            [
                "spec_runner.spec_lang_commands normalize-repo --check failed liveness watchdog: "
                f"{exc.reason_token}"
            ],
        )
    with _SCAN_CACHE_LOCK:
        _NORMALIZE_CHECK_CACHE[cache_key] = result
    return result


def _scan_normalization_mapping_ast_only(root: Path, *, harness: dict | None = None) -> list[str]:
    code, violations = _run_normalize_check_cached(root, scope="all")
    if code == 0:
        return []
    return violations or ["normalization.mapping_ast_only: normalize check failed"]


def _scan_normalization_library_mapping_ast_only(root: Path, *, harness: dict | None = None) -> list[str]:
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return []
    violations: list[str] = []
    for p in sorted(libs_root.rglob(SETTINGS.case.default_file_pattern)):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        try:
            specs = list(iter_spec_doc_tests(p.parent, file_pattern=p.name))
        except Exception as exc:  # noqa: BLE001
            violations.append(f"{rel}:1: unable to parse library spec file: {exc}")
            continue
        for spec in specs:
            case = spec.test
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            if str(case.get("type", "")).strip() != "spec_lang.export":
                continue
            defines = case.get("defines")
            if not isinstance(defines, dict) or not defines:
                violations.append(f"{rel}: case {case_id} must provide non-empty defines mapping")
                continue
            scopes = []
            raw_public = defines.get("public")
            raw_private = defines.get("private")
            if isinstance(raw_public, dict):
                scopes.append(("public", raw_public))
            if isinstance(raw_private, dict):
                scopes.append(("private", raw_private))
            if not scopes:
                violations.append(
                    f"{rel}: case {case_id} must provide defines.public or defines.private mapping"
                )
                continue
            for scope_name, scoped_map in scopes:
                for raw_name, expr in scoped_map.items():
                    name = str(raw_name).strip()
                    if not name:
                        violations.append(
                            f"{rel}: case {case_id} has empty symbol name in defines.{scope_name}"
                        )
                        continue
                    try:
                        compile_yaml_expr_to_sexpr(
                            expr,
                            field_path=(
                                f"{rel.as_posix()} case {case_id} "
                                f"defines.{scope_name}.{name}"
                            ),
                        )
                    except SpecLangYamlAstError as exc:
                        violations.append(str(exc))
    return violations


def _scan_normalization_docs_token_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    profile, errs = _load_normalization_profile(root)
    if errs:
        return errs
    assert profile is not None
    token_sync = profile.get("docs_token_sync")
    if not isinstance(token_sync, dict):
        return [f"{_NORMALIZATION_PROFILE_PATH}:1: docs_token_sync must be a mapping"]
    rules = token_sync.get("rules")
    if not isinstance(rules, list):
        return [f"{_NORMALIZATION_PROFILE_PATH}:1: docs_token_sync.rules must be a list"]
    violations: list[str] = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rid = str(rule.get("id", "NORMALIZATION_DOC_TOKEN_SYNC")).strip() or "NORMALIZATION_DOC_TOKEN_SYNC"
        rel = str(rule.get("file", "")).strip()
        if not rel:
            continue
        p = _join_contract_path(root, rel)
        if not p.exists():
            violations.append(f"{rel}:1: {rid}: missing file")
            continue
        text = p.read_text(encoding="utf-8")
        must = rule.get("must_contain", [])
        must_not = rule.get("must_not_contain", [])
        if isinstance(must, list):
            for tok in must:
                if isinstance(tok, str) and tok and tok not in text:
                    violations.append(f"{rel}:1: {rid}: missing token: {tok}")
        if isinstance(must_not, list):
            for tok in must_not:
                if isinstance(tok, str) and tok and tok in text:
                    line = text[: text.find(tok)].count("\n") + 1
                    violations.append(f"{rel}:{line}: {rid}: forbidden token present: {tok}")
    return violations


def _scan_normalization_spec_style_sync(root: Path, *, harness: dict | None = None) -> list[str]:
    profile, errs = _load_normalization_profile(root)
    if errs:
        return errs
    assert profile is not None
    style = profile.get("spec_style")
    if not isinstance(style, dict):
        return [f"{_NORMALIZATION_PROFILE_PATH}:1: spec_style must be a mapping"]
    max_lines = style.get("conformance_max_block_lines")
    if not isinstance(max_lines, int) or max_lines < 1:
        return [f"{_NORMALIZATION_PROFILE_PATH}:1: spec_style.conformance_max_block_lines must be a positive int"]

    violations: list[str] = []
    if _CONFORMANCE_MAX_BLOCK_LINES != max_lines:
        violations.append(
            "runners/python/spec_runner/governance_runtime.py:1: NORMALIZATION_SPEC_STYLE_SYNC: "
            f"_CONFORMANCE_MAX_BLOCK_LINES={_CONFORMANCE_MAX_BLOCK_LINES} must match profile value {max_lines}"
        )

    style_doc = root / "specs/conformance/style.md"
    if not style_doc.exists():
        violations.append("specs/conformance/style.md:1: NORMALIZATION_SPEC_STYLE_SYNC: missing style doc")
        return violations
    raw = style_doc.read_text(encoding="utf-8")
    expected_token = f"({max_lines} lines max)"
    if expected_token not in raw:
        violations.append(
            f"specs/conformance/style.md:1: NORMALIZATION_SPEC_STYLE_SYNC: missing block-size token {expected_token}"
        )
    required_style_tokens = (
        "block-first multiline expression formatting",
        "flow style is reserved for trivial atoms only",
        "nested operator arguments must remain multiline",
    )
    lower = raw.lower()
    for tok in required_style_tokens:
        if tok not in lower:
            violations.append(
                f"specs/conformance/style.md:1: NORMALIZATION_SPEC_STYLE_SYNC: missing readability token {tok!r}"
            )
    if "flow-sequence" in raw:
        line = raw[: raw.find("flow-sequence")].count("\n") + 1
        violations.append(
            f"specs/conformance/style.md:{line}: NORMALIZATION_SPEC_STYLE_SYNC: forbidden legacy token flow-sequence"
        )
    return violations


def _iter_non_md_executable_spec_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for rel_root in _EXECUTABLE_CASE_TREE_ROOTS:
        base = _join_contract_path(root, rel_root)
        if not base.exists() or not base.is_dir():
            continue
        for pattern in _EXECUTABLE_NON_MD_SPEC_GLOBS:
            files.extend(sorted(p for p in base.rglob(pattern) if p.is_file()))
    return files


def _scan_spec_executable_surface_markdown_only(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    for p in _iter_non_md_executable_spec_files(root):
        rel = p.relative_to(root).as_posix()
        violations.append(
            f"{rel}: executable surfaces must use .spec.md markdown case files only"
        )
    return violations


def _scan_spec_no_executable_yaml_json_in_case_trees(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    for p in _iter_non_md_executable_spec_files(root):
        rel = p.relative_to(root).as_posix()
        violations.append(
            f"{rel}: runnable .spec.yaml/.spec.yml/.spec.json is forbidden in canonical executable case trees"
        )
    return violations


def _scan_spec_library_cases_markdown_only(root: Path, *, harness: dict | None = None) -> list[str]:
    libs_root = root / "specs/libraries"
    if not libs_root.exists():
        return ["specs/libraries:1: missing libraries root"]
    violations: list[str] = []
    for pattern in _EXECUTABLE_NON_MD_SPEC_GLOBS:
        for p in sorted(x for x in libs_root.rglob(pattern) if x.is_file()):
            rel = p.relative_to(root).as_posix()
            violations.append(
                f"{rel}: spec_lang library cases must be authored in .spec.md"
            )
    return violations


def _scan_spec_generated_data_artifacts_not_embedded_in_spec_blocks(
    root: Path, *, harness: dict | None = None
) -> list[str]:
    violations: list[str] = []
    for glob in _DATA_ARTIFACT_GLOBS:
        for p in sorted(root.glob(glob)):
            if not p.is_file():
                continue
            text = p.read_text(encoding="utf-8")
            if "```yaml contract-spec" in text:
                rel = p.relative_to(root).as_posix()
                line = text[: text.find("```yaml contract-spec")].count("\n") + 1
                violations.append(
                    f"{rel}:{line}: data artifact surfaces must not embed executable contract-spec blocks"
                )
    return violations


def _scan_tests_unit_opt_out_non_regression(root: Path, *, harness: dict | None = None) -> list[str]:
    violations: list[str] = []
    tests_root = root / "tests"
    baseline_path = root / _UNIT_TEST_OPT_OUT_BASELINE_PATH
    if not tests_root.exists():
        return violations
    if not baseline_path.exists():
        return [f"{_UNIT_TEST_OPT_OUT_BASELINE_PATH}:1: missing opt-out baseline file"]

    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{_UNIT_TEST_OPT_OUT_BASELINE_PATH}:{exc.lineno}: invalid JSON baseline"]
    if not isinstance(baseline, dict):
        return [f"{_UNIT_TEST_OPT_OUT_BASELINE_PATH}:1: baseline must be a JSON object"]
    max_allowed = baseline.get("max_opt_out_file_count")
    if not isinstance(max_allowed, int):
        return [f"{_UNIT_TEST_OPT_OUT_BASELINE_PATH}:1: max_opt_out_file_count must be an integer"]

    unit_files = sorted(p for p in tests_root.glob("test_*_unit.py") if p.is_file())
    opt_out_count = 0
    for path in unit_files:
        rel = path.relative_to(root).as_posix()
        first_non_empty = ""
        first_line_no = 1
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip():
                first_non_empty = line.strip()
                first_line_no = idx
                break
        if first_non_empty.startswith(_UNIT_TEST_OPT_OUT_PREFIX):
            opt_out_count += 1
        else:
            violations.append(
                f"{rel}:{first_line_no}: unit test files must declare '{_UNIT_TEST_OPT_OUT_PREFIX} <reason>' for opt-out tracking"
            )
    if opt_out_count > max_allowed:
        violations.append(
            "tests: opt-out file count increased "
            f"({opt_out_count} > baseline {max_allowed}); convert coverage to .spec.md and lower baseline"
        )
    return violations


def _scan_docs_spec_index_reachability(root: Path, *, harness: dict | None = None) -> list[str]:
    expected = {
        "/specs/current.md",
        "/specs/schema/index.md",
        "/specs/contract/index.md",
        "/specs/governance/index.md",
        "/specs/libraries/index.md",
        "/specs/impl/index.md",
    }
    path = root / "specs/index.md"
    if not path.exists():
        return ["specs/index.md:1: missing canonical spec index"]
    text = path.read_text(encoding="utf-8")
    violations: list[str] = []
    for rel in sorted(expected):
        if rel not in text:
            violations.append(f"specs/index.md:1: missing canonical link {rel}")
    return violations


def _scan_docs_governance_check_family_map_complete(root: Path, *, harness: dict | None = None) -> list[str]:
    path = root / _GOVERNANCE_CHECK_CATALOG_MAP
    if not path.exists():
        return [f"{_GOVERNANCE_CHECK_CATALOG_MAP}:1: missing governance check family map"]
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{_GOVERNANCE_CHECK_CATALOG_MAP}:1: invalid YAML ({exc})"]
    if not isinstance(raw, dict):
        return [f"{_GOVERNANCE_CHECK_CATALOG_MAP}:1: expected mapping root"]
    families = raw.get("families")
    if not isinstance(families, list) or not families:
        return [f"{_GOVERNANCE_CHECK_CATALOG_MAP}:1: families must be a non-empty list"]
    prefixes: set[str] = set()
    violations: list[str] = []
    for idx, item in enumerate(families, start=1):
        if not isinstance(item, dict):
            violations.append(f"{_GOVERNANCE_CHECK_CATALOG_MAP}:1: families[{idx}] must be a mapping")
            continue
        prefix = str(item.get("check_prefix", "")).strip()
        if not prefix:
            violations.append(f"{_GOVERNANCE_CHECK_CATALOG_MAP}:1: families[{idx}].check_prefix required")
            continue
        prefixes.add(prefix)
    if violations:
        return violations
    for cid in sorted(_CHECKS):
        family_prefix = cid.split(".", 1)[0] + "."
        if family_prefix not in prefixes:
            violations.append(
                f"{_GOVERNANCE_CHECK_CATALOG_MAP}:1: missing mapping for check family prefix {family_prefix!r} (check {cid})"
            )
    return violations


def _scan_docs_canonical_freshness_strict(root: Path, *, harness: dict | None = None) -> list[str]:
    report_path = root / ".artifacts/docs-freshness-report.json"
    cmd = [
        sys.executable,
        "-m",
        "spec_runner.spec_lang_commands",
        "check-docs-freshness",
        "--strict",
        "--out",
        report_path.relative_to(root).as_posix(),
    ]
    cp = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=False)
    if cp.returncode == 0:
        return []
    out = (cp.stdout + cp.stderr).strip()
    if not out:
        return ["spec_runner.spec_lang_commands check-docs-freshness --strict failed with no output"]
    return [line for line in out.splitlines() if line.strip()]


GovernanceCheckOutcome = list[str] | dict[str, object]
GovernanceCheck = Callable[..., GovernanceCheckOutcome]


def _policy_outcome(
    *,
    subject: object,
    evaluate: list[object] | None = None,
    policy_path: str = "harness.evaluate",
    symbols: dict[str, object] | None = None,
    violations: list[str] | None = None,
) -> dict[str, object]:
    return {
        "subject": subject,
        "evaluate": evaluate,
        "policy_path": policy_path,
        "symbols": symbols or {},
        "violations": list(violations or []),
    }

_CHECKS: dict[str, GovernanceCheck] = {
    "contract.governance_check": _scan_contract_governance_check,
    "pending.no_resolved_markers": _scan_pending_no_resolved_markers,
    "docs.security_warning_contract": _scan_security_warning_docs,
    "docs.v1_scope_contract": _scan_v1_scope_doc,
    "docs.spec_index_reachability": _scan_docs_spec_index_reachability,
    "docs.governance_check_family_map_complete": _scan_docs_governance_check_family_map_complete,
    "docs.canonical_freshness_strict": _scan_docs_canonical_freshness_strict,
    "runtime.config_literals": _scan_runtime_config_literals,
    "runtime.settings_import_policy": _scan_runtime_settings_import_policy,
    "runtime.python_bin_resolver_sync": _scan_runtime_python_bin_resolver_sync,
    "runtime.runner_interface_gate_sync": _scan_runtime_runner_interface_gate_sync,
    "runtime.runner_adapter_python_impl_forbidden": _scan_runtime_runner_adapter_python_impl_forbidden,
    "runtime.local_ci_parity_python_lane_forbidden": _scan_runtime_local_ci_parity_python_lane_forbidden,
    "runtime.ci_python_lane_non_blocking_required": _scan_runtime_ci_python_lane_non_blocking_required,
    "runtime.required_rust_lane_blocking_status": _scan_runtime_required_rust_lane_blocking_status,
    "runtime.compatibility_lanes_non_blocking_status": _scan_runtime_compatibility_lanes_non_blocking_status,
    "runtime.compatibility_matrix_registration_required": _scan_runtime_compatibility_matrix_registration_required,
    "runtime.runner_certification_registry_valid": _scan_runtime_runner_certification_registry_valid,
    "runtime.runner_certification_surfaces_sync": _scan_runtime_runner_certification_surfaces_sync,
    "runtime.runner_certification_artifacts_contract_sync": _scan_runtime_runner_certification_artifacts_contract_sync,
    "runtime.runner_certification_required_lane_passes": _scan_runtime_runner_certification_required_lane_passes,
    "runtime.runner_certification_compat_lanes_non_blocking": _scan_runtime_runner_certification_compat_lanes_non_blocking,
    "runtime.make_python_parity_targets_forbidden": _scan_runtime_make_python_parity_targets_forbidden,
    "runtime.rust_only_prepush_required": _scan_runtime_rust_only_prepush_required,
    "runtime.prepush_parity_default_required": _scan_runtime_prepush_parity_default_required,
    "runtime.prepush_python_parity_not_optional_by_default": _scan_runtime_prepush_python_parity_not_optional_by_default,
    "runtime.git_hook_prepush_enforced": _scan_runtime_git_hook_prepush_enforced,
    "runtime.fast_path_consistency_required": _scan_runtime_fast_path_consistency_required,
    "runtime.local_ci_parity_entrypoint_documented": _scan_runtime_local_ci_parity_entrypoint_documented,
    "runtime.governance_triage_entrypoint_required": _scan_runtime_governance_triage_entrypoint_required,
    "runtime.prepush_uses_governance_triage_required": _scan_runtime_prepush_uses_governance_triage_required,
    "runtime.cigate_uses_governance_triage_required": _scan_runtime_cigate_uses_governance_triage_required,
    "runtime.triage_artifacts_emitted_required": _scan_runtime_triage_artifacts_emitted_required,
    "runtime.triage_failure_id_parsing_required": _scan_runtime_triage_failure_id_parsing_required,
    "runtime.triage_bypass_logged_required": _scan_runtime_triage_bypass_logged_required,
    "runtime.governance_triage_targeted_first_required": _scan_runtime_governance_triage_targeted_first_required,
    "runtime.local_prepush_broad_governance_forbidden": _scan_runtime_local_prepush_broad_governance_forbidden,
    "runtime.ci_gate_ownership_contract_required": _scan_runtime_ci_gate_ownership_contract_required,
    "runtime.governance_prefix_selection_from_changed_paths": _scan_runtime_governance_prefix_selection_from_changed_paths,
    "runtime.governance_triage_artifact_contains_selection_metadata": _scan_runtime_governance_triage_artifact_contains_selection_metadata,
    "runtime.ci_artifact_upload_paths_valid": _scan_runtime_ci_artifact_upload_paths_valid,
    "runtime.ci_workflow_critical_gate_required": _scan_runtime_ci_workflow_critical_gate_required,
    "runtime.ci_gate_default_no_python_governance_required": _scan_runtime_ci_gate_default_no_python_governance_required,
    "runtime.ci_gate_default_report_commands_forbidden": _scan_runtime_ci_gate_default_report_commands_forbidden,
    "runtime.public_runner_entrypoint_single": _scan_runtime_public_runner_entrypoint_single,
    "runtime.public_runner_default_rust": _scan_runtime_public_runner_default_rust,
    "runtime.python_lane_explicit_opt_in": _scan_runtime_python_lane_explicit_opt_in,
    "runtime.no_public_direct_rust_adapter_docs": _scan_runtime_no_public_direct_rust_adapter_docs,
    "runtime.api_http_oauth_env_only": _scan_runtime_api_http_oauth_env_only,
    "runtime.api_http_oauth_no_secret_literals": _scan_runtime_api_http_oauth_no_secret_literals,
    "runtime.api_http_live_mode_explicit": _scan_runtime_api_http_live_mode_explicit,
    "runtime.api_http_oauth_docs_sync": _scan_runtime_api_http_oauth_docs_sync,
    "runtime.api_http_verb_suite": _scan_runtime_api_http_verb_suite,
    "runtime.api_http_cors_support": _scan_runtime_api_http_cors_support,
    "runtime.api_http_scenario_roundtrip": _scan_runtime_api_http_scenario_roundtrip,
    "runtime.api_http_parity_contract_sync": _scan_runtime_api_http_parity_contract_sync,
    "runtime.chain_reference_resolution": _scan_runtime_chain_reference_resolution,
    "runtime.chain_ref_scalar_required": _scan_runtime_chain_reference_resolution,
    "runtime.chain_step_class_required": _scan_runtime_chain_step_class_required,
    "runtime.chain_cycle_forbidden": _scan_runtime_chain_cycle_forbidden,
    "runtime.chain_exports_target_derived_only": _scan_runtime_chain_exports_target_derived_only,
    "runtime.chain_exports_explicit_only": _scan_runtime_chain_exports_target_derived_only,
    "runtime.chain_exports_from_key_required": _scan_runtime_chain_exports_from_key_required,
    "runtime.chain_exports_list_only_required": _scan_runtime_chain_exports_list_only_required,
    "runtime.harness_exports_location_required": _scan_runtime_harness_exports_location_required,
    "runtime.harness_exports_schema_valid": _scan_runtime_harness_exports_schema_valid,
    "runtime.chain_imports_consumer_surface_unchanged": _scan_runtime_chain_imports_consumer_surface_unchanged,
    "runtime.chain_library_symbol_exports_valid": _scan_runtime_chain_library_symbol_exports_valid,
    "runtime.chain_import_alias_collision_forbidden": _scan_runtime_chain_import_alias_collision_forbidden,
    "runtime.chain_fail_fast_default": _scan_runtime_chain_fail_fast_default,
    "runtime.chain_state_template_resolution": _scan_runtime_chain_state_template_resolution,
    "runtime.chain_contract_single_location": _scan_runtime_chain_contract_single_location,
    "runtime.universal_chain_support_required": _scan_runtime_universal_chain_support_required,
    "runtime.chain_shared_context_required": _scan_runtime_chain_shared_context_required,
    "runtime.executable_spec_lang_includes_forbidden": _scan_runtime_executable_spec_lang_includes_forbidden,
    "runtime.domain_library_preferred_for_fs_ops": _scan_runtime_domain_library_preferred_for_fs_ops,
    "runtime.domain_library_preferred_for_http_helpers": _scan_runtime_domain_library_preferred_for_http_helpers,
    "runtime.spec_lang_export_type_forbidden": _scan_runtime_spec_lang_export_type_forbidden,
    "docs.api_http_tutorial_sync": _scan_docs_api_http_tutorial_sync,
    "docs.examples_prefer_domain_fs_helpers": _scan_docs_examples_prefer_domain_fs_helpers,
    "runtime.runner_interface_subcommands": _scan_runtime_runner_interface_subcommands,
    "runtime.runner_interface_ci_lane": _scan_runtime_runner_interface_ci_lane,
    "runtime.rust_adapter_no_delegate": _scan_runtime_rust_adapter_no_delegate,
    "runtime.rust_adapter_exec_smoke": _scan_runtime_rust_adapter_exec_smoke,
    "runtime.rust_adapter_subcommand_parity": _scan_runtime_rust_adapter_subcommand_parity,
    "runtime.assertions_via_spec_lang": _scan_runtime_assertions_via_spec_lang,
    "runtime.spec_lang_pure_no_effect_builtins": _scan_spec_lang_pure_no_effect_builtins,
    "runtime.orchestration_policy_via_spec_lang": _scan_runtime_orchestration_policy_via_spec_lang,
    "conformance.case_index_sync": _scan_conformance_case_index_sync,
    "conformance.purpose_warning_codes_sync": _scan_conformance_purpose_warning_codes_sync,
    "conformance.purpose_quality_gate": _scan_conformance_purpose_quality_gate,
    "contract.coverage_threshold": _scan_contract_coverage_threshold,
    "runtime.runner_independence_metric": _scan_runner_independence_metric,
    "runtime.runner_independence_non_regression": _scan_runner_independence_non_regression,
    "runtime.python_dependency_metric": _scan_python_dependency_metric,
    "runtime.python_dependency_non_regression": _scan_python_dependency_non_regression,
    "docs.operability_non_regression": _scan_docs_operability_non_regression,
    "docs.library_symbol_metadata_complete": _scan_docs_library_symbol_metadata_complete,
    "docs.library_symbol_params_sync": _scan_docs_library_symbol_params_sync,
    "docs.library_symbol_examples_present": _scan_docs_library_symbol_examples_present,
    "docs.library_symbol_catalog_sync": _scan_docs_library_symbol_catalog_sync,
    "docs.spec_case_doc_metadata_complete": _scan_docs_spec_case_doc_metadata_complete,
    "docs.spec_case_catalog_sync": _scan_docs_spec_case_catalog_sync,
    "docs.spec_domain_grouping_sync": _scan_docs_spec_domain_grouping_sync,
    "docs.compatibility_examples_labeled": _scan_docs_compatibility_examples_labeled,
    "docs.readme_rust_first_coherence": _scan_docs_readme_rust_first_coherence,
    "docs.generated_command_meta_no_python_exec": _scan_docs_generated_command_meta_no_python_exec,
    "spec.contract_assertions_non_regression": _scan_contract_assertions_non_regression,
    "spec.portability_non_regression": _scan_spec_portability_non_regression,
    "spec.spec_lang_adoption_non_regression": _scan_spec_lang_adoption_non_regression,
    "runtime.non_python_lane_no_python_exec": _scan_runtime_non_python_lane_no_python_exec,
    "runtime.rust_adapter_transitive_no_python": _scan_runtime_rust_adapter_transitive_no_python,
    "objective.scorecard_non_regression": _scan_objective_scorecard_non_regression,
    "objective.tripwires_clean": _scan_objective_tripwires_clean,
    "conformance.case_doc_style_guard": _scan_conformance_case_doc_style_guard,
    "docs.regex_doc_sync": _scan_regex_doc_sync,
    "assert.universal_core_sync": _scan_assert_universal_core_sync,
    "assert.sugar_compile_only_sync": _scan_assert_sugar_compile_only_sync,
    "assert.type_contract_subject_semantics_sync": _scan_assert_type_contract_subject_semantics_sync,
    "assert.compiler_schema_matrix_sync": _scan_assert_compiler_schema_matrix_sync,
    "assert.spec_lang_builtin_surface_sync": _scan_assert_spec_lang_builtin_surface_sync,
    "assert.subject_profiles_declared": _scan_assert_subject_profiles_declared,
    "assert.subject_profiles_json_only": _scan_assert_subject_profiles_json_only,
    "assert.domain_profiles_docs_sync": _scan_assert_domain_profiles_docs_sync,
    "assert.domain_library_usage_required": _scan_assert_domain_library_usage_required,
    "assert.adapter_projection_contract_sync": _scan_assert_adapter_projection_contract_sync,
    "spec_lang.stdlib_profile_complete": _scan_spec_lang_stdlib_profile_complete,
    "spec_lang.stdlib_py_php_parity": _scan_spec_lang_stdlib_py_php_parity,
    "spec_lang.stdlib_docs_sync": _scan_spec_lang_stdlib_docs_sync,
    "spec_lang.stdlib_conformance_coverage": _scan_spec_lang_stdlib_conformance_coverage,
    "docs.current_spec_only_contract": _scan_current_spec_only_contract,
    "docs.current_spec_policy_key_names": _scan_current_spec_policy_key_names,
    "governance.policy_library_usage_required": _scan_governance_policy_library_usage_required,
    "governance.policy_library_usage_non_regression": _scan_policy_library_usage_non_regression,
    "conformance.library_policy_usage_required": _scan_conformance_library_policy_usage_required,
    "governance.extractor_only_no_verdict_branching": _scan_governance_extractor_only_no_verdict_branching,
    "governance.structured_assertions_required": _scan_governance_structured_assertions_required,
    "runtime.rust_adapter_no_python_exec": _scan_runtime_rust_adapter_no_python_exec,
    "conformance.type_contract_docs": _scan_conformance_type_contract_docs,
    "conformance.api_http_portable_shape": _scan_conformance_api_http_portable_shape,
    "conformance.no_runner_logic_outside_harness": _scan_conformance_no_runner_logic_outside_harness,
    "conformance.extension_requires_capabilities": _scan_conformance_extension_requires_capabilities,
    "conformance.type_contract_field_sync": _scan_conformance_type_contract_field_sync,
    "impl.evaluate_ratio_non_regression": _scan_impl_evaluate_ratio_non_regression,
    "impl.library_usage_non_regression": _scan_impl_library_usage_non_regression,
    "conformance.spec_lang_fixture_library_usage": _scan_conformance_spec_lang_fixture_library_usage,
    "conformance.library_contract_cases_present": _scan_conformance_library_contract_cases_present,
    "conformance.evaluate_first_ratio_non_regression": _scan_conformance_evaluate_first_ratio_non_regression,
    "docs.reference_surface_complete": _scan_docs_reference_surface_complete,
    "docs.reference_index_sync": _scan_docs_reference_index_sync,
    "docs.book_chapter_order_canonical": _scan_docs_book_chapter_order_canonical,
    "docs.meta_schema_valid": _scan_docs_meta_schema_valid,
    "docs.reference_manifest_sync": _scan_docs_reference_manifest_sync,
    "docs.token_ownership_unique": _scan_docs_token_ownership_unique,
    "docs.token_dependency_resolved": _scan_docs_token_dependency_resolved,
    "docs.instructions_complete": _scan_docs_instructions_complete,
    "docs.command_examples_verified": _scan_docs_command_examples_verified,
    "docs.example_id_uniqueness": _scan_docs_example_id_uniqueness,
    "docs.generated_files_clean": _scan_docs_generated_files_clean,
    "docs.generator_registry_valid": _scan_docs_generator_registry_valid,
    "docs.generator_outputs_sync": _scan_docs_generator_outputs_sync,
    "docs.generation_spec_cases_present": _scan_docs_generation_spec_cases_present,
    "docs.generation_registry_surface_case_sync": _scan_docs_generation_registry_surface_case_sync,
    "docs.template_paths_valid": _scan_docs_template_paths_valid,
    "docs.template_data_sources_declared": _scan_docs_template_data_sources_declared,
    "docs.output_mode_contract_valid": _scan_docs_output_mode_contract_valid,
    "docs.generate_check_passes": _scan_docs_generate_check_passes,
    "docs.generated_sections_read_only": _scan_docs_generated_sections_read_only,
    "docs.runner_api_catalog_sync": _scan_docs_runner_api_catalog_sync,
    "docs.harness_type_catalog_sync": _scan_docs_harness_type_catalog_sync,
    "docs.spec_lang_builtin_catalog_sync": _scan_docs_spec_lang_builtin_catalog_sync,
    "docs.stdlib_symbol_docs_complete": _scan_docs_stdlib_symbol_docs_complete,
    "docs.stdlib_examples_complete": _scan_docs_stdlib_examples_complete,
    "docs.harness_reference_semantics_complete": _scan_docs_harness_reference_semantics_complete,
    "docs.runner_reference_semantics_complete": _scan_docs_runner_reference_semantics_complete,
    "docs.reference_namespace_chapters_sync": _scan_docs_reference_namespace_chapters_sync,
    "docs.docgen_quality_score_threshold": _scan_docs_docgen_quality_score_threshold,
    "docs.policy_rule_catalog_sync": _scan_docs_policy_rule_catalog_sync,
    "docs.traceability_catalog_sync": _scan_docs_traceability_catalog_sync,
    "docs.governance_check_catalog_sync": _scan_docs_governance_check_catalog_sync,
    "docs.metrics_field_catalog_sync": _scan_docs_metrics_field_catalog_sync,
    "docs.spec_schema_field_catalog_sync": _scan_docs_spec_schema_field_catalog_sync,
    "docs.required_sections": _scan_docs_required_sections,
    "docs.markdown_structured_assertions_required": _scan_docs_markdown_structured_assertions_required,
    "docs.examples_runnable": _scan_docs_examples_runnable,
    "docs.cli_flags_documented": _scan_docs_cli_flags_documented,
    "docs.contract_schema_book_sync": _scan_docs_contract_schema_book_sync,
    "docs.make_commands_sync": _scan_docs_make_commands_sync,
    "docs.adoption_profiles_sync": _scan_docs_adoption_profiles_sync,
    "docs.release_contract_automation_policy": _scan_docs_release_contract_automation_policy,
    "docs.layout_canonical_trees": _scan_docs_layout_canonical_trees,
    "docs.index_filename_policy": _scan_docs_index_filename_policy,
    "docs.filename_policy": _scan_docs_filename_policy,
    "docs.reviews_namespace_active": _scan_docs_reviews_namespace_active,
    "docs.reviews_prompt_schema_contract_sync": _scan_docs_reviews_prompt_schema_contract_sync,
    "docs.review_snapshot_template_contract_sync": _scan_docs_review_snapshot_template_contract_sync,
    "docs.review_tooling_contract_sync": _scan_docs_review_tooling_contract_sync,
    "docs.review_snapshots_schema_valid": _scan_docs_review_snapshots_schema_valid,
    "docs.reviews_discovery_prompt_present": _scan_docs_reviews_discovery_prompt_present,
    "docs.reviews_discovery_prompt_contract_sync": _scan_docs_reviews_discovery_prompt_contract_sync,
    "docs.reviews_discovery_workflow_sync": _scan_docs_reviews_discovery_workflow_sync,
    "docs.no_os_artifact_files": _scan_docs_no_os_artifact_files,
    "runtime.scope_sync": _scan_runtime_scope_sync,
    "runtime.profiling_contract_artifacts": _scan_runtime_profiling_contract_artifacts,
    "runtime.profiling_redaction_policy": _scan_runtime_profiling_redaction_policy,
    "runtime.profiling_span_taxonomy": _scan_runtime_profiling_span_taxonomy,
    "runtime.liveness_watchdog_contract_valid": _scan_runtime_liveness_watchdog_contract_valid,
    "runtime.liveness_stall_token_emitted": _scan_runtime_liveness_stall_token_emitted,
    "runtime.liveness_hard_cap_token_emitted": _scan_runtime_liveness_hard_cap_token_emitted,
    "runtime.gate_fail_fast_behavior_required": _scan_runtime_gate_fail_fast_behavior_required,
    "runtime.gate_skipped_steps_contract_required": _scan_runtime_gate_skipped_steps_contract_required,
    "runtime.profile_artifacts_on_fail_required": _scan_runtime_profile_artifacts_on_fail_required,
    "runtime.assert_block_decision_authority_required": _scan_runtime_assert_block_decision_authority_required,
    "runtime.meta_json_target_required": _scan_runtime_meta_json_target_required,
    "runtime.implicit_subject_binding_forbidden": _scan_runtime_implicit_subject_binding_forbidden,
    "runtime.ops_os_capability_required": _scan_runtime_ops_os_capability_required,
    "runtime.ops_os_stdlib_surface_sync": _scan_runtime_ops_os_stdlib_surface_sync,
    "runtime.contract_spec_fence_required": _scan_runtime_contract_spec_fence_required,
    "runtime.case_contract_block_required": _scan_runtime_case_contract_block_required,
    "runtime.contract_step_asserts_required": _scan_runtime_contract_step_asserts_required,
    "runtime.contract_job_dispatch_in_contract_required": _scan_runtime_contract_job_dispatch_in_contract_required,
    "runtime.harness_jobs_metadata_map_required": _scan_runtime_harness_jobs_metadata_map_required,
    "runtime.ops_job_capability_required": _scan_runtime_ops_job_capability_required,
    "runtime.ops_job_nested_dispatch_forbidden": _scan_runtime_ops_job_nested_dispatch_forbidden,
    "runtime.when_hooks_schema_valid": _scan_runtime_when_hooks_schema_valid,
    "runtime.when_ordering_contract_required": _scan_runtime_when_ordering_contract_required,
    "runtime.when_fail_hook_required_behavior": _scan_runtime_when_fail_hook_required_behavior,
    "runtime.when_complete_hook_required_behavior": _scan_runtime_when_complete_hook_required_behavior,
    "runtime.contract_job_hooks_refactor_applied": _scan_runtime_contract_job_hooks_refactor_applied,
    "architecture.harness_workflow_components_required": _scan_architecture_harness_workflow_components_required,
    "architecture.harness_local_workflow_duplication_forbidden": _scan_architecture_harness_local_workflow_duplication_forbidden,
    "schema.harness_type_overlay_complete": _scan_schema_harness_type_overlay_complete,
    "schema.harness_contract_overlay_sync": _scan_schema_harness_contract_overlay_sync,
    "runtime.harness_subject_target_map_declared": _scan_runtime_harness_subject_target_map_declared,
    "orchestration.ops_symbol_grammar": _scan_orchestration_ops_symbol_grammar,
    "orchestration.ops_registry_sync": _scan_orchestration_ops_registry_sync,
    "orchestration.ops_capability_bindings": _scan_orchestration_ops_capability_bindings,
    "naming.filename_policy": _scan_naming_filename_policy,
    "normalization.virtual_root_paths_only": _scan_normalization_virtual_root_paths_only,
    "reference.contract_paths_exist": _scan_reference_contract_paths_exist,
    "reference.symbols_exist": _scan_reference_symbols_exist,
    "reference.policy_symbols_resolve": _scan_reference_policy_symbols_resolve,
    "reference.library_exports_used": _scan_reference_library_exports_used,
    "reference.private_symbols_forbidden": _scan_reference_private_symbols_forbidden,
    "reference.check_ids_exist": _scan_reference_check_ids_exist,
    "reference.external_refs_policy": _scan_reference_external_refs_policy,
    "reference.token_anchors_exist": _scan_reference_token_anchors_exist,
    "spec.layout_domain_trees": _scan_spec_layout_domain_trees,
    "spec.taxonomy_hard_cut_required": _scan_spec_taxonomy_hard_cut_required,
    "spec.domain_index_sync": _scan_spec_domain_index_sync,
    "spec.executable_surface_markdown_only": _scan_spec_executable_surface_markdown_only,
    "spec.no_executable_yaml_json_in_case_trees": _scan_spec_no_executable_yaml_json_in_case_trees,
    "spec.library_cases_markdown_only": _scan_spec_library_cases_markdown_only,
    "spec.generated_data_artifacts_not_embedded_in_spec_blocks": _scan_spec_generated_data_artifacts_not_embedded_in_spec_blocks,
    "tests.unit_opt_out_non_regression": _scan_tests_unit_opt_out_non_regression,
    "schema.registry_valid": _scan_schema_registry_valid,
    "schema.registry_docs_sync": _scan_schema_registry_docs_sync,
    "schema.registry_compiled_sync": _scan_schema_registry_compiled_sync,
    "schema.no_prose_only_rules": _scan_schema_no_prose_only_rules,
    "schema.type_profiles_complete": _scan_schema_type_profiles_complete,
    "schema.contract_target_on_forbidden": _scan_schema_contract_target_on_forbidden,
    "schema.contract_imports_explicit_required": _scan_schema_contract_imports_explicit_required,
    "library.domain_ownership": _scan_library_domain_ownership,
    "library.domain_index_sync": _scan_library_domain_index_sync,
    "library.public_surface_model": _scan_library_public_surface_model,
    "library.single_public_symbol_per_case_required": _scan_library_single_public_symbol_per_case,
    "library.colocated_symbol_tests_required": _scan_library_colocated_symbol_tests_required,
    "library.verb_first_schema_keys_required": _scan_library_verb_first_schema_keys_required,
    "schema.verb_first_contract_sync": _scan_schema_verb_first_contract_sync,
    "normalization.profile_sync": _scan_normalization_profile_sync,
    "normalization.mapping_ast_only": _scan_normalization_mapping_ast_only,
    "normalization.library_mapping_ast_only": _scan_normalization_library_mapping_ast_only,
    "normalization.docs_token_sync": _scan_normalization_docs_token_sync,
    "normalization.spec_style_sync": _scan_normalization_spec_style_sync,
}


def _is_governance_case_payload(case_payload: dict[str, Any]) -> bool:
    if str(case_payload.get("type", "")).strip() != "contract.check":
        return False
    harness = case_payload.get("harness")
    if not isinstance(harness, dict):
        return False
    check_cfg = harness.get("check")
    if not isinstance(check_cfg, dict):
        return False
    return str(check_cfg.get("profile", "")).strip() == "governance.scan"


def _governance_check_id(case_payload: dict[str, Any]) -> str:
    harness = case_payload.get("harness")
    if not isinstance(harness, dict):
        return ""
    check_cfg = harness.get("check")
    if not isinstance(check_cfg, dict):
        return ""
    config = check_cfg.get("config")
    if not isinstance(config, dict):
        return ""
    return str(config.get("check", "")).strip()


def run_governance_check(case, *, ctx) -> None:
    if hasattr(case, "raw_case"):
        t = dict(getattr(case, "raw_case") or {})
    else:
        t = dict(getattr(case, "test") or {})
    check_id = _governance_check_id(t)
    if not check_id:
        raise ValueError("contract.check profile governance.scan requires harness.check.config.check")
    fn = _CHECKS.get(check_id)
    if fn is None:
        supported = ", ".join(sorted(_CHECKS))
        raise ValueError(f"unknown governance check: {check_id} (supported: {supported})")

    h = t.get("harness") or {}
    if not isinstance(h, dict):
        raise TypeError("harness must be a mapping")
    root = Path(str(h.get("root", "."))).resolve()
    fn_params = inspect.signature(fn).parameters
    if "harness" in fn_params:
        raw_outcome = fn(root, harness=h)
    else:
        raw_outcome = fn(root)

    if "evaluate" in h:
        raise ValueError(
            "contract.check profile governance.scan forbids harness.evaluate; encode obligations in assert blocks"
        )
    orch = h.get("orchestration_policy")
    if isinstance(orch, dict) and "evaluate" in orch:
        raise ValueError(
            "contract.check profile governance.scan forbids harness.orchestration_policy.evaluate; encode obligations in assert blocks"
        )

    subject: object = {}
    symbols: dict[str, object] = {}
    if isinstance(raw_outcome, dict):
        subject = raw_outcome.get("subject")
        symbols_raw = raw_outcome.get("symbols")
        symbols = symbols_raw if isinstance(symbols_raw, dict) else {}
        violations_raw = raw_outcome.get("violations")
        if isinstance(violations_raw, list):
            violations = [str(v) for v in violations_raw if str(v).strip()]
        else:
            violations = []
    else:
        violations = [str(v) for v in raw_outcome if str(v).strip()]
        subject = {"violations": violations}

    if isinstance(subject, dict) and "violations" not in subject:
        subject = {**subject, "violations": list(violations)}

    case_key = f"{case.doc_path.resolve().as_posix()}::{str(t.get('id', '<unknown>')).strip() or '<unknown>'}"
    chain_symbols = dict(ctx.get_case_chain_imports(case_key=case_key))
    if chain_symbols:
        symbols = {**chain_symbols, **symbols}
    spec_lang_imports = compile_import_bindings((h or {}).get("spec_lang"))
    spec_lang_capabilities = capabilities_from_harness(h)

    case_id = str(t.get("id", "<unknown>")).strip() or "<unknown>"
    summary = {
        "passed": not violations,
        "check_id": check_id,
        "case_id": case_id,
        "violation_count": len(violations),
    }
    text = (
        f"PASS: {check_id}"
        if not violations
        else f"FAIL: {check_id}\n" + "\n".join(violations)
    )
    meta_json = build_meta_subject(
        case=case,
        ctx=ctx,
        case_key=case_key,
        harness=h,
        artifacts={"text": text, "summary_json": summary, "violation_count": len(violations)},
    )

    assert_tree = compile_assert_tree(
        t.get("contract"),
        raw_expect=t.get("expect"),
        type_name="contract.check",
        strict_steps=True,
    )

    def _artifact_for_key(key: str) -> object:
        if key == "text":
            return text
        if key == "summary_json":
            return summary
        if key == "violation_count":
            return len(violations)
        if key == "meta_json":
            return meta_json
        raise ValueError(f"unknown assertion artifact for contract.check governance.scan: {key}")

    evaluate_internal_assert_tree(
        assert_tree,
        case_id=case_id,
        subject_for_key=_artifact_for_key,
        limits=SpecLangLimits(),
        symbols=symbols,
        imports=spec_lang_imports,
        capabilities=spec_lang_capabilities,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run governance spec cases with project-owned contract.check governance.scan harness."
    )
    ap.add_argument("--cases", default="specs/governance/cases", help="Path to governance case docs directory")
    ap.add_argument(
        "--case-file-pattern",
        default=SETTINGS.case.default_file_pattern,
        help="Glob pattern for case files when --cases points to a directory",
    )
    ap.add_argument(
        "--check-prefix",
        action="append",
        default=[],
        help="Optional governance check id prefix filter; can be passed multiple times",
    )
    ap.add_argument(
        "--exclude-check-prefix",
        action="append",
        default=[],
        help="Optional governance check id exclusion prefix; can be passed multiple times",
    )
    ap.add_argument("--timing-out", default=".artifacts/governance-timing.json")
    ap.add_argument("--profile", action="store_true", help="Emit per-case harness timing profile JSON")
    ap.add_argument("--profile-out", default=".artifacts/governance-profile.json")
    ap.add_argument("--profile-level", default="", help="off|basic|detailed|debug (default off)")
    ap.add_argument("--profile-summary-out", default="", help="Run trace summary markdown output path")
    ap.add_argument("--profile-heartbeat-ms", type=int, default=0, help="Profiler heartbeat interval (ms)")
    ap.add_argument("--profile-stall-threshold-ms", type=int, default=0, help="Profiler stall warning threshold (ms)")
    ap.add_argument("--liveness-level", default="", help="off|basic|strict (default off)")
    ap.add_argument("--liveness-stall-ms", type=int, default=0, help="No-progress stall window in ms")
    ap.add_argument("--liveness-min-events", type=int, default=0, help="Minimum progress events per stall window")
    ap.add_argument("--liveness-hard-cap-ms", type=int, default=0, help="Emergency hard cap in ms")
    ap.add_argument("--liveness-kill-grace-ms", type=int, default=0, help="TERM->KILL grace interval in ms")
    ap.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Worker count override (0=auto, 1=sequential for hang isolation)",
    )
    ns = ap.parse_args(argv)
    if str(ns.liveness_level).strip():
        os.environ["SPEC_RUNNER_LIVENESS_LEVEL"] = str(ns.liveness_level).strip()
    if int(ns.liveness_stall_ms or 0) > 0:
        os.environ["SPEC_RUNNER_LIVENESS_STALL_MS"] = str(int(ns.liveness_stall_ms))
    if int(ns.liveness_min_events or 0) > 0:
        os.environ["SPEC_RUNNER_LIVENESS_MIN_EVENTS"] = str(int(ns.liveness_min_events))
    if int(ns.liveness_hard_cap_ms or 0) > 0:
        os.environ["SPEC_RUNNER_LIVENESS_HARD_CAP_MS"] = str(int(ns.liveness_hard_cap_ms))
    if int(ns.liveness_kill_grace_ms or 0) > 0:
        os.environ["SPEC_RUNNER_LIVENESS_KILL_GRACE_MS"] = str(int(ns.liveness_kill_grace_ms))

    liveness_cfg = _effective_governance_liveness()

    _reset_scan_caches()
    repo_root = Path(__file__).resolve().parents[3]
    profiler_cfg = profile_config_from_args(
        profile_level=str(ns.profile_level).strip() or None,
        profile_out=None,
        profile_summary_out=str(ns.profile_summary_out).strip() or None,
        profile_heartbeat_ms=ns.profile_heartbeat_ms if int(ns.profile_heartbeat_ms or 0) > 0 else None,
        profile_stall_threshold_ms=ns.profile_stall_threshold_ms if int(ns.profile_stall_threshold_ms or 0) > 0 else None,
        runner_impl=str(os.environ.get("SPEC_RUNNER_IMPL", "python")),
        command="governance",
        args=list(argv or []),
        env=dict(os.environ),
    )
    profiler = RunProfiler(profiler_cfg)
    if profiler.cfg.enabled:
        profiler.event(
            kind="checkpoint",
            attrs={
                "phase": "governance.liveness_config",
                "liveness_level": liveness_cfg.level,
                "liveness_stall_ms": int(liveness_cfg.stall_ms),
                "liveness_min_events": int(liveness_cfg.min_events),
                "liveness_hard_cap_ms": int(liveness_cfg.hard_cap_ms),
                "liveness_kill_grace_ms": int(liveness_cfg.kill_grace_ms),
            },
        )

    case_pattern = str(ns.case_file_pattern).strip()
    if not case_pattern:
        print("ERROR: --case-file-pattern requires a non-empty value", file=sys.stderr)
        return 2

    cases_path = Path(str(ns.cases))
    if not cases_path.exists():
        print(f"ERROR: cases path does not exist: {cases_path}", file=sys.stderr)
        return 2

    failures: list[str] = []
    started = time.perf_counter()
    include_prefixes = tuple(str(x).strip() for x in (ns.check_prefix or []) if str(x).strip())
    exclude_prefixes = tuple(str(x).strip() for x in (ns.exclude_check_prefix or []) if str(x).strip())
    governance_cases = [
        case
        for case in iter_cases(cases_path, file_pattern=case_pattern)
        if _is_governance_case_payload(case.test)
    ]
    if profiler.cfg.enabled:
        profiler.event(
            kind="checkpoint",
            attrs={"phase": "governance.case_loading.complete", "case_count": len(governance_cases)},
        )
    if include_prefixes:
        governance_cases = [
            case
            for case in governance_cases
            if any(_governance_check_id(case.test).startswith(p) for p in include_prefixes)
        ]
    if exclude_prefixes:
        governance_cases = [
            case
            for case in governance_cases
            if not any(_governance_check_id(case.test).startswith(p) for p in exclude_prefixes)
        ]
    if (include_prefixes or exclude_prefixes) and not governance_cases:
        print("ERROR: governance filter selected zero cases", file=sys.stderr)
        return 2
    timing_rows: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []
    workers_used = 1
    progress_lock = threading.Lock()
    last_progress_ts = time.monotonic()
    active_cases: dict[int, dict[str, Any]] = {}

    def _mark_progress(
        *,
        phase: str,
        idx: int | None = None,
        case_id: str | None = None,
        check_id: str | None = None,
        status: str | None = None,
        elapsed_ms: float | None = None,
    ) -> None:
        nonlocal last_progress_ts
        now = time.monotonic()
        with progress_lock:
            last_progress_ts = now
            if idx is not None and case_id and check_id:
                if status in {"pass", "fail"}:
                    active_cases.pop(int(idx), None)
                else:
                    active_cases[int(idx)] = {
                        "case_id": case_id,
                        "check_id": check_id,
                        "started_at": now,
                    }
        if _GOVERNANCE_TRACE:
            parts = [f"[governance.trace] {phase}"]
            if idx is not None:
                parts.append(f"idx={idx}")
            if check_id:
                parts.append(f"check={check_id}")
            if case_id:
                parts.append(f"case={case_id}")
            if status:
                parts.append(f"status={status}")
            if elapsed_ms is not None:
                parts.append(f"ms={elapsed_ms:.2f}")
            print(" ".join(parts), flush=True)
        if profiler.cfg.enabled:
            attrs: dict[str, Any] = {"phase": phase}
            if idx is not None:
                attrs["index"] = int(idx)
            if case_id:
                attrs["case_id"] = case_id
            if check_id:
                attrs["check_id"] = check_id
            if status:
                attrs["status"] = status
            if elapsed_ms is not None:
                attrs["elapsed_ms"] = round(float(elapsed_ms), 3)
            profiler.event(kind="checkpoint", attrs=attrs)
    try:
        with TemporaryDirectory(prefix="spec-runner-governance-") as td:
            td_path = Path(td)

            def _run_one(args: tuple[int, Any]) -> tuple[int, str, str, float, str | None, list[dict[str, Any]]]:
                idx, case = args
                case_id = str(case.test.get("id", "<unknown>")).strip() or "<unknown>"
                check_id = _governance_check_id(case.test)
                _mark_progress(phase="governance.case.start", idx=idx, case_id=case_id, check_id=check_id)
                case_tmp = td_path / f"case_{idx}"
                case_tmp.mkdir(parents=True, exist_ok=True)
                ctx = SpecRunContext(
                    tmp_path=case_tmp,
                    patcher=MiniMonkeyPatch(),
                    capture=MiniCapsys(),
                    profile_enabled=bool(ns.profile),
                    profiler=profiler if profiler.cfg.enabled else None,
                )
                case_started = time.perf_counter()
                token = _ACTIVE_PROFILER.set(profiler if profiler.cfg.enabled else None)
                try:
                    if profiler.cfg.enabled:
                        profiler.event(
                            kind="checkpoint",
                            attrs={
                                "phase": "governance.case_compile.start",
                                "case_id": case_id,
                                "check_id": check_id,
                            },
                        )
                    span_cm = (
                        profiler.span(
                            name="check.execute",
                            kind="check",
                            phase="governance.check",
                            attrs={"check_id": check_id, "case_id": case_id},
                        )
                        if profiler.cfg.enabled
                        else contextlib.nullcontext()
                    )
                    with span_cm:
                        if profiler.cfg.enabled:
                            profiler.event(
                                kind="checkpoint",
                                attrs={
                                    "phase": "governance.assertion.evaluate.start",
                                    "case_id": case_id,
                                    "check_id": check_id,
                                },
                            )
                        run_case(case, ctx=ctx, type_runners={"contract.check": run_governance_check})
                        if profiler.cfg.enabled:
                            profiler.event(
                                kind="checkpoint",
                                attrs={
                                    "phase": "governance.assertion.evaluate.complete",
                                    "case_id": case_id,
                                    "check_id": check_id,
                                },
                            )
                    elapsed_ms = (time.perf_counter() - case_started) * 1000.0
                    _mark_progress(
                        phase="governance.case.finish",
                        idx=idx,
                        case_id=case_id,
                        check_id=check_id,
                        status="pass",
                        elapsed_ms=elapsed_ms,
                    )
                    return idx, case_id, check_id, elapsed_ms, None, list(ctx.profile_rows)
                except BaseException as e:  # noqa: BLE001
                    elapsed_ms = (time.perf_counter() - case_started) * 1000.0
                    if profiler.cfg.enabled:
                        profiler.event(
                            kind="checkpoint",
                            attrs={
                                "phase": "governance.check.error",
                                "case_id": case_id,
                                "check_id": check_id,
                                "error": str(e),
                            },
                        )
                    _mark_progress(
                        phase="governance.case.finish",
                        idx=idx,
                        case_id=case_id,
                        check_id=check_id,
                        status="fail",
                        elapsed_ms=elapsed_ms,
                    )
                    return idx, case_id, check_id, elapsed_ms, f"{case_id}: {e}", list(ctx.profile_rows)
                finally:
                    if profiler.cfg.enabled:
                        profiler.event(
                            kind="checkpoint",
                            attrs={
                                "phase": "governance.check.complete",
                                "case_id": case_id,
                                "check_id": check_id,
                            },
                        )
                    _ACTIVE_PROFILER.reset(token)

            requested_workers = int(getattr(ns, "workers", 0) or 0)
            if requested_workers < 0:
                print("ERROR: --workers must be >= 0", file=sys.stderr)
                return 2

            if len(governance_cases) <= 1:
                for idx, case in enumerate(governance_cases):
                    _idx, case_id, check_id, elapsed_ms, failure, case_profile_rows = _run_one((idx, case))
                    timing_rows.append(
                        {
                            "index": int(_idx),
                            "case_id": case_id,
                            "check_id": check_id,
                            "duration_ms": round(float(elapsed_ms), 3),
                            "status": "fail" if failure else "pass",
                        }
                    )
                    profile_rows.extend(case_profile_rows)
                    if failure:
                        failures.append(failure)
            else:
                max_workers = min(max(1, os.cpu_count() or 1), len(governance_cases))
                if requested_workers > 1:
                    max_workers = min(requested_workers, len(governance_cases))
                workers_used = max_workers
                results: list[tuple[int, str, str, float, str | None, list[dict[str, Any]]]] = []
                stall_ms = int(liveness_cfg.stall_ms) if str(liveness_cfg.level).strip().lower() != "off" else 0
                heartbeat_ms = int(
                    str(os.environ.get("SPEC_RUNNER_GOVERNANCE_PROGRESS_HEARTBEAT_MS", "1000")).strip() or "1000"
                )
                heartbeat_seconds = max(float(heartbeat_ms) / 1000.0, 0.25)
                stalled = False
                running_case_hard_cap_ms = max(int(stall_ms * 6), 30_000) if stall_ms > 0 else 0
                progress_log_every_seconds = max(
                    float(
                        str(os.environ.get("SPEC_RUNNER_GOVERNANCE_PROGRESS_LOG_INTERVAL_SECONDS", "5")).strip() or "5"
                    ),
                    1.0,
                )
                last_progress_log_ts = 0.0
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    pending: set[concurrent.futures.Future[tuple[int, str, str, float, str | None, list[dict[str, Any]]]]] = {
                        executor.submit(_run_one, (idx, case))
                        for idx, case in enumerate(governance_cases)
                    }
                    while pending:
                        done, pending = concurrent.futures.wait(
                            pending,
                            timeout=heartbeat_seconds,
                            return_when=concurrent.futures.FIRST_COMPLETED,
                        )
                        if done:
                            for fut in done:
                                results.append(fut.result())
                            continue
                        with progress_lock:
                            inactive_for_ms = (time.monotonic() - last_progress_ts) * 1000.0
                            running_snapshot = [
                                {
                                    "index": idx,
                                    "case_id": rec.get("case_id"),
                                    "check_id": rec.get("check_id"),
                                    "running_ms": round((time.monotonic() - float(rec.get("started_at", 0.0))) * 1000.0, 1),
                                }
                                for idx, rec in sorted(active_cases.items(), key=lambda x: x[0])
                            ]
                        longest_running_ms = max(
                            (_safe_float(x.get("running_ms", 0.0), 0.0) for x in running_snapshot),
                            default=0.0,
                        )
                        now_ts = time.monotonic()
                        if not _GOVERNANCE_TRACE and (now_ts - last_progress_log_ts) >= progress_log_every_seconds:
                            completed = len(results)
                            total = len(governance_cases)
                            running_hint = ""
                            if running_snapshot and len(running_snapshot) <= 3:
                                running_hint = f" running_cases={json.dumps(running_snapshot, sort_keys=True)}"
                            print(
                                "[governance.progress] "
                                f"completed={completed}/{total} pending={len(pending)} "
                                f"running={len(running_snapshot)} inactive_ms={int(inactive_for_ms)} "
                                f"longest_running_ms={int(longest_running_ms)}{running_hint}",
                                file=sys.stderr,
                                flush=True,
                            )
                            last_progress_log_ts = now_ts
                        if profiler.cfg.enabled:
                            profiler.event(
                                kind="heartbeat",
                                attrs={
                                    "phase": "governance.case_pool.wait",
                                    "pending_futures": len(pending),
                                    "running_cases": running_snapshot,
                                    "inactive_for_ms": round(inactive_for_ms, 1),
                                    "longest_running_ms": round(longest_running_ms, 1),
                                },
                            )
                        should_stall = False
                        stall_reason = "stall.runner.no_progress"
                        if stall_ms > 0 and inactive_for_ms >= float(stall_ms):
                            if not running_snapshot:
                                should_stall = True
                            elif running_case_hard_cap_ms > 0 and longest_running_ms >= float(running_case_hard_cap_ms):
                                should_stall = True
                                stall_reason = "stall.runner.case_no_completion"
                        if should_stall:
                            stalled = True
                            msg = (
                                f"{stall_reason} after {int(inactive_for_ms)}ms "
                                f"(pending={len(pending)} longest_running_ms={int(longest_running_ms)} "
                                f"running={json.dumps(running_snapshot, sort_keys=True)})"
                            )
                            failures.append(msg)
                            if profiler.cfg.enabled:
                                profiler.event(
                                    kind="stall_warning",
                                    attrs={
                                        "phase": "governance.case_pool.wait",
                                        "reason_token": stall_reason,
                                        "inactive_for_ms": round(inactive_for_ms, 1),
                                        "longest_running_ms": round(longest_running_ms, 1),
                                        "running_case_hard_cap_ms": int(running_case_hard_cap_ms),
                                        "pending_futures": len(pending),
                                        "running_cases": running_snapshot,
                                    },
                                )
                            for fut in pending:
                                fut.cancel()
                            executor.shutdown(wait=False, cancel_futures=True)
                            break
                if stalled:
                    pending.clear()
                for _idx, case_id, check_id, elapsed_ms, failure, case_profile_rows in sorted(results, key=lambda x: x[0]):
                    timing_rows.append(
                        {
                            "index": int(_idx),
                            "case_id": case_id,
                            "check_id": check_id,
                            "duration_ms": round(float(elapsed_ms), 3),
                            "status": "fail" if failure else "pass",
                        }
                    )
                    profile_rows.extend(case_profile_rows)
                    if failure:
                        failures.append(failure)
    finally:
        profile_out_raw = str(os.environ.get("SPEC_RUNNER_PROFILE_OUT", "")).strip() or "/.artifacts/run-trace.json"
        profile_summary_out_raw = str(ns.profile_summary_out).strip() or str(
            os.environ.get("SPEC_RUNNER_PROFILE_SUMMARY_OUT", "")
        ).strip() or "/.artifacts/run-trace-summary.md"
        profile_out_path = _resolve_contract_config_path(repo_root, profile_out_raw, field="run_governance_specs.profile_out_trace")
        profile_summary_out_path = _resolve_contract_config_path(
            repo_root,
            profile_summary_out_raw,
            field="run_governance_specs.profile_summary_out_trace",
        )
        profiler.close(
            status="fail" if failures else "pass",
            out_path=profile_out_path,
            summary_out_path=profile_summary_out_path,
            exit_code=1 if failures else 0,
        )

    total_ms = (time.perf_counter() - started) * 1000.0
    timing_payload = {
        "version": 1,
        "status": "fail" if failures else "pass",
        "summary": {
            "case_count": len(governance_cases),
            "failed_count": len(failures),
            "workers_used": int(workers_used),
            "total_duration_ms": round(float(total_ms), 3),
        },
        "cases": timing_rows,
    }
    timing_out = _resolve_contract_config_path(repo_root, str(ns.timing_out), field="run_governance_specs.timing_out")
    timing_out.parent.mkdir(parents=True, exist_ok=True)
    timing_out.write_text(json.dumps(timing_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {ns.timing_out}")
    if ns.profile:
        sorted_profile = sorted(profile_rows, key=lambda row: float(row.get("duration_ms", 0.0)), reverse=True)
        timing_summary_raw = timing_payload.get("summary")
        timing_summary = timing_summary_raw if isinstance(timing_summary_raw, dict) else {}
        profile_payload = {
            "version": 1,
            "status": timing_payload["status"],
            "summary": {
                "case_count": len(governance_cases),
                "record_count": len(sorted_profile),
                "total_duration_ms": timing_summary.get("total_duration_ms"),
            },
            "top_slowest": sorted_profile[:20],
            "records": sorted_profile,
        }
        profile_out = _resolve_contract_config_path(repo_root, str(ns.profile_out), field="run_governance_specs.profile_out")
        profile_out.parent.mkdir(parents=True, exist_ok=True)
        profile_out.write_text(json.dumps(profile_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {ns.profile_out}")

    if failures:
        for line in failures:
            print(f"ERROR: {line}", file=sys.stderr)
        return 1

    print(f"OK: governance specs passed ({cases_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
