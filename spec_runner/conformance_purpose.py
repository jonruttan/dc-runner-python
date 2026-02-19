from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from spec_runner.doc_parser import iter_spec_doc_tests
from spec_runner.purpose_lint import (
    POLICY_REL_PATH,
    load_purpose_lint_policy,
    purpose_quality_warnings,
    resolve_purpose_lint_config,
    warning_severity_for_code,
)

PURPOSE_WARNING_CODES = ("PUR001", "PUR002", "PUR003", "PUR004")
PURPOSE_WARNING_CODE_TO_DESCRIPTION = {
    "PUR001": "purpose duplicates title",
    "PUR002": "purpose word count below minimum",
    "PUR003": "purpose contains placeholder token",
    "PUR004": "purpose lint configuration/policy error",
}
PURPOSE_WARNING_CODE_TO_HINT = {
    "PUR001": "Rewrite purpose to explain intent or risk not already stated in title.",
    "PUR002": "Expand purpose to meet the configured minimum word count.",
    "PUR003": "Replace placeholder tokens with concrete, implementation-neutral intent.",
    "PUR004": "Fix purpose_lint settings or policy file shape/version before rerunning.",
}
PURPOSE_WARNING_CODE_TO_SUGGESTED_EDIT = {
    "PUR001": "Rewrite `purpose` to state intent or risk not already present in `title`.",
    "PUR002": "Expand `purpose` with concrete behavior intent to meet the minimum word count.",
    "PUR003": "Replace placeholder tokens with concrete, implementation-neutral intent text.",
    "PUR004": "Fix `purpose_lint` configuration or policy schema/version before rerunning.",
}


@dataclass(frozen=True)
class ConformancePurposeRow:
    id: str
    title: str
    purpose: str
    type: str
    file: str
    purpose_lint: dict[str, Any]
    warnings: list[dict[str, str]]


def _display_path(path: Path, *, cwd: Path) -> str:
    try:
        return str(path.resolve().relative_to(cwd.resolve()))
    except ValueError:
        return str(path.resolve())


def _warning(code: str, message: str, *, cfg: dict[str, Any]) -> dict[str, Any]:
    suggested = PURPOSE_WARNING_CODE_TO_SUGGESTED_EDIT.get(
        code,
        "Update purpose lint configuration and provide concrete purpose text.",
    )
    if code == "PUR002":
        min_words = int(cfg.get("min_words", 8))
        suggested = (
            "Expand `purpose` with concrete behavior intent "
            f"to at least {min_words} words."
        )
    return {
        "code": code,
        "message": message,
        "severity": warning_severity_for_code(code, cfg),
        "hint": PURPOSE_WARNING_CODE_TO_HINT.get(code, "Review warning details and update purpose lint configuration."),
        "suggested_edit": suggested,
    }


def _quality_warning_to_structured(msg: str, *, cfg: dict[str, Any]) -> dict[str, str]:
    if msg == "purpose duplicates title":
        return _warning("PUR001", msg, cfg=cfg)
    if msg.startswith("purpose word count "):
        return _warning("PUR002", msg, cfg=cfg)
    if msg.startswith("purpose contains placeholder token(s):"):
        return _warning("PUR003", msg, cfg=cfg)
    return _warning("PUR004", msg, cfg=cfg)


def collect_conformance_purpose_rows(cases_dir: Path, *, purpose_policy: dict[str, Any]) -> list[ConformancePurposeRow]:
    cwd = Path.cwd()
    rows: list[ConformancePurposeRow] = []
    for spec in iter_spec_doc_tests(cases_dir):
        test = dict(spec.test)
        cfg, cfg_errs = resolve_purpose_lint_config(test, purpose_policy)
        warns: list[dict[str, str]] = [_warning("PUR004", str(e), cfg=cfg) for e in cfg_errs]
        warns.extend(
            _quality_warning_to_structured(w, cfg=cfg)
            for w in purpose_quality_warnings(
                str(test.get("title", "")).strip(),
                str(test.get("purpose", "")).strip(),
                cfg,
                honor_enabled=False,
            )
        )
        rows.append(
            ConformancePurposeRow(
                id=str(test.get("id", "")).strip(),
                title=str(test.get("title", "")).strip(),
                purpose=str(test.get("purpose", "")).strip(),
                type=str(test.get("type", "")).strip(),
                file=_display_path(spec.doc_path, cwd=cwd),
                purpose_lint=cfg,
                warnings=warns,
            )
        )
    rows.sort(key=lambda r: (r.id, r.file))
    return rows


def conformance_purpose_report_jsonable(cases_dir: Path, *, repo_root: Path) -> dict[str, Any]:
    policy, policy_errs, policy_path = load_purpose_lint_policy(repo_root)
    rows = collect_conformance_purpose_rows(cases_dir, purpose_policy=policy)
    row_warning_count = sum(len(r.warnings) for r in rows)
    warning_code_counts: dict[str, int] = {}
    warning_severity_counts: dict[str, int] = {}
    for row in rows:
        for w in row.warnings:
            code = str(w.get("code", "")).strip() or "PUR004"
            warning_code_counts[code] = warning_code_counts.get(code, 0) + 1
            sev = str(w.get("severity", "")).strip().lower()
            if sev in {"info", "warn", "error"}:
                warning_severity_counts[sev] = warning_severity_counts.get(sev, 0) + 1
    if policy_errs:
        warning_code_counts["PUR004"] = warning_code_counts.get("PUR004", 0) + len(policy_errs)
        warning_severity_counts["error"] = warning_severity_counts.get("error", 0) + len(policy_errs)
    return {
        "version": 1,
        "summary": {
            "total_rows": len(rows),
            "rows_with_warnings": sum(1 for r in rows if r.warnings),
            "row_warning_count": row_warning_count,
            "policy_error_count": len(policy_errs),
            "total_warning_count": row_warning_count + len(policy_errs),
            "warning_code_counts": warning_code_counts,
            "warning_severity_counts": warning_severity_counts,
        },
        "policy": {
            "path": POLICY_REL_PATH,
            "exists": policy_path.exists(),
            "config": policy,
            "errors": policy_errs,
        },
        "rows": [asdict(r) for r in rows],
    }
