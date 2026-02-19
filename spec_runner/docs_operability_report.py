#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from spec_runner.quality_metrics import docs_operability_report_jsonable


def _to_markdown(payload: dict) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "# Docs Operability Report",
        "",
        f"- total docs: {int(summary.get('total_docs', 0))}",
        f"- overall docs operability ratio: {float(summary.get('overall_docs_operability_ratio', 0.0)):.4f}",
        "",
        "## Segment Summary",
        "",
        "| segment | case_count | docs_operability_ratio | runnable_example_coverage_ratio | command_doc_validation_ratio | required_sections_compliance_ratio | token_sync_compliance_ratio | opt_out_density_ratio |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for seg, row in sorted((payload.get("segments") or {}).items()):
        lines.append(
            f"| {seg} | {int(row.get('case_count', 0))} | "
            f"{float(row.get('mean_docs_operability_ratio', 0.0)):.4f} | "
            f"{float(row.get('mean_runnable_example_coverage_ratio', 0.0)):.4f} | "
            f"{float(row.get('mean_command_doc_validation_ratio', 0.0)):.4f} | "
            f"{float(row.get('mean_required_sections_compliance_ratio', 0.0)):.4f} | "
            f"{float(row.get('mean_token_sync_compliance_ratio', 0.0)):.4f} | "
            f"{float(row.get('mean_opt_out_density_ratio', 0.0)):.4f} |"
        )
    return "\n".join(lines) + "\n"


def _load_config(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise TypeError("config payload must be a mapping")
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Emit docs operability metric report as JSON or Markdown.")
    ap.add_argument("--out", help="Optional output path for report.")
    ap.add_argument("--format", choices=("json", "md"), default="json", help="Output format.")
    ap.add_argument("--config", default="", help="Optional YAML/JSON config file path.")
    ns = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]
    config: dict | None = None
    if str(ns.config).strip():
        config = _load_config(Path(str(ns.config)))

    payload = docs_operability_report_jsonable(repo_root, config=config)
    raw = _to_markdown(payload) if ns.format == "md" else json.dumps(payload, indent=2, sort_keys=True) + "\n"

    if ns.out:
        out = Path(ns.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(raw, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(raw, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
