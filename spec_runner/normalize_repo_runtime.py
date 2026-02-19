#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from pathlib import Path
from typing import Any

import yaml

from spec_runner.codecs import load_external_cases
from spec_runner.normalize_docs_layout import main as normalize_docs_layout_main
from spec_runner.spec_lang_format import main as spec_lang_format_main
from spec_runner.split_library_cases_per_symbol import main as split_library_cases_per_symbol_main


ROOT = Path(__file__).resolve().parents[3]
PROFILE_PATH = ROOT / "specs/schema/normalization_profile_v1.yaml"
_EXECUTABLE_CASE_TREE_ROOTS = (
    "specs/conformance/cases",
    "specs/governance/cases",
    "specs/impl",
)
_NON_MD_SPEC_GLOBS = ("*.spec.yaml", "*.spec.yml", "*.spec.json")
_DATA_ARTIFACT_GLOBS = (
    "specs/governance/metrics/*.json",
    "specs/governance/metrics/*.yaml",
    "docs/book/reference_manifest.yaml",
    "specs/schema/*.yaml",
)
_HARNESS_FILES = (
    "runners/python/spec_runner/harnesses/text_file.py",
    "runners/python/spec_runner/harnesses/cli_run.py",
    "runners/python/spec_runner/harnesses/orchestration_run.py",
    "runners/python/spec_runner/harnesses/docs_generate.py",
    "runners/python/spec_runner/harnesses/api_http.py",
)
_CHAIN_CLASS_VALUES = {"MUST", "MAY", "MUST_NOT"}
_CONTRACT_CLASS_VALUES = {"MUST", "MAY", "MUST_NOT"}
_LEGACY_CLASS_VALUES = {"must", "can", "cannot"}

def _load_profile(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: profile must be a mapping")
    return payload


def _scope_paths(profile: dict[str, Any], scope: str) -> list[str]:
    paths = profile.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("profile.paths must be a mapping")
    keys: tuple[str, ...]
    if scope == "all":
        keys = ("specs", "contracts", "tests")
    else:
        keys = (scope,)
    out: list[str] = []
    for key in keys:
        values = paths.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"profile.paths.{key} must be a list")
        for v in values:
            if isinstance(v, str) and v.strip():
                out.append(v.strip())
    return out


def _parse_explicit_paths(raw_csv: str, raw_paths: list[str]) -> list[str]:
    out: list[str] = []
    if raw_csv.strip():
        for item in raw_csv.split(","):
            token = item.strip()
            if token:
                out.append(token)
    for item in raw_paths:
        token = str(item).strip()
        if token:
            out.append(token)
    seen: set[str] = set()
    uniq: list[str] = []
    for rel in out:
        if rel in seen:
            continue
        seen.add(rel)
        uniq.append(rel)
    return uniq


def _run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    merged = "\n".join(x for x in (stdout, stderr) if x)
    return int(proc.returncode), merged


def _run_inproc(entry: Any, argv: list[str]) -> tuple[int, str]:
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
        code = int(entry(argv))
    return code, capture.getvalue().strip()


def _line_for(text: str, token: str) -> int:
    if not token:
        return 1
    idx = text.find(token)
    if idx < 0:
        return 1
    return text[:idx].count("\n") + 1


def _check_docs_tokens(profile: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    token_sync = profile.get("docs_token_sync", {})
    if not isinstance(token_sync, dict):
        return ["specs/schema/normalization_profile_v1.yaml:1: NORMALIZATION_PROFILE: docs_token_sync must be a mapping"]
    rules = token_sync.get("rules", [])
    if not isinstance(rules, list):
        return ["specs/schema/normalization_profile_v1.yaml:1: NORMALIZATION_PROFILE: docs_token_sync.rules must be a list"]
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = str(rule.get("id", "NORMALIZATION_DOC_TOKEN_SYNC")).strip() or "NORMALIZATION_DOC_TOKEN_SYNC"
        rel = str(rule.get("file", "")).strip()
        if not rel:
            continue
        p = ROOT / rel
        if not p.exists():
            issues.append(f"{rel}:1: {rule_id}: missing file")
            continue
        text = p.read_text(encoding="utf-8")
        must = rule.get("must_contain", [])
        must_not = rule.get("must_not_contain", [])
        if isinstance(must, list):
            for tok in must:
                if isinstance(tok, str) and tok and tok not in text:
                    issues.append(f"{rel}:1: {rule_id}: missing token: {tok}")
        if isinstance(must_not, list):
            for tok in must_not:
                if isinstance(tok, str) and tok and tok in text:
                    line = _line_for(text, tok)
                    issues.append(f"{rel}:{line}: {rule_id}: forbidden token present: {tok}")
    return issues


def _apply_replacements(profile: dict[str, Any]) -> tuple[list[str], int]:
    changed = 0
    issues: list[str] = []
    repl = profile.get("replacements", {})
    if not isinstance(repl, dict):
        return (["specs/schema/normalization_profile_v1.yaml:1: NORMALIZATION_PROFILE: replacements must be a mapping"], 0)
    rules = repl.get("rules", [])
    if not isinstance(rules, list):
        return (["specs/schema/normalization_profile_v1.yaml:1: NORMALIZATION_PROFILE: replacements.rules must be a list"], 0)
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = str(rule.get("id", "NORMALIZATION_REPLACEMENT")).strip() or "NORMALIZATION_REPLACEMENT"
        rel = str(rule.get("file", "")).strip()
        if not rel:
            continue
        p = ROOT / rel
        if not p.exists():
            issues.append(f"{rel}:1: {rule_id}: missing file")
            continue
        edits = rule.get("edits", [])
        if not isinstance(edits, list):
            issues.append(f"{rel}:1: {rule_id}: edits must be a list")
            continue
        original = p.read_text(encoding="utf-8")
        updated = original
        for e in edits:
            if not isinstance(e, dict):
                continue
            old = e.get("old")
            new = e.get("new")
            if not isinstance(old, str) or not isinstance(new, str):
                continue
            updated = updated.replace(old, new)
        if updated != original:
            p.write_text(updated, encoding="utf-8")
            changed += 1
    return issues, changed


def _check_replacements_drift(profile: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    repl = profile.get("replacements", {})
    if not isinstance(repl, dict):
        return issues
    rules = repl.get("rules", [])
    if not isinstance(rules, list):
        return issues
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = str(rule.get("id", "NORMALIZATION_REPLACEMENT")).strip() or "NORMALIZATION_REPLACEMENT"
        rel = str(rule.get("file", "")).strip()
        p = ROOT / rel
        if not rel or not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        edits = rule.get("edits", [])
        if not isinstance(edits, list):
            continue
        for e in edits:
            if not isinstance(e, dict):
                continue
            old = e.get("old")
            if isinstance(old, str) and old and old in text:
                line = _line_for(text, old)
                issues.append(f"{rel}:{line}: {rule_id}: normalization drift requires normalize-fix")
    return issues


def _check_dogfood_executable_surface() -> list[str]:
    issues: list[str] = []
    for rel_root in _EXECUTABLE_CASE_TREE_ROOTS:
        base = ROOT / rel_root
        if not base.exists() or not base.is_dir():
            continue
        for pattern in _NON_MD_SPEC_GLOBS:
            for p in sorted(x for x in base.rglob(pattern) if x.is_file()):
                rel = p.relative_to(ROOT).as_posix()
                issues.append(
                    f"{rel}:1: NORMALIZATION_EXECUTABLE_SURFACE_MARKDOWN_ONLY: canonical executable surfaces must use .spec.md"
                )
    libs_root = ROOT / "specs/libraries"
    if libs_root.exists():
        for pattern in _NON_MD_SPEC_GLOBS:
            for p in sorted(x for x in libs_root.rglob(pattern) if x.is_file()):
                rel = p.relative_to(ROOT).as_posix()
                issues.append(
                    f"{rel}:1: NORMALIZATION_LIBRARY_CASES_MARKDOWN_ONLY: spec_lang library cases must use .spec.md"
                )
    for glob in _DATA_ARTIFACT_GLOBS:
        for p in sorted(ROOT.glob(glob)):
            if not p.is_file():
                continue
            raw = p.read_text(encoding="utf-8")
            token = "```yaml contract-spec"
            if token in raw:
                line = _line_for(raw, token)
                rel = p.relative_to(ROOT).as_posix()
                issues.append(
                    f"{rel}:{line}: NORMALIZATION_DATA_ARTIFACT_NON_EXECUTABLE: data artifacts must not embed yaml contract-spec fences"
                )
    return issues


def _check_harness_componentization() -> list[str]:
    issues: list[str] = []
    required_tokens = (
        "build_execution_context(",
        "run_assertions_with_context(",
        "resolve_subject_for_target(",
    )
    forbidden_tokens = (
        "compile_import_bindings(",
        "limits_from_harness(",
        "load_spec_lang_symbols_for_case(",
        "evaluate_internal_assert_tree(",
    )
    for rel in _HARNESS_FILES:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for tok in required_tokens:
            if tok not in text:
                issues.append(f"{rel}:1: NORMALIZATION_HARNESS_COMPONENTIZATION: missing token {tok}")
        for tok in forbidden_tokens:
            if tok in text:
                issues.append(f"{rel}:1: NORMALIZATION_HARNESS_COMPONENTIZATION: forbidden legacy token {tok}")
    return issues


def _check_spec_lang_library_type_forbidden() -> list[str]:
    issues: list[str] = []
    for rel, case in _iter_spec_markdown_cases():
        case_id = str(case.get("id", "<missing>")).strip() or "<missing>"
        if str(case.get("type", "")).strip() == "spec_lang.export":
            issues.append(
                f"{rel}:1: NORMALIZATION_SPEC_EXPORT_HARD_CUT: case {case_id} uses forbidden type spec_lang.export; use spec.export"
            )
    return issues


def _iter_spec_markdown_cases() -> list[tuple[str, dict[str, Any]]]:
    pairs: list[tuple[str, dict[str, Any]]] = []
    roots = (ROOT / "specs", ROOT / "tests")
    for base in roots:
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.spec.md")):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT).as_posix()
            try:
                loaded = load_external_cases(p, formats={"md"})
            except Exception:
                continue
            for _doc_path, case in loaded:
                if isinstance(case, dict):
                    pairs.append((rel, case))
    return pairs


def _check_chain_contract_shape() -> list[str]:
    issues: list[str] = []
    for rel, case in _iter_spec_markdown_cases():
        case_id = str(case.get("id", "<missing>")).strip() or "<missing>"
        if "chain" in case:
            issues.append(
                f"{rel}:1: NORMALIZATION_CHAIN_SINGLE_LOCATION: case {case_id} top-level chain is forbidden; use harness.use"
            )
        harness = case.get("harness")
        if not isinstance(harness, dict):
            continue
        for key, value in harness.items():
            if key in {"chain", "use"}:
                continue
            if isinstance(value, dict) and "chain" in value:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SINGLE_LOCATION: case {case_id} type-specific {key}.chain is forbidden; use harness.use"
                )
        if "chain" in harness:
            issues.append(
                f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.chain is forbidden; use harness.use"
            )
        use = harness.get("use")
        if use is None:
            continue
        if not isinstance(use, list):
            issues.append(
                f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use must be a non-empty list when provided"
            )
            continue
        if not use:
            issues.append(
                f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use must be a non-empty list when provided"
            )
            continue
        for idx, step in enumerate(use):
            if not isinstance(step, dict):
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use[{idx}] must be mapping"
                )
                continue
            alias = str(step.get("as", "")).strip()
            ref = step.get("ref")
            symbols = step.get("symbols")
            if not alias:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use[{idx}].as must be non-empty string"
                )
            if isinstance(ref, dict):
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use[{idx}].ref legacy mapping form is forbidden; use scalar [path][#case_id]"
                )
            elif not isinstance(ref, str) or not ref.strip():
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use[{idx}].ref must be non-empty string"
                )
            if not isinstance(symbols, list) or not symbols:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use[{idx}].symbols must be non-empty list"
                )
            elif any(not str(name).strip() for name in symbols):
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use[{idx}].symbols entries must be non-empty strings"
                )
            if "class" in step or "allow_continue" in step:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use[{idx}] contains forbidden chain-only keys"
                )
            if "imports" in step or "exports" in step:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.use[{idx}] contains forbidden keys imports/exports"
                )
        raw_exports = harness.get("exports")
        if raw_exports is not None and not isinstance(raw_exports, list):
            issues.append(
                f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.exports must be a list when provided"
            )
        if isinstance(raw_exports, list):
            for exp_idx, exp in enumerate(raw_exports):
                if not isinstance(exp, dict):
                    issues.append(
                        f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.exports[{exp_idx}] must be mapping"
                    )
                    continue
                if "from_target" in exp:
                    issues.append(
                        f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.exports[{exp_idx}] legacy key from_target is forbidden; use from"
                    )
                if "as" not in exp or not str(exp.get("as", "")).strip():
                    issues.append(
                        f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.exports[{exp_idx}].as is required"
                    )
                from_source = str(exp.get("from", "")).strip()
                if from_source != "assert.function":
                    issues.append(
                        f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.exports[{exp_idx}].from must be assert.function"
                    )
                if not str(exp.get("path", "")).strip():
                    issues.append(
                        f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.exports[{exp_idx}].path is required for from=assert.function"
                    )
                params = exp.get("params")
                if params is not None and (not isinstance(params, list) or not params):
                    issues.append(
                        f"{rel}:1: NORMALIZATION_CHAIN_SCHEMA: case {case_id} harness.exports[{exp_idx}].params must be non-empty list when provided"
                    )
    return issues


def _check_executable_spec_lang_includes_forbidden() -> list[str]:
    issues: list[str] = []
    for rel, case in _iter_spec_markdown_cases():
        case_id = str(case.get("id", "<missing>")).strip() or "<missing>"
        harness = case.get("harness")
        if not isinstance(harness, dict):
            continue
        spec_lang = harness.get("spec_lang")
        if not isinstance(spec_lang, dict):
            continue
        includes = spec_lang.get("includes")
        if isinstance(includes, list) and includes:
            issues.append(
                f"{rel}:1: NORMALIZATION_EXECUTABLE_CHAIN_FIRST: case {case_id} harness.spec_lang.includes is forbidden for executable cases; use harness.chain"
            )
    return issues


def _check_library_single_public_symbol() -> list[str]:
    # Removed with hard-cut: spec_lang.export is forbidden.
    return []


def _check_contract_terminology_hard_cut() -> list[str]:
    issues: list[str] = []
    for rel, case in _iter_spec_markdown_cases():
        case_id = str(case.get("id", "<missing>")).strip() or "<missing>"
        if "assert" in case:
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} legacy top-level assert key is forbidden; use contract"
            )
        contract = case.get("contract")
        if contract is None:
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} missing required contract key"
            )
            continue
        if isinstance(contract, list):
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} v1 contract list is forbidden; use contract.defaults + contract.steps"
            )
            continue
        if not isinstance(contract, dict):
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract must be mapping"
            )
            continue
        defaults = contract.get("defaults")
        if defaults is not None and not isinstance(defaults, dict):
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.defaults must be mapping"
            )
        steps = contract.get("steps")
        if not isinstance(steps, list):
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.steps must be a list"
            )
            continue
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.steps[{idx}] must be mapping"
                )
                continue
            step_class = str(step.get("class", "MUST")).strip() or "MUST"
            if step_class in _LEGACY_CLASS_VALUES or step_class not in _CONTRACT_CLASS_VALUES:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.steps[{idx}].class must be MUST, MAY, MUST_NOT"
                )
            if "asserts" in step:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.steps[{idx}].asserts is forbidden; use assert"
                )
            if "target" in step:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.steps[{idx}].target is forbidden; use imports"
                )
            if "on" in step:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.steps[{idx}].on is forbidden; use imports"
                )
            raw_assert = step.get("assert")
            if raw_assert is None:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.steps[{idx}].assert is required"
                )
            elif isinstance(raw_assert, list) and not raw_assert:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: case {case_id} contract.steps[{idx}].assert list must be non-empty"
                )

    spec_root = ROOT / "specs"
    if spec_root.exists():
        for p in sorted(spec_root.rglob("*.spec.md")):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT).as_posix()
            raw = p.read_text(encoding="utf-8")
            if "spec-test" in raw:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: legacy spec-test token is forbidden; use contract-spec"
                )
            if "```yaml contract-spec" not in raw:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_TERMS: missing required contract-spec fence token"
                )
    return issues


def _check_contract_job_dispatch_hard_cut() -> list[str]:
    issues: list[str] = []
    for rel, case in _iter_spec_markdown_cases():
        case_id = str(case.get("id", "<missing>")).strip() or "<missing>"
        if str(case.get("type", "")).strip() != "contract.job":
            continue
        harness = case.get("harness")
        if not isinstance(harness, dict):
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} harness must be mapping"
            )
            continue
        if "job" in harness:
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} legacy harness.job is forbidden; use harness.jobs"
            )
        jobs = harness.get("jobs")
        if not isinstance(jobs, dict) or not jobs:
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} harness.jobs must be non-empty mapping"
            )
            continue
        for name, entry in jobs.items():
            if not isinstance(name, str) or not name.strip():
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} harness.jobs keys must be non-empty strings"
                )
            if not isinstance(entry, dict):
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} harness.jobs.{name} must be mapping"
                )
                continue
            if "ref" in entry:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} harness.jobs.{name}.ref is forbidden"
                )
            helper = str(entry.get("helper", "")).strip()
            if not helper:
                issues.append(
                    f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} harness.jobs.{name}.helper is required"
                )

        contract = case.get("contract")
        raw = yaml.safe_dump(contract, sort_keys=False)
        if "ops.job.dispatch" not in raw:
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} contract must include ops.job.dispatch expression"
            )

        spec_lang = harness.get("spec_lang")
        caps = spec_lang.get("capabilities") if isinstance(spec_lang, dict) else None
        if not isinstance(caps, list) or "ops.job" not in caps:
            issues.append(
                f"{rel}:1: NORMALIZATION_CONTRACT_JOB_DISPATCH: case {case_id} harness.spec_lang.capabilities must include ops.job"
            )
    return issues


def _check_when_hooks_shape() -> list[str]:
    issues: list[str] = []
    allowed = {"must", "may", "must_not", "fail", "complete"}
    for rel, case in _iter_spec_markdown_cases():
        case_id = str(case.get("id", "<missing>")).strip() or "<missing>"
        harness = case.get("harness")
        if harness is None:
            continue
        if not isinstance(harness, dict):
            continue
        if "on" in harness:
            issues.append(
                f"{rel}:1: NORMALIZATION_WHEN_HOOKS: case {case_id} harness.on is forbidden; use when"
            )
        if "when" in harness:
            issues.append(
                f"{rel}:1: NORMALIZATION_WHEN_HOOKS: case {case_id} harness.when is forbidden; use when"
            )
        hooks = case.get("when")
        if hooks is None:
            continue
        if not isinstance(hooks, dict):
            issues.append(
                f"{rel}:1: NORMALIZATION_WHEN_HOOKS: case {case_id} when must be a mapping"
            )
            continue
        for key, exprs in hooks.items():
            key_name = str(key).strip()
            if key_name not in allowed:
                issues.append(
                    f"{rel}:1: NORMALIZATION_WHEN_HOOKS: case {case_id} when contains unknown key {key_name}"
                )
                continue
            if not isinstance(exprs, list) or not exprs:
                issues.append(
                    f"{rel}:1: NORMALIZATION_WHEN_HOOKS: case {case_id} when.{key_name} must be non-empty list"
                )
                continue
            for idx, expr in enumerate(exprs):
                if not isinstance(expr, dict):
                    issues.append(
                        f"{rel}:1: NORMALIZATION_WHEN_HOOKS: case {case_id} when.{key_name}[{idx}] must be mapping expression"
                    )
    return issues


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Unified normalization check/fix runner for specs, contracts, and tests.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="verify normalization without modifying files")
    mode.add_argument("--write", action="store_true", help="apply normalization rewrites")
    ap.add_argument("--scope", choices=("specs", "contracts", "tests", "all"), default="all")
    ap.add_argument("--paths", default="", help="comma-separated files/directories for changed-path normalization")
    ap.add_argument("--path", action="append", default=[], help="repeatable file/directory path for changed-path normalization")
    ap.add_argument("--profile", default=str(PROFILE_PATH), help="path to normalization profile yaml")
    ns = ap.parse_args(argv)

    profile = _load_profile(Path(ns.profile))
    explicit_paths = _parse_explicit_paths(str(ns.paths), [str(x) for x in ns.path])
    scope_paths = explicit_paths if explicit_paths else _scope_paths(profile, ns.scope)
    if not scope_paths:
        print("specs/schema/normalization_profile_v1.yaml:1: NORMALIZATION_PROFILE: no paths selected for scope")
        return 1

    mode_flag = "--check" if ns.check else "--write"
    changed_path_mode = bool(explicit_paths)

    issues: list[str] = []
    if not changed_path_mode:
        docs_layout_code, docs_layout_out = _run_inproc(normalize_docs_layout_main, [mode_flag])
        if docs_layout_code != 0:
            for line in docs_layout_out.splitlines():
                line = line.strip()
                if line:
                    issues.append(f"docs:1: NORMALIZATION_DOCS_LAYOUT: {line}")
        split_lib_code, split_lib_out = _run_inproc(
            split_library_cases_per_symbol_main,
            [mode_flag, "specs/libraries"],
        )
        if split_lib_code != 0:
            for line in split_lib_out.splitlines():
                line = line.strip()
                if line:
                    issues.append(f"specs:1: NORMALIZATION_LIBRARY_SINGLE_PUBLIC_SYMBOL: {line}")
    style_code, style_out = _run_inproc(spec_lang_format_main, [mode_flag, *scope_paths])
    if style_code != 0:
        for line in style_out.splitlines():
            line = line.strip()
            if line:
                issues.append(f"specs:1: NORMALIZATION_SPEC_STYLE: {line}")

    if ns.write:
        changed = 0
        if not changed_path_mode:
            repl_issues, changed = _apply_replacements(profile)
            issues.extend(repl_issues)
            token_issues = _check_docs_tokens(profile)
            issues.extend(token_issues)
            issues.extend(_check_dogfood_executable_surface())
        if issues:
            for issue in sorted(issues):
                print(issue)
            return 1
        print(f"OK: normalization fix complete (replacement files changed: {changed})")
        return 0

    if not changed_path_mode:
        issues.extend(_check_replacements_drift(profile))
        issues.extend(_check_docs_tokens(profile))
        issues.extend(_check_dogfood_executable_surface())
        issues.extend(_check_harness_componentization())
        issues.extend(_check_spec_lang_library_type_forbidden())
        issues.extend(_check_chain_contract_shape())
        issues.extend(_check_executable_spec_lang_includes_forbidden())
        issues.extend(_check_library_single_public_symbol())
        issues.extend(_check_contract_terminology_hard_cut())
        issues.extend(_check_contract_job_dispatch_hard_cut())
        issues.extend(_check_when_hooks_shape())
    if issues:
        for issue in sorted(issues):
            print(issue)
        return 1

    print("OK: normalization check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
