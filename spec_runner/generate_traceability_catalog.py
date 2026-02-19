#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from spec_runner.docs_generators import parse_generated_block, replace_generated_block, write_json


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return repo_root / str(raw).lstrip("/")


def _count_list(node: dict[str, Any], key: str) -> int:
    value = node.get(key)
    if not isinstance(value, list):
        return 0
    return len(value)


def _build_payload(repo_root: Path) -> dict[str, Any]:
    trace_path = repo_root / "specs/contract/traceability_v1.yaml"
    payload = yaml.safe_load(trace_path.read_text(encoding="utf-8"))
    links = payload.get("links") if isinstance(payload, dict) else None
    if not isinstance(links, list):
        raise ValueError("specs/contract/traceability_v1.yaml: links must be a list")

    rows: list[dict[str, Any]] = []
    for raw in links:
        if not isinstance(raw, dict):
            continue
        rid = str(raw.get("rule_id", "")).strip()
        if not rid:
            continue
        rows.append(
            {
                "rule_id": rid,
                "policy_ref": str(raw.get("policy_ref", "")).strip(),
                "contract_ref_count": _count_list(raw, "contract_refs"),
                "schema_ref_count": _count_list(raw, "schema_refs"),
                "conformance_case_count": _count_list(raw, "conformance_case_ids"),
                "unit_test_ref_count": _count_list(raw, "unit_test_refs"),
                "implementation_ref_count": _count_list(raw, "implementation_refs"),
            }
        )
    rows = sorted(rows, key=lambda x: str(x.get("rule_id", "")))
    return {
        "version": 1,
        "summary": {
            "link_count": len(rows),
            "rules_with_conformance_cases": sum(1 for r in rows if int(r.get("conformance_case_count", 0)) > 0),
            "rules_with_unit_tests": sum(1 for r in rows if int(r.get("unit_test_ref_count", 0)) > 0),
            "rules_with_implementation_refs": sum(1 for r in rows if int(r.get("implementation_ref_count", 0)) > 0),
        },
        "links": rows,
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = dict(payload.get("summary") or {})
    lines = [
        "## Generated Traceability Catalog",
        "",
        f"- link_count: {int(summary.get('link_count', 0))}",
        f"- rules_with_conformance_cases: {int(summary.get('rules_with_conformance_cases', 0))}",
        f"- rules_with_unit_tests: {int(summary.get('rules_with_unit_tests', 0))}",
        f"- rules_with_implementation_refs: {int(summary.get('rules_with_implementation_refs', 0))}",
        "",
        "| rule_id | policy_ref | contract_refs | schema_refs | conformance_cases | unit_tests | implementation_refs |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in payload.get("links") or []:
        lines.append(
            f"| `{row.get('rule_id', '')}` | `{row.get('policy_ref', '')}` | "
            f"{int(row.get('contract_ref_count', 0))} | {int(row.get('schema_ref_count', 0))} | "
            f"{int(row.get('conformance_case_count', 0))} | {int(row.get('unit_test_ref_count', 0))} | "
            f"{int(row.get('implementation_ref_count', 0))} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate traceability catalog JSON and markdown section.")
    ap.add_argument("--out", default=".artifacts/traceability-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/95_appendix_traceability_reference.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _build_payload(repo_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    md_block = _render_md(payload)
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="traceability_catalog",
        body=md_block,
    )

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        if parse_generated_block(doc_path.read_text(encoding="utf-8"), surface_id="traceability_catalog").strip() != md_block.strip():
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
