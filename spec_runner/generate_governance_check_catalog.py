#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from spec_runner.doc_parser import iter_spec_doc_tests
from spec_runner.governance_runtime import _CHECKS
from spec_runner.settings import case_file_name
from spec_runner.docs_generators import parse_generated_block, replace_generated_block, write_json


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return repo_root / str(raw).lstrip("/")


def _cases_by_check(cases_root: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for spec in iter_spec_doc_tests(cases_root, file_pattern=case_file_name("*")):
        case = spec.test if isinstance(spec.test, dict) else {}
        if str(case.get("type", "")).strip() != "governance.check":
            continue
        check = str(case.get("check", "")).strip()
        case_id = str(case.get("id", "")).strip()
        if not check or not case_id:
            continue
        out.setdefault(check, []).append(case_id)
    for key in list(out):
        out[key] = sorted(set(out[key]))
    return out


def _build_payload(repo_root: Path) -> dict[str, Any]:
    checks = _CHECKS
    if not isinstance(checks, dict):
        raise ValueError("spec_runner.governance_runtime._CHECKS must be a mapping")
    case_map = _cases_by_check(repo_root / "specs/governance/cases/core")

    rows: list[dict[str, Any]] = []
    for check_id in sorted(str(x) for x in checks.keys()):
        case_ids = case_map.get(check_id, [])
        rows.append(
            {
                "check_id": check_id,
                "case_count": len(case_ids),
                "case_ids": case_ids,
                "has_case": len(case_ids) > 0,
            }
        )

    return {
        "version": 1,
        "summary": {
            "check_count": len(rows),
            "checks_with_cases": sum(1 for r in rows if bool(r.get("has_case"))),
            "checks_without_cases": sum(1 for r in rows if not bool(r.get("has_case"))),
        },
        "checks": rows,
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = dict(payload.get("summary") or {})
    lines = [
        "## Generated Governance Check Catalog",
        "",
        f"- check_count: {int(summary.get('check_count', 0))}",
        f"- checks_with_cases: {int(summary.get('checks_with_cases', 0))}",
        f"- checks_without_cases: {int(summary.get('checks_without_cases', 0))}",
        "",
        "| check_id | case_count | has_case |",
        "|---|---|---|",
    ]
    for row in payload.get("checks") or []:
        lines.append(
            f"| `{row.get('check_id', '')}` | {int(row.get('case_count', 0))} | "
            f"{str(bool(row.get('has_case', False))).lower()} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate governance check catalog JSON and markdown section.")
    ap.add_argument("--out", default=".artifacts/governance-check-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/96_appendix_governance_checks_reference.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _build_payload(repo_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    md_block = _render_md(payload)
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="governance_check_catalog",
        body=md_block,
    )

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        if parse_generated_block(doc_path.read_text(encoding="utf-8"), surface_id="governance_check_catalog").strip() != md_block.strip():
            print(f"{ns.doc_out}: generated content out of date")
            return 1
        if out_path.exists() and out_path.read_text(encoding="utf-8") != expected_json:
            print(f"{ns.out}: generated content out of date")
            return 1
        return 0

    write_json(out_path, payload)
    doc_path.write_text(updated_doc, encoding="utf-8")
    print(f"wrote {ns.out}")
    print(f"wrote {ns.doc_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
