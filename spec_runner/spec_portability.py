from __future__ import annotations

from pathlib import Path
from typing import Any

from spec_runner.codecs import load_external_cases
from spec_runner.dispatcher import iter_cases
from spec_runner.settings import SETTINGS
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


def default_spec_portability_config() -> dict[str, Any]:
    cfg = SETTINGS.spec_portability
    return {
        "roots": list(cfg.roots),
        "core_types": list(cfg.core_types),
        "segment_rules": [{"prefix": r.prefix, "segment": r.segment} for r in cfg.segment_rules],
        "runtime_capability_tokens": list(cfg.runtime_capability_tokens),
        "runtime_capability_prefixes": list(cfg.runtime_capability_prefixes),
        "weights": {
            "non_evaluate_leaf_share": float(cfg.weights.non_evaluate_leaf_share),
            "expect_impl_overlay": float(cfg.weights.expect_impl_overlay),
            "runtime_specific_capability": float(cfg.weights.runtime_specific_capability),
            "non_core_type": float(cfg.weights.non_core_type),
        },
        "report": {"top_n": int(cfg.report.top_n)},
        "recursive": bool(cfg.recursive),
        "min_overall_ratio": cfg.min_overall_ratio,
        "min_segment_ratios": dict(cfg.min_segment_ratios),
        "enforce": bool(cfg.enforce),
    }


def resolve_spec_portability_config(raw: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[str]]:
    cfg = default_spec_portability_config()
    errs: list[str] = []
    override = raw or {}
    if not isinstance(override, dict):
        return cfg, ["portability metric config must be a mapping"]

    for key in (
        "roots",
        "core_types",
        "segment_rules",
        "runtime_capability_tokens",
        "runtime_capability_prefixes",
        "recursive",
        "min_overall_ratio",
        "min_segment_ratios",
        "enforce",
    ):
        if key in override:
            cfg[key] = override[key]

    if "weights" in override:
        w = override["weights"]
        if not isinstance(w, dict):
            errs.append("portability_metric.weights must be a mapping")
        else:
            merged = dict(cfg["weights"])
            merged.update(w)
            cfg["weights"] = merged

    if "report" in override:
        r = override["report"]
        if not isinstance(r, dict):
            errs.append("portability_metric.report must be a mapping")
        else:
            merged = dict(cfg["report"])
            merged.update(r)
            cfg["report"] = merged

    roots = _as_list_of_strings(cfg.get("roots"))
    if not roots:
        errs.append("portability_metric.roots must be a non-empty list of non-empty strings")
    cfg["roots"] = roots

    core_types = _as_list_of_strings(cfg.get("core_types"))
    if not core_types:
        errs.append("portability_metric.core_types must be a non-empty list of non-empty strings")
    cfg["core_types"] = core_types

    raw_rules = cfg.get("segment_rules")
    segment_rules: list[dict[str, str]] = []
    if not isinstance(raw_rules, list) or not raw_rules:
        errs.append("portability_metric.segment_rules must be a non-empty list of mappings")
    else:
        for i, item in enumerate(raw_rules):
            if not isinstance(item, dict):
                errs.append(f"portability_metric.segment_rules[{i}] must be a mapping")
                continue
            prefix = str(item.get("prefix", "")).strip()
            segment = str(item.get("segment", "")).strip()
            if not prefix or not segment:
                errs.append(f"portability_metric.segment_rules[{i}] requires non-empty prefix and segment")
                continue
            segment_rules.append({"prefix": prefix, "segment": segment})
    cfg["segment_rules"] = segment_rules

    cfg["runtime_capability_tokens"] = _as_list_of_strings(cfg.get("runtime_capability_tokens"))
    cfg["runtime_capability_prefixes"] = _as_list_of_strings(cfg.get("runtime_capability_prefixes"))
    cfg["recursive"] = bool(cfg.get("recursive", True))

    weights = cfg.get("weights")
    if not isinstance(weights, dict):
        errs.append("portability_metric.weights must be a mapping")
    else:
        for key in (
            "non_evaluate_leaf_share",
            "expect_impl_overlay",
            "runtime_specific_capability",
            "non_core_type",
        ):
            try:
                raw_val = weights.get(key, 0.0)
                val = float(raw_val)
            except (TypeError, ValueError):
                errs.append(f"portability_metric.weights.{key} must be a number")
                continue
            if val < 0:
                errs.append(f"portability_metric.weights.{key} must be >= 0")
            weights[key] = val
        cfg["weights"] = weights

    report = cfg.get("report")
    if not isinstance(report, dict):
        errs.append("portability_metric.report must be a mapping")
    else:
        try:
            raw_top_n = report.get("top_n", 0)
            top_n = int(raw_top_n)
        except (TypeError, ValueError):
            errs.append("portability_metric.report.top_n must be an integer")
            top_n = 0
        if top_n < 1:
            errs.append("portability_metric.report.top_n must be >= 1")
        report["top_n"] = top_n
        cfg["report"] = report

    if cfg.get("min_overall_ratio") is not None:
        try:
            cfg["min_overall_ratio"] = float(cfg["min_overall_ratio"])
        except (TypeError, ValueError):
            errs.append("portability_metric.min_overall_ratio must be a number when provided")

    msr = cfg.get("min_segment_ratios")
    if msr is None:
        cfg["min_segment_ratios"] = {}
    elif not isinstance(msr, dict):
        errs.append("portability_metric.min_segment_ratios must be a mapping when provided")
        cfg["min_segment_ratios"] = {}
    else:
        clean_msr: dict[str, float] = {}
        for k, v in msr.items():
            name = str(k).strip()
            if not name:
                errs.append("portability_metric.min_segment_ratios contains empty segment key")
                continue
            try:
                clean_msr[name] = float(v)
            except (TypeError, ValueError):
                errs.append(f"portability_metric.min_segment_ratios.{name} must be numeric")
        cfg["min_segment_ratios"] = clean_msr

    cfg["enforce"] = bool(cfg.get("enforce", False))
    return cfg, errs


def _match_segment(rel_path: str, segment_rules: list[dict[str, str]]) -> str:
    normalized = rel_path.replace("\\", "/")
    for rule in segment_rules:
        prefix = str(rule["prefix"]).replace("\\", "/").rstrip("/")
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return str(rule["segment"])
    return "other"


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


def _has_runtime_specific_capability(
    caps: list[str],
    *,
    tokens: set[str],
    prefixes: tuple[str, ...],
) -> bool:
    for raw in caps:
        cap = raw.strip()
        if not cap:
            continue
        if cap in tokens:
            return True
        for prefix in prefixes:
            if cap.startswith(prefix):
                return True
    return False


def _summarize_segment(rows: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    if count == 0:
        return {
            "case_count": 0,
            "mean_self_contained_ratio": 0.0,
            "mean_implementation_reliance_ratio": 0.0,
            "mean_logic_self_contained_ratio": 0.0,
            "mean_logic_reliance_ratio": 0.0,
            "mean_execution_portability_ratio": 0.0,
            "mean_execution_coupling_ratio": 0.0,
            "penalty_counts": {
                "non_evaluate_leaf": 0,
                "expect_impl_overlay": 0,
                "runtime_specific_capability": 0,
                "non_core_type": 0,
            },
        }
    total_self = sum(float(r["self_contained_ratio"]) for r in rows)
    total_impl = sum(float(r["implementation_reliance_ratio"]) for r in rows)
    total_logic_self = sum(float(r["logic_self_contained_ratio"]) for r in rows)
    total_logic_rel = sum(float(r["logic_reliance_ratio"]) for r in rows)
    total_exec_port = sum(float(r["execution_portability_ratio"]) for r in rows)
    total_exec_coupling = sum(float(r["execution_coupling_ratio"]) for r in rows)
    return {
        "case_count": count,
        "mean_self_contained_ratio": total_self / count,
        "mean_implementation_reliance_ratio": total_impl / count,
        "mean_logic_self_contained_ratio": total_logic_self / count,
        "mean_logic_reliance_ratio": total_logic_rel / count,
        "mean_execution_portability_ratio": total_exec_port / count,
        "mean_execution_coupling_ratio": total_exec_coupling / count,
        "penalty_counts": {
            "non_evaluate_leaf": sum(1 for r in rows if float(r["penalties"]["non_evaluate_leaf_share"]) > 0.0),
            "expect_impl_overlay": sum(1 for r in rows if float(r["penalties"]["expect_impl_overlay"]) > 0.0),
            "runtime_specific_capability": sum(
                1 for r in rows if float(r["penalties"]["runtime_specific_capability"]) > 0.0
            ),
            "non_core_type": sum(1 for r in rows if float(r["penalties"]["non_core_type"]) > 0.0),
        },
    }


def spec_portability_report_jsonable(repo_root: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    root = repo_root.resolve()
    cfg, config_errors = resolve_spec_portability_config(config)
    rows: list[dict[str, Any]] = []
    scan_errors: list[str] = []

    core_types = set(cfg["core_types"])
    token_set = set(cfg["runtime_capability_tokens"])
    prefix_tuple = tuple(cfg["runtime_capability_prefixes"])
    weights = cfg["weights"]
    recursive = bool(cfg["recursive"])

    for rel_root in cfg["roots"]:
        try:
            base = resolve_contract_path(root, rel_root, field="spec_portability.roots[]")
        except VirtualPathError:
            scan_errors.append(f"{rel_root}: invalid spec root path")
            continue
        if not base.exists() or not base.is_dir():
            scan_errors.append(f"{rel_root}: missing spec root directory")
            continue

        case_pairs: list[tuple[Path, dict[str, Any]]] = []
        if recursive:
            files = sorted(base.rglob(SETTINGS.case.default_file_pattern))
            for file_path in files:
                if not file_path.is_file():
                    continue
                for doc_path, case in load_external_cases(file_path, formats={"md"}):
                    case_pairs.append((doc_path, case))
        else:
            for spec in iter_cases(base, file_pattern=SETTINGS.case.default_file_pattern):
                case_pairs.append((spec.doc_path, spec.test))

        for doc_path, case in case_pairs:
            case_id = str(case.get("id", "<unknown>")).strip() or "<unknown>"
            case_type = str(case.get("type", "")).strip()
            try:
                rel_path = str(doc_path.resolve().relative_to(root)).replace("\\", "/")
            except ValueError:
                rel_path = str(doc_path)
            segment = _match_segment(rel_path, cfg["segment_rules"])

            try:
                ops = _collect_leaf_ops(case.get("contract", []) or [])
            except BaseException as exc:  # noqa: BLE001
                scan_errors.append(f"{rel_path}: case {case_id}: failed to inspect assert tree ({exc})")
                continue

            total_leaf = len(ops)
            non_eval_leaf = sum(1 for op in ops if op != "evaluate")
            non_eval_share = 0.0 if total_leaf == 0 else non_eval_leaf / total_leaf

            expect = case.get("expect")
            has_expect_impl = False
            if isinstance(expect, dict):
                impl = expect.get("impl")
                has_expect_impl = isinstance(impl, dict) and len(impl) > 0

            requires = case.get("requires")
            caps = []
            if isinstance(requires, dict):
                caps = _as_list_of_strings(requires.get("capabilities"))
            has_runtime_capability = _has_runtime_specific_capability(
                caps,
                tokens=token_set,
                prefixes=prefix_tuple,
            )

            non_core_type = bool(case_type) and case_type not in core_types

            penalties = {
                "non_evaluate_leaf_share": weights["non_evaluate_leaf_share"] * non_eval_share,
                "expect_impl_overlay": weights["expect_impl_overlay"] if has_expect_impl else 0.0,
                "runtime_specific_capability": (
                    weights["runtime_specific_capability"] if has_runtime_capability else 0.0
                ),
                "non_core_type": weights["non_core_type"] if non_core_type else 0.0,
            }
            total_penalty = sum(float(x) for x in penalties.values())
            score = max(0.0, min(1.0, 1.0 - total_penalty))
            logic_self = 1.0 - non_eval_share
            logic_rel = non_eval_share
            execution_penalty = (
                float(penalties["expect_impl_overlay"])
                + float(penalties["runtime_specific_capability"])
                + float(penalties["non_core_type"])
            )
            execution_portability = max(0.0, min(1.0, 1.0 - execution_penalty))
            execution_coupling = 1.0 - execution_portability

            reasons: list[str] = []
            if penalties["non_evaluate_leaf_share"] > 0:
                reasons.append(
                    f"non-evaluate leaf share {non_eval_leaf}/{total_leaf}"
                )
            if penalties["expect_impl_overlay"] > 0:
                reasons.append("expect.impl overlay present")
            if penalties["runtime_specific_capability"] > 0:
                reasons.append("runtime-specific capability declared")
            if penalties["non_core_type"] > 0:
                reasons.append(f"non-core type {case_type}")

            rows.append(
                {
                    "id": case_id,
                    "type": case_type,
                    "segment": segment,
                    "file": rel_path,
                    "leaf_counts": {
                        "total": total_leaf,
                        "evaluate": total_leaf - non_eval_leaf,
                        "non_evaluate": non_eval_leaf,
                    },
                    "penalties": penalties,
                    "self_contained_ratio": score,
                    "implementation_reliance_ratio": 1.0 - score,
                    "logic_self_contained_ratio": logic_self,
                    "logic_reliance_ratio": logic_rel,
                    "execution_portability_ratio": execution_portability,
                    "execution_coupling_ratio": execution_coupling,
                    "reasons": reasons,
                }
            )

    rows.sort(key=lambda r: (str(r["segment"]), float(r["self_contained_ratio"]), str(r["file"]), str(r["id"])))

    segments_order = [str(rule["segment"]) for rule in cfg["segment_rules"]] + ["other"]
    segments_unique: list[str] = []
    for s in segments_order:
        if s not in segments_unique:
            segments_unique.append(s)
    for row in rows:
        seg = str(row["segment"])
        if seg not in segments_unique:
            segments_unique.append(seg)

    segments: dict[str, Any] = {}
    for seg in segments_unique:
        seg_rows = [r for r in rows if r["segment"] == seg]
        segments[seg] = _summarize_segment(seg_rows)

    total_cases = len(rows)
    if total_cases:
        overall_self = sum(float(r["self_contained_ratio"]) for r in rows) / total_cases
        overall_impl = sum(float(r["implementation_reliance_ratio"]) for r in rows) / total_cases
        overall_logic_self = sum(float(r["logic_self_contained_ratio"]) for r in rows) / total_cases
        overall_logic_rel = sum(float(r["logic_reliance_ratio"]) for r in rows) / total_cases
        overall_exec_port = sum(float(r["execution_portability_ratio"]) for r in rows) / total_cases
        overall_exec_coupling = sum(float(r["execution_coupling_ratio"]) for r in rows) / total_cases
    else:
        overall_self = 0.0
        overall_impl = 0.0
        overall_logic_self = 0.0
        overall_logic_rel = 0.0
        overall_exec_port = 0.0
        overall_exec_coupling = 0.0

    top_n = int(cfg["report"]["top_n"])
    worst_cases = sorted(
        rows,
        key=lambda r: (float(r["self_contained_ratio"]), str(r["file"]), str(r["id"])),
    )[:top_n]

    return {
        "version": 1,
        "summary": {
            "total_cases": total_cases,
            "overall_self_contained_ratio": overall_self,
            "overall_implementation_reliance_ratio": overall_impl,
            "overall_logic_self_contained_ratio": overall_logic_self,
            "overall_logic_reliance_ratio": overall_logic_rel,
            "overall_execution_portability_ratio": overall_exec_port,
            "overall_execution_coupling_ratio": overall_exec_coupling,
        },
        "segments": segments,
        "worst_cases": worst_cases,
        "cases": rows,
        "config": cfg,
        "errors": [*config_errors, *scan_errors],
    }
