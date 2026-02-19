from __future__ import annotations

import hashlib
import fnmatch
import json
import re
from pathlib import Path
from typing import Any, Mapping

import yaml
from spec_runner.codecs import load_external_cases
from spec_runner.contract_governance import contract_coverage_jsonable
from spec_runner.dispatcher import iter_cases
from spec_runner.docs_quality import (
    check_command_examples_verified,
    check_instructions_complete,
    check_token_dependency_resolved,
    check_token_ownership_unique,
    load_docs_meta_for_paths,
    load_reference_manifest,
    manifest_chapter_paths,
)
from spec_runner.settings import SETTINGS
from spec_runner.spec_lang import SpecLangLimits
from spec_runner.spec_lang_libraries import load_spec_lang_symbols_for_case
from spec_runner.spec_portability import spec_portability_report_jsonable
from spec_runner.virtual_paths import VirtualPathError, resolve_contract_path


def _as_list_of_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            s = item.strip()
            if s:
                out.append(s)
    return out


def _match_segment(rel_path: str, segment_rules: list[dict[str, str]]) -> str:
    normalized = rel_path.replace("\\", "/").lstrip("/")
    for rule in segment_rules:
        prefix = str(rule["prefix"]).replace("\\", "/").lstrip("/").rstrip("/")
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return str(rule["segment"])
    return "other"


def _safe_ratio(num: float, den: float, *, default: float = 0.0) -> float:
    if den <= 0:
        return default
    return num / den


def _is_governance_case(case: Mapping[str, Any]) -> bool:
    case_type = str(case.get("type", "")).strip()
    if case_type != "contract.check":
        return False
    harness = case.get("harness")
    if not isinstance(harness, dict):
        return False
    check_cfg = harness.get("check")
    if not isinstance(check_cfg, dict):
        return False
    return str(check_cfg.get("profile", "")).strip() == "governance.scan"


def _summarize_segment(rows: list[dict[str, Any]], fields: list[str]) -> dict[str, Any]:
    count = len(rows)
    out: dict[str, Any] = {"case_count": count}
    for field in fields:
        if count == 0:
            out[f"mean_{field}"] = 0.0
        else:
            out[f"mean_{field}"] = sum(float(r.get(field, 0.0)) for r in rows) / count
    return out


def _compile_direction_map(value: object, *, default_direction: str = "non_decrease") -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.strip():
                out[item.strip()] = default_direction
        return out
    if isinstance(value, dict):
        for k, v in value.items():
            key = str(k).strip()
            if not key:
                continue
            direction = str(v).strip() if isinstance(v, str) else default_direction
            if direction not in {"non_decrease", "non_increase"}:
                direction = default_direction
            out[key] = direction
    return out


def compare_metric_non_regression(
    *,
    current: dict[str, Any],
    baseline: dict[str, Any],
    summary_fields: object,
    segment_fields: object,
    epsilon: float,
) -> list[str]:
    violations: list[str] = []
    summary_map = _compile_direction_map(summary_fields)
    if not summary_map:
        return ["non-regression config summary_fields must declare at least one field"]

    seg_map_in = segment_fields if isinstance(segment_fields, dict) else {}
    compiled_seg_map: dict[str, dict[str, str]] = {}
    for segment, fields in seg_map_in.items():
        seg = str(segment).strip()
        if not seg:
            continue
        compiled = _compile_direction_map(fields)
        if not compiled:
            violations.append(f"segment_fields.{seg} must declare at least one field")
            continue
        compiled_seg_map[seg] = compiled

    def _resolve(payload: object, dotted: str) -> float | None:
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

    for field, direction in summary_map.items():
        cur = _resolve(current, f"summary.{field}")
        base = _resolve(baseline, f"summary.{field}")
        if cur is None:
            violations.append(f"summary.{field}: missing numeric current metric")
            continue
        if base is None:
            violations.append(f"baseline summary.{field}: missing numeric baseline metric")
            continue
        if direction == "non_decrease" and cur + epsilon < base:
            violations.append(f"summary.{field}: regressed from baseline {base:.12g} to {cur:.12g}")
        if direction == "non_increase" and cur - epsilon > base:
            violations.append(f"summary.{field}: increased from baseline {base:.12g} to {cur:.12g}")

    for segment, fields in compiled_seg_map.items():
        for field, direction in fields.items():
            cur = _resolve(current, f"segments.{segment}.{field}")
            base = _resolve(baseline, f"segments.{segment}.{field}")
            if cur is None:
                violations.append(f"segments.{segment}.{field}: missing numeric current metric")
                continue
            if base is None:
                violations.append(f"baseline segments.{segment}.{field}: missing numeric baseline metric")
                continue
            if direction == "non_decrease" and cur + epsilon < base:
                violations.append(
                    f"segments.{segment}.{field}: regressed from baseline {base:.12g} to {cur:.12g}"
                )
            if direction == "non_increase" and cur - epsilon > base:
                violations.append(
                    f"segments.{segment}.{field}: increased from baseline {base:.12g} to {cur:.12g}"
                )

    return violations


def _load_baseline_json(repo_root: Path, baseline_path: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        path = resolve_contract_path(repo_root, baseline_path, field="baseline_path")
    except VirtualPathError as exc:
        return None, [str(exc)]
    if not path.exists():
        return None, [f"{baseline_path}:1: missing baseline metrics file"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{baseline_path}:1: invalid JSON baseline: {exc.msg} at line {exc.lineno} column {exc.colno}"]
    if not isinstance(payload, dict):
        return None, [f"{baseline_path}:1: baseline payload must be a JSON object"]
    return payload, []


def default_spec_lang_adoption_config() -> dict[str, Any]:
    cfg = SETTINGS.spec_portability
    return {
        "roots": list(cfg.roots),
        "segment_rules": [{"prefix": r.prefix, "segment": r.segment} for r in cfg.segment_rules],
        "recursive": bool(cfg.recursive),
        "tests_glob": "tests/test_*_unit.py",
        "native_escape_test_tokens": ["not yet representable", "DSL", "spec model"],
    }


def _collect_leaf_ops(node: object, *, inherited_target: str | None = None) -> list[str]:
    ops: list[str] = []
    if isinstance(node, list):
        for child in node:
            ops.extend(_collect_leaf_ops(child, inherited_target=inherited_target))
        return ops
    if not isinstance(node, dict):
        return ops
    if "steps" in node and isinstance(node.get("steps"), list):
        defaults = node.get("defaults")
        default_on = str((defaults or {}).get("on", "")).strip() if isinstance(defaults, dict) else ""
        for step in node.get("steps") or []:
            if not isinstance(step, dict):
                continue
            step_target = str(step.get("on", "")).strip() or default_on or inherited_target
            checks = step.get("assert")
            if isinstance(checks, list):
                for child in checks:
                    ops.extend(_collect_leaf_ops(child, inherited_target=step_target))
            elif checks is not None:
                ops.extend(_collect_leaf_ops(checks, inherited_target=step_target))
        return ops
    step_class = str(node.get("class", "")).strip() if "class" in node else ""
    if step_class in {"MUST", "MAY", "MUST_NOT"} and "asserts" in node:
        node_target = str(node.get("target", "")).strip() or inherited_target
        checks = node.get("asserts")
        if isinstance(checks, list):
            for child in checks:
                ops.extend(_collect_leaf_ops(child, inherited_target=node_target))
        return ops
    present_groups = [k for k in ("MUST", "MAY", "MUST_NOT") if k in node]
    if present_groups:
        node_target = str(node.get("target", "")).strip() or inherited_target
        for key in present_groups:
            children = node.get(key, [])
            if isinstance(children, list):
                for child in children:
                    ops.extend(_collect_leaf_ops(child, inherited_target=node_target))
        return ops
    if "target" in node:
        return ops
    if "evaluate" in node:
        return ["evaluate"]
    # Expression-mapping leaf (operator-keyed mapping AST) counts as evaluate.
    return ["evaluate"]
    return ops


def _contains_key_recursive(payload: object, key: str) -> bool:
    if isinstance(payload, dict):
        if key in payload:
            return True
        return any(_contains_key_recursive(v, key) for v in payload.values())
    if isinstance(payload, list):
        return any(_contains_key_recursive(v, key) for v in payload)
    return False


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


def _count_python_decision_branches(repo_root: Path) -> int:
    """
    Counts explicit check-level policy verdict branches in governance script.
    This tracks migration progress toward centralized policy evaluation.
    """
    p = repo_root / "runners/python/spec_runner/governance_runtime.py"
    if not p.exists():
        return 0
    raw = p.read_text(encoding="utf-8")
    patterns = ("if not ok:",)
    return sum(raw.count(tok) for tok in patterns)


def _library_public_surface_ratio(repo_root: Path) -> tuple[float, int, int]:
    libs_root = repo_root / "specs/libraries"
    if not libs_root.exists():
        return 1.0, 0, 0
    public_count = 0
    total_count = 0
    for lib_file in sorted(libs_root.rglob(SETTINGS.case.default_file_pattern)):
        if not lib_file.is_file():
            continue
        for _doc_path, case in load_external_cases(lib_file, formats={"md"}):
            if str(case.get("type", "")).strip() != "contract.export":
                continue
            defines = case.get("defines")
            if not isinstance(defines, dict):
                continue
            public_keys: list[str] = []
            private_keys: list[str] = []
            scoped_public = defines.get("public")
            scoped_private = defines.get("private")
            if isinstance(scoped_public, dict):
                public_keys.extend(str(k).strip() for k in scoped_public.keys())
            if isinstance(scoped_private, dict):
                private_keys.extend(str(k).strip() for k in scoped_private.keys())
            public_keys = [k for k in public_keys if k]
            private_keys = [k for k in private_keys if k]
            public_count += len(public_keys)
            total_count += len(public_keys) + len(private_keys)
    if total_count == 0:
        return 1.0, 0, 0
    return float(public_count) / float(total_count), public_count, total_count


def spec_lang_adoption_report_jsonable(repo_root: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    root = repo_root.resolve()
    cfg = default_spec_lang_adoption_config()
    if isinstance(config, dict):
        cfg.update(config)

    roots = _as_list_of_strings(cfg.get("roots"))
    raw_rules_obj = cfg.get("segment_rules")
    raw_rules = raw_rules_obj if isinstance(raw_rules_obj, list) else []
    rules: list[dict[str, str]] = []
    for item in raw_rules:
        if isinstance(item, dict):
            prefix = str(item.get("prefix", "")).strip()
            seg = str(item.get("segment", "")).strip()
            if prefix and seg:
                rules.append({"prefix": prefix, "segment": seg})

    recursive = bool(cfg.get("recursive", True))
    rows: list[dict[str, Any]] = []
    errs: list[str] = []

    for rel_root in roots:
        try:
            base = resolve_contract_path(root, rel_root, field="roots[]")
        except VirtualPathError:
            errs.append(f"{rel_root}: invalid spec root path")
            continue
        if not base.exists() or not base.is_dir():
            errs.append(f"{rel_root}: missing spec root directory")
            continue

        if recursive:
            files = sorted(base.rglob(SETTINGS.case.default_file_pattern))
            case_pairs: list[tuple[Path, dict[str, Any]]] = []
            for file_path in files:
                if not file_path.is_file():
                    continue
                for doc_path, case in load_external_cases(file_path, formats={"md"}):
                    case_pairs.append((doc_path, case))
        else:
            case_pairs = [(spec.doc_path, spec.test) for spec in iter_cases(base, file_pattern=SETTINGS.case.default_file_pattern)]

        for doc_path, case in case_pairs:
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            case_type = str(case.get("type", "")).strip()
            try:
                rel_path = str(doc_path.resolve().relative_to(root)).replace("\\", "/")
            except ValueError:
                rel_path = str(doc_path)
            segment = _match_segment(rel_path, rules)
            ops = _collect_leaf_ops(case.get("contract", []) or [])
            total_leaf = len(ops)
            eval_leaf = sum(1 for op in ops if op == "evaluate")
            logic_ratio = 1.0 if total_leaf == 0 else _safe_ratio(eval_leaf, total_leaf, default=1.0)
            native_hint = False
            harness = case.get("harness")
            has_library_paths = False
            governance_symbol_resolution = 1.0
            if isinstance(harness, dict):
                spec_lang_cfg = harness.get("spec_lang")
                if isinstance(spec_lang_cfg, dict):
                    lib_paths = spec_lang_cfg.get("includes")
                    has_library_paths = isinstance(lib_paths, list) and any(
                        isinstance(x, str) and x.strip() for x in lib_paths
                    )
                chain_cfg = harness.get("chain")
                if isinstance(chain_cfg, dict):
                    imports_cfg = chain_cfg.get("imports")
                    if isinstance(imports_cfg, list):
                        for item in imports_cfg:
                            if not isinstance(item, dict):
                                continue
                            names = item.get("names")
                            if isinstance(names, list) and any(
                                isinstance(x, str) and x.strip() for x in names
                            ):
                                has_library_paths = True
                                break
                if _is_governance_case(case):
                    try:
                        symbols = load_spec_lang_symbols_for_case(
                            doc_path=doc_path,
                            harness=harness,
                            limits=SpecLangLimits(),
                        )
                        if not symbols:
                            governance_symbol_resolution = 0.0
                    except Exception as exc:  # noqa: BLE001
                        governance_symbol_resolution = 0.0
                        errs.append(
                            f"{rel_path}: case {case_id} unable to load governance symbols ({exc})"
                        )
            if _is_governance_case(case):
                native_hint = False
            rows.append(
                {
                    "id": case_id,
                    "type": case_type,
                    "file": rel_path,
                    "segment": segment,
                    "logic_self_contained_ratio": logic_ratio,
                    "native_logic_escape_hint": 1.0 if native_hint else 0.0,
                    "library_backed_policy": 1.0 if (_is_governance_case(case) and has_library_paths) else 0.0,
                    "library_backed_case": 1.0 if has_library_paths else 0.0,
                    "governance_symbol_resolution": governance_symbol_resolution
                    if _is_governance_case(case)
                    else 1.0,
                }
            )

    tests_glob = str(cfg.get("tests_glob", "tests/test_*_unit.py")).strip() or "tests/test_*_unit.py"
    escape_tokens = [t.lower() for t in _as_list_of_strings(cfg.get("native_escape_test_tokens"))]
    unit_opt_out_count = 0
    for p in sorted(root.glob(tests_glob)):
        text = p.read_text(encoding="utf-8")
        if "# SPEC-OPT-OUT:" not in text:
            continue
        lower = text.lower()
        if not escape_tokens or any(tok in lower for tok in escape_tokens):
            unit_opt_out_count += 1

    rows.sort(key=lambda r: (str(r["segment"]), str(r["file"]), str(r["id"])))
    segments_order = [str(r["segment"]) for r in rules] + ["other"]
    seen: list[str] = []
    for seg in segments_order + [str(r["segment"]) for r in rows]:
        if seg not in seen:
            seen.append(seg)

    segments: dict[str, Any] = {}
    for seg in seen:
        seg_rows = [r for r in rows if str(r["segment"]) == seg]
        summary = _summarize_segment(
            seg_rows,
            [
                "logic_self_contained_ratio",
                "native_logic_escape_hint",
                "library_backed_policy",
                "library_backed_case",
            ],
        )
        summary["native_logic_escape_case_ratio"] = summary.pop("mean_native_logic_escape_hint")
        summary["library_backed_policy_ratio"] = summary.pop("mean_library_backed_policy")
        summary["library_backed_case_ratio"] = summary.pop("mean_library_backed_case")
        segments[seg] = summary

    total = len(rows)
    overall_logic = _safe_ratio(sum(float(r["logic_self_contained_ratio"]) for r in rows), float(total), default=0.0)
    native_ratio = _safe_ratio(sum(float(r["native_logic_escape_hint"]) for r in rows), float(total), default=0.0)
    gov_rows = [r for r in rows if _is_governance_case(r)]
    gov_total = len(gov_rows)
    gov_library_ratio = _safe_ratio(
        sum(float(r.get("library_backed_policy", 0.0)) for r in gov_rows),
        float(gov_total),
        default=0.0,
    )
    impl_rows = [r for r in rows if str(r.get("segment", "")) == "impl"]
    impl_library_case_ratio = _safe_ratio(
        sum(float(r.get("library_backed_case", 0.0)) for r in impl_rows),
        float(len(impl_rows)),
        default=0.0,
    )
    gov_symbol_resolution_ratio = _safe_ratio(
        sum(float(r.get("governance_symbol_resolution", 0.0)) for r in gov_rows),
        float(gov_total),
        default=1.0,
    )
    library_public_ratio, library_public_count, library_total_count = _library_public_surface_ratio(root)

    for seg, summary in segments.items():
        seg_gov_rows = [
            r
            for r in rows
            if str(r.get("segment", "")) == seg and _is_governance_case(r)
        ]
        if not seg_gov_rows:
            summary["governance_symbol_resolution_ratio"] = 1.0
        else:
            summary["governance_symbol_resolution_ratio"] = _safe_ratio(
                sum(float(r.get("governance_symbol_resolution", 0.0)) for r in seg_gov_rows),
                float(len(seg_gov_rows)),
                default=1.0,
            )

    return {
        "version": 1,
        "summary": {
            "total_cases": total,
            "overall_logic_self_contained_ratio": overall_logic,
            "native_logic_escape_case_ratio": native_ratio,
            "governance_library_backed_policy_ratio": gov_library_ratio,
            "impl_library_backed_case_ratio": impl_library_case_ratio,
            "governance_symbol_resolution_ratio": gov_symbol_resolution_ratio,
            "library_public_surface_ratio": library_public_ratio,
            "library_public_symbol_count": library_public_count,
            "library_total_symbol_count": library_total_count,
            "unit_opt_out_count": unit_opt_out_count,
            "python_decision_branch_count": _count_python_decision_branches(root),
        },
        "segments": segments,
        "cases": rows,
        "config": cfg,
        "errors": errs,
    }


def default_runner_independence_config() -> dict[str, Any]:
    return {
        "segment_files": {
            "gate_scripts": ["scripts/ci_gate.sh", "scripts/core_gate.sh", "scripts/docs_doctor.sh"],
            "ci_workflows": [".github/workflows/*.yml", ".github/workflows/*.yaml"],
            "adapter_interfaces": [
                "runners/public/runner_adapter.sh",
                "runners/python/runner_adapter.sh",
                "runners/rust/runner_adapter.sh",
                "runners/rust/spec_runner_cli/src/main.rs",
            ],
        },
        "direct_runtime_tokens": [
            "spec_lang_commands run-governance-specs",
            "spec_lang_commands spec-lang-format --check specs",
            "scripts/spec_portability_report.py",
            "python -m pytest",
            "php runners/php/spec_runner.php",
        ],
        "direct_runtime_token_segments": ["gate_scripts", "ci_workflows"],
        "gate_required_tokens": ["SPEC_RUNNER_BIN", "runners/public/runner_adapter.sh"],
        "rust_ci_required_tokens": [
            "core-gate-rust-adapter:",
            "SPEC_RUNNER_BIN: ./runners/public/runner_adapter.sh",
            "SPEC_RUNNER_IMPL: rust",
            "run: ./scripts/core_gate.sh",
        ],
    }


def _matches_any_pattern(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        pat = str(pattern).replace("\\", "/")
        if fnmatch.fnmatch(normalized, pat):
            return True
    return False


def default_python_dependency_config() -> dict[str, Any]:
    return {
        "segment_files": {
            "default_gate": ["scripts/ci_gate.sh", "scripts/core_gate.sh", "scripts/docs_doctor.sh"],
            "public_adapter": ["runners/public/runner_adapter.sh"],
            "rust_adapter": ["runners/rust/runner_adapter.sh", "runners/rust/spec_runner_cli/src/main.rs"],
            "ci_workflows": [".github/workflows/*.yml", ".github/workflows/*.yaml"],
            "python_surfaces": ["scripts/python/*.sh", "scripts/python/*.py"],
        },
        "non_python_segments": ["default_gate", "rust_adapter"],
        "python_allowed_globs": [
            "scripts/python/*.sh",
            "scripts/python/*.py",
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
        ],
        "python_tokens": [
            "python -m ",
            "python3 ",
            "/usr/bin/env python",
            "PYTHON_BIN",
            "resolve_python_bin",
            "spec_lang_commands run-governance-specs",
            "spec_lang_commands spec-lang-format",
            "scripts/spec_portability_report.py",
            "scripts/ci_gate_summary.py",
            "python -m pytest",
        ],
        "rust_transitive_forbidden_tokens": [
            "runners/public/runner_adapter.sh",
            "runners/python/runner_adapter.sh",
            "spec_lang_commands run-governance-specs",
            "scripts/ci_gate_summary.py",
            "python -m ",
            "python3 ",
        ],
        "default_gate_required_tokens": [
            'SPEC_RUNNER_BIN="${ROOT_DIR}/runners/public/runner_adapter.sh"',
        ],
        "runtime_trace_path": ".artifacts/gate-exec-trace.json",
    }


def python_dependency_report_jsonable(repo_root: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    root = repo_root.resolve()
    cfg = default_python_dependency_config()
    if isinstance(config, dict):
        cfg.update(config)

    segment_files_obj = cfg.get("segment_files")
    segment_files: dict[str, Any] = segment_files_obj if isinstance(segment_files_obj, dict) else {}
    python_tokens = _as_list_of_strings(cfg.get("python_tokens"))
    rust_transitive_tokens = _as_list_of_strings(cfg.get("rust_transitive_forbidden_tokens"))
    non_python_segments = set(_as_list_of_strings(cfg.get("non_python_segments")))
    allowed_globs = _as_list_of_strings(cfg.get("python_allowed_globs"))
    default_gate_required_tokens = _as_list_of_strings(cfg.get("default_gate_required_tokens"))
    runtime_trace_path = str(cfg.get("runtime_trace_path", ".artifacts/gate-exec-trace.json")).strip()

    rows: list[dict[str, Any]] = []
    static_hits: list[dict[str, Any]] = []
    errors: list[str] = []
    default_gate_files = {"scripts/ci_gate.sh", "scripts/core_gate.sh", "scripts/docs_doctor.sh"}
    default_gate_total = 0
    default_gate_clean = 0
    non_python_hit_count = 0
    transitive_hit_count = 0
    scope_violation_count = 0

    for segment, patterns in segment_files.items():
        seg = str(segment).strip()
        if not seg:
            continue
        if not isinstance(patterns, list):
            errors.append(f"segment_files.{seg} must be a list")
            continue
        files: set[Path] = set()
        for pat in patterns:
            if not isinstance(pat, str) or not pat.strip():
                continue
            for path in root.glob(pat.strip()):
                if path.is_file():
                    files.add(path)
        for path in sorted(files):
            rel = str(path.resolve().relative_to(root)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            token_hits = [tok for tok in python_tokens if tok and tok in text]
            transitive_hits = [tok for tok in rust_transitive_tokens if tok and tok in text] if seg == "rust_adapter" else []
            in_non_python = seg in non_python_segments
            is_allowed_surface = _matches_any_pattern(rel, allowed_globs)
            if rel in default_gate_files:
                default_gate_total += 1
                has_required_defaults = all(tok in text for tok in default_gate_required_tokens)
                if has_required_defaults and not token_hits:
                    default_gate_clean += 1

            if in_non_python and token_hits:
                non_python_hit_count += len(token_hits)
                for tok in token_hits:
                    static_hits.append({"kind": "non_python_exec_token", "file": rel, "token": tok, "segment": seg})
            if transitive_hits:
                transitive_hit_count += len(transitive_hits)
                for tok in transitive_hits:
                    static_hits.append(
                        {"kind": "rust_transitive_token", "file": rel, "token": tok, "segment": seg}
                    )
            if token_hits and not is_allowed_surface:
                scope_violation_count += len(token_hits)

            rows.append(
                {
                    "file": rel,
                    "segment": seg,
                    "python_token_count": float(len(token_hits)),
                    "transitive_token_count": float(len(transitive_hits)),
                    "allowed_python_surface": 1.0 if is_allowed_surface else 0.0,
                }
            )

    runtime_trace: list[dict[str, Any]] = []
    runtime_non_python_hits = 0
    try:
        trace_file = resolve_contract_path(root, runtime_trace_path, field="runtime_trace_path")
    except VirtualPathError:
        trace_file = root / runtime_trace_path.lstrip("/")
    if trace_file.exists():
        try:
            payload = json.loads(trace_file.read_text(encoding="utf-8"))
            steps = payload.get("steps") if isinstance(payload, dict) else None
            runner_impl = str(payload.get("runner_impl", "")).strip() if isinstance(payload, dict) else ""
            lane = runner_impl if runner_impl in {"rust", "python"} else "rust"
            if isinstance(steps, list):
                for row in steps:
                    if not isinstance(row, dict):
                        continue
                    command = row.get("command")
                    if not isinstance(command, list):
                        continue
                    command_text = " ".join(str(x) for x in command)
                    cmd_hits = [tok for tok in python_tokens if tok and tok in command_text]
                    if lane == "rust" and cmd_hits:
                        runtime_non_python_hits += len(cmd_hits)
                    runtime_trace.append(
                        {
                            "name": str(row.get("name", "")),
                            "lane": lane,
                            "command": command,
                            "python_tokens": cmd_hits,
                        }
                    )
        except json.JSONDecodeError as exc:
            errors.append(
                f"{runtime_trace_path}:1: invalid JSON runtime trace: {exc.msg} at line {exc.lineno} column {exc.colno}"
            )

    rows.sort(key=lambda r: (str(r["segment"]), str(r["file"])))
    total_files = len(rows)
    default_lane_ratio = _safe_ratio(float(default_gate_clean), float(max(1, default_gate_total)), default=0.0)

    return {
        "version": 1,
        "summary": {
            "total_files": total_files,
            "non_python_lane_python_exec_count": int(non_python_hit_count + runtime_non_python_hits),
            "transitive_adapter_python_exec_count": int(transitive_hit_count),
            "default_lane_python_free_ratio": default_lane_ratio,
            "python_usage_scope_violation_count": int(scope_violation_count),
        },
        "files": rows,
        "evidence": {
            "static_hits": static_hits,
            "runtime_trace": runtime_trace,
        },
        "config": cfg,
        "errors": errors,
    }


def runner_independence_report_jsonable(repo_root: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    root = repo_root.resolve()
    cfg = default_runner_independence_config()
    if isinstance(config, dict):
        cfg.update(config)

    segment_files_obj = cfg.get("segment_files")
    segment_files: dict[str, Any] = segment_files_obj if isinstance(segment_files_obj, dict) else {}
    direct_tokens = _as_list_of_strings(cfg.get("direct_runtime_tokens"))
    token_segments = set(_as_list_of_strings(cfg.get("direct_runtime_token_segments")))
    gate_required = _as_list_of_strings(cfg.get("gate_required_tokens"))
    rust_required = _as_list_of_strings(cfg.get("rust_ci_required_tokens"))

    rows: list[dict[str, Any]] = []
    errors: list[str] = []

    for segment, patterns in segment_files.items():
        seg = str(segment).strip()
        if not seg:
            continue
        if not isinstance(patterns, list):
            errors.append(f"segment_files.{seg} must be a list")
            continue
        files: set[Path] = set()
        for pat in patterns:
            if not isinstance(pat, str) or not pat.strip():
                continue
            for p in root.glob(pat.strip()):
                if p.is_file():
                    files.add(p)
        for path in sorted(files):
            rel = str(path.resolve().relative_to(root)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            direct_hits = 0
            if not token_segments or seg in token_segments:
                direct_hits = sum(text.count(tok) for tok in direct_tokens)

            if seg == "gate_scripts":
                iface_ratio = _safe_ratio(
                    float(sum(1 for tok in gate_required if tok in text)),
                    float(max(1, len(gate_required))),
                    default=1.0,
                )
                rust_ratio = 1.0
            elif seg == "ci_workflows":
                iface_ratio = 1.0 if "SPEC_RUNNER_BIN" in text else 0.0
                rust_ratio = _safe_ratio(
                    float(sum(1 for tok in rust_required if tok in text)),
                    float(max(1, len(rust_required))),
                    default=1.0,
                )
            else:
                iface_ratio = 1.0
                rust_ratio = 1.0

            no_direct = 1.0 if direct_hits == 0 else 0.0
            score = (no_direct + iface_ratio + rust_ratio) / 3.0
            rows.append(
                {
                    "file": rel,
                    "segment": seg,
                    "direct_runtime_invocation_count": float(direct_hits),
                    "runner_interface_usage_ratio": iface_ratio,
                    "rust_primary_path_coverage_ratio": rust_ratio,
                    "runner_independence_ratio": score,
                }
            )
    rows.sort(key=lambda r: (str(r["segment"]), str(r["file"])))
    segments: dict[str, Any] = {}
    segment_order = [str(k).strip() for k in segment_files.keys() if str(k).strip()]
    seen = []
    for seg in segment_order + [str(r["segment"]) for r in rows]:
        if seg not in seen:
            seen.append(seg)

    for seg in seen:
        seg_rows = [r for r in rows if str(r["segment"]) == seg]
        summary = _summarize_segment(
            seg_rows,
            [
                "runner_independence_ratio",
                "runner_interface_usage_ratio",
                "rust_primary_path_coverage_ratio",
                "direct_runtime_invocation_count",
            ],
        )
        summary["direct_runtime_invocation_count"] = sum(
            int(r.get("direct_runtime_invocation_count", 0)) for r in seg_rows
        )
        segments[seg] = summary

    total = len(rows)
    overall_ratio = _safe_ratio(sum(float(r["runner_independence_ratio"]) for r in rows), float(total), default=0.0)
    direct_total = sum(int(r.get("direct_runtime_invocation_count", 0)) for r in rows)
    rust_coverage_ratio = _safe_ratio(
        sum(float(r["rust_primary_path_coverage_ratio"]) for r in rows),
        float(total),
        default=0.0,
    )

    return {
        "version": 1,
        "summary": {
            "total_files": total,
            "overall_runner_independence_ratio": overall_ratio,
            "direct_runtime_invocation_count": direct_total,
            "rust_subcommand_native_coverage_ratio": rust_coverage_ratio,
        },
        "segments": segments,
        "files": rows,
        "config": cfg,
        "errors": errors,
    }


def default_docs_operability_config() -> dict[str, Any]:
    return {
        "reference_manifest": "docs/book/reference_manifest.yaml",
        "segment_rules": [
            {"prefix": "docs/book", "segment": "book"},
            {"prefix": "specs/contract", "segment": "contract"},
            {"prefix": "specs/schema", "segment": "schema"},
            {"prefix": "specs/impl", "segment": "impl_docs"},
        ],
    }


def docs_operability_report_jsonable(repo_root: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    root = repo_root.resolve()
    cfg = default_docs_operability_config()
    if isinstance(config, dict):
        cfg.update(config)

    manifest_rel = str(cfg.get("reference_manifest", "")).strip() or "docs/book/reference_manifest.yaml"
    manifest, manifest_errs = load_reference_manifest(root, manifest_rel)
    rel_paths = manifest_chapter_paths(manifest)
    metas, meta_issues, _meta_lines = load_docs_meta_for_paths(root, rel_paths)

    for rel in rel_paths:
        if rel in metas:
            try:
                doc_path = resolve_contract_path(root, rel, field="reference_manifest path")
            except VirtualPathError:
                continue
            metas[rel]["__text__"] = doc_path.read_text(encoding="utf-8")

    token_owner_issues = check_token_ownership_unique(metas)
    token_dep_issues = check_token_dependency_resolved(metas)
    section_issues = check_instructions_complete(root, metas)
    example_issues = check_command_examples_verified(root, rel_paths)

    issue_paths = {
        "token": {i.path for i in [*token_owner_issues, *token_dep_issues]},
        "sections": {i.path for i in section_issues},
        "examples": {i.path for i in example_issues},
    }

    rules_obj = cfg.get("segment_rules")
    rules = rules_obj if isinstance(rules_obj, list) else []
    segment_rules: list[dict[str, str]] = []
    for item in rules:
        if isinstance(item, dict):
            prefix = str(item.get("prefix", "")).strip()
            seg = str(item.get("segment", "")).strip()
            if prefix and seg:
                segment_rules.append({"prefix": prefix, "segment": seg})

    rows: list[dict[str, Any]] = []
    for rel in rel_paths:
        meta = metas.get(rel, {})
        segment = _match_segment(rel, segment_rules)
        examples = meta.get("examples", []) if isinstance(meta, dict) else []
        if not isinstance(examples, list):
            examples = []
        total_examples = 0
        runnable = 0
        opted_out = 0
        for ex in examples:
            if not isinstance(ex, dict):
                continue
            total_examples += 1
            if ex.get("runnable") is True:
                runnable += 1
            elif ex.get("runnable") is False:
                opted_out += 1

        runnable_ratio = _safe_ratio(float(runnable), float(total_examples), default=1.0)
        opt_out_density = _safe_ratio(float(opted_out), float(total_examples), default=0.0)
        command_ratio = 0.0 if rel in issue_paths["examples"] else 1.0
        section_ratio = 0.0 if rel in issue_paths["sections"] else 1.0
        token_ratio = 0.0 if rel in issue_paths["token"] else 1.0
        operability_ratio = (runnable_ratio + command_ratio + section_ratio + token_ratio) / 4.0

        rows.append(
            {
                "path": rel,
                "segment": segment,
                "runnable_example_coverage_ratio": runnable_ratio,
                "command_doc_validation_ratio": command_ratio,
                "required_sections_compliance_ratio": section_ratio,
                "token_sync_compliance_ratio": token_ratio,
                "opt_out_density_ratio": opt_out_density,
                "docs_operability_ratio": operability_ratio,
            }
        )

    rows.sort(key=lambda r: (str(r["segment"]), str(r["path"])))

    segments: dict[str, Any] = {}
    order = [str(rule["segment"]) for rule in segment_rules] + ["other"]
    seen: list[str] = []
    for seg in order + [str(r["segment"]) for r in rows]:
        if seg not in seen:
            seen.append(seg)

    for seg in seen:
        seg_rows = [r for r in rows if str(r["segment"]) == seg]
        segments[seg] = _summarize_segment(
            seg_rows,
            [
                "docs_operability_ratio",
                "runnable_example_coverage_ratio",
                "command_doc_validation_ratio",
                "required_sections_compliance_ratio",
                "token_sync_compliance_ratio",
                "opt_out_density_ratio",
            ],
        )

    total = len(rows)
    overall_ratio = _safe_ratio(sum(float(r["docs_operability_ratio"]) for r in rows), float(total), default=0.0)

    errors = [i.render() for i in [*manifest_errs, *meta_issues, *token_owner_issues, *token_dep_issues, *section_issues, *example_issues]]

    return {
        "version": 1,
        "summary": {
            "total_docs": total,
            "overall_docs_operability_ratio": overall_ratio,
        },
        "segments": segments,
        "docs": rows,
        "config": cfg,
        "errors": errors,
    }


def default_contract_assertions_config() -> dict[str, Any]:
    return {
        "paths": [
            "specs/contract/03_assertions.md",
            "specs/schema/schema_v1.md",
            "docs/book/30_assertion_model.md",
            "specs/contract/03b_spec_lang_v1.md",
        ],
        "segment_rules": [
            {"prefix": "specs/contract", "segment": "contract"},
            {"prefix": "specs/schema", "segment": "schema"},
            {"prefix": "docs/book", "segment": "book"},
        ],
        "required_tokens": ["must", "can", "cannot", "evaluate"],
    }


def contract_assertions_report_jsonable(repo_root: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    root = repo_root.resolve()
    cfg = default_contract_assertions_config()
    if isinstance(config, dict):
        cfg.update(config)

    paths = _as_list_of_strings(cfg.get("paths"))
    required_tokens = _as_list_of_strings(cfg.get("required_tokens"))
    raw_rules_obj = cfg.get("segment_rules")
    raw_rules = raw_rules_obj if isinstance(raw_rules_obj, list) else []
    rules: list[dict[str, str]] = []
    for item in raw_rules:
        if isinstance(item, dict):
            prefix = str(item.get("prefix", "")).strip()
            seg = str(item.get("segment", "")).strip()
            if prefix and seg:
                rules.append({"prefix": prefix, "segment": seg})

    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    token_presence_map: dict[str, set[str]] = {}

    for rel in paths:
        try:
            p = resolve_contract_path(root, rel, field="contract_assertions.paths[]")
        except VirtualPathError:
            errors.append(f"{rel}:1: invalid contract assertion doc path")
            continue
        if not p.exists():
            errors.append(f"{rel}:1: missing contract assertion doc")
            continue
        text = p.read_text(encoding="utf-8").lower()
        segment = _match_segment(rel, rules)
        present = {tok for tok in required_tokens if tok.lower() in text}
        token_presence_map[rel] = present
        ratio = _safe_ratio(float(len(present)), float(max(1, len(required_tokens))), default=0.0)
        rows.append(
            {
                "path": rel,
                "segment": segment,
                "required_token_coverage_ratio": ratio,
                "missing_required_token_count": float(max(0, len(required_tokens) - len(present))),
            }
        )

    rows.sort(key=lambda r: (str(r["segment"]), str(r["path"])))

    union_tokens: set[str] = set()
    intersection_tokens: set[str] | None = None
    for present in token_presence_map.values():
        union_tokens |= present
        if intersection_tokens is None:
            intersection_tokens = set(present)
        else:
            intersection_tokens &= present
    intersection_tokens = intersection_tokens or set()
    token_sync_ratio = _safe_ratio(float(len(intersection_tokens)), float(max(1, len(union_tokens))), default=1.0)

    coverage_payload = contract_coverage_jsonable(root)
    cov_summary = coverage_payload.get("summary") if isinstance(coverage_payload, dict) else {}
    if not isinstance(cov_summary, dict):
        cov_summary = {}
    must_rules = int(cov_summary.get("must_rules", 0))
    must_covered = int(cov_summary.get("must_covered", 0))
    must_coverage_ratio = _safe_ratio(float(must_covered), float(max(1, must_rules)), default=0.0)

    segments: dict[str, Any] = {}
    order = [str(rule["segment"]) for rule in rules] + ["other"]
    seen: list[str] = []
    for seg in order + [str(r["segment"]) for r in rows]:
        if seg not in seen:
            seen.append(seg)
    for seg in seen:
        seg_rows = [r for r in rows if str(r["segment"]) == seg]
        segments[seg] = _summarize_segment(
            seg_rows,
            ["required_token_coverage_ratio", "missing_required_token_count"],
        )

    total = len(rows)
    token_cov_overall = _safe_ratio(
        sum(float(r["required_token_coverage_ratio"]) for r in rows),
        float(total),
        default=0.0,
    )
    overall_ratio = (token_cov_overall + must_coverage_ratio + token_sync_ratio) / 3.0

    return {
        "version": 1,
        "summary": {
            "total_docs": total,
            "overall_contract_assertions_ratio": overall_ratio,
            "overall_required_token_coverage_ratio": token_cov_overall,
            "contract_must_coverage_ratio": must_coverage_ratio,
            "token_sync_ratio": token_sync_ratio,
        },
        "segments": segments,
        "docs": rows,
        "config": cfg,
        "errors": errors,
    }


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _lookup_metric_number(payload: object, dotted: str) -> float | None:
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


def _load_yaml_mapping(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"{path}:1: missing YAML file"]
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return {}, [f"{path}:1: invalid YAML: {exc}"]
    if payload is None:
        return {}, []
    if not isinstance(payload, dict):
        return {}, [f"{path}:1: YAML payload must be a mapping"]
    return payload, []


def _render_metric_value(value: float | None) -> str:
    if value is None:
        return "missing"
    return f"{value:.6f}"


def _metric_score_from_config(value: float | None, cfg: dict[str, Any]) -> float:
    if value is None:
        return 0.0
    mode = str(cfg.get("mode", "direct")).strip().lower()
    scale_raw = cfg.get("scale", 1.0)
    try:
        scale = float(scale_raw)
    except (TypeError, ValueError):
        scale = 1.0
    if scale <= 0:
        scale = 1.0
    normalized = value / scale
    if mode == "one_minus":
        return _clamp01(1.0 - normalized)
    return _clamp01(normalized)


def _collect_portability_counter_shares(payload: dict[str, Any]) -> dict[str, float]:
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return {
            "runtime_specific_capability_penalty_share": 0.0,
            "expect_impl_overlay_penalty_share": 0.0,
        }
    runtime_hits = 0
    impl_hits = 0
    total = 0
    for row in cases:
        if not isinstance(row, dict):
            continue
        penalties = row.get("penalties")
        if not isinstance(penalties, dict):
            continue
        total += 1
        if float(penalties.get("runtime_specific_capability", 0.0)) > 0.0:
            runtime_hits += 1
        if float(penalties.get("expect_impl_overlay", 0.0)) > 0.0:
            impl_hits += 1
    den = float(max(1, total))
    return {
        "runtime_specific_capability_penalty_share": float(runtime_hits) / den,
        "expect_impl_overlay_penalty_share": float(impl_hits) / den,
    }


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def validate_metric_baseline_notes(
    repo_root: Path,
    *,
    notes_path: str,
    baseline_paths: list[str],
) -> list[str]:
    try:
        note_file = resolve_contract_path(repo_root, notes_path, field="baseline_notes.path")
    except VirtualPathError as exc:
        return [str(exc)]
    payload, errs = _load_yaml_mapping(note_file)
    if errs:
        return errs
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return [f"{notes_path}:1: entries must be a non-empty list"]

    by_path: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rel = str(entry.get("baseline", "")).strip()
        if rel:
            by_path[rel] = entry
            by_path[rel.lstrip("/")] = entry

    violations: list[str] = []
    for rel in baseline_paths:
        try:
            path = resolve_contract_path(repo_root, rel, field="baseline_paths[]")
        except VirtualPathError as exc:
            violations.append(str(exc))
            continue
        if not path.exists():
            violations.append(f"{rel}:1: baseline file missing")
            continue
        entry = by_path.get(rel) or by_path.get(rel.lstrip("/"))
        if entry is None:
            violations.append(f"{notes_path}:1: missing baseline update note entry for {rel}")
            continue
        note_hash = str(entry.get("sha256", "")).strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", note_hash):
            violations.append(f"{notes_path}:1: entry for {rel} must include sha256 hex digest")
            continue
        actual_hash = _sha256_file(path)
        if note_hash != actual_hash:
            violations.append(
                f"{notes_path}:1: sha256 mismatch for {rel} (note={note_hash} actual={actual_hash})"
            )
        rationale = str(entry.get("rationale", "")).strip()
        measurement_change = str(entry.get("measurement_model_change", "")).strip().lower()
        if not rationale:
            violations.append(f"{notes_path}:1: entry for {rel} missing non-empty rationale")
        if measurement_change not in {"yes", "no"}:
            violations.append(
                f"{notes_path}:1: entry for {rel} measurement_model_change must be 'yes' or 'no'"
            )
    return violations


def default_objective_scorecard_config() -> dict[str, Any]:
    return {
        "manifest_path": "specs/governance/metrics/objective_manifest.yaml",
        "thresholds": {
            "green_min": 0.75,
            "yellow_min": 0.50,
        },
        "tripwire_status": {},
    }


def objective_scorecard_report_jsonable(repo_root: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    root = repo_root.resolve()
    cfg = default_objective_scorecard_config()
    if isinstance(config, dict):
        cfg.update(config)
    thresholds_obj = cfg.get("thresholds")
    thresholds: dict[str, Any] = thresholds_obj if isinstance(thresholds_obj, dict) else {}
    try:
        green_min = float(thresholds.get("green_min", 0.75))
    except (TypeError, ValueError):
        green_min = 0.75
    try:
        yellow_min = float(thresholds.get("yellow_min", 0.50))
    except (TypeError, ValueError):
        yellow_min = 0.50

    manifest_path = str(cfg.get("manifest_path", "")).strip() or "specs/governance/metrics/objective_manifest.yaml"
    try:
        manifest_file = resolve_contract_path(root, manifest_path, field="objective_manifest.path")
    except VirtualPathError as exc:
        manifest_file = root / manifest_path.lstrip("/")
        manifest_errs = [str(exc)]
    else:
        manifest_errs = []
    manifest, yaml_errs = _load_yaml_mapping(manifest_file)
    manifest_errs.extend(yaml_errs)
    objectives = manifest.get("objectives")
    if not isinstance(objectives, list):
        objectives = []

    portability = spec_portability_report_jsonable(root, config=None)
    spec_lang = spec_lang_adoption_report_jsonable(root, config=None)
    runner_indep = runner_independence_report_jsonable(root, config=None)
    python_dependency = python_dependency_report_jsonable(root, config=None)
    docs_operability = docs_operability_report_jsonable(root, config=None)
    contract_assertions = contract_assertions_report_jsonable(root, config=None)

    portability_counters = _collect_portability_counter_shares(portability)
    sources: dict[str, Any] = {
        "spec_portability": portability,
        "spec_lang_adoption": spec_lang,
        "runner_independence": runner_indep,
        "python_dependency": python_dependency,
        "docs_operability": docs_operability,
        "contract_assertions": contract_assertions,
        "derived": {
            **portability_counters,
        },
    }
    report_errors: list[str] = [*manifest_errs]
    for label, payload in (
        ("spec_portability", portability),
        ("spec_lang_adoption", spec_lang),
        ("runner_independence", runner_indep),
        ("python_dependency", python_dependency),
        ("docs_operability", docs_operability),
        ("contract_assertions", contract_assertions),
    ):
        errs = payload.get("errors") if isinstance(payload, dict) else []
        if isinstance(errs, list):
            for err in errs:
                s = str(err).strip()
                if s:
                    report_errors.append(f"{label}: {s}")
    tripwire_status_obj = cfg.get("tripwire_status")
    tripwire_status: dict[str, Any] = tripwire_status_obj if isinstance(tripwire_status_obj, dict) else {}

    objective_rows: list[dict[str, Any]] = []
    all_tripwire_hits: list[dict[str, str]] = []
    recommendations: list[str] = []
    for raw_obj in objectives:
        if not isinstance(raw_obj, dict):
            continue
        objective_id = str(raw_obj.get("id", "")).strip() or "<unknown>"
        name = str(raw_obj.get("name", "")).strip() or objective_id

        primary_obj = raw_obj.get("primary")
        primary_cfg: dict[str, Any] = primary_obj if isinstance(primary_obj, dict) else {}
        primary_source = str(primary_cfg.get("source", "")).strip()
        primary_field = str(primary_cfg.get("field", "")).strip()
        primary_value = _lookup_metric_number(sources.get(primary_source), primary_field) if primary_source else None
        primary_score = _metric_score_from_config(primary_value, primary_cfg)

        counters_obj = raw_obj.get("counters")
        counter_cfgs = counters_obj if isinstance(counters_obj, list) else []
        counter_rows: list[dict[str, Any]] = []
        counter_scores: list[float] = []
        for raw_counter in counter_cfgs:
            if not isinstance(raw_counter, dict):
                continue
            cid = str(raw_counter.get("id", "")).strip() or "counter"
            source = str(raw_counter.get("source", "")).strip()
            field = str(raw_counter.get("field", "")).strip()
            value = _lookup_metric_number(sources.get(source), field) if source else None
            score = _metric_score_from_config(value, raw_counter)
            counter_rows.append(
                {
                    "id": cid,
                    "source": source,
                    "field": field,
                    "value": value,
                    "value_rendered": _render_metric_value(value),
                    "score": score,
                }
            )
            counter_scores.append(score)

        tripwires_obj = raw_obj.get("tripwires")
        objective_tripwires = tripwires_obj if isinstance(tripwires_obj, list) else []
        tripwire_hits: list[dict[str, str]] = []
        for raw_tw in objective_tripwires:
            if not isinstance(raw_tw, dict):
                continue
            check_id = str(raw_tw.get("check_id", "")).strip()
            if not check_id:
                continue
            status = tripwire_status.get(check_id, "unknown")
            if isinstance(status, bool):
                is_fail = not status
            else:
                status_str = str(status).strip().lower()
                is_fail = status_str in {"fail", "failing", "error", "false", "0"}
            if is_fail:
                tripwire_hits.append(
                    {
                        "check_id": check_id,
                        "reason": str(raw_tw.get("reason", "")).strip() or "tripwire failed",
                    }
                )

        primary_weight = float(raw_obj.get("primary_weight", 0.6))
        counter_weight = float(raw_obj.get("counter_weight", 0.4))
        counter_avg = sum(counter_scores) / len(counter_scores) if counter_scores else primary_score
        denom = primary_weight + counter_weight
        if denom <= 0:
            objective_score = primary_score
        else:
            objective_score = _clamp01((primary_weight * primary_score + counter_weight * counter_avg) / denom)

        status = "green"
        if tripwire_hits:
            status = "red"
        elif objective_score < yellow_min:
            status = "red"
        elif objective_score < green_min:
            status = "yellow"
        if status in {"red", "yellow"}:
            corr_obj = raw_obj.get("course_correction")
            corr: dict[str, Any] = corr_obj if isinstance(corr_obj, dict) else {}
            line = str(corr.get("action", "")).strip()
            if line:
                recommendations.append(f"{objective_id}: {line}")

        row = {
            "id": objective_id,
            "name": name,
            "score": objective_score,
            "status": status,
            "primary": {
                "source": primary_source,
                "field": primary_field,
                "value": primary_value,
                "value_rendered": _render_metric_value(primary_value),
                "score": primary_score,
            },
            "counters": counter_rows,
            "tripwire_hits": tripwire_hits,
        }
        objective_rows.append(row)
        for hit in tripwire_hits:
            all_tripwire_hits.append(
                {
                    "objective_id": objective_id,
                    "check_id": hit["check_id"],
                    "reason": hit["reason"],
                }
            )

    objective_rows.sort(key=lambda r: str(r.get("id", "")))
    scores = [float(r.get("score", 0.0)) for r in objective_rows]
    overall_min = min(scores) if scores else 0.0
    overall_mean = (sum(scores) / len(scores)) if scores else 0.0
    status_counts = {
        "green": sum(1 for r in objective_rows if r.get("status") == "green"),
        "yellow": sum(1 for r in objective_rows if r.get("status") == "yellow"),
        "red": sum(1 for r in objective_rows if r.get("status") == "red"),
    }
    overall_status = "green"
    if status_counts["red"] > 0:
        overall_status = "red"
    elif status_counts["yellow"] > 0:
        overall_status = "yellow"

    uniq_recos = sorted({r for r in recommendations if r})
    return {
        "version": 1,
        "summary": {
            "objective_count": len(objective_rows),
            "overall_min_score": overall_min,
            "overall_mean_score": overall_mean,
            "overall_status": overall_status,
            "tripwire_hit_count": len(all_tripwire_hits),
            "status_counts": status_counts,
        },
        "objectives": objective_rows,
        "tripwire_hits": all_tripwire_hits,
        "course_correction_recommendations": uniq_recos,
        "manifest_path": manifest_path,
        "config": cfg,
        "errors": report_errors,
    }
