#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

from spec_runner.conformance_purpose import conformance_purpose_report_jsonable


def _to_markdown(payload: dict) -> str:
    summary = payload.get("summary") or {}
    code_counts = summary.get("warning_code_counts") or {}
    severity_counts = summary.get("warning_severity_counts") or {}
    lines = [
        "# Conformance Purpose Report",
        "",
        f"- total cases: {int(summary.get('total_rows', 0))}",
        f"- rows with warnings: {int(summary.get('rows_with_warnings', 0))}",
        f"- total warnings: {int(summary.get('total_warning_count', 0))}",
    ]
    if code_counts:
        parts = [f"{k}={int(v)}" for k, v in sorted(code_counts.items())]
        lines.append(f"- warning codes: {', '.join(parts)}")
    if severity_counts:
        parts = [f"{k}={int(v)}" for k, v in sorted(severity_counts.items())]
        lines.append(f"- warning severities: {', '.join(parts)}")
    lines.extend(
        [
        "",
        "## Warnings",
        "",
        "| id | type | severity | code | warning | hint | suggested edit | file |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    had_any = False
    for row in payload.get("rows", []):
        rid = str(row.get("id", "")).strip()
        rtype = str(row.get("type", "")).strip()
        file_ = str(row.get("file", "")).strip()
        for w in row.get("warnings", []) or []:
            had_any = True
            if isinstance(w, dict):
                code = str(w.get("code", "")).strip()
                message = str(w.get("message", "")).strip()
                severity = str(w.get("severity", "")).strip().lower() or "warn"
                hint = str(w.get("hint", "")).strip()
                suggested_edit = str(w.get("suggested_edit", "")).strip()
            else:
                code = "PUR004"
                message = str(w).strip()
                severity = "error"
                hint = "Review warning details and update purpose lint configuration."
                suggested_edit = "Update purpose lint configuration and provide concrete purpose text."
            ww = message.replace("|", "\\|")
            hh = hint.replace("|", "\\|")
            ee = suggested_edit.replace("|", "\\|")
            lines.append(f"| {rid} | {rtype} | {severity} | {code} | {ww} | {hh} | {ee} | {file_} |")
    if not had_any:
        lines.append("| - | - | - | - | none | - | - | - |")
    return "\n".join(lines) + "\n"


def _filtered_only_warnings(payload: dict) -> dict:
    out = copy.deepcopy(payload)
    rows = [r for r in out.get("rows", []) if (r.get("warnings") or [])]
    out["rows"] = rows
    summary = out.get("summary") or {}
    summary["total_rows"] = len(rows)
    summary["rows_with_warnings"] = len(rows)
    summary["row_warning_count"] = sum(len(r.get("warnings") or []) for r in rows)
    summary["total_warning_count"] = int(summary.get("row_warning_count", 0)) + int(summary.get("policy_error_count", 0))
    code_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    for r in rows:
        for w in r.get("warnings") or []:
            if isinstance(w, dict):
                code = str(w.get("code", "")).strip() or "PUR004"
                sev = str(w.get("severity", "")).strip().lower()
            else:
                code = "PUR004"
                sev = "error"
            code_counts[code] = code_counts.get(code, 0) + 1
            if sev in {"info", "warn", "error"}:
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
    if int(summary.get("policy_error_count", 0)) > 0:
        code_counts["PUR004"] = code_counts.get("PUR004", 0) + int(summary.get("policy_error_count", 0))
        severity_counts["error"] = severity_counts.get("error", 0) + int(summary.get("policy_error_count", 0))
    summary["warning_code_counts"] = code_counts
    summary["warning_severity_counts"] = severity_counts
    summary["only_warnings"] = True
    out["summary"] = summary
    return out


def _safe_slug(case_id: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", str(case_id).strip())
    s = s.strip("-")
    return s or "unknown-case"


def _emit_patch_snippets(payload: dict, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    for row in payload.get("rows", []):
        warnings = row.get("warnings") or []
        if not warnings:
            continue
        rid = str(row.get("id", "")).strip() or "UNKNOWN"
        path = out_dir / f"{_safe_slug(rid)}.md"
        lines = [f"# {rid}", "", f"file: `{row.get('file', '')}`", ""]
        for i, w in enumerate(warnings, start=1):
            if isinstance(w, dict):
                code = str(w.get("code", "")).strip()
                msg = str(w.get("message", "")).strip()
                hint = str(w.get("hint", "")).strip()
                edit = str(w.get("suggested_edit", "")).strip()
            else:
                code = "PUR004"
                msg = str(w).strip()
                hint = "Review warning details and update purpose lint configuration."
                edit = "Update purpose lint configuration and provide concrete purpose text."
            lines.extend(
                [
                    f"## Warning {i} ({code})",
                    f"- message: {msg}",
                    f"- hint: {hint}",
                    f"- suggested_edit: {edit}",
                    "",
                    "```yaml",
                    f"purpose: \"{edit}\"",
                    "```",
                    "",
                ]
            )
        path.write_text("\n".join(lines), encoding="utf-8")
        created += 1
    return created


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Emit conformance purpose report.")
    ap.add_argument(
        "--cases",
        default="specs/conformance/cases",
        help="Path to conformance case docs directory",
    )
    ap.add_argument("--out", help="Optional output path for report.")
    ap.add_argument(
        "--format",
        choices=("json", "md"),
        default="json",
        help="Output format.",
    )
    ap.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Return non-zero exit when the report contains warnings.",
    )
    ap.add_argument(
        "--fail-on-severity",
        choices=("warn", "error"),
        default="",
        help="Return non-zero exit when warnings at or above this severity are present.",
    )
    ap.add_argument(
        "--only-warnings",
        action="store_true",
        help="Emit only rows that contain warnings.",
    )
    ap.add_argument(
        "--emit-patches",
        default="",
        help="Optional directory to write per-case remediation snippet markdown files.",
    )
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = conformance_purpose_report_jsonable(Path(ns.cases), repo_root=repo_root)
    if ns.only_warnings:
        payload = _filtered_only_warnings(payload)
    if str(ns.emit_patches).strip():
        patch_dir = Path(str(ns.emit_patches))
        count = _emit_patch_snippets(payload, patch_dir)
        print(f"wrote {count} patch snippet file(s) to {patch_dir}")
    if ns.format == "md":
        raw = _to_markdown(payload)
    else:
        raw = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.out:
        out = Path(ns.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(raw, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(raw, end="")
    summary = payload.get("summary") or {}
    total_warn = int(summary.get("total_warning_count", 0))
    threshold = str(ns.fail_on_severity).strip().lower()
    if not threshold and ns.fail_on_warn:
        threshold = "warn"
    if threshold:
        sev_counts = summary.get("warning_severity_counts") or {}
        warn_count = int(sev_counts.get("warn", 0))
        error_count = int(sev_counts.get("error", 0))
        at_or_above = error_count if threshold == "error" else (warn_count + error_count)
        if at_or_above > 0:
            print(
                f"ERROR: conformance purpose report has {at_or_above} warning(s) at or above severity '{threshold}'",
                file=sys.stderr,
            )
            return 1
    elif ns.fail_on_warn and total_warn > 0:
        print(
            f"ERROR: conformance purpose report has {total_warn} warning(s)",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
