#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from spec_runner.docs_generators import parse_generated_block, replace_generated_block, write_json


def _resolve_cli_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return repo_root / str(raw).lstrip("/")


def _summary_keys(payload: dict[str, Any]) -> list[str]:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return []
    return sorted(str(k) for k in summary.keys())


def _segment_keys(payload: dict[str, Any]) -> dict[str, list[str]]:
    segments = payload.get("segments")
    if not isinstance(segments, dict):
        return {}
    out: dict[str, list[str]] = {}
    for segment, value in segments.items():
        if isinstance(value, dict):
            out[str(segment)] = sorted(str(k) for k in value.keys())
    return dict(sorted(out.items()))


def _build_payload(repo_root: Path) -> dict[str, Any]:
    metrics_dir = repo_root / "specs/metrics"
    files = sorted(metrics_dir.glob("*_baseline.json"))
    baselines: list[dict[str, Any]] = []
    all_summary: set[str] = set()
    all_segments: set[str] = set()
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        summary_fields = _summary_keys(payload)
        segment_fields = _segment_keys(payload)
        all_summary.update(summary_fields)
        for segment, fields in segment_fields.items():
            all_segments.add(segment)
            for field in fields:
                all_segments.add(f"{segment}.{field}")
        baselines.append(
            {
                "file": f"/{path.relative_to(repo_root).as_posix()}",
                "summary_fields": summary_fields,
                "segments": segment_fields,
                "segment_count": len(segment_fields),
            }
        )
    return {
        "version": 1,
        "summary": {
            "baseline_count": len(baselines),
            "unique_summary_field_count": len(all_summary),
            "unique_segment_field_count": len([x for x in all_segments if "." in x]),
        },
        "baselines": baselines,
        "unique_summary_fields": sorted(all_summary),
        "unique_segment_fields": sorted(x for x in all_segments if "." in x),
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = dict(payload.get("summary") or {})
    lines = [
        "## Generated Metrics Field Catalog",
        "",
        f"- baseline_count: {int(summary.get('baseline_count', 0))}",
        f"- unique_summary_field_count: {int(summary.get('unique_summary_field_count', 0))}",
        f"- unique_segment_field_count: {int(summary.get('unique_segment_field_count', 0))}",
        "",
        "| baseline | summary_fields | segment_count |",
        "|---|---|---|",
    ]
    for row in payload.get("baselines") or []:
        lines.append(
            f"| `{row.get('file', '')}` | {len(row.get('summary_fields') or [])} | {int(row.get('segment_count', 0))} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate metrics field catalog JSON and markdown section.")
    ap.add_argument("--out", default=".artifacts/metrics-field-catalog.json")
    ap.add_argument("--doc-out", default="docs/book/97_appendix_metrics_reference.md")
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    payload = _build_payload(repo_root)
    out_path = _resolve_cli_path(repo_root, str(ns.out))
    doc_path = _resolve_cli_path(repo_root, str(ns.doc_out))
    md_block = _render_md(payload)
    updated_doc = replace_generated_block(
        doc_path.read_text(encoding="utf-8"),
        surface_id="metrics_field_catalog",
        body=md_block,
    )

    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if ns.check:
        if parse_generated_block(doc_path.read_text(encoding="utf-8"), surface_id="metrics_field_catalog").strip() != md_block.strip():
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
