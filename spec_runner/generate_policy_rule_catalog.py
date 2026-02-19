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


def _build_payload(repo_root: Path) -> dict[str, Any]:
    policy_path = repo_root / "specs/contract/policy_v1.yaml"
    payload = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    rules = payload.get("rules") if isinstance(payload, dict) else None
    if not isinstance(rules, list):
        raise ValueError("specs/contract/policy_v1.yaml: rules must be a list")

    rows: list[dict[str, Any]] = []
    for raw in rules:
        if not isinstance(raw, dict):
            continue
        rid = str(raw.get("id", "")).strip()
        if not rid:
            continue
        refs = raw.get("references")
        ref_count = len(refs) if isinstance(refs, list) else 0
        rows.append(
            {
                "id": rid,
                "norm": str(raw.get("norm", "")).strip(),
                "scope": str(raw.get("scope", "")).strip(),
                "applies_to": str(raw.get("applies_to", "")).strip(),
                "introduced_in": str(raw.get("introduced_in", "")).strip(),
                "deprecated_in": str(raw.get("deprecated_in", "")).strip(),
                "removed_in": str(raw.get("removed_in", "")).strip(),
                "reference_count": int(ref_count),
            }
        )

    norm_counts: dict[str, int] = {"MUST": 0, "SHOULD": 0, "MUST_NOT": 0}
    lifecycle_counts: dict[str, int] = {"active": 0, "deprecated": 0, "removed": 0}
    for row in rows:
        norm = str(row.get("norm", "")).upper()
        if norm in norm_counts:
            norm_counts[norm] += 1
        removed_in = str(row.get("removed_in", "")).strip()
        deprecated_in = str(row.get("deprecated_in", "")).strip()
        if removed_in:
            lifecycle_counts["removed"] += 1
        elif deprecated_in:
            lifecycle_counts["deprecated"] += 1
        else:
            lifecycle_counts["active"] += 1

    rows = sorted(rows, key=lambda x: str(x.get("id", "")))
    return {
        "version": 1,
        "summary": {
            "rule_count": len(rows),
            "must_count": norm_counts["MUST"],
            "should_count": norm_counts["SHOULD"],
            "must_not_count": norm_counts["MUST_NOT"],
            "active_count": lifecycle_counts["active"],
            "deprecated_count": lifecycle_counts["deprecated"],
            "removed_count": lifecycle_counts["removed"],
        },
        "rules": rows,
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = dict(payload.get("summary") or {})
    lines = [
        "## Generated Contract Policy Rule Catalog",
        "",
        f"- rule_count: {int(summary.get('rule_count', 0))}",
        f"- must_count: {int(summary.get('must_count', 0))}",
        f"- should_count: {int(summary.get('should_count', 0))}",
        f"- must_not_count: {int(summary.get('must_not_count', 0))}",
        f"- active_count: {int(summary.get('active_count', 0))}",
        f"- deprecated_count: {int(summary.get('deprecated_count', 0))}",
        f"- removed_count: {int(summary.get('removed_count', 0))}",
        "",
        "| id | norm | scope | applies_to | references | lifecycle |",
        "|---|---|---|---|---|---|",
    ]
    for row in payload.get("rules") or []:
        lifecycle = "active"
        if str(row.get("removed_in", "")).strip():
            lifecycle = "removed"
        elif str(row.get("deprecated_in", "")).strip():
            lifecycle = "deprecated"
        lines.append(
            f"| `{row.get('id', '')}` | `{row.get('norm', '')}` | `{row.get('scope', '')}` | "
            f"`{row.get('applies_to', '')}` | {int(row.get('reference_count', 0))} | `{lifecycle}` |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate contract policy rule catalog JSON and markdown section.")
    ap.add_argument("--out", default=".artifacts/policy-rule-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/94_appendix_contract_policy_reference.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _build_payload(repo_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    md_block = _render_md(payload)
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="policy_rule_catalog",
        body=md_block,
    )

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        if parse_generated_block(doc_path.read_text(encoding="utf-8"), surface_id="policy_rule_catalog").strip() != md_block.strip():
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
