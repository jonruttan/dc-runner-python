#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from spec_runner.docs_generators import (
    parse_generated_block,
    replace_generated_block,
    write_json,
)
from spec_runner.docs_template_engine import render_moustache
from spec_runner.schema_registry import compile_registry


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return repo_root / str(raw).lstrip("/")


def _build_payload(repo_root: Path) -> dict[str, Any]:
    compiled, errs = compile_registry(repo_root)
    if compiled is None:
        raise ValueError("; ".join(errs))
    profiles = dict(compiled.get("type_profiles") or {})
    semantics: dict[str, dict[str, Any]] = {
        "contract.check": {
            "summary": "Runs canonical contract checks using harness.check profiles.",
            "defaults": ["evaluate-only assertions", "MUST/MAY/MUST_NOT class semantics"],
            "failure_modes": ["unknown check profile", "invalid check config"],
        },
        "contract.export": {
            "summary": "Declares reusable contract symbol exports for chain imports.",
            "defaults": ["harness.exports with from=assert.function"],
            "failure_modes": ["invalid export shape", "unresolvable export path"],
        },
        "contract.job": {
            "summary": "Executes harness.jobs metadata through contract-driven ops.job.dispatch.",
            "defaults": ["dispatch from contract assertions", "summary_json output target"],
            "failure_modes": ["missing job metadata", "dispatch helper error"],
        },
    }

    rows: list[dict[str, Any]] = []
    for case_type, prof in sorted(profiles.items()):
        fields = sorted(dict(prof.get("fields") or {}).keys())
        required_top_level = list(prof.get("required_top_level") or [])
        allowed_extra = list(prof.get("allowed_top_level_extra") or [])
        type_semantics = semantics.get(
            case_type,
            {
                "summary": "Harness type profile declared in schema registry.",
                "defaults": [],
                "failure_modes": ["schema validation failure"],
            },
        )
        rows.append(
            {
                "case_type": case_type,
                "field_count": len(fields),
                "fields": fields,
                "required_top_level": required_top_level,
                "allowed_top_level_extra": allowed_extra,
                "required_top_level_md": ", ".join(f"`{x}`" for x in required_top_level) or "-",
                "allowed_top_level_extra_md": ", ".join(f"`{x}`" for x in allowed_extra) or "-",
                "summary": type_semantics["summary"],
                "defaults": type_semantics["defaults"],
                "failure_modes": type_semantics["failure_modes"],
                "examples": [
                    {
                        "title": "Case type usage",
                        "snippet": f"type: {case_type}",
                    }
                ],
            }
        )
    complete = 0
    for row in rows:
        if (
            str(row.get("summary", "")).strip()
            and isinstance(row.get("defaults"), list)
            and isinstance(row.get("failure_modes"), list)
            and isinstance(row.get("examples"), list)
            and bool(row.get("examples"))
        ):
            complete += 1
    coverage = 0.0 if not rows else (complete / len(rows))
    return {
        "version": 2,
        "summary": {
            "type_profile_count": len(rows),
            "total_type_field_count": sum(int(r.get("field_count", 0)) for r in rows),
        },
        "quality": {
            "semantics_complete_count": complete,
            "semantics_coverage_ratio": round(coverage, 4),
            "score": round(coverage, 4),
        },
        "type_profiles": rows,
    }


def _render_md(payload: dict[str, Any], *, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    return render_moustache(template, {"harness": payload}, strict=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate harness type catalog from schema registry.")
    ap.add_argument("--out", default=".artifacts/harness-type-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/92_appendix_harness_type_reference.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _build_payload(repo_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    md_block = _render_md(payload, template_path=repo_root / "docs/book/templates/harness_type_catalog_template.md")
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="harness_type_catalog",
        body=md_block,
    )

    import json

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        if parse_generated_block(doc_path.read_text(encoding="utf-8"), surface_id="harness_type_catalog").strip() != md_block.strip():
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
