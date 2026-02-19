from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml
from spec_runner.codecs import load_external_cases
from spec_runner.purpose_lint import load_purpose_lint_policy

_NORMATIVE_CONTRACT_DOCS = [
    "specs/contract/00_design_goals.md",
    "specs/contract/versioning.md",
    "specs/contract/01_discovery.md",
    "specs/contract/02_case_shape.md",
    "specs/contract/03_assertions.md",
    "specs/contract/03a_regex_portability_v1.md",
    "specs/contract/03b_spec_lang_v1.md",
    "specs/contract/04_harness.md",
    "specs/contract/05_errors.md",
    "specs/contract/06_conformance.md",
    "specs/contract/07_portable_spec_authoring.md",
    "specs/contract/08_v1_scope.md",
    "specs/contract/09_internal_representation.md",
    "specs/contract/10_docs_quality.md",
    "specs/contract/11_adoption_profiles.md",
    "specs/contract/12_runner_interface.md",
    "specs/contract/13_runtime_scope.md",
    "specs/contract/14_spec_lang_libraries.md",
    "specs/contract/15_governance_subject_model.md",
    "specs/contract/16_rust_primary_transition.md",
    "specs/contract/17_objective_metrics.md",
    "specs/contract/20_subject_profiles_v1.md",
]


def _read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _collect_fixture_case_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    for _, case in load_external_cases(path, formats={"md"}):
        rid = str(case.get("id", "")).strip()
        if rid:
            ids.add(rid)
    return ids


@dataclass(frozen=True)
class RuleCoverage:
    rule_id: str
    norm: str
    lifecycle_status: str
    introduced_in: str
    deprecated_in: str | None
    removed_in: str | None
    has_traceability: bool
    has_tests: bool
    has_conformance_cases: bool
    is_covered: bool


def _exists_repo_or_runner(repo_root: Path, rel: str) -> bool:
    p = repo_root / rel
    if p.exists():
        return True
    return (repo_root / "tools/spec_runner" / rel).exists()


def _load_policy_and_trace(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any], set[str]]:
    policy_path = repo_root / "specs/contract/policy_v1.yaml"
    trace_path = repo_root / "specs/contract/traceability_v1.yaml"
    cases_dir = repo_root / "specs/conformance/cases"
    policy = _read_yaml(policy_path) or {}
    trace = _read_yaml(trace_path) or {}
    conformance_ids = _collect_fixture_case_ids(cases_dir)
    return policy, trace, conformance_ids


def _parse_contract_version(label: str) -> int | None:
    s = str(label).strip().lower()
    if len(s) < 2 or not s.startswith("v"):
        return None
    n = s[1:]
    if not n.isdigit():
        return None
    return int(n)


def build_contract_coverage(repo_root: Path) -> list[RuleCoverage]:
    repo_root = repo_root.resolve()
    policy, trace, _conformance_ids = _load_policy_and_trace(repo_root)
    rules = policy.get("rules") or []
    links = trace.get("links") or []
    if not isinstance(rules, list) or not isinstance(links, list):
        return []

    links_by_rule: dict[str, dict[str, Any]] = {}
    for l in links:
        if isinstance(l, dict):
            rid = str(l.get("rule_id", "")).strip()
            if rid and rid not in links_by_rule:
                links_by_rule[rid] = l

    out: list[RuleCoverage] = []
    for r in rules:
        if not isinstance(r, dict):
            continue
        rid = str(r.get("id", "")).strip()
        if not rid:
            continue
        norm = str(r.get("norm", "")).upper()
        introduced_in = None if r.get("introduced_in") is None else str(r.get("introduced_in"))
        deprecated_in = None if r.get("deprecated_in") is None else str(r.get("deprecated_in"))
        removed_in = None if r.get("removed_in") is None else str(r.get("removed_in"))
        if removed_in:
            lifecycle_status = "removed"
        elif deprecated_in:
            lifecycle_status = "deprecated"
        else:
            lifecycle_status = "active"
        link = links_by_rule.get(rid)
        has_trace = link is not None
        conformance_case_ids = (link.get("conformance_case_ids") if isinstance(link, dict) else []) or []
        unit_test_refs = (link.get("unit_test_refs") if isinstance(link, dict) else []) or []
        has_tests = isinstance(unit_test_refs, list) and len(unit_test_refs) > 0
        has_conf = isinstance(conformance_case_ids, list) and len(conformance_case_ids) > 0
        if norm == "MUST":
            is_covered = has_trace and (has_tests or has_conf)
        else:
            is_covered = has_trace
        out.append(
            RuleCoverage(
                rule_id=rid,
                norm=norm,
                lifecycle_status=lifecycle_status,
                introduced_in="" if introduced_in is None else introduced_in,
                deprecated_in=deprecated_in,
                removed_in=removed_in,
                has_traceability=has_trace,
                has_tests=has_tests,
                has_conformance_cases=has_conf,
                is_covered=is_covered,
            )
        )
    return out


def contract_coverage_jsonable(repo_root: Path) -> dict[str, Any]:
    coverage = build_contract_coverage(repo_root)
    total = len(coverage)
    covered = sum(1 for r in coverage if r.is_covered)
    must_total = sum(1 for r in coverage if r.norm == "MUST")
    must_covered = sum(1 for r in coverage if r.norm == "MUST" and r.is_covered)
    active_total = sum(1 for r in coverage if r.lifecycle_status == "active")
    deprecated_total = sum(1 for r in coverage if r.lifecycle_status == "deprecated")
    removed_total = sum(1 for r in coverage if r.lifecycle_status == "removed")
    return {
        "version": 1,
        "summary": {
            "total_rules": total,
            "covered_rules": covered,
            "coverage_ratio": 0.0 if total == 0 else covered / total,
            "must_rules": must_total,
            "must_covered": must_covered,
            "active_rules": active_total,
            "deprecated_rules": deprecated_total,
            "removed_rules": removed_total,
        },
        "rules": [asdict(r) for r in coverage],
    }


def check_contract_governance(repo_root: Path) -> list[str]:
    errs: list[str] = []
    repo_root = repo_root.resolve()

    policy, trace, conformance_ids = _load_policy_and_trace(repo_root)
    _purpose_policy, purpose_policy_errs, _ = load_purpose_lint_policy(repo_root)
    for e in purpose_policy_errs:
        errs.append(f"{e}")
    rules = policy.get("rules") or []
    links = trace.get("links") or []
    if not isinstance(rules, list):
        return ["policy-v1.yaml rules must be a list"]
    if not isinstance(links, list):
        return ["traceability-v1.yaml links must be a list"]

    rules_by_id: dict[str, dict[str, Any]] = {}
    allowed_norms = {"MUST", "SHOULD", "MUST_NOT"}

    for r in rules:
        if not isinstance(r, dict):
            errs.append("policy rule entries must be mappings")
            continue
        rid = str(r.get("id", "")).strip()
        if not rid:
            errs.append("policy rule missing id")
            continue
        if rid in rules_by_id:
            errs.append(f"duplicate policy rule id: {rid}")
        rules_by_id[rid] = r
        norm = str(r.get("norm", "")).upper()
        if norm not in allowed_norms:
            errs.append(f"invalid norm for {rid}: {norm!r}")
        introduced = str(r.get("introduced_in", "")).strip()
        if not introduced:
            errs.append(f"policy rule missing introduced_in: {rid}")
        introduced_n = _parse_contract_version(introduced) if introduced else None
        if introduced and introduced_n is None:
            errs.append(f"invalid introduced_in for {rid}: {introduced!r}")
        deprecated = str(r.get("deprecated_in", "")).strip()
        deprecated_n = _parse_contract_version(deprecated) if deprecated else None
        if deprecated and deprecated_n is None:
            errs.append(f"invalid deprecated_in for {rid}: {deprecated!r}")
        removed = str(r.get("removed_in", "")).strip()
        removed_n = _parse_contract_version(removed) if removed else None
        if removed and removed_n is None:
            errs.append(f"invalid removed_in for {rid}: {removed!r}")
        if removed and not deprecated:
            errs.append(f"removed_in requires deprecated_in for {rid}")
        if introduced_n is not None and deprecated_n is not None and deprecated_n < introduced_n:
            errs.append(f"deprecated_in precedes introduced_in for {rid}")
        if introduced_n is not None and removed_n is not None and removed_n <= introduced_n:
            errs.append(f"removed_in must be greater than introduced_in for {rid}")
        if deprecated_n is not None and removed_n is not None and removed_n <= deprecated_n:
            errs.append(f"removed_in must be greater than deprecated_in for {rid}")
        for field in ("rationale", "risk_if_violated"):
            if not str(r.get(field, "")).strip():
                errs.append(f"policy rule missing {field}: {rid}")
        refs = r.get("references")
        if not isinstance(refs, list) or not refs:
            errs.append(f"policy rule references must be a non-empty list: {rid}")
            refs = []
        for rel in refs:
            srel = str(rel)
            if not _exists_repo_or_runner(repo_root, srel):
                errs.append(f"missing policy reference for {rid}: {srel}")

    links_by_rule: dict[str, dict[str, Any]] = {}
    referenced_contract_docs: set[str] = set()
    for l in links:
        if not isinstance(l, dict):
            errs.append("traceability link entries must be mappings")
            continue
        rid = str(l.get("rule_id", "")).strip()
        if not rid:
            errs.append("traceability link missing rule_id")
            continue
        if rid in links_by_rule:
            errs.append(f"duplicate traceability rule_id: {rid}")
        links_by_rule[rid] = l
        if rid not in rules_by_id:
            errs.append(f"traceability references unknown policy rule: {rid}")
        want_policy_ref = f"specs/contract/policy_v1.yaml#{rid}"
        got_policy_ref = str(l.get("policy_ref", "")).strip()
        if got_policy_ref != want_policy_ref:
            errs.append(
                f"traceability policy_ref mismatch for {rid}: "
                f"expected {want_policy_ref}, got {got_policy_ref or '<missing>'}"
            )
        cref = l.get("contract_refs") or []
        if isinstance(cref, list):
            for rel in cref:
                referenced_contract_docs.add(str(rel))

    for rid in rules_by_id:
        if rid not in links_by_rule:
            errs.append(f"policy rule missing traceability link: {rid}")

    for rid, rule in rules_by_id.items():
        norm = str(rule.get("norm", "")).upper()
        link = links_by_rule.get(rid)
        if not link:
            continue

        conformance_case_ids = link.get("conformance_case_ids") or []
        unit_test_refs = link.get("unit_test_refs") or []
        if not isinstance(conformance_case_ids, list):
            errs.append(f"traceability conformance_case_ids must be a list: {rid}")
            conformance_case_ids = []
        if not isinstance(unit_test_refs, list):
            errs.append(f"traceability unit_test_refs must be a list: {rid}")
            unit_test_refs = []

        if norm == "MUST" and not conformance_case_ids and not unit_test_refs:
            errs.append(f"MUST rule missing test evidence (conformance_case_ids/unit_test_refs): {rid}")

        for rel in link.get("contract_refs") or []:
            if not _exists_repo_or_runner(repo_root, str(rel)):
                errs.append(f"missing contract_ref for {rid}: {rel}")
        for rel in link.get("schema_refs") or []:
            if not _exists_repo_or_runner(repo_root, str(rel)):
                errs.append(f"missing schema_ref for {rid}: {rel}")
        for rel in unit_test_refs:
            if not _exists_repo_or_runner(repo_root, str(rel)):
                errs.append(f"missing unit_test_ref for {rid}: {rel}")
        for rel in link.get("implementation_refs") or []:
            if not _exists_repo_or_runner(repo_root, str(rel)):
                errs.append(f"missing implementation_ref for {rid}: {rel}")

        for cid in conformance_case_ids:
            c = str(cid)
            if c not in conformance_ids:
                errs.append(f"missing conformance case id for {rid}: {c}")

    for rel in _NORMATIVE_CONTRACT_DOCS:
        if not _exists_repo_or_runner(repo_root, rel):
            errs.append(f"missing normative contract doc: {rel}")
        elif rel not in referenced_contract_docs:
            errs.append(f"normative contract doc missing traceability coverage: {rel}")

    return errs
