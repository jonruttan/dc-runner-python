#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from spec_runner.codecs import load_external_cases
from spec_runner.docs_generators import parse_generated_block, replace_generated_block, write_json
from spec_runner.docs_template_engine import render_moustache
from spec_runner.spec_domain import normalize_case_domain

_CASE_DOC_ALLOWED_KEYS = {
    "summary",
    "description",
    "audience",
    "since",
    "tags",
    "see_also",
    "deprecated",
}


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return repo_root / str(raw).lstrip("/")


def _as_non_empty_string(value: Any, *, field: str, issues: list[str], where: str) -> str:
    out = str(value or "").strip()
    if not out:
        issues.append(f"{where}: {field} must be a non-empty string")
    return out


def _anchor_for(case_id: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", case_id.lower()).strip("_")
    return f"case-{slug}" if slug else "case"


def _domain_label(raw: object, *, where: str, issues: list[str]) -> str:
    try:
        return normalize_case_domain(raw) or "unscoped"
    except (TypeError, ValueError):
        issues.append(f"{where}: domain must be a non-empty string when provided")
        return "unscoped"


def _validate_case_doc(raw_doc: Any, *, where: str, issues: list[str], required: bool) -> dict[str, Any] | None:
    if not isinstance(raw_doc, dict):
        if required:
            issues.append(f"{where}: doc must be a mapping")
        return None
    unknown = sorted(str(k) for k in raw_doc.keys() if str(k) not in _CASE_DOC_ALLOWED_KEYS)
    if unknown:
        issues.append(f"{where}: unsupported doc keys: {', '.join(unknown)}")
    summary = _as_non_empty_string(raw_doc.get("summary"), field="doc.summary", issues=issues, where=where)
    description = _as_non_empty_string(
        raw_doc.get("description"), field="doc.description", issues=issues, where=where
    )
    audience = _as_non_empty_string(raw_doc.get("audience"), field="doc.audience", issues=issues, where=where)
    since = _as_non_empty_string(raw_doc.get("since", "v1"), field="doc.since", issues=issues, where=where)

    tags_raw = raw_doc.get("tags")
    tags: list[str]
    if tags_raw is None:
        tags = []
    elif isinstance(tags_raw, list) and all(isinstance(x, str) and str(x).strip() for x in tags_raw):
        tags = [str(x).strip() for x in tags_raw]
    else:
        issues.append(f"{where}: doc.tags must be a list of non-empty strings when provided")
        tags = []

    see_also_raw = raw_doc.get("see_also")
    see_also: list[str]
    if see_also_raw is None:
        see_also = []
    elif isinstance(see_also_raw, list) and all(isinstance(x, str) and str(x).strip() for x in see_also_raw):
        see_also = [str(x).strip() for x in see_also_raw]
    else:
        issues.append(f"{where}: doc.see_also must be a list of non-empty strings when provided")
        see_also = []

    deprecated_raw = raw_doc.get("deprecated")
    deprecated: dict[str, str] | None = None
    if deprecated_raw is not None:
        if not isinstance(deprecated_raw, dict):
            issues.append(f"{where}: doc.deprecated must be a mapping when provided")
        else:
            deprecated = {
                "replacement": _as_non_empty_string(
                    deprecated_raw.get("replacement"),
                    field="doc.deprecated.replacement",
                    issues=issues,
                    where=where,
                ),
                "reason": _as_non_empty_string(
                    deprecated_raw.get("reason"),
                    field="doc.deprecated.reason",
                    issues=issues,
                    where=where,
                ),
            }

    return {
        "summary": summary,
        "description": description,
        "audience": audience,
        "since": since,
        "tags": tags,
        "see_also": see_also,
        "deprecated": deprecated,
    }


def _build_payload(repo_root: Path, *, specs_root: Path) -> dict[str, Any]:
    issues: list[str] = []
    rows: list[dict[str, Any]] = []

    for doc_path, case in load_external_cases(specs_root, formats={"md"}, md_pattern="*.spec.md"):
        case_id = str(case.get("id", "")).strip()
        if not case_id:
            continue
        case_type = str(case.get("type", "")).strip()
        rel = "/" + doc_path.resolve().relative_to(repo_root.resolve()).as_posix()
        where = f"{rel}: case {case_id}"
        raw_doc = case.get("doc")
        required = case_type == "contract.export"
        case_doc = _validate_case_doc(raw_doc, where=where, issues=issues, required=required)
        if case_doc is None:
            continue
        rows.append(
            {
                "case_id": case_id,
                "type": case_type,
                "domain": _domain_label(case.get("domain"), where=where, issues=issues),
                "title": str(case.get("title", "")).strip(),
                "source_doc": rel,
                "anchor": _anchor_for(case_id),
                "summary": case_doc["summary"],
                "description": case_doc["description"],
                "audience": case_doc["audience"],
                "since": case_doc["since"],
                "tags": case_doc["tags"],
                "see_also": case_doc["see_also"],
                "deprecated": case_doc["deprecated"],
            }
        )

    if issues:
        raise ValueError("\n".join(issues[:200]))

    rows_sorted = sorted(
        rows,
        key=lambda r: (
            str(r.get("domain", "")),
            str(r.get("type", "")),
            str(r.get("case_id", "")),
        ),
    )
    domain_counts: dict[str, int] = {}
    domain_types: dict[str, set[str]] = {}
    for row in rows_sorted:
        domain = str(row.get("domain", "unscoped")).strip() or "unscoped"
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        domain_types.setdefault(domain, set()).add(str(row.get("type", "")).strip())
    domain_summary = [
        {
            "domain": d,
            "case_count": domain_counts[d],
            "types": sorted(x for x in domain_types.get(d, set()) if x),
            "anchor": _anchor_for(f"domain-{d}"),
        }
        for d in sorted(domain_counts)
    ]
    type_counts: dict[str, int] = {}
    for row in rows_sorted:
        t = str(row.get("type", ""))
        type_counts[t] = type_counts.get(t, 0) + 1
    type_summary = [
        {"type": t, "case_count": type_counts[t], "anchor": _anchor_for(t)} for t in sorted(type_counts)
    ]

    return {
        "version": 1,
        "summary": {
            "case_count": len(rows_sorted),
            "type_count": len(type_summary),
            "domain_count": len(domain_summary),
            "source_root": "/" + specs_root.resolve().relative_to(repo_root.resolve()).as_posix(),
        },
        "domains": domain_summary,
        "types": type_summary,
        "cases": rows_sorted,
    }


def _render_md(payload: dict[str, Any], *, template_path: Path, key: str) -> str:
    template = template_path.read_text(encoding="utf-8")
    return render_moustache(template, {key: payload}, strict=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate spec case doc catalog and markdown reference pages.")
    ap.add_argument("--cases", default="specs")
    ap.add_argument("--out", default=".artifacts/spec-case-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/93l_spec_case_reference.md")
    ap.add_argument("--index-out", default="docs/book/93m_spec_case_index.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    specs_root = _resolve_cli_path(repo_root, str(ns.cases))
    payload = _build_payload(repo_root, specs_root=specs_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    index_path = _resolve_cli_path(repo_root, str(ns.index_out))
    ref_block = _render_md(
        payload,
        template_path=repo_root / "docs/book/templates/spec_case_reference_template.md",
        key="catalog",
    )
    index_block = _render_md(
        payload,
        template_path=repo_root / "docs/book/templates/spec_case_index_template.md",
        key="catalog",
    )
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="spec_case_reference",
        body=ref_block,
    )
    updated_index = replace_generated_block(
        index_path.read_text(encoding="utf-8"),
        surface_id="spec_case_index",
        body=index_block,
    )

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        if parse_generated_block(
            doc_path.read_text(encoding="utf-8"),
            surface_id="spec_case_reference",
        ).strip() != ref_block.strip():
            print(f"{ns.doc_out}: generated content out of date")
            return 1
        if parse_generated_block(
            index_path.read_text(encoding="utf-8"),
            surface_id="spec_case_index",
        ).strip() != index_block.strip():
            print(f"{ns.index_out}: generated content out of date")
            return 1
        if out_path.exists() and out_path.read_text(encoding="utf-8") != expected_json:
            print(f"{ns.out}: generated content out of date")
            return 1
        return 0

    write_json(out_path, payload)
    doc_path.write_text(updated_doc, encoding="utf-8")
    index_path.write_text(updated_index, encoding="utf-8")
    print(f"wrote {ns.out}")
    print(f"wrote {ns.doc_out}")
    print(f"wrote {ns.index_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
