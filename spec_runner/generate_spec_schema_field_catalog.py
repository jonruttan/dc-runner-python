#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from spec_runner.docs_generators import replace_generated_block, write_json
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
    top_fields = dict(compiled.get("top_level_fields") or {})
    type_profiles = dict(compiled.get("type_profiles") or {})

    top_rows: list[dict[str, Any]] = []
    for key, meta in sorted(top_fields.items()):
        top_rows.append(
            {
                "key": str(key),
                "type": str(meta.get("type", "any")),
                "required": bool(meta.get("required", False)),
                "since": str(meta.get("since", "v1")),
            }
        )

    profile_rows: list[dict[str, Any]] = []
    for case_type, prof in sorted(type_profiles.items()):
        fields = sorted(dict(prof.get("fields") or {}).keys())
        profile_rows.append(
            {
                "case_type": case_type,
                "field_count": len(fields),
                "fields": fields,
                "required_top_level": list(prof.get("required_top_level") or []),
                "allowed_top_level_extra": list(prof.get("allowed_top_level_extra") or []),
            }
        )

    return {
        "version": 1,
        "summary": {
            "top_level_field_count": len(top_rows),
            "type_profile_count": len(profile_rows),
            "total_type_field_count": sum(int(r.get("field_count", 0)) for r in profile_rows),
        },
        "top_level_fields": top_rows,
        "type_profiles": profile_rows,
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = dict(payload.get("summary") or {})
    lines = [
        "## Generated Spec Schema Field Catalog",
        "",
        f"- top_level_field_count: {int(summary.get('top_level_field_count', 0))}",
        f"- type_profile_count: {int(summary.get('type_profile_count', 0))}",
        f"- total_type_field_count: {int(summary.get('total_type_field_count', 0))}",
        "",
        "### Top-Level Fields",
        "",
        "| key | type | required | since |",
        "|---|---|---|---|",
    ]
    for row in payload.get("top_level_fields") or []:
        lines.append(
            f"| `{row.get('key', '')}` | `{row.get('type', 'any')}` | "
            f"{str(bool(row.get('required', False))).lower()} | `{row.get('since', 'v1')}` |"
        )
    lines += ["", "### Type Profiles", "", "| case_type | field_count | required_top_level |", "|---|---|---|"]
    for row in payload.get("type_profiles") or []:
        required = ", ".join(f"`{x}`" for x in row.get("required_top_level") or []) or "-"
        lines.append(
            f"| `{row.get('case_type', '')}` | {int(row.get('field_count', 0))} | {required} |"
        )
    lines.append("")
    return "\n".join(lines)


def _update_doc(path: Path, *, surface_id: str, body: str, check: bool) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    updated = replace_generated_block(text, surface_id=surface_id, body=body)
    if check:
        return text == updated, path.as_posix()
    path.write_text(updated, encoding="utf-8")
    return True, path.as_posix()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate schema field catalog JSON and markdown sections.")
    ap.add_argument("--out", default=".artifacts/spec-schema-field-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/98_appendix_spec_case_shape_reference.md")
    ap.add_argument("--schema-doc-out", default="specs/schema/schema_v1.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _build_payload(repo_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    schema_doc_path = _resolve_cli_path(repo_root, str(ns.schema_doc_out))
    md_block = _render_md(payload)

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        ok_doc, doc_name = _update_doc(doc_path, surface_id="spec_schema_field_catalog", body=md_block, check=True)
        ok_schema, schema_name = _update_doc(schema_doc_path, surface_id="spec_schema_field_catalog", body=md_block, check=True)
        if not ok_doc:
            print(f"{doc_name}: generated content out of date")
            return 1
        if not ok_schema:
            print(f"{schema_name}: generated content out of date")
            return 1
        if out_path.exists() and out_path.read_text(encoding="utf-8") != expected_json:
            print(f"{ns.out}: generated content out of date")
            return 1
        return 0

    _update_doc(doc_path, surface_id="spec_schema_field_catalog", body=md_block, check=False)
    _update_doc(schema_doc_path, surface_id="spec_schema_field_catalog", body=md_block, check=False)
    write_json(out_path, payload)
    print(f"wrote {ns.out}")
    print(f"wrote {ns.doc_out}")
    print(f"wrote {ns.schema_doc_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
